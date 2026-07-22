from flask import Flask,jsonify
import requests
import psycopg2

app = Flask(__name__)

@app.route("/users")
def users():

    return jsonify(
        [
            {"id":1,"name":"Ganesha"},
            {"id":2,"name":"Muruga"}
        ]
    )

@app.route("/health")
def health():
    return {"status":"UP"},200

@app.route("/ready")
def ready():
    return {"status":"READY"},200

conn = psycopg2.connect(
    host="postgres",
    database="paypal",
    user="admin",
    password="password"
)

@app.route("/login",methods=["POST"])
def login():

    data=request.json

    email=data["email"]
    password=data["password"]

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

    if not row:
        return {"status":"failed"},401

    return {
        "id":row[0],
        "name":row[1],
        "wallet":float(row[2])
    }

@app.route("/profile/<id>")
def profile(id):

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

    return {
        "name":row[1],
        "email":row[2],
        "wallet":float(row[4])
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3002)