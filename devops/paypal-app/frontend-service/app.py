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

# ----------------------------------
# Configuration
# ----------------------------------

USER_SERVICE = "http://user-service"

APP_NAME = os.getenv("APP_NAME", "PayPal Checkout")
ENV_NAME = os.getenv("ENV_NAME", "DEV")


# ----------------------------------
# Home
# ----------------------------------

@app.route("/")
def home():
    return redirect("/login")


# ----------------------------------
# Login
# ----------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    print("METHOD =", request.method)

    if request.method == "GET":
        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME
        )

    print("POST RECEIVED")

    email = request.form["email"]
    password = request.form["password"]

    print(email, password)

    response = requests.post(
        f"{USER_SERVICE}/login",
        json={
            "email": email,
            "password": password
        }
    )

    print("User service status =", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME,
            error="Invalid Email or Password"
        )

    customer = response.json()

    print(customer)

    return render_template(
        "dashboard.html",
        customer=customer
    )

# ----------------------------------
# Logout
# ----------------------------------

@app.route("/logout")
def logout():
    return redirect("/login")


# ----------------------------------
# Users API
# ----------------------------------

@app.route("/users")
def users():

    response = requests.get(
        f"{USER_SERVICE}/users"
    )

    return jsonify(response.json())


# ----------------------------------
# Health
# ----------------------------------

@app.route("/health")
def health():
    return {"status": "UP"}, 200


# ----------------------------------
# Readiness
# ----------------------------------

@app.route("/ready")
def ready():
    return {"status": "READY"}, 200


# ----------------------------------
# Main
# ----------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001
    )