# Import modules
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
from get_weather import getWeather


# Configure application session["contacts"]
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database
db = SQL("sqlite:///weather.db")

# Give error if page not found
@app.errorhandler(404)
def page_not_found(e):
    return apology("Page not found", 404)


# Index Marketing page
@app.route("/")
def index():
    return render_template("index.html")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    # Check if page was loaded
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    # Check if user gave the details
    if not username or not password:
        return apology("Did not fill out the required details.")

    # Check if password is correct according to username
    users = db.execute("SELECT * FROM users WHERE username = ?;", username)
    if len(users) != 1 or not check_password_hash(users[0]["hash"], password):
        return apology("Invalid username or password")

    # Set session attributes
    session["user_id"] = users[0]["id"]

    return redirect("/home")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    # Check if page was loaded
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")

    # Check if username and password was there and username is new
    if not username or not password:
        return apology("Invalid username or password")
    user_exists = any(db.execute("SELECT * FROM users WHERE username = ?;", username))
    if user_exists:
        return apology("Username is already used")

    # Insert new password
    db.execute("INSERT INTO users(username, hash) VALUES(?, ?);", username, generate_password_hash(password))

    return redirect("/home")


@app.route("/home", methods=["GET"])
@login_required
def home():
    user = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[0]["username"]
    return render_template("home.html", username=user)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/location", methods=["GET"])
@login_required
def location():
    return render_template("location.html")

@app.route("/weather", methods=["POST", "GET"])
@login_required
def weather():

    # Check if the location exists
    location = request.form.get("location")
    if not location:
        return redirect("/location")

    # Get the weather data and check if it is there
    data = getWeather(location)
    if data is None:
        return apology("Invalid location")

    # Put it in the html file
    return render_template("weather.html", hour=data["hourly"], day=data["daily"], current=data["current"])
