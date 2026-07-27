from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    session
)

import os
import requests
import psycopg2

app = Flask(__name__)
app.secret_key = "paypal-secret-key"

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

USER_SERVICE = "http://user-service"
PAYMENT_SERVICE = "http://payment-service"  

APP_NAME = os.getenv("APP_NAME", "PayPal Checkout")
ENV_NAME = os.getenv("ENV_NAME", "DEV")

def get_db_connection():

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
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

    session["customer_id"] = customer["id"]
    return render_template(
        "dashboard.html",
        APP_NAME=APP_NAME,
        customer=customer
    )


@app.route("/dashboard")
def dashboard():

    if "customer_id" not in session:
        return redirect("/login")

    customer_id = session["customer_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            name,
            email,
            wallet,
            phone,
            address
        FROM customers
        WHERE id=%s
    """, (customer_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    customer = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "wallet": row[3],
        "phone": row[4],
        "address": row[5],
        "transactions": []
    }

    cur.execute(
        """
        SELECT
            id,
            receiver_email,
            amount,
            created_at

        FROM transactions

        WHERE customer_id=%s

        ORDER BY created_at DESC

        LIMIT 5
        """,
        (
            session["customer_id"],
        )
    )

    rows = cur.fetchall()

    customer["transactions"] = []

    for row in rows:

        customer["transactions"].append({

            "id": row[0],

            "description": row[1],

            "amount": row[2],

            "date": row[3]

        })

    return render_template(
        "dashboard.html",
        APP_NAME=APP_NAME,
        customer=customer
    )
# ---------------------------------------------------
# Pay
# ---------------------------------------------------
@app.route("/pay", methods=["GET", "POST"])
def pay():

    if "customer_id" not in session:
        return redirect("/login")

    if request.method == "GET":

        return render_template(
            "pay.html",
            APP_NAME=APP_NAME
        )

    receiver = request.form["receiver"]
    amount = request.form["amount"]

    app.logger.warning(
        f"PAY REQUEST -> {receiver} : {amount}"
    )

    response = requests.post(
        f"{PAYMENT_SERVICE}/payment",
        json={
            "customer_id": session["customer_id"],          # Temporary until session/login stores ID
            "receiver_email": receiver,
            "amount": float(amount)
        }
    )

    result = response.json()

    return render_template(
        "payment-success.html",
        payment=result
    )

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
    session.clear()
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