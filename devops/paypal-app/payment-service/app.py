from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def get_connection():

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@app.route("/health")
def health():
    return {"status": "UP"}, 200

@app.route("/ready")
def ready():

    return {"status": "READY"}, 200

@app.route("/payment", methods=["POST"])
def pay():

    data = request.json

    customer_id = data["customer_id"]
    receiver_email = data["receiver_email"]
    amount = float(data["amount"])

    conn = get_connection()
    cur = conn.cursor()

    ###############################################
    # Get sender
    ###############################################

    cur.execute(
        """
        SELECT id,name,email,wallet
        FROM customers
        WHERE id=%s
        """,
        (customer_id,)
    )

    sender = cur.fetchone()

    if sender is None:

        cur.close()
        conn.close()

        return jsonify({
            "status":"FAILED",
            "message":"Sender not found"
        }),404

    ###############################################
    # Get receiver
    ###############################################

    cur.execute(
        """
        SELECT id,name,email,wallet
        FROM customers
        WHERE email=%s
        """,
        (receiver_email,)
    )

    receiver = cur.fetchone()

    if receiver is None:

        cur.close()
        conn.close()

        return jsonify({
            "status":"FAILED",
            "message":"Receiver not found"
        }),404

    sender_wallet = float(sender[3])
    receiver_wallet = float(receiver[3])

    ###############################################
    # Balance validation
    ###############################################

    if sender_wallet < amount:

        cur.close()
        conn.close()

        return jsonify({
            "status":"FAILED",
            "message":"Insufficient Balance"
        }),400

    ###############################################
    # Debit Sender
    ###############################################

    cur.execute(
        """
        UPDATE customers
        SET wallet=%s
        WHERE id=%s
        """,
        (
            sender_wallet-amount,
            sender[0]
        )
    )

    ###############################################
    # Credit Receiver
    ###############################################

    cur.execute(
        """
        UPDATE customers
        SET wallet=%s
        WHERE id=%s
        """,
        (
            receiver_wallet+amount,
            receiver[0]
        )
    )

    ###############################################
    # Insert Transaction
    ###############################################

    cur.execute(
        """
        INSERT INTO transactions
        (
            sender_id,
            receiver_email,
            amount
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            sender[0],
            receiver_email,
            amount
        )
    )

    txn_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({

        "status":"SUCCESS",

        "transaction_id":txn_id,

        "sender":sender[2],

        "receiver":receiver_email,

        "amount":amount,

        "remaining_balance":sender_wallet-amount

    })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=3003
    )