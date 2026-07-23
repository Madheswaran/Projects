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

# -------------------------------
# Configuration
# -------------------------------

USER_SERVICE = "http://user-service"

APP_NAME = os.getenv("APP_NAME", "PayPal Checkout")
ENV_NAME = os.getenv("ENV_NAME", "DEV")


# -------------------------------
# Home
# -------------------------------

@app.route("/")
def home():
    return redirect("/login")


# -------------------------------
# Login
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME
        )

    email = request.form["email"]
    password = request.form["password"]

    response = requests.post(
        f"{USER_SERVICE}/login",
        json={
            "email": email,
            "password": password
        }
    )

    if response.status_code != 200:

        return render_template(
            "login.html",
            APP_NAME=APP_NAME,
            ENV_NAME=ENV_NAME,
            error="Invalid Email or Password"
        )

    customer = response.json()

    return render_template(
        "dashboard.html",
        customer=customer
    )


# -------------------------------
# Logout
# -------------------------------

@app.route("/logout")
def logout():
    return redirect("/login")


# ===================================================
# User Service APIs
# ===================================================

@app.route("/users")
def users():

    response = requests.get(
        f"{USER_SERVICE}/users"
    )

    return jsonify(response.json())


@app.route("/profile/<customer_id>")
def profile(customer_id):

    response = requests.get(
        f"{USER_SERVICE}/profile/{customer_id}"
    )

    return jsonify(response.json())


@app.route("/wallet/<customer_id>")
def wallet(customer_id):

    response = requests.get(
        f"{USER_SERVICE}/wallet/{customer_id}"
    )

    return jsonify(response.json())


@app.route("/transactions/<customer_id>")
def transactions(customer_id):

    response = requests.get(
        f"{USER_SERVICE}/transactions/{customer_id}"
    )

    return jsonify(response.json())


@app.route("/pay", methods=["POST"])
def pay():

    response = requests.post(
        f"{USER_SERVICE}/pay",
        json=request.json
    )

    return jsonify(response.json()), response.status_code


# -------------------------------
# Health Check
# -------------------------------

@app.route("/health")
def health():
    return {"status": "UP"}, 200


# -------------------------------
# Readiness Probe
# -------------------------------

@app.route("/ready")
def ready():
    return {"status": "READY"}, 200


# -------------------------------
# Application Entry
# -------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001
    )