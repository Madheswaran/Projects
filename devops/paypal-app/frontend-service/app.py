from flask import Flask, request, redirect, jsonify

import os
import requests

app = Flask(__name__)

USER_SERVICE = "http://user-service"

APP_NAME = os.getenv("APP_NAME", "PayPal Checkout")
ENV_NAME = os.getenv("ENV_NAME", "DEV")

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return f"""
        <html>
        <head>
            <title>{APP_NAME}</title>
        </head>

        <body>

        <h1>{APP_NAME}</h1>
        <h3>{ENV_NAME}</h3>

        <form method="POST">

            <label>Email</label><br>
            <input type="text" name="email"><br><br>

            <label>Password</label><br>
            <input type="password" name="password"><br><br>

            <button type="submit">Login</button>

        </form>

        </body>
        </html>
        """

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

        return """
        <h2>Login Failed</h2>
        <a href="/login">Try Again</a>
        """

    customer = response.json()

    return f"""
    <html>

    <body>

    <h1>Welcome {customer["name"]}</h1>

    <p>Customer ID : {customer["id"]}</p>

    <p>Wallet : ${customer["wallet"]}</p>

    <br>

    <a href="/logout">Logout</a>

    </body>

    </html>
    """

@app.route("/logout")
def logout():
    return redirect("/login")

@app.route("/users")
def users():

    response = requests.get(f"{USER_SERVICE}/users")

    return jsonify(response.json())

@app.route("/health")
def health():
    return {"status": "UP"}, 200


@app.route("/ready")
def ready():
    return {"status": "READY"}, 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001
    )