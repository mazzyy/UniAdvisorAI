import google.generativeai as genai
import os
import PyPDF2
import docx
import json
import io
import pymupdf
from paddleocr import PaddleOCR
from PIL import Image
from dotenv import load_dotenv
import numpy as np

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize once globally (English model, you can change)
ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

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
    
    def extract_text(self, file_content, filename):
        """Extract text based on file type"""
        try:
            
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

    
    def parse_images(self, file_content, filename, output_folder="extracted_images"):
        print("parse_images")
        
        os.makedirs(output_folder, exist_ok=True)

        
        doc = pymupdf.open(stream=file_content, filetype="pdf")
        image_found = False
        image_count = 0

        ocr_text = ''
        for page_number, page in enumerate(doc, start=1):
            print("page_number ",page_number)
            image_list = page.get_images(full=True)

            if len(image_list) > 0:
                print("Image Found")
                image_found = True
                
                
                for img_index, img in enumerate(image_list, start=1):
                    xref = img[0]  # XREF of the image
                    base_image = doc.extract_image(xref)

                    image_bytes = base_image["image"]
                    ocr_text += f" {self.transcribe_image(image_bytes)}"
                    # print("ocr_text: ",ocr_text)
                    image_ext = base_image["ext"]

                    image_filename = os.path.join(
                        output_folder,
                        f"{filename}_page{page_number}_img{img_index}.{image_ext}"
                    )

                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)

                    image_count += 1
            print("----"*10)

        if image_found:
            print(f"Found and extracted {image_count} images.")
            print(f"OCR of extracted images: {ocr_text} ")
        else:
            print("No images found in the PDF.")

        return image_found, image_count, ocr_text
    
    def transcribe_image(self, image_bytes: bytes) -> str:
        """
        Run OCR on a single image (in bytes) and return extracted text.
        """
        try:
            # Convert bytes → PIL image
            image = Image.open(io.BytesIO(image_bytes))

            # PaddleOCR expects a file path or numpy array
            img_np = np.array(image)

            # Run OCR
            result = ocr_model.ocr(img_np)
            
            # print("RESULT: ",result)
            # print("type(result[0]): ", type(result[0]))

            # Extract text from result structure
            # extracted_text = ' '.join(result['rec_texts'])
            # print("result[0]['rec_texts'] : ", result[0]['rec_texts'])
            # for line in result:
            #     for part in line:
            #         extracted_text.append(part[1][0])   # part[1][0] = text

            return "\n".join(result[0]['rec_texts'])

        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return ""
    