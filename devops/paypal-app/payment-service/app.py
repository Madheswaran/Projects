from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)


DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "paypal")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


def get_connection():

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@app.route("/health")
def health():
    return {"status": "UP"}


@app.route("/pay", methods=["POST"])
def pay():

    data = request.json

    customer_id = data["customer_id"]
    amount = float(data["amount"])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT wallet
        FROM customers
        WHERE id=%s
        """,
        (customer_id,)
    )

    row = cur.fetchone()

    if row is None:

        cur.close()
        conn.close()

        return {"message": "Customer not found"}, 404

    wallet = float(row[0])

    if wallet < amount:

        cur.close()
        conn.close()

        return {"message": "Insufficient Balance"}, 400

    new_wallet = wallet - amount

    cur.execute(
        """
        UPDATE customers
        SET wallet=%s
        WHERE id=%s
        """,
        (
            new_wallet,
            customer_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({

        "message": "Payment Successful",

        "remaining_balance": new_wallet

    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=3003
    )