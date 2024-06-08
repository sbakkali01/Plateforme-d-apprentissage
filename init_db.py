import sqlite3
from hashlib import sha256
import os

# Connexion à la base de données (ou création si elle n'existe pas)
conn = sqlite3.connect('apprentissage.db')
c = conn.cursor()

# Création des tables
def setup_db():

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT,
        etudes TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS cours_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        niveau TEXT,
        url TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS exercices_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        niveau TEXT,
        url TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        user_question TEXT,
        bot_response TEXT,
        user_id INTEGER,
        image TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS exercise_chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER,
        user_question TEXT,
        bot_response TEXT,
        user_id INTEGER,
        image TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

# Ajout des utilisateurs initiaux
def add_user(username, password, role, etudes):
    password_hash = sha256(password.encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO utilisateurs (username, password_hash, role, etudes) VALUES (?, ?, ?, ?)",
              (username, password_hash, role, etudes))
    conn.commit()

# Chargement des utilisateurs à partir d'un fichier texte
def load_users_from_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            username, password, role, etudes = line.strip().split(',')
            add_user(username, password, role, etudes)

# Ajout des cours et exercices initiaux
def add_course(nom, description, niveau, url):
    c.execute('SELECT COUNT(*) FROM cours_table WHERE nom=?', (nom,))
    data = c.fetchone()
    count = data[0] if data else 0
    if count > 0:
        c.execute('UPDATE cours_table SET description=?, niveau=?, url=? WHERE nom=?', (description, niveau, url, nom))
        print('Course updated')
    else:
        c.execute('INSERT INTO cours_table(nom, description, niveau, url) VALUES (?,?,?,?)', (nom, description, niveau, url))
        print('Course added')
    conn.commit()

def add_exercise(nom, description, niveau, url):
    c.execute('SELECT COUNT(*) FROM exercices_table WHERE nom=?', (nom,))
    data = c.fetchone()
    count = data[0] if data else 0
    if count > 0:
        c.execute('UPDATE exercices_table SET description=?, niveau=?, url=? WHERE nom=?', (description, niveau, url, nom))
        print('Exercice updated')
    else:
        c.execute('INSERT INTO exercices_table(nom, description, niveau, url) VALUES (?,?,?,?)', (nom, description, niveau, url))
        print('Exercice added')
    conn.commit()

# Chargement des cours et exercices depuis des répertoires
def load_courses_from_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.pdf') or filename.endswith('.mp4'):
            nom = os.path.splitext(filename)[0]
            description = "Description du cours"
            niveau = "Débutant"  # Peut être modifié en fonction de votre logique
            url = filename
            add_course(nom, description, niveau, url)

def load_exercises_from_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.pdf') or filename.endswith('.mp4'):
            nom = os.path.splitext(filename)[0]
            description = "Description de l'exercice"
            niveau = "Débutant"  # Peut être modifié en fonction de votre logique
            url = filename
            add_exercise(nom, description, niveau, url)

# Initialisation de la base de données
setup_db()
load_users_from_file('backlog.txt')
load_courses_from_directory('./cours/')  # Spécifiez le répertoire des cours
load_exercises_from_directory('./exercices/')  # Spécifiez le répertoire des exercices

# Fermeture de la connexion à la base de données
conn.close()
