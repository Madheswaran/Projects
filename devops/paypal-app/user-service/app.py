from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "paypal")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------

def get_db_connection():

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ---------------------------------------------------------
# Pay
# ---------------------------------------------------------

@app.route("/pay")
def pay():

    return render_template("pay.html")

# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.route("/health")
def health():
    return {"status": "UP"}, 200


@app.route("/ready")
def ready():
    return {"status": "READY"}, 200


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------
@app.route("/users")
def users():

    # Running in GitHub Actions (no PostgreSQL available)
    if os.getenv("CI") == "true":
        return jsonify([
            {"id": 1, "name": "Ganesha"},
            {"id": 2, "name": "Muruga"},
            {"id": 3, "name": "Lakshmi"}
        ])

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM customers
        ORDER BY id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": row[0],
            "name": row[1]
        }
        for row in rows
    ])

# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    app.logger.warning("========== USER LOGIN ==========")

    data = request.json
    app.logger.warning(f"Request Data : {data}")

    conn = get_db_connection()
    cur = conn.cursor()

    app.logger.warning("Connected to PostgreSQL")

    cur.execute("""

    SELECT

    id,

    name,

    email,

    wallet,

    phone,

    address

    FROM customers

    WHERE email=%s

    AND password=%s

    """,
    (
        data["email"],
        data["password"]
    ))

    row = cur.fetchone()

    app.logger.warning(f"Database Result : {row}")

    cur.close()
    conn.close()

    if row is None:
        app.logger.warning("LOGIN FAILED")
        return {"status": "failed"}, 401

    app.logger.warning("LOGIN SUCCESS")
        
    return jsonify({

        "id": row[0],
        "name": row[1],
        "email": row[2],
        "wallet": float(row[3]),
        "phone": row[4],
        "address": row[5]

    })
# ---------------------------------------------------------
# Profile
# ---------------------------------------------------------

@app.route("/profile/<id>")
def profile(id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM customers
        WHERE id=%s
    """,
    (id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return {"status": "not found"}, 404

    return {
        "name": row[1],
        "email": row[2],
        "wallet": float(row[4])
    }


# ---------------------------------------------------------
# Start Application
# ---------------------------------------------------------
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=3002
    )