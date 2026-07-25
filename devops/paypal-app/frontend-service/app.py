from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify
)

import os
import requests

app = Flask(__name__)

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

USER_SERVICE = "http://user-service"

APP_NAME = os.getenv("APP_NAME", "PayPal Checkout")
ENV_NAME = os.getenv("ENV_NAME", "DEV")


# ---------------------------------------------------
# Home
# ---------------------------------------------------

@app.route("/")
def home():
    return redirect("/login")


# ---------------------------------------------------
# Login
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    app.logger.warning(f"LOGIN METHOD = {request.method}")

    if request.method == "GET":

        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME
        )

    app.logger.warning("POST /login RECEIVED")

    email = request.form["email"]
    password = request.form["password"]

    app.logger.warning(f"EMAIL = {email}")
    app.logger.warning(f"USER_SERVICE = {USER_SERVICE}")

    try:

        response = requests.post(
            f"{USER_SERVICE}/login",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )

        app.logger.warning(f"Response Status = {response.status_code}")
        app.logger.warning(f"Response Body = {response.text}")

    except Exception as e:

        app.logger.exception("Failed to call user-service")

        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME,
            error=str(e)
        )

    if response.status_code != 200:

        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME,
            error="Invalid Email or Password"
        )

    customer = response.json()

    app.logger.warning(f"Customer = {customer}")

    # Temporary sample transactions
    customer["transactions"] = [

        {
            "id": 1001,
            "description": "Amazon Shopping",
            "amount": 1200
        },

        {
            "id": 1002,
            "description": "Netflix Subscription",
            "amount": 499
        },

        {
            "id": 1003,
            "description": "Electricity Bill",
            "amount": 1850
        }

    ]

    return render_template(
        "dashboard.html",
        APP_NAME=APP_NAME,
        customer=customer
    )


# ---------------------------------------------------
# Pay
# ---------------------------------------------------

@app.route("/pay")
def pay():

    return """
    <h2>Pay Money</h2>
    <p>This feature will be implemented in the Payment Service.</p>
    <a href="/login">Home</a>
    """


# ---------------------------------------------------
# Add Money
# ---------------------------------------------------

@app.route("/add-money")
def add_money():

    return """
    <h2>Add Money</h2>
    <p>This feature will be implemented later.</p>
    <a href="/login">Home</a>
    """


# ---------------------------------------------------
# Profile
# ---------------------------------------------------

@app.route("/profile")
def profile():

    return """
    <h2>User Profile</h2>
    <p>This page will show profile information.</p>
    <a href="/login">Home</a>
    """


# ---------------------------------------------------
# Logout
# ---------------------------------------------------

@app.route("/logout")
def logout():

    return redirect("/login")


# ---------------------------------------------------
# Users API
# ---------------------------------------------------

@app.route("/users")
def users():

    response = requests.get(
        f"{USER_SERVICE}/users",
        timeout=10
    )

    return jsonify(response.json())


# ---------------------------------------------------
# Health
# ---------------------------------------------------

@app.route("/health")
def health():

    return {
        "status": "UP"
    }, 200


# ---------------------------------------------------
# Readiness
# ---------------------------------------------------

@app.route("/ready")
def ready():

    return {
        "status": "READY"
    }, 200


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=3001
    )