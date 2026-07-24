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
# Create Database Objects
# ---------------------------------------------------------

def initialize_database():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers
        (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100),
            wallet NUMERIC(10,2)
        )
    """)

    cur.execute("SELECT COUNT(*) FROM customers")

    count = cur.fetchone()[0]

    if count == 0:

        cur.execute("""
            INSERT INTO customers
            (name,email,password,wallet)
            VALUES
            ('Ganesha','ganesha@gmail.com','paypal123',5000),
            ('Muruga','muruga@gmail.com','paypal123',12000),
            ('Lakshmi','lakshmi@gmail.com','paypal123',25000)
        """)

    conn.commit()

    cur.close()
    conn.close()

    print("Database initialized.")


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

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,name
        FROM customers
        ORDER BY id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(
        [
            {
                "id": r[0],
                "name": r[1]
            }
            for r in rows
        ]
    )


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,name,wallet
        FROM customers
        WHERE email=%s
        AND password=%s
    """,
    (
        data["email"],
        data["password"]
    ))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row is None:
        return {"status": "failed"}, 401

    return {
        "id": row[0],
        "name": row[1],
        "wallet": float(row[2])
    }


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

initialize_database()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3002
    )