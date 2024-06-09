import os
import sqlite3

import PyPDF2
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template, session
from werkzeug.utils import secure_filename
from datetime import timedelta
from blueprints.authentication.authentication import authentication_bp
from blueprints.cours.cours import cours_bp
from blueprints.exercices.exercices import exercices_bp
from flask_session import Session
app = Flask(__name__)
app.register_blueprint(cours_bp)
app.secret_key="hello"
app.permanent_session_lifetime=timedelta(seconds=20)
app.register_blueprint(exercices_bp)
app.register_blueprint(authentication_bp)
app.config['UPLOAD_FOLDER'] = 'cours'
app.config['SECRET_KEY'] = 'cle_secrete'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Function to execute a SQL query
def run_query(query, args=()):
    conn = sqlite3.connect('apprentissage.db')
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()
    conn.close()
    return None


# Route for the main page
@app.route('/')
def index():
    return render_template('home.html')


@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/cours")
def cours_page():
    return render_template("cours.html")


@app.route("/exercices")
def exercices_page():
    return render_template("exercices.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    if pdf_path.endswith('.pdf'):
        try:
            if not os.path.exists(pdf_path):
                print(f"File does not exist: {pdf_path}")  # Log if file does not exist
                return None

            reader = PyPDF2.PdfReader(pdf_path)
            print(f"Number of pages: {reader.pages}")  # Log number of pages
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    else:
        return "The content is a video."


# Function to generate prompt for courses
def generate_prompt(course_text, user_question, history):
    history_text = "\n".join([f"Q: {h[0]}\nA: {h[1]}" for h in history])
    return f"""
    Here is the course content:

    {course_text}
    Previous conversations:
    {history_text}

    The student's question: "{user_question}"

    Répond à cette question pour aider l'élève à comprendre le concept brièvement et clairement ? En outre : s'il 
    existe un texte du cours, vous pouvez fournir des exemples ou des informations supplémentaires pour aider 
    l'étudiant à mieux comprendre le concept, lui donner des exercices comme des QCM à pratiquer, et l'envoyer à la 
    section du cours en question. mieux comprendre le concept, leur donner des exercices comme des QCM pour 
    s'entraîner, et les envoyer à la section du cours en question."""


# Route to handle chat messages for courses
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    print(f"Received data: {data}")  # Log to debug incoming data

    if 'course_id' not in data or 'course_url' not in data:
        return jsonify({'error': 'Missing course_id or course_url'}), 400

    user_question = data['message']
    course_id = data['course_id']
    course_url = data['course_url']
    course_text = extract_text_from_pdf(course_url)
    if not course_text:
        course_text = "the course is a video on deep learning, AI, and machine learning, or data science."
    user_id = session.get('user_id', 0)  # Get user_id from session
    history = run_query(
        "SELECT user_question, bot_response FROM chat_history WHERE course_id=? and user_id=? ORDER BY timestamp DESC "
        "LIMIT 10",
        (course_id, user_id))
    prompt = generate_prompt(course_text, user_question, history)
    image = data.get('image')
    if image:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant for an online learning platform."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                            }
                        }
                    ]
                }
            ]

        )
    else:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant for an online learning platform."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ]
                }
            ]

        )
    bot_response = response.choices[0].message.content

    # Save to chat history
    conn = sqlite3.connect('apprentissage.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (course_id, user_question, bot_response, user_id, image) VALUES (?, ?, ?, ?, ?)",
        (course_id, user_question, bot_response, user_id, image))
    conn.commit()
    conn.close()
    return jsonify({'response': bot_response})


# Function to generate prompt for exercises
def generate_exercise_prompt(exercise_text, user_question, history):
    history_text = "\n".join([f"Q: {h[0]}\nA: {h[1]}" for h in history])
    return f"""
    Voici le contenu de l'exercice:

    {exercise_text}

    Voici les précedentes conversations:
    {history_text}

    La réponse de l'étudiant est la suivante: "{user_question}"

    """


# Route to handle chat messages for exercises
@app.route('/chat_exercises', methods=['POST'])
def chat_exercises():
    data = request.get_json()
    print(f"Received data: {data}")  # Log to debug incoming data

    if 'exercice_id' not in data or 'exercice_url' not in data:
        return jsonify({'error': 'Missing exercise_id or exercise_url'}), 400

    user_question = data['message']
    exercise_id = data['exercice_id']
    exercise_url = "." + data['exercice_url']

    exercise_text = extract_text_from_pdf(exercise_url)
    if not exercise_text:
        exercise_text = "The exercise is "
    user_id = session.get('user_id', 0)  # Get user_id from session
    history = run_query(
        "SELECT user_question, bot_response FROM exercise_chat_history WHERE exercise_id=? and user_id=? ORDER BY "
        "timestamp DESC LIMIT 10",
        (exercise_id, user_id))
    exercice_solutions = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Résoud le TP qui t'es donné et donne les réponses que tu as trouvé."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": exercise_text
                    },
                ]
            }
        ]
    )
    solution = exercice_solutions.choices[0].message.content
    prompt = generate_exercise_prompt(exercise_text, user_question, history)
    image = data.get('image')
    if image:
        feedback = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""Corrige la solution de l'étudiant pour l'aider à comprendre ses erreurs et à progresser. Fais un feedback 
    globale de sa réponse à l'exercice en comparant à la réponse que tu as toi meme générer aupravant : "{solution}" Tu peux lui donner des conseils, des explications
    supplémentaires, des exemples, ou des exercices supplémentaires pour l'aider à comprendre le concept. Tu peux 
    aussi lui donner des astuces pour mieux comprendre le concept et progresser."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                            }
                        }
                    ]
                }
            ]

        )
    else:
        feedback = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""Corrige la solution de l'étudiant pour l'aider à comprendre ses erreurs et à progresser. Fais un feedback 
    globale de sa réponse à l'exercice en comparant à la réponse que tu as toi meme générer aupravant : "{solution}" Tu peux lui donner des conseils, des explications
    supplémentaires, des exemples, ou des exercices supplémentaires pour l'aider à comprendre le concept. Tu peux 
    aussi lui donner des astuces pour mieux comprendre le concept et progresser."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ]
                }
            ]

        )
    bot_response = feedback.choices[0].message.content

    recommended_exercises = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""Par rapport au feedback que tu as donnée à l'étudiant, propose à l'étudiant des 
                exercices supplémentaires pour l'aider à s'entraîner et à progresser. Tu peux lui donner des 
                exercices similaires, des exercices plus difficiles ou plus faciles, ou des exercices qui couvrent 
                des concepts connexes pour l'aider à mieux comprendre le concept. Tu peux aussi lui donner des 
                astuces pour mieux comprendre le concept et progresser. N'hésite pas a lui conseiller des ressources
                supplémentaires pour l'aider à progresser."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": bot_response
                    },
                ]
            }
        ]
    )

    total_response = recommended_exercises.choices[0].message.content + "\n\n Feedback: \n\n " + bot_response

    # Save to exercise chat history
    conn = sqlite3.connect('apprentissage.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO exercise_chat_history (exercise_id, user_question, bot_response, user_id, image) VALUES (?, ?, "
        "?, ?, ?)",
        (exercise_id, user_question, total_response, user_id, image))
    conn.commit()
    conn.close()
    recommended_exercises = recommended_exercises.choices[0].message.content

    return jsonify({'feedback': bot_response, 'recommended': recommended_exercises})


@app.route('/chat_history/<int:course_id>')
def chat_history(course_id):
    user_id = session.get('user_id', 0)  # Get user_id from session
    history = run_query(
        "SELECT user_question, bot_response, timestamp, image FROM chat_history WHERE course_id=? and user_id=? ORDER "
        "BY timestamp DESC LIMIT 20",
        (course_id, user_id))
    return jsonify([{'user_question': h[0], 'bot_response': h[1], 'timestamp': h[2], 'image': h[3]} for h in history])


@app.route('/exercise_chat_history/<int:exercise_id>')
def exercise_chat_history(exercise_id):
    user_id = session.get('user_id', 0)  # Get user_id from session
    history = run_query(
        "SELECT user_question, bot_response, timestamp, image FROM exercise_chat_history WHERE exercise_id=? and "
        "user_id=? ORDER BY timestamp DESC LIMIT 20",
        (exercise_id, user_id))
    return jsonify([{'user_question': h[0], 'bot_response': h[1], 'timestamp': h[2], 'image': h[3]} for h in history])


# Route to serve course files
@app.route('/cours/<path:filename>')
def download_course(filename):
    return send_from_directory('cours', filename)


# Route to serve exercise files
@app.route('/exercices/<path:filename>')
def download_exercice(filename):
    return send_from_directory('exercices', filename)

# Route to handle file uploads
@app.route('/upload_cours', methods=['POST'])
def upload_cours():
    app.config['UPLOAD_FOLDER'] = 'cours'
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'status': 'success', 'filename': filename}), 200
    return jsonify({'error': 'File upload failed'}), 500


@app.route('/upload_exercices', methods=['POST'])
def upload_exercice():
    app.config['UPLOAD_FOLDER'] = 'exercices'
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'status': 'success', 'filename': filename}), 200
    return jsonify({'error': 'File upload failed'}), 500


@app.route('/add_course', methods=['POST'])
def add_course():
    data = request.get_json()
    nom = data['nom']
    description = data['description']
    niveau = data['niveau']
    url = data['url']
    conn = sqlite3.connect('apprentissage.db')
    c = conn.cursor()
    c.execute("INSERT INTO cours_table (nom, description, niveau, url) VALUES (?, ?, ?, ?)",
              (nom, description, niveau, url))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Course added successfully.'})


@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    data = request.get_json()
    nom = data['nom']
    description = data['description']
    niveau = data['niveau']
    url = data['url']
    conn = sqlite3.connect('apprentissage.db')
    c = conn.cursor()
    c.execute("INSERT INTO exercices_table (nom, description, niveau, url) VALUES (?, ?, ?, ?)",
              (nom, description, niveau, url))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Exercise added successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
