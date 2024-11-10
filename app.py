# app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for
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

# Route to sign up
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        conn.commit()
        return jsonify(message="Sign-up successful"), 200
    except mysql.connector.Error as err:
        return jsonify(error=str(err)), 500
    finally:
        cursor.close()
        conn.close()

# Route to login
@app.route('/login', methods=['POST'])
def login():
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

# Route to update user info
@app.route('/updateInfo', methods=['POST'])
def update_info():
    data = request.get_json()
    username = data['username']
    field1 = data['field1']
    field2 = data['field2']

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

# Run the server
if __name__ == '__main__':
    app.run(debug=True)

