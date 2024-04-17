# from flask import Flask, render_template, request, redirect, url_for, flash, session
# import psycopg2

# app = Flask(__name__)
# app.secret_key = 'C7mV_?<W;uT=fT%"cjM7>SrB'

from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C7mV_?<W;uT=fT%"cjM7>SrB'

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="psc",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(100),
        role VARCHAR(20)
    );
""")
conn.commit()

cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id SERIAL PRIMARY KEY,
        course_name VARCHAR(100) UNIQUE,
        course_description VARCHAR(255),
        teacher_id INT
    );
""")
conn.commit()

cur.execute("""
    CREATE TABLE IF NOT EXISTS enrolled_courses (
        student_id INT,
        course_id INT,
        FOREIGN KEY (student_id) REFERENCES users(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
""")
conn.commit()

cur.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content TEXT NOT NULL,
        user_id INT,
        course_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
""")
conn.commit()

cur.execute("""
    CREATE TABLE IF NOT EXISTS replies (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        user_id INT,
        thread_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (thread_id) REFERENCES threads(id)
    );
""")
conn.commit()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Input validation
        if len(username) > 50:
            error = 'Username exceeds maximum length of 50 characters.'
            return render_template('signup.html', error=error, message=message)

        if len(password) > 100:
            error = 'Password exceeds maximum length of 100 characters.'
            return render_template('signup.html', error=error, message=message)

        hashed_password = hashpw(password.encode('utf-8'), gensalt())

        try:
            cur.execute("""
                INSERT INTO users (username, password, role) 
                VALUES (%s, %s, %s)
            """, (username, hashed_password.decode('utf-8'), role))
            conn.commit()
            message = 'Registration successful! Please login.'
            return redirect(url_for('index'))
        except psycopg2.IntegrityError as e:
            conn.rollback()  # Rollback the current transaction
            if "value too long for type character varying(50)" in str(e):
                error = 'Username exceeds maximum length of 50 characters.'
            else:
                error = 'An error occurred during registration.'

    return render_template('signup.html', error=error, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute("SELECT password, role FROM users WHERE username=%s", (username,))
        user_data = cur.fetchone()

        if user_data and checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
            session['username'] = username
            session['role'] = user_data[1]
            if user_data[1] == 'student':
                return redirect(url_for('student_dashboard'))
            elif user_data[1] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')
@app.route('/student/dashboard')
def student_dashboard():
    if 'username' not in session or session['role'] != 'student':
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')

    try:
        with conn.cursor() as cur:
            # Fetch all courses
            cur.execute("SELECT course_name, course_description FROM courses")
            courses = cur.fetchall()

            # Fetch threads related to each course
            course_threads = {}
            for course in courses:
                cur.execute("SELECT id FROM courses WHERE course_name=%s", (course[0],))
                course_id = cur.fetchone()[0]

                cur.execute("SELECT COUNT(id) FROM threads WHERE course_id=%s", (course_id,))
                thread_count = cur.fetchone()[0]

                course_threads[course[0]] = thread_count

            return render_template('student_dashboard.html', courses=courses, course_threads=course_threads)
    except Exception as e:
        print(f"Error fetching courses and threads: {e}")
        flash('An error occurred while fetching courses and threads.', 'error')
        return redirect('/')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'username' not in session or session['role'] != 'teacher':
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')

    try:
        with conn.cursor() as cur:
            # Fetch all courses
            cur.execute("SELECT course_name, course_description FROM courses")
            courses = cur.fetchall()

            # Fetch threads related to each course
            course_threads = {}
            for course in courses:
                cur.execute("SELECT id FROM courses WHERE course_name=%s", (course[0],))
                course_id = cur.fetchone()[0]

                cur.execute("SELECT COUNT(id) FROM threads WHERE course_id=%s", (course_id,))
                thread_count = cur.fetchone()[0]

                course_threads[course[0]] = thread_count

            return render_template('teacher_dashboard.html', courses=courses, course_threads=course_threads)
    except Exception as e:
        print(f"Error fetching courses and threads: {e}")
        flash('An error occurred while fetching courses and threads.', 'error')
        return redirect('/')


@app.route('/create_course', methods=['POST'])
def create_course():
    if 'username' not in session:
        flash('You are not logged in.', 'error')
        return redirect('/')

    course_name = request.form['course_name']
    course_description = request.form['course_description']

    try:
        with conn.cursor() as cur:
            # Fetch the teacher_id based on the teacher's username
            cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            teacher_id = cur.fetchone()[0]

            # Insert the course into the courses table
            cur.execute("INSERT INTO courses (course_name, course_description, teacher_id) VALUES (%s, %s, %s)", 
                        (course_name, course_description, teacher_id))
            conn.commit()
            flash('Course created successfully!', 'success')
            return redirect('/teacher/dashboard')
    except Exception as e:
        print(f"Error creating course: {e}")  # Log the error
        flash(f'An error occurred: {e}', 'error')
        return redirect('/teacher/dashboard')


@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    if 'username' not in session or session['role'] != 'student':
        flash('You are not authorized to enroll in a course.', 'error')
        return redirect(url_for('student_dashboard'))

    course_name = request.form['course_name']

    try:
        with conn.cursor() as cur:
            # Fetch the course_id based on the course_name
            cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
            course_id = cur.fetchone()[0]

            # Fetch the student_id based on the username stored in session
            cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            student_id = cur.fetchone()[0]

            # Insert enrollment into enrolled_courses table
            cur.execute("INSERT INTO enrolled_courses (student_id, course_id) VALUES (%s, %s)", (student_id, course_id))
            conn.commit()

            flash('Successfully enrolled in the course!', 'success')
            return redirect(url_for('student_dashboard'))

    except Exception as e:
        print(f"Error enrolling in course: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('student_dashboard'))


@app.route('/drop_course/<course_name>', methods=['POST'])
def drop_course(course_name):
    if 'username' not in session or session['role'] != 'student':
        flash('You are not authorized to drop a course.', 'error')
        return redirect(url_for('student_dashboard'))

    try:
        with conn.cursor() as cur:
            # Fetch the student_id based on the username stored in session
            cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            student_id = cur.fetchone()[0]

            # Fetch the course_id based on the course name
            cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
            course_id = cur.fetchone()[0]

            # Delete enrollment from enrolled_courses table
            cur.execute("DELETE FROM enrolled_courses WHERE student_id=%s AND course_id=%s", (student_id, course_id))
            conn.commit()

            flash('Successfully dropped the course!', 'success')
            return redirect(url_for('student_dashboard'))

    except Exception as e:
        print(f"Error dropping course: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('student_dashboard'))


@app.route('/create_thread', methods=['POST'])
def create_thread():
    title = request.form['title']
    content = request.form['content']
    course_name = request.form['course_name']

    cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
    course_id = cur.fetchone()[0]

    cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO threads (title, content, user_id, course_id) 
        VALUES (%s, %s, %s, %s)
    """, (title, content, user_id, course_id))
    conn.commit()

    return redirect(url_for('course_discussion', course_name=course_name))

@app.route('/create_reply/<int:thread_id>', methods=['POST'])
def create_reply(thread_id):
    if 'username' not in session:
        flash('You are not logged in.', 'error')
        return redirect('/')

    content = request.form['content']

    try:
        with conn.cursor() as cur:
            # Fetch user_id based on the username stored in session
            cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            user_id = cur.fetchone()[0]

            # Insert reply into replies table
            cur.execute("""
                INSERT INTO replies (content, user_id, thread_id) 
                VALUES (%s, %s, %s)
            """, (content, user_id, thread_id))
            conn.commit()

            flash('Reply added successfully!', 'success')
            return redirect(url_for('view_thread', thread_id=thread_id))

    except Exception as e:
        print(f"Error adding reply: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('view_thread', thread_id=thread_id))


@app.route('/course_discussion/<course_name>')
def course_discussion(course_name):
    if 'username' not in session or session['role'] != 'student':
        flash('You are not authorized to view this page.', 'error')
        return redirect(url_for('student_dashboard'))

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
            course_id = cur.fetchone()[0]

            cur.execute("SELECT * FROM threads WHERE course_id=%s", (course_id,))
            threads = cur.fetchall()

            return render_template('course_discussion.html', threads=threads, courses=[course_name])
    except Exception as e:
        print(f"Error fetching course discussion: {e}")
        flash('An error occurred while fetching course discussion.', 'error')
        return redirect(url_for('student_dashboard'))


@app.route('/view_thread/<int:thread_id>')
def view_thread(thread_id):
    cur.execute("SELECT * FROM threads WHERE id=%s", (thread_id,))
    thread = cur.fetchone()

    cur.execute("""
        SELECT replies.id, replies.content, users.username 
        FROM replies JOIN users ON replies.user_id = users.id
        WHERE replies.thread_id=%s
    """, (thread_id,))
    replies = cur.fetchall()

    return render_template('view_thread.html', thread=thread, replies=replies)

if __name__ == '__main__':
    app.run(debug=True)
