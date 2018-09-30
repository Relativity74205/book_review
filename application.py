import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import User, Review
from functions_database import *


app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.before_first_request
def initialize_session_vars():
    session['username'] = None
    session['last_search'] = None
    session['userid'] = None


@app.route("/", methods=["GET", "POST"])
def index():
    session['last_search'] = None

    error_msg = request.args.get('error_message')
    return render_template("index.html", error_message=error_msg, username=session['username'])


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == 'GET':
        return render_template("registration.html", username=session['username'])
    if request.method == 'POST':
        username = request.form.get("name")
        user_query = search_user(username, db)
        if len(user_query) > 0:
            return render_template("registration.html", error_message="username already taken", username=session['username'])
        elif not request.form.get("password") == request.form.get("password_confirm"):
            return render_template("registration.html", error_message="passwords do not match", username=session['username'])
        else:
            user = User(username)
            user.hash_password(request.form.get("password"))
            user.add_user(db)
            return redirect(url_for('index'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html", username=session['username'])
    if request.method == 'POST':
        username = request.form.get("name")

        user_query = search_user(username, db)
        if len(user_query) == 1:
            user = User(user_query[0]['username'])
            user.set_password(user_query[0]['password_hashed'])
            if user.verify_password(request.form.get("password")):
                session['username'] = username
                session['userid'] = user_query[0]['id']
                return render_template("search.html", username=session['username'])
            else:
                return render_template("login.html",
                                       error_message="username not found or password does not match",
                                       username=session['username'])
        else:
            return render_template("login.html",
                                   error_message="username not found or password does not match",
                                   username=session['username'])


@app.route("/logout", methods=["POST"])
def logout():
    session['username'] = None
    return redirect(url_for('index'))


@app.route("/search", methods=["GET", "POST"])
def search():
    if session['username'] is not None:
        if request.method == 'GET' and session.get('last_search', None) is None:
            return render_template("search.html", username=session['username'])
        elif request.method == 'GET' and session.get('last_search', None) is not None:
            search_result = search_book(session.get('last_search', None), db)
            return render_template("search.html",
                                   username=session['username'],
                                   books=search_result,
                                   search_text=session['last_search'])
        elif request.method == 'POST':
            search_result = search_book(request.form.get("searchtext"), db)
            session['last_search'] = request.form.get("searchtext")
            return render_template("search.html",
                                   username=session['username'],
                                   books=search_result,
                                   search_text=request.form.get("searchtext"))
    else:
        return redirect(url_for('index', error_message="no login"), code=307)


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    if request.method == 'POST':
        if session['userid'] is None:
            return redirect(url_for('index', error_message="User has no login, return to index"), code=307)
        elif not check_user_already_reviewed(book_id, session['userid'], db):
            if request.form.get("review_text") == '':
                error_msg = 'No review written'
            else:
                review = Review(book_id,
                                session['userid'],
                                request.form.get("review_text"),
                                request.form.get("review_points"))
                review.add_review(db)
                error_msg = None
        else:
            error_msg = 'User has already reviewed this book'
    elif request.method == 'GET':
        error_msg = None

    book_object = get_book(book_id=book_id, db=db)
    reviews = get_reviews(book_id=book_id, db=db)
    goodread = requests.get("https://www.goodreads.com/book/review_counts.json",
                            params={"key": os.getenv("GOODREAD_KEY"), "isbns": book_object['isbn']})
    goodread_json = goodread.json()['books'][0]
    return render_template("book.html",
                           book_data=book_object,
                           reviews=reviews,
                           username=session['username'],
                           goodread=goodread_json,
                           error_message=error_msg)


@app.route("/api/<string:isbn>")
def api_isbn(isbn):
    book_with_reviews = get_book_by_isbn(isbn, db)
    book_dict = {}

    if book_with_reviews is None:
        return 'This page does not exist', 404
    else:
        for k, v in book_with_reviews.items():
            book_dict[k] = str(v)
        return jsonify(book_dict), 200


@app.route("/create_user")
def create_user():
    return render_template("index.html")


