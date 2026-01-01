from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from document_parser import DocumentParser
from rag_pipeline import DAADCourseRAG

app = Flask(__name__)

CORS(app)

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
        
        if not files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
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
            print(f"Content-Type: {file.content_type}")
            
            try:
                text = parser.extract_text(file, file.filename)
                
                if text and len(text) > 50:
                    documents_to_parse.append(('transcript', text))
                    extracted_data['raw_documents']['transcript'] = text[:500]
                    print(f"✅ Extracted {len(text)} characters from transcript")
                else:
                    print("⚠️  No text extracted from transcript")
            except Exception as e:
                print(f"❌ Error processing transcript: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # CV/Resume
        if 'cv' in files:
            print("\n📄 Processing CV/RESUME...")
            file = files['cv']
            print(f"Filename: {file.filename}")
            print(f"Content-Type: {file.content_type}")
            
            try:
                text = parser.extract_text(file, file.filename)
                
                if text and len(text) > 50:
                    documents_to_parse.append(('cv', text))
                    extracted_data['raw_documents']['cv'] = text[:500]
                    print(f"✅ Extracted {len(text)} characters from CV")
                else:
                    print("⚠️  No text extracted from CV")
            except Exception as e:
                print(f"❌ Error processing CV: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Degree
        if 'degree' in files:
            print("\n📜 Processing DEGREE CERTIFICATE...")
            file = files['degree']
            print(f"Filename: {file.filename}")
            
            try:
                text = parser.extract_text(file, file.filename)
                
                if text and len(text) > 50:
                    documents_to_parse.append(('degree', text))
                    extracted_data['raw_documents']['degree'] = text[:500]
                    print(f"✅ Extracted {len(text)} characters from degree")
                else:
                    print("⚠️  No text extracted from degree")
            except Exception as e:
                print(f"❌ Error processing degree: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Language Certificate
        if 'language_cert' in files:
            print("\n🌍 Processing LANGUAGE CERTIFICATE...")
            file = files['language_cert']
            print(f"Filename: {file.filename}")
            
            try:
                text = parser.extract_text(file, file.filename)
                
                if text and len(text) > 50:
                    documents_to_parse.append(('language_cert', text))
                    extracted_data['raw_documents']['language_cert'] = text[:500]
                    print(f"✅ Extracted {len(text)} characters from language cert")
                else:
                    print("⚠️  No text extracted from language certificate")
            except Exception as e:
                print(f"❌ Error processing language cert: {str(e)}")
                import traceback
                traceback.print_exc()
        
        if not documents_to_parse:
            print("❌ No documents could be processed")
            return jsonify({
                'success': False,
                'error': 'Could not extract text from any uploaded documents. Please check file formats (PDF or DOCX only).'
            }), 400
        
        # Parse all documents and merge data
        print(f"\n🔄 Parsing {len(documents_to_parse)} documents with Gemini...")
        
        for doc_type, text in documents_to_parse:
            print(f"\n--- Parsing {doc_type} ---")
            try:
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
                    
                    print(f"✅ Successfully parsed {doc_type}")
                else:
                    print(f"⚠️  Failed to parse {doc_type}")
            except Exception as e:
                print(f"❌ Error parsing {doc_type}: {str(e)}")
                import traceback
                traceback.print_exc()
        
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
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
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

@app.route('/api/get-recommendations', methods=['POST'])
def get_recommendations():
    """
    Get top university recommendations based on user profile
    """
    try:
        print("\n" + "="*60)
        print("🎓 GETTING UNIVERSITY RECOMMENDATIONS")
        print("="*60)
        
        data = request.json
        user_id = data.get('userId')
        query = data.get('query')
        
        print(f"User ID: {user_id}")
        print(f"Query: {query}")
        
        # Get recommendations from RAG
        search_results = rag.search_courses(query, n_results=10)
        
        # Format recommendations
        recommendations = []
        if search_results and 'metadatas' in search_results and len(search_results['metadatas']) > 0:
            metadatas = search_results['metadatas'][0]
            documents = search_results['documents'][0]
            
            for i, (metadata, doc_text) in enumerate(zip(metadatas, documents)):
                # Parse the document text to extract details
                lines = doc_text.split('\n')
                admission_req = ''
                language_req = ''
                deadline = ''
                
                for line in lines:
                    if 'Admission Requirements:' in line:
                        admission_req = line.split('Admission Requirements:')[1].strip()
                    elif 'Language Requirements:' in line:
                        language_req = line.split('Language Requirements:')[1].strip()
                    elif 'Deadline:' in line:
                        deadline = line.split('Deadline:')[1].strip()
                
                recommendation = {
                    'course': metadata.get('course', 'N/A'),
                    'institution': metadata.get('institution', 'N/A'),
                    'url': metadata.get('url', '#'),
                    'degree_type': metadata.get('degree_type', 'N/A'),
                    'admission_requirements': admission_req,
                    'language_requirements': language_req,
                    'deadline': deadline,
                    'match_score': max(70, min(95, 85 + (i * -2)))
                }
                recommendations.append(recommendation)
                print(f"✓ Found: {recommendation['course']} at {recommendation['institution']}")
        
        print(f"\n✅ Returning {len(recommendations)} recommendations")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        print(f"❌ Error getting recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat-with-recommendations', methods=['POST'])
def chat_with_recommendations():
    """Chat endpoint that can also return new recommendations"""
    try:
        print("\n💬 Chat with recommendations request")
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
        
        recommendation_keywords = ['recommend', 'suggest', 'show', 'find', 'best', 'top', 'university', 'program']
        needs_recommendations = any(keyword in query.lower() for keyword in recommendation_keywords)
        
        new_recommendations = []
        if needs_recommendations:
            search_results = rag.search_courses(query, n_results=3)
            
            if search_results and 'metadatas' in search_results:
                metadatas = search_results['metadatas'][0]
                documents = search_results['documents'][0]
                
                for metadata, doc_text in zip(metadatas, documents):
                    lines = doc_text.split('\n')
                    admission_req = ''
                    language_req = ''
                    deadline = ''
                    
                    for line in lines:
                        if 'Admission Requirements:' in line:
                            admission_req = line.split('Admission Requirements:')[1].strip()
                        elif 'Language Requirements:' in line:
                            language_req = line.split('Language Requirements:')[1].strip()
                        elif 'Deadline:' in line:
                            deadline = line.split('Deadline:')[1].strip()
                    
                    new_recommendations.append({
                        'course': metadata.get('course', 'N/A'),
                        'institution': metadata.get('institution', 'N/A'),
                        'url': metadata.get('url', '#'),
                        'degree_type': metadata.get('degree_type', 'N/A'),
                        'admission_requirements': admission_req,
                        'language_requirements': language_req,
                        'deadline': deadline,
                        'match_score': 88
                    })
        
        return jsonify({
            'success': True,
            'response': formatted,
            'new_recommendations': new_recommendations if new_recommendations else None
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
    app.run(debug=True, port=5001, host='0.0.0.0')