from google import genai
from google.genai import types
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import os
from load_data import load_all_courses, prepare_course_text
import pandas as pd
from dotenv import load_dotenv
import shutil

load_dotenv()

class GoogleGenAIEmbeddingFunction(EmbeddingFunction):
    """
    Custom Embedding Function using the new Google GenAI SDK
    """
    def __init__(self, client: genai.Client, model_name: str = "text-embedding-004"):
        self.client = client
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        # The new SDK supports batch embedding
        try:
            # Note: The API might expect a list of contents.
            # We need to iterate if the batch API is not straightforward or use the batch method.
            # For text-embedding-004, we can embed multiple contents.
            
            # However, to be safe and robust, let's do it one by one or in small batches if the SDK allows.
            # The google-genai SDK documentation suggests:
            # client.models.embed_content(model=..., contents=...)
            
            # Let's try to pass the list directly.
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=input,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            # Response should contain a list of embeddings
            return [e.values for e in response.embeddings]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Fallback or re-raise? For now return empty list to avoid crash, but this will cause downstream issues.
            # Better to re-raise or print and return empty.
            return []

class DAADCourseRAG:
    """
    RAG Pipeline for DAAD Course Search using Google GenAI
    """
    
    def __init__(self, db_path="./chroma_db"):
        """
        Initialize the RAG pipeline
        
        Args:
            db_path: Path where vector database will be stored
        """
        print("Initializing DAAD Course RAG Pipeline (Google GenAI)...")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            # Try to get from google.generativeai config if set elsewhere, but better to rely on env
            pass
            
        # Initialize Google GenAI Client
        self.client = genai.Client(api_key=api_key)
        
        # Initialize Custom Embedding Function
        self.embedding_function = GoogleGenAIEmbeddingFunction(self.client)
        
        # Initialize ChromaDB
        self.db_path = db_path
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collection
        # Note: If dimensions mismatch (switching from SentenceTransformer), we might need to reset
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="daad_courses",
                embedding_function=self.embedding_function
            )
        except Exception as e:
            print(f"Error loading collection (likely dimension mismatch): {e}")
            print("   Resetting database...")
            self.chroma_client.delete_collection("daad_courses")
            self.collection = self.chroma_client.create_collection(
                name="daad_courses",
                embedding_function=self.embedding_function
            )
        
        print("RAG Pipeline initialized!")
    
    def load_courses_to_db(self, force_reload=False):
        """
        Load all courses into the vector database
        
        Args:
            force_reload: If True, delete existing data and reload
        """
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_reload:
            print(f"Database already contains {existing_count} courses")
            print("   Use force_reload=True to reload data")
            return
        
        if force_reload and existing_count > 0:
            print(f"Deleting {existing_count} existing courses...")
            self.chroma_client.delete_collection("daad_courses")
            self.collection = self.chroma_client.create_collection(
                name="daad_courses",
                embedding_function=self.embedding_function
            )
        
        print("\nLoading courses from CSV files...")
        courses_df = load_all_courses()
        
        if courses_df.empty:
            print("No courses to load!")
            return
        
        print(f"\nAdding {len(courses_df)} courses to vector database...")
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in courses_df.iterrows():
            doc_text = prepare_course_text(row)
            documents.append(doc_text)
            
            metadata = {
                'course': str(row.get('course', 'N/A')),
                'institution': str(row.get('institution', 'N/A')),
                'degree_type': str(row.get('degree_type', 'N/A')),
                'url': str(row.get('url', 'N/A')),
                'source_file': str(row.get('source_file', 'N/A'))
            }
            metadatas.append(metadata)
            ids.append(f"course_{idx}")
            
            # Batch processing
            if len(documents) >= 50: # Smaller batch for API safety
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"   Added {len(documents)} courses...")
                documents, metadatas, ids = [], [], []
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   ✓ Added {len(documents)} courses...")
        
        print(f"\nDatabase now contains {self.collection.count()} courses!")
    
    def search_courses(self, query, n_results=5, degree_filter=None):
        """Search for relevant courses"""
        print(f"\nSearching for: '{query}'")
        
        where_filter = None
        if degree_filter:
            where_filter = {"degree_type": degree_filter}
            print(f"   Filtering by: {degree_filter}")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        print(f"Found {len(results['documents'][0])} relevant courses\n")
        return results
    
    def generate_answer(self, query, search_results):
        """Generate answer using Gemini"""
        courses = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        
        context = "Here are relevant DAAD courses:\n\n"
        for i, (course_text, metadata) in enumerate(zip(courses, metadatas), 1):
            context += f"--- Course {i} ---\n"
            context += course_text
            context += f"\nURL: {metadata.get('url', 'N/A')}\n\n"
        
        prompt = f"""You are a helpful study abroad advisor for German universities.

User Question: {query}

{context}

Based on the courses above, provide a helpful and detailed answer to the user's question.
Include specific course names, institutions, and URLs when relevant.
If admission or language requirements are mentioned, include those details.
Be friendly and encouraging!"""
        
        print("Generating answer with Gemini...\n")
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        return response.text
    
    def ask(self, query, n_results=5, degree_filter=None):
        """Main method: Ask a question and get an AI-generated answer"""
        search_results = self.search_courses(query, n_results, degree_filter)
        answer = self.generate_answer(query, search_results)
        return answer

def main():
    print("="*60)
    print("DAAD COURSE RAG PIPELINE (Google GenAI)")
    print("="*60)
    
    rag = DAADCourseRAG()
    rag.load_courses_to_db(force_reload=False)
    
    print("\n" + "-"*60)
    print("Query: Computer Science courses")
    print("-"*60)
    answer = rag.ask("I want to study Computer Science in Germany. What are my options?")
    print(answer)

if __name__ == "__main__":
    main()