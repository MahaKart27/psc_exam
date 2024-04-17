from flask import Flask, request, jsonify, session, redirect
import psycopg2
from flask_session import Session
from flask_cors import CORS
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)
CORS(app) 
app.config['SECRET_KEY'] = '::UN.3QQov{a^U^}r>-{2v/'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

# Database configuration
db_name = 'psc'
db_user = 'postgres'
db_password = ''
db_host = 'localhost'

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host
)

# Create users table if not exists
with conn.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL
        );
    """)
    conn.commit()
    print("Table 'users' created successfully")

# Create courses table if not exists
with conn.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            course_name VARCHAR(100) NOT NULL,
            course_description TEXT,
            teacher_username VARCHAR(50)
        );
    """)
    conn.commit()
    print("Table 'courses' created successfully")

# Create student_courses table if not exists
with conn.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_courses (
            id SERIAL PRIMARY KEY,
            student_username VARCHAR(50) NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)
    conn.commit()
    print("Table 'student_courses' created successfully")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # Input validation
    if not username or not password or not role:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    # Hash the password
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    # Check if username already exists
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        # Insert new user
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password.decode('utf-8'), role))
        conn.commit()
        print(f"User '{username}' registered successfully")

    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Input validation
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    with conn.cursor() as cursor:
        cursor.execute("SELECT password, role FROM users WHERE username=%s", (username,))
        user_data = cursor.fetchone()

        if user_data and checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
            session['username'] = username
            session['role'] = user_data[1]
            return jsonify({'success': True, 'role': user_data[1]}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/create-course', methods=['POST'])
def create_course():
    if 'username' not in session or session['role'] != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    course_name = data.get('course_name')
    course_description = data.get('course_description')
    
    if not course_name or not course_description:
        return jsonify({'success': False, 'message': 'Course name and description are required'}), 400
    
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO courses (course_name, course_description, teacher_username) VALUES (%s, %s, %s)", (course_name, course_description, session['username']))
        conn.commit()
    
    return jsonify({'success': True, 'message': 'Course created successfully'}), 201

@app.route('/courses', methods=['GET'])
def get_courses():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
    
    course_list = [{'id': course[0], 'course_name': course[1], 'course_description': course[2]} for course in courses]
    return jsonify(course_list), 200

@app.route('/enroll-course', methods=['POST'])
def enroll_course():
    if 'username' not in session or session['role'] != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({'success': False, 'message': 'Course ID is required'}), 400
    
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO student_courses (student_username, course_id) VALUES (%s, %s)", (session['username'], course_id))
        conn.commit()
    
    return jsonify({'success': True, 'message': 'Enrolled in course successfully'}), 200

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
