from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import traceback
import os

from document_parser import DocumentParser
from rag_pipeline import DAADCourseRAG

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = DocumentParser()
rag = DAADCourseRAG()

# Load courses into the vector store at startup
rag.load_courses_to_db()

# Simple in‑memory session store (replace with a DB for production)
user_sessions: Dict[str, Dict[str, Any]] = {}

@app.post("/api/parse-documents")
async def parse_documents(
    transcript: Optional[UploadFile] = File(None),
    cv: Optional[UploadFile] = File(None),
    degree: Optional[UploadFile] = File(None),
    language_cert: Optional[UploadFile] = File(None),
):
    """Parse uploaded documents and extract structured data.
    Accepts up to four files (PDF or DOCX) and returns a JSON payload
    containing personal, academic and language information.
    """
    print("\n" + "=" * 60)
    print("NEW DOCUMENT PARSING REQUEST")
    print("=" * 60)
    try:
        files = {
            "transcript": transcript,
            "cv": cv,
            "degree": degree,
            "language_cert": language_cert,
        }
        # Filter out None values
        received = {k: v for k, v in files.items() if v is not None}
        print(f"Files received: {list(received.keys())}")
        if not received:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No files uploaded"},
            )

        extracted_data = {
            "personal_info": {},
            "academic_info": {},
            "language_info": {},
            "raw_documents": {},
        }
        documents_to_parse: List[tuple] = []

        # Helper to process a single file
        async def process_file(key: str, upload: UploadFile):
            print(f"\n📄 Processing {key.upper()}...")
            print(f"Filename: {upload.filename}")
            print(f"Content-Type: {upload.content_type}")
            try:
                # Read file bytes and pass a file‑like object to the parser
                contents = await upload.read()
                # Rewind for parser if it expects a stream
                from io import BytesIO
                file_obj = BytesIO(contents)
                text = parser.extract_text(file_obj, upload.filename)
                if text and len(text) > 50:
                    documents_to_parse.append((key, text))
                    extracted_data["raw_documents"][key] = text[:500]
                    print(f"Extracted {len(text)} characters from {key}")
                else:
                    print(f"No text extracted from {key}")
            except Exception as e:
                print(f"Error processing {key}: {str(e)}")
                traceback.print_exc()

        # Process each provided file
        for key, upload in received.items():
            await process_file(key, upload)

        if not documents_to_parse:
            print("No documents could be processed")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Could not extract text from any uploaded documents. Please check file formats (PDF or DOCX only).",
                },
            )

        print(f"\nParsing {len(documents_to_parse)} documents with Gemini...")
        for doc_type, text in documents_to_parse:
            print(f"\n--- Parsing {doc_type} ---")
            try:
                parsed = parser.parse_any_document(text, doc_type)
                if parsed:
                    # Merge personal info
                    if parsed.get("student_name") and not extracted_data["personal_info"].get("name"):
                        extracted_data["personal_info"]["name"] = parsed["student_name"]
                    if parsed.get("email"):
                        extracted_data["personal_info"]["email"] = parsed["email"]
                    if parsed.get("phone"):
                        extracted_data["personal_info"]["phone"] = parsed["phone"]
                    if parsed.get("nationality"):
                        extracted_data["personal_info"]["nationality"] = parsed["nationality"]
                    # Merge academic info
                    for field in [
                        "university",
                        "degree",
                        "major",
                        "cgpa",
                        "gpa_scale",
                        "graduation_date",
                        "courses",
                        "honors",
                        "skills",
                    ]:
                        if parsed.get(field):
                            extracted_data["academic_info"][field] = parsed[field]
                    print(f"✅ Successfully parsed {doc_type}")
                else:
                    print(f"Failed to parse {doc_type}")
            except Exception as e:
                print(f"Error parsing {doc_type}: {str(e)}")
                traceback.print_exc()

        print("\n" + "=" * 60)
        print("DOCUMENT PARSING COMPLETED")
        print("=" * 60)
        print("Extracted Data Summary:")
        print(f"Personal Info: {extracted_data['personal_info']}")
        print(f"Academic Info: {extracted_data['academic_info']}")
        print(f"Language Info: {extracted_data['language_info']}")
        print("=" * 60 + "\n")
        return JSONResponse(content={"success": True, "data": extracted_data})
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Server error: {str(e)}"},
        )

@app.post("/api/save-application")
async def save_application(request: Request):
    """Save completed application form for a user."""
    try:
        print("\nSaving application...")
        data = await request.json()
        user_id = data.get("userId")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing userId")
        user_sessions[user_id] = {
            "profile": data.get("profile"),
            "countries": data.get("countries"),
            "preferences": data.get("preferences"),
        }
        print(f"Application saved for user: {user_id}")
        return JSONResponse(content={"success": True, "message": "Application saved successfully"})
    except Exception as e:
        print(f"Error saving application: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )

@app.post("/api/get-recommendations")
async def get_recommendations(request: Request):
    """Get top university recommendations based on user profile and query."""
    try:
        print("\n" + "=" * 60)
        print("GETTING UNIVERSITY RECOMMENDATIONS")
        print("=" * 60)
        data = await request.json()
        user_id = data.get("userId")
        query = data.get("query")
        print(f"User ID: {user_id}")
        print(f"Query: {query}")
        search_results = rag.search_courses(query, n_results=10)
        recommendations: List[Dict[str, Any]] = []
        if search_results and "metadatas" in search_results and len(search_results["metadatas"][0]) > 0:
            metadatas = search_results["metadatas"][0]
            documents = search_results["documents"][0]
            for i, (metadata, doc_text) in enumerate(zip(metadatas, documents)):
                lines = doc_text.split("\n")
                admission_req = language_req = deadline = ""
                for line in lines:
                    if "Admission Requirements:" in line:
                        admission_req = line.split("Admission Requirements:")[1].strip()
                    elif "Language Requirements:" in line:
                        language_req = line.split("Language Requirements:")[1].strip()
                    elif "Deadline:" in line:
                        deadline = line.split("Deadline:")[1].strip()
                recommendation = {
                    "course": metadata.get("course", "N/A"),
                    "institution": metadata.get("institution", "N/A"),
                    "url": metadata.get("url", "#"),
                    "degree_type": metadata.get("degree_type", "N/A"),
                    "admission_requirements": admission_req,
                    "language_requirements": language_req,
                    "deadline": deadline,
                    "match_score": max(70, min(95, 85 + (i * -2))),
                }
                recommendations.append(recommendation)
                print(f"Found: {recommendation['course']} at {recommendation['institution']}")
        print(f"\nReturning {len(recommendations)} recommendations")
        print("=" * 60 + "\n")
        return JSONResponse(content={"success": True, "recommendations": recommendations})
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )

@app.post("/api/chat-with-recommendations")
async def chat_with_recommendations(request: Request):
    """Chat endpoint that can also return new recommendations based on the query."""
    try:
        print("\nChat with recommendations request")
        data = await request.json()
        query = data.get("query")
        user_id = data.get("userId")
        user_data = user_sessions.get(user_id, {})
        enhanced_query = query
        if user_data:
            profile = user_data.get("profile", {})
            countries = user_data.get("countries", [])
            context = f"\nUser Context: Looking for {profile.get('desired_degree')} in {profile.get('field_of_study')}."
            if countries:
                context += f" Interested in: {', '.join(countries)}."
            enhanced_query = query + context
        answer = rag.ask(enhanced_query, n_results=5)
        formatted = format_response(answer)
        recommendation_keywords = ["recommend", "suggest", "show", "find", "best", "top", "university", "program"]
        needs_recommendations = any(keyword in query.lower() for keyword in recommendation_keywords)
        new_recommendations: List[Dict[str, Any]] = []
        if needs_recommendations:
            search_results = rag.search_courses(query, n_results=3)
            if search_results and "metadatas" in search_results:
                metadatas = search_results["metadatas"][0]
                documents = search_results["documents"][0]
                for metadata, doc_text in zip(metadatas, documents):
                    lines = doc_text.split("\n")
                    admission_req = language_req = deadline = ""
                    for line in lines:
                        if "Admission Requirements:" in line:
                            admission_req = line.split("Admission Requirements:")[1].strip()
                        elif "Language Requirements:" in line:
                            language_req = line.split("Language Requirements:")[1].strip()
                        elif "Deadline:" in line:
                            deadline = line.split("Deadline:")[1].strip()
                    new_recommendations.append({
                        "course": metadata.get("course", "N/A"),
                        "institution": metadata.get("institution", "N/A"),
                        "url": metadata.get("url", "#"),
                        "degree_type": metadata.get("degree_type", "N/A"),
                        "admission_requirements": admission_req,
                        "language_requirements": language_req,
                        "deadline": deadline,
                        "match_score": 88,
                    })
        return JSONResponse(
            content={
                "success": True,
                "response": formatted,
                "new_recommendations": new_recommendations if new_recommendations else None,
            }
        )
    except Exception as e:
        print(f"Chat error: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )

def format_response(text: str) -> List[Dict[str, Any]]:
    """Format response into structured sections for the frontend."""
    sections: List[Dict[str, Any]] = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line and line[0].isdigit() and "." in line[:4]:
            sections.append({"type": "numbered", "content": line})
        elif line.startswith("*") or line.startswith("-") or line.startswith("•"):
            sections.append({"type": "bullet", "content": line.lstrip("*-• ")})
        elif line.startswith("**") and line.endswith("**"):
            sections.append({"type": "header", "content": line.strip("*")})
        else:
            sections.append({"type": "text", "content": line})
    return sections

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy", "message": "API is running"})

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("DAAD Application System API Started (FastAPI)")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)