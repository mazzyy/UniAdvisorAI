import google.generativeai as genai
import os
import PyPDF2
import docx
import json
import io
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DocumentParser:
    """
    Parse academic documents and extract structured information using Gemini
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    
    def extract_text_from_pdf(self, file_content):
        """Extract text from PDF"""
        try:
            # Create a BytesIO object from file content
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            print(f"📄 PDF has {len(pdf_reader.pages)} pages")
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                print(f"Page {i+1} extracted {len(page_text)} characters")
            
            print(f"✅ Total extracted: {len(text)} characters")
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, file_content):
        """Extract text from DOCX"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            print(f"✅ DOCX extracted: {len(text)} characters")
            return text
        except Exception as e:
            print(f"❌ Error reading DOCX: {str(e)}")
            return ""
    
    def extract_text(self, file, filename):
        """Extract text based on file type"""
        try:
            # Read file content
            file_content = file.read()
            print(f"📥 File size: {len(file_content)} bytes")
            
            if filename.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_content)
            elif filename.lower().endswith(('.docx', '.doc')):
                text = self.extract_text_from_docx(file_content)
            else:
                print(f"❌ Unsupported file format: {filename}")
                return ""
            
            # Show preview of extracted text
            if text:
                preview = text[:500].replace('\n', ' ')
                print(f"📝 Text preview: {preview}...")
            
            return text
        except Exception as e:
            print(f"❌ Error extracting text: {str(e)}")
            return ""
    
    def parse_any_document(self, document_text, doc_type="transcript"):
        """
        Parse any document (transcript, CV, degree) and extract all available information
        """
        prompt = f"""
You are an expert at extracting information from academic documents (transcripts, CVs, resumes, degree certificates).

Analyze this document carefully and extract ALL available information.

Document text:
{document_text[:4000]}

Extract and return ONLY this JSON (use null for missing fields):
{{
  "student_name": "Full name of the person",
  "email": "Email address if found",
  "phone": "Phone number if found",
  "university": "Name of university/institution",
  "degree": "Degree program (e.g., Bachelor of Science in Computer Science)",
  "major": "Major/Field of study",
  "cgpa": 3.5,
  "gpa_scale": 4.0,
  "graduation_date": "Graduation date or expected",
  "courses": ["Course 1", "Course 2"],
  "honors": "Any honors/awards",
  "skills": ["Skill 1", "Skill 2"],
  "work_experience": "Brief work experience if CV",
  "nationality": "Nationality if mentioned"
}}

IMPORTANT: 
1. Return ONLY the JSON object
2. No markdown code blocks
3. No explanations
4. Parse the actual text carefully - there IS information in this document
"""
        
        try:
            print(f"🤖 Sending {len(document_text)} characters to Gemini...")
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            print(f"📨 Gemini response length: {len(text)} characters")
            print(f"Raw response: {text[:300]}...")
            
            # Clean the response - remove markdown code blocks
            text = text.replace('```json', '').replace('```', '').strip()
            
            # Find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = text[json_start:json_end]
                print(f"🔍 Extracted JSON: {json_text[:200]}...")
                
                data = json.loads(json_text)
                print(f"✅ Successfully parsed data")
                
                # Log what we found
                for key, value in data.items():
                    if value and value != "null":
                        print(f"  ✓ {key}: {value}")
                
                return data
            else:
                print("❌ No JSON found in response")
                return None
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Failed text: {text[:500]}")
            return None
        except Exception as e:
            print(f"❌ Error parsing document: {e}")
            import traceback
            traceback.print_exc()
            return None