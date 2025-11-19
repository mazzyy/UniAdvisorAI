import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
import os
from load_data import load_all_courses, prepare_course_text
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
# Configure Gemini
# os.environ["GOOGLE_API_KEY"] = "AIzaSyC-ygakb22_-h-sQQkJI8Q8P5Xg-7CPVm8"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DAADCourseRAG:
    """
    RAG Pipeline for DAAD Course Search
    """
    
    def __init__(self, db_path="./chroma_db"):
        """
        Initialize the RAG pipeline
        
        Args:
            db_path: Path where vector database will be stored
        """
        print("🚀 Initializing DAAD Course RAG Pipeline...")
        
        # Initialize ChromaDB (vector database)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use sentence transformers for embeddings (converts text to vectors)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection (like a table in a database)
        self.collection = self.client.get_or_create_collection(
            name="daad_courses",
            embedding_function=self.embedding_function
        )
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        print("✅ RAG Pipeline initialized!")
    
    def load_courses_to_db(self, force_reload=False):
        """
        Load all courses into the vector database
        
        Args:
            force_reload: If True, delete existing data and reload
        """
        # Check if database already has data
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_reload:
            print(f"ℹ️  Database already contains {existing_count} courses")
            print("   Use force_reload=True to reload data")
            return
        
        if force_reload and existing_count > 0:
            print(f"🗑️  Deleting {existing_count} existing courses...")
            # Delete collection and recreate
            self.client.delete_collection("daad_courses")
            self.collection = self.client.get_or_create_collection(
                name="daad_courses",
                embedding_function=self.embedding_function
            )
        
        print("\n📥 Loading courses from CSV files...")
        courses_df = load_all_courses()
        
        if courses_df.empty:
            print("❌ No courses to load!")
            return
        
        print(f"\n💾 Adding {len(courses_df)} courses to vector database...")
        
        # Prepare data for ChromaDB
        documents = []  # Text descriptions
        metadatas = []  # Structured data
        ids = []        # Unique IDs
        
        for idx, row in courses_df.iterrows():
            # Create searchable text
            doc_text = prepare_course_text(row)
            documents.append(doc_text)
            
            # Store metadata (structured info we can filter on)
            metadata = {
                'course': str(row.get('course', 'N/A')),
                'institution': str(row.get('institution', 'N/A')),
                'degree_type': str(row.get('degree_type', 'N/A')),
                'url': str(row.get('url', 'N/A')),
                'source_file': str(row.get('source_file', 'N/A'))
            }
            metadatas.append(metadata)
            
            # Create unique ID
            ids.append(f"course_{idx}")
            
            # Add in batches of 100 (ChromaDB works better with batches)
            if len(documents) >= 100:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"   ✓ Added {len(documents)} courses...")
                documents, metadatas, ids = [], [], []
        
        # Add remaining courses
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   ✓ Added {len(documents)} courses...")
        
        total_count = self.collection.count()
        print(f"\n✅ Database now contains {total_count} courses!")
    
    def search_courses(self, query, n_results=5, degree_filter=None):
        """
        Search for relevant courses
        
        Args:
            query: User's search question
            n_results: Number of courses to return
            degree_filter: Filter by degree type (e.g., 'Bachelor', 'Masters', 'PhD')
        
        Returns:
            List of relevant courses
        """
        print(f"\n🔍 Searching for: '{query}'")
        
        # Build filter if degree type specified
        where_filter = None
        if degree_filter:
            where_filter = {"degree_type": degree_filter}
            print(f"   Filtering by: {degree_filter}")
        
        # Search in vector database
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        print(f"✅ Found {len(results['documents'][0])} relevant courses\n")
        
        return results
    
    def generate_answer(self, query, search_results):
        """
        Use Gemini to generate a helpful answer based on search results
        
        Args:
            query: User's question
            search_results: Results from vector database search
        
        Returns:
            Generated answer from Gemini
        """
        # Extract course information
        courses = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        
        # Build context for Gemini
        context = "Here are relevant DAAD courses:\n\n"
        
        for i, (course_text, metadata) in enumerate(zip(courses, metadatas), 1):
            context += f"--- Course {i} ---\n"
            context += course_text
            context += f"\nURL: {metadata.get('url', 'N/A')}\n\n"
        
        # Create prompt for Gemini
        prompt = f"""You are a helpful study abroad advisor for German universities.

User Question: {query}

{context}

Based on the courses above, provide a helpful and detailed answer to the user's question.
Include specific course names, institutions, and URLs when relevant.
If admission or language requirements are mentioned, include those details.
Be friendly and encouraging!"""
        
        print("🤖 Generating answer with Gemini...\n")
        
        # Generate response
        response = self.model.generate_content(prompt)
        
        return response.text
    
    def ask(self, query, n_results=5, degree_filter=None):
        """
        Main method: Ask a question and get an AI-generated answer
        
        Args:
            query: User's question
            n_results: Number of courses to consider
            degree_filter: Filter by degree type
        
        Returns:
            AI-generated answer
        """
        # Step 1: Search for relevant courses
        search_results = self.search_courses(query, n_results, degree_filter)
        
        # Step 2: Generate answer with Gemini
        answer = self.generate_answer(query, search_results)
        
        return answer


def main():
    """
    Example usage
    """
    print("="*60)
    print("DAAD COURSE RAG PIPELINE")
    print("="*60)
    
    # Initialize RAG pipeline
    rag = DAADCourseRAG()
    
    # Load courses into database (only needed once)
    rag.load_courses_to_db(force_reload=False)
    
    print("\n" + "="*60)
    print("EXAMPLE QUERIES")
    print("="*60)
    
    # Example 1: General search
    print("\n" + "-"*60)
    print("Query 1: Computer Science courses")
    print("-"*60)
    answer = rag.ask("I want to study Computer Science in Germany. What are my options?")
    print(answer)
    
    # Example 2: Filter by degree
    print("\n" + "-"*60)
    print("Query 2: PhD programs")
    print("-"*60)
    answer = rag.ask(
        "What PhD programs are available in AI or Machine Learning?",
        degree_filter="PhD"
    )
    print(answer)
    
    # Example 3: Specific requirements
    print("\n" + "-"*60)
    print("Query 3: English-taught programs")
    print("-"*60)
    answer = rag.ask("Which universities offer English-taught Masters programs?")
    print(answer)


if __name__ == "__main__":
    main()