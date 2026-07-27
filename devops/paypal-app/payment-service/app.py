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
    app.logger.warning(f"Incoming JSON: {data}")

    customer_id = data["customer_id"]
    receiver_email = data["receiver"]
    amount = float(data["amount"])

    conn = get_connection()
    cur = conn.cursor()

    #################################################
    # Get Sender
    #################################################

    cur.execute(
        """
        SELECT id, name, email, wallet
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
            "status": "FAILED",
            "message": "Sender not found"
        }), 404

    #################################################
    # Get Receiver
    #################################################

    cur.execute(
        """
        SELECT id, name, email, wallet
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
            "status": "FAILED",
            "message": "Receiver not found"
        }), 404

    sender_wallet = float(sender[3])
    receiver_wallet = float(receiver[3])

    #################################################
    # Validate Balance
    #################################################

    if sender_wallet < amount:

        cur.close()
        conn.close()

        return jsonify({
            "status": "FAILED",
            "message": "Insufficient Balance"
        }), 400

    #################################################
    # Update Wallets
    #################################################

    new_wallet = sender_wallet - amount

    cur.execute(
        """
        UPDATE customers
        SET wallet=%s
        WHERE id=%s
        """,
        (
            new_wallet,
            sender[0]
        )
    )

    cur.execute(
        """
        UPDATE customers    
        SET wallet=%s
        WHERE id=%s
        """,
        (
            receiver_wallet + amount,
            receiver[0]
        )
    )

    #################################################
    # Save Transaction
    #################################################

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
            customer_id,
            receiver_email,
            amount
        )
    )

    transaction_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    #################################################
    # Response
    #################################################

    return jsonify({

        "status": "SUCCESS",

        "transaction_id": transaction_id,

        "message": "Payment Successful",

        "customer_id": customer_id,

        "receiver": receiver_email,

        "amount": amount,

        "remaining_balance": new_wallet

    })

@app.route("/add-money", methods=["POST"])
def add_money():

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

        return jsonify({

            "status": "FAILED",

            "message": "Customer not found"

        }),404

    new_wallet = float(row[0]) + amount

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

        "status": "SUCCESS",

        "message": "Money Added Successfully",

        "amount": amount,

        "remaining_balance": new_wallet

    })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=3003
    )