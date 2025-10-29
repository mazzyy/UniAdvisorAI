import google.generativeai as genai
import os
import PyPDF2
import docx
import re

os.environ["GOOGLE_API_KEY"] = "AIzaSyC-ygakb22_-h-sQQkJI8Q8P5Xg-7CPVm8"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DocumentParser:
    """
    Parse academic documents and extract structured information using Gemini
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    
    def extract_text_from_pdf(self, file):
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def extract_text_from_docx(self, file):
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def extract_text(self, file, filename):
        """Extract text based on file type"""
        if filename.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            return self.extract_text_from_docx(file)
        else:
            return "Unsupported file format"
    
    def parse_transcript(self, transcript_text):
        """
        Parse transcript and extract structured data using Gemini
        """
        prompt = f"""
You are an expert at extracting information from academic transcripts.
Analyze the following transcript and extract ONLY the information that is present. 
Return ONLY a valid JSON object with these fields (use null for missing data):

{{
  "student_name": "Full name of the student",
  "university": "Name of the university/institution",
  "degree": "Degree program (e.g., Bachelor of Science in Computer Science)",
  "major": "Major/Field of study",
  "cgpa": "CGPA or GPA (as a number)",
  "gpa_scale": "GPA scale (e.g., 4.0, 10.0)",
  "graduation_date": "Graduation date or expected graduation",
  "courses": ["List of major courses taken"],
  "honors": "Any honors or distinctions"
}}

Transcript:
{transcript_text}

Return ONLY the JSON object, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            import json
            text = response.text.strip()
            
            # Try to find JSON in the response
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"Error parsing transcript: {e}")
            return None
    
    def parse_degree_certificate(self, certificate_text):
        """
        Parse degree certificate
        """
        prompt = f"""
Extract information from this degree certificate.
Return ONLY a valid JSON object:

{{
  "student_name": "Full name",
  "degree": "Degree awarded",
  "university": "University name",
  "graduation_date": "Date of graduation",
  "classification": "Degree classification/honors if mentioned"
}}

Certificate:
{certificate_text}

Return ONLY the JSON object.
"""
        
        try:
            response = self.model.generate_content(prompt)
            import json
            text = response.text.strip()
            
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"Error parsing certificate: {e}")
            return None
    
    def parse_language_certificate(self, certificate_text):
        """
        Parse language certificate (IELTS/TOEFL/etc)
        """
        prompt = f"""
Extract information from this language test certificate.
Return ONLY a valid JSON object:

{{
  "test_type": "Type of test (IELTS, TOEFL, etc)",
  "overall_score": "Overall score",
  "test_date": "Date of test",
  "listening": "Listening score",
  "reading": "Reading score",
  "writing": "Writing score",
  "speaking": "Speaking score",
  "validity_date": "Expiry date if mentioned"
}}

Certificate:
{certificate_text}

Return ONLY the JSON object.
"""
        
        try:
            response = self.model.generate_content(prompt)
            import json
            text = response.text.strip()
            
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"Error parsing language certificate: {e}")
            return None