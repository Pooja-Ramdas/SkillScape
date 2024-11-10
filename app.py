from flask import Flask, render_template, request, jsonify, redirect, url_for, session 
import mysql.connector
from database_config import DB_CONFIG

app = Flask(__name__)

# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Route to home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to the signup page (GET) and signup form submission (POST)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form submission
        data = request.get_json()
        username = data['username']
        password = data['password']
        email = data['email']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
            conn.commit()
            session['username'] = username  # Store username in session
            return jsonify(message="Sign-up successful"), 200
        except mysql.connector.Error as err:
            return jsonify(error=str(err)), 500
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

# Route to the info page (GET) and submit additional info (POST)
@app.route('/info', methods=['GET', 'POST'])
def info():
    if 'username' not in session:
        return redirect(url_for('index'))  # Redirect to index if not logged in

    if request.method == 'POST':
        # Handle additional info submission
        data = request.get_json()
        field1 = data['field1']
        field2 = data['field2']
        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET field1 = %s, field2 = %s WHERE username = %s", (field1, field2, username))
            conn.commit()
            return jsonify(message="Information updated successfully"), 200
        except mysql.connector.Error as err:
            return jsonify(error=str(err)), 500
        finally:
            cursor.close()
            conn.close()
    return render_template('info.html')

# Route to the login page (GET) and login form submission (POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission
        data = request.get_json()
        username = data['username']
        password = data['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                return jsonify(message="Login successful"), 200
            else:
                return jsonify(error="Invalid credentials"), 401
        except mysql.connector.Error as err:
            return jsonify(error=str(err)), 500
        finally:
            cursor.close()
            conn.close()
    # Display the login page for GET request
    return render_template('login.html')

# Route to the home page after login or completing additional info
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))  # Redirect to index if not logged in
    return render_template('home.html')

# Route to log out and redirect to index page
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    return redirect(url_for('index'))

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
