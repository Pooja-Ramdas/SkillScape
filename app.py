from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, g
import mysql.connector
from database_config import DB_CONFIG
from datetime import datetime
import secrets
import bcrypt

app = Flask(__name__)
app.secret_key = 'Secret Key'

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Setup the database connection before each request
@app.before_request
def before_request():
    g.db = get_db_connection()

# Close the database connection after each request
@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Route to home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/certificates')
def certificates():
    cursor = g.db.cursor(dictionary=True)
    cursor.execute("SELECT name, date FROM certificates WHERE studentID = %s", (session.get('user_id'),))
    certificates = cursor.fetchall()
    cursor.close()
    return render_template('certificates.html', certificates=certificates)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            # Here you could add code to save contact message to the database
            # or send it via email.
            
            flash("Thank you for your message!", "success")
            return redirect(url_for('contact'))
        
        return render_template('contact.html')

@app.route('/courses')
def courses():
    cursor = g.db.cursor(dictionary=True)
    cursor.execute("SELECT courseID, name, description FROM courses")
    courses = cursor.fetchall()
    cursor.close()
    return render_template('courses.html', courses=courses)


# Function to get a student's ID
def get_student_id(username):
    cursor = g.db.cursor(dictionary=True)
    query = "SELECT studentID FROM students WHERE name = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    return result['studentID'] if result else None


# Route to the signup page (GET) and signup form submission (POST)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form submission
        username = request.form['username']
        user_id = get_student_id(username)
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        contact_number = request.form['contact_number']

        # Validate passwords
        if password != confirm_password:
            return render_template('signup.html', error="Passwords don't match")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Get the current date for the enrollment date
        enrollment_date = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert user data with the hashed password
            cursor.execute(
                "INSERT INTO Students (name, email, enrollment_date, contact_number, course, skills, password) "
                "VALUES (%s, %s, %s, %s, NULL, NULL, %s)", 
                (username, email, enrollment_date, contact_number, hashed_password)
            )
            conn.commit()
            return redirect(url_for('info'))

        except mysql.connector.Error as err:
            return render_template('signup.html', error=f"Database error: {err}")

        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')


# Route to render the info page (GET)
@app.route('/info', methods=['GET'])
def info():
    return render_template('info.html')

# Route for submitting the info form (POST)
@app.route('/submit_info', methods=['POST'])
def submit_info():
    if request.method == 'POST':
        degree = request.form['degree']
        skills = request.form['skills']
        focus_level = request.form['focus-level']
        time_management = request.form['time-management']
        motivation = request.form['motivation']

        username = session.get('username')
        if not username:
            print("No username found in session.")
            return redirect(url_for('login'))

        student_id = get_student_id(username)
        if not student_id:
            print("Student ID not found.")
            return render_template('info.html', error="Student ID not found.")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Students SET course = %s, skills = %s WHERE studentID = %s",
                (degree, skills, student_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                print("No rows were updated. Check if studentID exists in the table.")
                return render_template('info.html', error="An error occurred while updating your information.")
            return redirect(url_for('home'))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return render_template('info.html', error="An error occurred while updating your information.")
        finally:
            cursor.close()
            conn.close()


# Route to the login page (GET) and login form submission (POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM students WHERE name = %s", (username,))
            user = cursor.fetchone()

            # Verify user existence and password
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['username'] = user['name']
                session['user_id'] = user['studentID']
                print(f"User logged in: {session['username']}")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password.", "danger")
                return render_template('login.html')

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template('login.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')


# Home route
@app.route('/home')
def home():
    if 'username' not in session:
        print("Username not found in session.")
        return redirect(url_for('login'))

    username = session['username']
    print(f"User in session: {username}")
    return render_template('home.html', username=username)

# Route to log out
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data on logout
    return redirect(url_for('login'))

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    if 'username' not in session:
        return jsonify({"message": "User not logged in"}), 401

    data = request.get_json()
    new_username = data['username']
    new_password = data['password']

    # Hash the new password before updating
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Get the current user's ID
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID not found in session"}), 400

    # Update username and password in the database
    cursor = g.db.cursor(dictionary=True)
    try:
        cursor.execute(
            "UPDATE students SET name = %s, password = %s WHERE studentID = %s",
            (new_username, hashed_password, user_id)
        )
        g.db.commit()
        session['username'] = new_username  # Update the session with the new username
        return jsonify({"message": "Settings updated successfully!"})
    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({"message": "User not logged in"}), 401

    user_id = session['user_id']

    cursor = g.db.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE studentID = %s", (user_id,))
        g.db.commit()
        session.clear()  # Log out the user
        return jsonify({"message": "Your account has been deleted successfully!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
