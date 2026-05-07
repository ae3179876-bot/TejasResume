from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import requests

# ================= LOAD ENV =================
load_dotenv()

# ================= FLASK APP =================
app = Flask(__name__, static_folder='.')
CORS(app)

# ================= API KEY =================
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
print(f"🔑 API Key loaded: {'✅ Yes' if GROQ_API_KEY else '❌ No'}")

# ================= HTML ROUTES =================
@app.route('/')
def py():
    return send_from_directory('.', 'welcomepage.html')

@app.route('/login')
def login():
    return send_from_directory('.', 'loginpage.html')

@app.route('/work-experience')
def work_experince():
    return send_from_directory('.', 'work-experience.html')

@app.route('/analyzer')
def analyzer():
    return send_from_directory('.', 'analyzer.html')

@app.route('/education')
def education():
    return send_from_directory('.', 'education.html')

@app.route('/project')
def project():
    return send_from_directory('.', 'project.html')

@app.route('/skill')
def skill():
    return send_from_directory('.', 'skill.html')

@app.route('/template-selection')
def template_selection():
    return send_from_directory('.', 'template-selection.html')

@app.route('/certification')
def certification():
    return send_from_directory('.', 'certification.html')

@app.route('/userpage')
def user():
    return send_from_directory('.', 'Userpage.html')

@app.route('/summary')
def summary():
    return send_from_directory('.', 'summary.html')

@app.route('/resume-analyzer')
def resume_analyzer():
    return send_from_directory('.', 'resume-analyzer.html')

# ================= GENERATE SUMMARY =================
@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    try:
        data = request.json
        user_data = data.get('userData', {})

        prompt = f"""You are an expert resume writer. Create a compelling, professional summary for:

Name: {user_data.get('firstName', '')} {user_data.get('surname', '')}
Profession: {user_data.get('profession', 'Professional')}
Location: {user_data.get('city', '')}, {user_data.get('country', '')}

Write a powerful 3-4 sentence professional summary that highlights their expertise and value proposition. Write ONLY the summary, no explanations."""

        if GROQ_API_KEY:
            print("🤖 Calling Groq API for summary generation...")

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional resume writer. Create concise, impactful summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 250
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )

            if response.status_code == 200:
                result = response.json()

                generated_summary = (
                    result.get('choices', [{}])[0]
                    .get('message', {})
                    .get('content', '')
                    .strip()
                )

                print("✅ Summary generated successfully!")

                return jsonify({
                    'success': True,
                    'summary': generated_summary,
                    'using_api': True
                })

            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)

                raise Exception(f"API returned {response.status_code}")

        else:
            fallback_summary = f"""{user_data.get('firstName', '')} {user_data.get('surname', '')} is a dedicated {user_data.get('profession', 'professional')} with strong problem-solving abilities. Committed to delivering high-quality results and continuous growth. Eager to contribute expertise to a dynamic organization."""

            return jsonify({
                'success': True,
                'summary': fallback_summary,
                'using_api': False,
                'warning': 'Using template summary (API not configured)'
            })

    except Exception as e:
        print(f"❌ Error: {str(e)}")

        fallback_summary = f"""{user_data.get('firstName', '')} {user_data.get('surname', '')} is a skilled {user_data.get('profession', 'professional')} with a passion for excellence. Brings valuable expertise and a solution-oriented mindset to every challenge."""

        return jsonify({
            'success': True,
            'summary': fallback_summary,
            'using_api': False,
            'error': str(e)
        })

# ================= RESUME ANALYZER =================
@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        data = request.json
        resume_text = data.get('resumeText', '')

        if not resume_text or len(resume_text) < 50:
            return jsonify({
                'success': False,
                'error': 'Please provide valid resume content (minimum 50 characters)'
            })

        prompt = f"""You are an expert resume analyst and ATS specialist.

Analyze the following resume:

{resume_text[:5000]}

Return ONLY valid JSON in this exact format:

{{
    "score": 85,
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "keywords": [],
    "detailed_analysis": ""
}}
"""

        if GROQ_API_KEY:
            print("🤖 Calling Groq API for resume analysis...")

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "Return ONLY valid JSON. No markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 2000
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )

            if response.status_code == 200:
                result = response.json()

                analysis_text = (
                    result.get('choices', [{}])[0]
                    .get('message', {})
                    .get('content', '')
                    .strip()
                )

                print(f"📊 AI response received")

                # ================= CLEAN JSON =================
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0]

                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0]

                analysis_text = analysis_text.strip()

                # ================= PARSE =================
                analysis = json.loads(analysis_text)

                required_fields = [
                    'score',
                    'strengths',
                    'weaknesses',
                    'suggestions',
                    'keywords',
                    'detailed_analysis'
                ]

                for field in required_fields:
                    if field not in analysis:

                        if field == 'score':
                            analysis[field] = 50

                        elif field == 'detailed_analysis':
                            analysis[field] = "Analysis generated successfully."

                        else:
                            analysis[field] = []

                print("✅ Resume analysis completed!")

                return jsonify({
                    'success': True,
                    'analysis': analysis
                })

            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)

                return jsonify({
                    'success': False,
                    'error': f'API returned status {response.status_code}'
                })

        else:
            return jsonify({
                'success': False,
                'error': 'Groq API key not configured'
            })

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {str(e)}")

        return jsonify({
            'success': False,
            'error': 'Failed to parse AI response. Please try again.'
        })

    except Exception as e:
        print(f"❌ Error in analyze-resume: {str(e)}")

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ================= START SERVER =================
if __name__ == '__main__':
    print("🚀 Starting Flask server...")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )