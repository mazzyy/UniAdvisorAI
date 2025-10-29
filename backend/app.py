from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from document_parser import DocumentParser
from rag_pipeline import DAADCourseRAG

app = Flask(__name__)
CORS(app)

# Initialize services
parser = DocumentParser()
rag = DAADCourseRAG()
rag.load_courses_to_db()

# Store sessions
user_sessions = {}

@app.route('/api/parse-documents', methods=['POST'])
def parse_documents():
    """
    Parse uploaded documents and extract data
    """
    try:
        files = request.files
        
        extracted_data = {
            'personal_info': {},
            'academic_info': {},
            'language_info': {},
            'raw_documents': {}
        }
        
        # Parse transcript
        if 'transcript' in files:
            file = files['transcript']
            text = parser.extract_text(file, file.filename)
            extracted_data['raw_documents']['transcript'] = text[:500]
            
            transcript_data = parser.parse_transcript(text)
            if transcript_data:
                extracted_data['personal_info']['name'] = transcript_data.get('student_name')
                extracted_data['academic_info']['university'] = transcript_data.get('university')
                extracted_data['academic_info']['degree'] = transcript_data.get('degree')
                extracted_data['academic_info']['major'] = transcript_data.get('major')
                extracted_data['academic_info']['cgpa'] = transcript_data.get('cgpa')
                extracted_data['academic_info']['gpa_scale'] = transcript_data.get('gpa_scale')
                extracted_data['academic_info']['graduation_date'] = transcript_data.get('graduation_date')
                extracted_data['academic_info']['courses'] = transcript_data.get('courses', [])
        
        # Parse degree certificate
        if 'degree' in files:
            file = files['degree']
            text = parser.extract_text(file, file.filename)
            extracted_data['raw_documents']['degree'] = text[:500]
            
            degree_data = parser.parse_degree_certificate(text)
            if degree_data:
                if not extracted_data['personal_info'].get('name'):
                    extracted_data['personal_info']['name'] = degree_data.get('student_name')
                if not extracted_data['academic_info'].get('degree'):
                    extracted_data['academic_info']['degree'] = degree_data.get('degree')
                extracted_data['academic_info']['classification'] = degree_data.get('classification')
        
        # Parse language certificate
        if 'language_cert' in files:
            file = files['language_cert']
            text = parser.extract_text(file, file.filename)
            extracted_data['raw_documents']['language_cert'] = text[:500]
            
            lang_data = parser.parse_language_certificate(text)
            if lang_data:
                extracted_data['language_info'] = lang_data
        
        return jsonify({
            'success': True,
            'data': extracted_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-application', methods=['POST'])
def save_application():
    """
    Save completed application form
    """
    try:
        data = request.json
        user_id = data.get('userId')
        
        user_sessions[user_id] = {
            'profile': data.get('profile'),
            'countries': data.get('countries'),
            'preferences': data.get('preferences')
        }
        
        return jsonify({
            'success': True,
            'message': 'Application saved successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint with context
    """
    try:
        data = request.json
        query = data.get('query')
        user_id = data.get('userId')
        
        # Get user context
        user_data = user_sessions.get(user_id, {})
        
        # Build enhanced query
        enhanced_query = query
        if user_data:
            profile = user_data.get('profile', {})
            countries = user_data.get('countries', [])
            
            context = f"\nUser Context: Looking for {profile.get('desired_degree')} in {profile.get('field_of_study')}."
            if countries:
                context += f" Interested in: {', '.join(countries)}."
            
            enhanced_query = query + context
        
        # Get answer from RAG
        answer = rag.ask(enhanced_query, n_results=5)
        
        # Format response
        formatted = format_response(answer)
        
        return jsonify({
            'success': True,
            'response': formatted
        })
    
    except Exception as e:
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
        
        # Numbered items
        if line and line[0].isdigit() and '.' in line[:4]:
            sections.append({
                'type': 'numbered',
                'content': line
            })
        # Bullet points
        elif line.startswith('*') or line.startswith('-') or line.startswith('•'):
            sections.append({
                'type': 'bullet',
                'content': line.lstrip('*-• ')
            })
        # Headers (bold text with **)
        elif line.startswith('**') and line.endswith('**'):
            sections.append({
                'type': 'header',
                'content': line.strip('*')
            })
        # Regular text
        else:
            sections.append({
                'type': 'text',
                'content': line
            })
    
    return sections

if __name__ == '__main__':
    print("🚀 DAAD Application System API Started")
    app.run(debug=True, port=5000)