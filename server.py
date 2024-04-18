from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from bcrypt import hashpw, gensalt, checkpw
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS status (
#         id SERIAL PRIMARY KEY,
#         student_id INT,
#         course_id INT,
#         status VARCHAR(20),
#         FOREIGN KEY (student_id) REFERENCES users(id),
#         FOREIGN KEY (course_id) REFERENCES courses(id)
#     );
# """)
# conn.commit()

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
            session['role'] = user_data[1]  # Corrected line
            if user_data[1] == 'student':  # Changed user_data[3] to user_data[1]
                return redirect(url_for('student_dashboard'))
            elif user_data[1] == 'teacher':  # Changed user_data[3] to user_data[1]
                return redirect(url_for('teacher_dashboard'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')
# In your Flask route for the student dashboard
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

            # Fetch enrolled courses for the student
            cur.execute("""
                SELECT courses.course_name, courses.course_description 
                FROM enrolled_courses 
                JOIN courses ON enrolled_courses.course_id = courses.id 
                WHERE enrolled_courses.student_id = (
                    SELECT id FROM users WHERE username = %s
                )
            """, (session['username'],))
            enrolled_courses = cur.fetchall()

            # Fetch approved courses for the student
            cur.execute("""
                SELECT course_name 
                FROM enrolled_courses 
                WHERE student_id = (
                    SELECT id FROM users WHERE username = %s
                ) AND status = 'approved'
            """, (session['username'],))
            approved_courses = [row[0] for row in cur.fetchall()]

            # Fetch paid courses for the student
            cur.execute("""
                SELECT course_name 
                FROM enrolled_courses 
                WHERE student_id = (
                    SELECT id FROM users WHERE username = %s
                ) AND payment_status = 'paid'
            """, (session['username'],))
            paid_courses = [row[0] for row in cur.fetchall()]

            print("Approved Courses:", approved_courses)  # Debugging line

            return render_template('student_dashboard.html', courses=courses, enrolled_courses=enrolled_courses, approved_courses=approved_courses, paid_courses=paid_courses)
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
        conn.rollback()
        return redirect('/')

@app.route('/teacher/enrollments/<course_name>')
def enrollments(course_name):
    if 'username' not in session or session['role'] != 'teacher':
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')

    try:
        with conn.cursor() as cur:
            # Fetch enrollments for the specified course from the enrolled_courses table
            cur.execute("""
                SELECT student_name, course_name
                FROM enrolled_courses
                WHERE course_name = %s;
            """, (course_name,))
            enrollments = cur.fetchall()

            return render_template('teacher_enrollments.html', enrollments=enrollments, course_name=course_name)
    except Exception as e:
        print(f"Error fetching enrollments: {e}")
        flash('An error occurred while fetching enrollments.', 'error')
        return redirect('/teacher/dashboard')
@app.route('/teacher/approve_enrollment/<course_name>/<string:student_name>', methods=['POST'])
def approve_enrollment(course_name, student_name):
    if 'username' not in session or session['role'] != 'teacher':
        flash('You are not authorized to approve enrollments.', 'error')
        return redirect(url_for('teacher_dashboard'))

    email = request.form['email']
    message_body = request.form['message']

    try:
        with conn.cursor() as cur:
            # Fetch the enrollment details
            cur.execute("""
                SELECT * FROM enrolled_courses 
                WHERE course_name=%s AND student_name=%s
            """, (course_name, student_name))
            
            enrollment = cur.fetchone()

            if enrollment:
                # Update enrollment status
                cur.execute("""
                    UPDATE enrolled_courses 
                    SET status='approved' 
                    WHERE course_name=%s AND student_name=%s
                """, (course_name, student_name))

                # Update status table
                cur.execute("""
                    INSERT INTO status (student_id, student_name, course_id, course_name, status)
                    VALUES (%s, %s, %s, %s, 'approved')
                    ON CONFLICT (student_id, course_id) 
                    DO UPDATE SET status='approved';
                """, (enrollment[0], enrollment[2], enrollment[1], enrollment[3]))

                conn.commit()

                # Send email
                send_email("Enrollment Approval", email, f"Your enrollment for {course_name} in {student_name} has been approved. Message from teacher: {message_body}")
                
                flash('Enrollment approved successfully and email sent!', 'success')
                return redirect(url_for('enrollments', course_name=course_name))
            else:
                flash('Enrollment not found.', 'error')
                return redirect(url_for('teacher_dashboard'))

    except Exception as e:
        print(f"Error approving enrollment: {e}")
        conn.rollback()
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/reject_enrollment/<course_name>/<string:student_name>', methods=['POST'])
def reject_enrollment(course_name, student_name):
    if 'username' not in session or session['role'] != 'teacher':
        flash('You are not authorized to reject enrollments.', 'error')
        return redirect(url_for('teacher_dashboard'))

    email = request.form['email']
    message_body = request.form['message']

    try:
        with conn.cursor() as cur:
            # Fetch the enrollment details
            cur.execute("""
                SELECT * FROM enrolled_courses 
                WHERE course_name=%s AND student_name=%s
            """, (course_name, student_name))
            
            enrollment = cur.fetchone()

            if enrollment:
                # Delete enrollment record
                cur.execute("""
                    DELETE FROM enrolled_courses 
                    WHERE course_name=%s AND student_name=%s
                """, (course_name, student_name))

                # Delete status
                cur.execute("""
                    DELETE FROM status 
                    WHERE course_name=%s AND student_name=%s
                """, (course_name, student_name))

                conn.commit()

                # Send email
                send_email("Enrollment Rejection", email, f"Your enrollment for {course_name} in {student_name} has been rejected. Message from teacher: {message_body}")
                
                flash('Enrollment rejected successfully and email sent!', 'success')
                return redirect(url_for('enrollments', course_name=course_name))
            else:
                flash('Enrollment not found.', 'error')
                return redirect(url_for('teacher_dashboard'))

    except Exception as e:
        print(f"Error rejecting enrollment: {e}")
        conn.rollback()
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('teacher_dashboard'))

def send_email(subject, recipient, message_body):
    sender_email = 'mahavirkarthik27@msitprogram.net'  # Replace with your email address
    sender_password = 'karthik@272'  # Replace with your email password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject

    message.attach(MIMEText(message_body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Replace with your SMTP server and port
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
        print(f"Email sent successfully to {recipient}.")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
@app.route('/payment/<course_name>/<student_name>/<billing_amount>', methods=['GET', 'POST'])
def payment(course_name, student_name, billing_amount):
    if request.method == 'POST':
        email = request.form['email']
        payment_option = request.form['payment_option']
        payment_method = request.form['payment_method']
        emi_months = request.form.get('emi_months', None)

        # Process payment (for experiment, this is a mockup)
        if payment_method == 'card' or payment_method == 'wallet':
            flash('Payment successful!', 'success')

            # Update payment_status to 'paid' in the status table
            try:
                with conn.cursor() as cur:
                    # Fetch the course_id based on the course_name
                    cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
                    course_id = cur.fetchone()[0]

                    # Fetch student_id based on the student_name
                    cur.execute("SELECT id FROM users WHERE username=%s", (student_name,))
                    student_id = cur.fetchone()[0]

                    # Update payment_status to 'paid'
                    cur.execute("""
                        UPDATE status
                        SET payment_status = 'paid'
                        WHERE student_id = %s AND course_id = %s
                    """, (student_id, course_id))
                    conn.commit()

                    # Send payment receipt email
                    send_payment_receipt(email, course_name, student_name, billing_amount)

                    return redirect(url_for('student_dashboard'))

            except Exception as e:
                print(f"Error updating payment status: {e}")
                flash(f'An error occurred while updating payment status: {e}', 'error')

    return render_template('payment.html', course_name=course_name, student_name=student_name, billing_amount=billing_amount)


def send_payment_receipt(student_email, course_name, billing_amount):
    sender_email = 'mahavirkarthik27@msitprogram.net'
    sender_password = 'karthik@272'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = student_email
    message['Subject'] = 'Payment Receipt'

    body = f"Dear Student,\n\nThank you for your payment of {billing_amount} for the course {course_name}.\n\nRegards,\nYour School"

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, student_email, message.as_string())
        print(f"Email sent successfully to {student_email}.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")



def send_payment_receipt(student_email, student_name, course_name, billing_amount):
    sender_email = 'mahavirkarthik27@msitprogram.net'
    sender_password = 'karthik@272'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = student_email  # Use student_email instead of student_name
    message['Subject'] = 'Payment Receipt'

    body = f"Dear {student_name},\n\nThank you for your payment of {billing_amount} for the course {course_name}.\n\nRegards,\nYour School"

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, student_email, message.as_string())
        print(f"Email sent successfully to {student_email}.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    if 'username' not in session or session['role'] != 'student':
        flash('You are not authorized to enroll in a course.', 'error')
        return redirect(url_for('student_dashboard'))

    course_name = request.form.get('course_name')  # Retrieve course_name from form data

    try:
        with conn.cursor() as cur:
            # Fetch the student_id based on the username stored in session
            cur.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            student_id = cur.fetchone()[0]

            # Fetch the course_id based on the course_name
            cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
            course_id = cur.fetchone()[0]

            # Check if the enrollment already exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM enrolled_courses 
                    WHERE student_id=%s AND course_id=%s
                )
            """, (student_id, course_id))
            enrollment_exists = cur.fetchone()[0]

            if enrollment_exists:
                flash('You are already enrolled in this course.', 'error')
                return redirect(url_for('student_dashboard'))

            # Insert enrollment into enrolled_courses table
            cur.execute("""
                INSERT INTO enrolled_courses (student_id, student_name, course_id, course_name, payment_status) 
                VALUES (%s, %s, %s, %s, 'pending')
            """, (student_id, session['username'], course_id, course_name))
            conn.commit()

            flash('Successfully enrolled in the course! Please proceed with the payment.', 'success')
            return render_template('payment.html', course_name=course_name, student_name=session['username'], billing_amount=1000)  # Set billing_amount based on the course price

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
    if 'username' not in session:
        flash('You are not logged in.', 'error')
        return redirect(url_for('index'))

    try:
        with conn.cursor() as cur:
            # Fetch course_id based on the course_name
            cur.execute("SELECT id FROM courses WHERE course_name=%s", (course_name,))
            course_id = cur.fetchone()[0]

            # Fetch threads related to the course
            cur.execute("SELECT * FROM threads WHERE course_id=%s", (course_id,))
            threads = cur.fetchall()

            return render_template('course_discussion.html', threads=threads, courses=[course_name])
    except Exception as e:
        print(f"Error fetching course discussion: {e}")
        flash('An error occurred while fetching course discussion.', 'error')
        return redirect(url_for('index'))


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
