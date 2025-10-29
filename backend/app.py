from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from document_parser import DocumentParser
from rag_pipeline import DAADCourseRAG

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3001", "http://127.0.0.1:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

parser = DocumentParser()
rag = DAADCourseRAG()
rag.load_courses_to_db()

user_sessions = {}

@app.route('/api/parse-documents', methods=['POST'])
def parse_documents():
    """
    Parse uploaded documents and extract data
    """
    try:
        print("\n" + "="*60)
        print("📥 NEW DOCUMENT PARSING REQUEST")
        print("="*60)
        
        files = request.files
        print(f"📁 Files received: {list(files.keys())}")
        
        extracted_data = {
            'personal_info': {},
            'academic_info': {},
            'language_info': {},
            'raw_documents': {}
        }
        
        # Process each document type
        documents_to_parse = []
        
        # Transcript
        if 'transcript' in files:
            print("\n📄 Processing TRANSCRIPT...")
            file = files['transcript']
            print(f"Filename: {file.filename}")
            text = parser.extract_text(file, file.filename)
            
            if text and len(text) > 50:
                documents_to_parse.append(('transcript', text))
                extracted_data['raw_documents']['transcript'] = text[:500]
            else:
                print("⚠️  No text extracted from transcript")
        
        # CV/Resume
        if 'cv' in files:
            print("\n📄 Processing CV/RESUME...")
            file = files['cv']
            print(f"Filename: {file.filename}")
            text = parser.extract_text(file, file.filename)
            
            if text and len(text) > 50:
                documents_to_parse.append(('cv', text))
                extracted_data['raw_documents']['cv'] = text[:500]
            else:
                print("⚠️  No text extracted from CV")
        
        # Degree
        if 'degree' in files:
            print("\n📜 Processing DEGREE CERTIFICATE...")
            file = files['degree']
            print(f"Filename: {file.filename}")
            text = parser.extract_text(file, file.filename)
            
            if text and len(text) > 50:
                documents_to_parse.append(('degree', text))
                extracted_data['raw_documents']['degree'] = text[:500]
            else:
                print("⚠️  No text extracted from degree")
        
        # Language Certificate
        if 'language_cert' in files:
            print("\n🌍 Processing LANGUAGE CERTIFICATE...")
            file = files['language_cert']
            print(f"Filename: {file.filename}")
            text = parser.extract_text(file, file.filename)
            
            if text and len(text) > 50:
                documents_to_parse.append(('language_cert', text))
                extracted_data['raw_documents']['language_cert'] = text[:500]
            else:
                print("⚠️  No text extracted from language certificate")
        
        # Parse all documents and merge data
        print(f"\n🔄 Parsing {len(documents_to_parse)} documents with Gemini...")
        
        for doc_type, text in documents_to_parse:
            print(f"\n--- Parsing {doc_type} ---")
            parsed = parser.parse_any_document(text, doc_type)
            
            if parsed:
                # Merge personal info
                if parsed.get('student_name') and not extracted_data['personal_info'].get('name'):
                    extracted_data['personal_info']['name'] = parsed['student_name']
                if parsed.get('email'):
                    extracted_data['personal_info']['email'] = parsed['email']
                if parsed.get('phone'):
                    extracted_data['personal_info']['phone'] = parsed['phone']
                if parsed.get('nationality'):
                    extracted_data['personal_info']['nationality'] = parsed['nationality']
                
                # Merge academic info
                if parsed.get('university'):
                    extracted_data['academic_info']['university'] = parsed['university']
                if parsed.get('degree'):
                    extracted_data['academic_info']['degree'] = parsed['degree']
                if parsed.get('major'):
                    extracted_data['academic_info']['major'] = parsed['major']
                if parsed.get('cgpa'):
                    extracted_data['academic_info']['cgpa'] = parsed['cgpa']
                if parsed.get('gpa_scale'):
                    extracted_data['academic_info']['gpa_scale'] = parsed['gpa_scale']
                if parsed.get('graduation_date'):
                    extracted_data['academic_info']['graduation_date'] = parsed['graduation_date']
                if parsed.get('courses'):
                    extracted_data['academic_info']['courses'] = parsed['courses']
                if parsed.get('honors'):
                    extracted_data['academic_info']['honors'] = parsed['honors']
                if parsed.get('skills'):
                    extracted_data['academic_info']['skills'] = parsed['skills']
                
                # Language info (for language certificates)
                if doc_type == 'language_cert':
                    extracted_data['language_info'] = {
                        'test_type': parsed.get('test_type'),
                        'overall_score': parsed.get('overall_score')
                    }
        
        print("\n" + "="*60)
        print("✅ DOCUMENT PARSING COMPLETED")
        print("="*60)
        print("📊 Extracted Data Summary:")
        print(f"Personal Info: {extracted_data['personal_info']}")
        print(f"Academic Info: {extracted_data['academic_info']}")
        print(f"Language Info: {extracted_data['language_info']}")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'data': extracted_data
        })
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-application', methods=['POST'])
def save_application():
    """Save completed application form"""
    try:
        print("\n💾 Saving application...")
        data = request.json
        user_id = data.get('userId')
        
        user_sessions[user_id] = {
            'profile': data.get('profile'),
            'countries': data.get('countries'),
            'preferences': data.get('preferences')
        }
        
        print(f"✅ Application saved for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Application saved successfully'
        })
    
    except Exception as e:
        print(f"❌ Error saving application: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with context"""
    try:
        print("\n💬 Chat request received")
        data = request.json
        query = data.get('query')
        user_id = data.get('userId')
        
        user_data = user_sessions.get(user_id, {})
        
        enhanced_query = query
        if user_data:
            profile = user_data.get('profile', {})
            countries = user_data.get('countries', [])
            
            context = f"\nUser Context: Looking for {profile.get('desired_degree')} in {profile.get('field_of_study')}."
            if countries:
                context += f" Interested in: {', '.join(countries)}."
            
            enhanced_query = query + context
        
        answer = rag.ask(enhanced_query, n_results=5)
        formatted = format_response(answer)
        
        return jsonify({
            'success': True,
            'response': formatted
        })
    
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_response(text):
    """Format response into structured sections"""
    sections = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line and line[0].isdigit() and '.' in line[:4]:
            sections.append({'type': 'numbered', 'content': line})
        elif line.startswith('*') or line.startswith('-') or line.startswith('•'):
            sections.append({'type': 'bullet', 'content': line.lstrip('*-• ')})
        elif line.startswith('**') and line.endswith('**'):
            sections.append({'type': 'header', 'content': line.strip('*')})
        else:
            sections.append({'type': 'text', 'content': line})
    
    return sections

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

if __name__ == '__main__':
    print("="*60)
    print("🚀 DAAD Application System API Started")
    print("="*60)
    app.run(debug=True, port=5000, host='0.0.0.0')