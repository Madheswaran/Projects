from flask import Flask,jsonify
import requests
import psycopg2
import os

DB_HOST = os.getenv("DB_HOST","postgres")
DB_NAME = os.getenv("DB_NAME","paypal")
DB_USER = os.getenv("DB_USER","admin")
DB_PASSWORD = os.getenv("DB_PASSWORD","password")

app = Flask(__name__)

@app.route("/users")
def users():

    if os.getenv("CI") == "true":
        return jsonify(
            [
                {"id":1,"name":"Ganesha"},
                {"id":2,"name":"Muruga"}
            ]
        )

    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute(
        """
        select id,name
        from customers
        """
    )

    rows=cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(
        [
            {
                "id":r[0],
                "name":r[1]
            }
            for r in rows
        ]
    )

@app.route("/health")
def health():
    return {"status":"UP"},200

@app.route("/ready")
def ready():
    return {"status":"READY"},200

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST","postgres"),
        database=os.getenv("DB_NAME","paypal"),
        user=os.getenv("DB_USER","admin"),
        password=os.getenv("DB_PASSWORD","password")
    )

@app.route("/login",methods=["POST"])
def login():

    data=request.json

    email=data["email"]
    password=data["password"]

    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute(
      """
      select id,name,wallet
      from customers
      where email=%s
      and password=%s
      """,
      (email,password)
    )

    row=cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"status":"failed"},401

    return {
        "id":row[0],
        "name":row[1],
        "wallet":float(row[2])
    }

@app.route("/profile/<id>")
def profile(id):

    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute(
      """
      select *
      from customers
      where id=%s
      """,
      (id,)
    )

    row=cur.fetchone()

    cur.close()
    conn.close()

    return {
        "name":row[1],
        "email":row[2],
        "wallet":float(row[4])
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3002)