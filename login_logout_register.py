from flask import render_template, request, url_for, redirect
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
import sqlite3
from config import app, authenticate_user, create_connection

# Register a new user
def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Username already exists"
    finally:
        conn.close()

#register
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = register_user(username, password)
        if error:
            return error, 400
        return redirect(url_for('login'))
    else:
        return render_template('login.html')

#login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pin')

        user = authenticate_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to the 'visual' route after successful login
        else:
            return "Invalid username or password", 400
    else:
        return render_template('login.html')

#logout    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))