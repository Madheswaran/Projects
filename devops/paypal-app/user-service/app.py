from flask import Flask,jsonify

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


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3002)