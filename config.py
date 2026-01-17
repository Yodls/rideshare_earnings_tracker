from flask import Flask, g
from flask_login import LoginManager, current_user, UserMixin
from werkzeug.security import check_password_hash
import psycopg2
import os


# App config
class Config:
    SECRET_KEY = "secretkey"
    SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    CACHE_TYPE = "simple"

    # Database connection
    DB_USER = "user"
    DB_PASSWORD = "password"
    DB_HOST = "host"
    DB_PORT = "port"
    DB_NAME = "datebase"


def create_connection():
    return psycopg2.connect(
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
    )


app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Define the User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        # Flask-Login expects a string id
        return str(self.id)


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return User(id=user_id, username=result[0])
    finally:
        cursor.close()
        conn.close()


def authenticate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,),
        )
        result = cursor.fetchone()
        if result is None:
            return None

        user_id, hashed_password = result
        if check_password_hash(hashed_password, password):
            return User(id=user_id, username=username)
        return None
    finally:
        cursor.close()
        conn.close()
