from flask import Flask, render_template_string
from flask import request
#from app import app
#import subprocess
import os
import requests

app = Flask(__name__)

#user_input = input()

#os.system(user_input)

<!DOCTYPE html>
<html>

<head>

<title>{{ APP_NAME }}</title>

<style>

*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:Arial,Helvetica,sans-serif;
}

body{

background:#eef2f7;

display:flex;

justify-content:center;

align-items:center;

height:100vh;

}

.container{

width:1100px;

height:650px;

display:flex;

background:white;

border-radius:18px;

overflow:hidden;

box-shadow:0 15px 40px rgba(0,0,0,.25);

}

.left{

width:40%;

padding:60px;

display:flex;

flex-direction:column;

justify-content:center;

background:white;

}

.left h1{

font-size:34px;

color:#003087;

margin-bottom:15px;

}

.left h3{

margin-bottom:40px;

color:#666;

}

input{

width:100%;

padding:14px;

margin-top:8px;

margin-bottom:25px;

border-radius:8px;

border:1px solid #ccc;

font-size:16px;

}

button{

width:100%;

padding:15px;

background:#0070ba;

color:white;

font-size:18px;

border:none;

border-radius:8px;

cursor:pointer;

transition:.3s;

}

button:hover{

background:#005ea6;

}

.right{

width:60%;

background:#f7f9fc;

display:flex;

justify-content:center;

align-items:center;

padding:40px;

}

.right img{

width:100%;

max-width:650px;

}

.footer{

margin-top:20px;

font-size:13px;

color:gray;

text-align:center;

}

</style>

</head>

<body>

<div class="container">

<div class="left">

<h1>{{ APP_NAME }}</h1>

<h3>Environment : {{ ENV_NAME }}</h3>

<form action="/login" method="POST">

<label>Email</label>

<input
name="email"
type="email"
placeholder="Enter Email"
required>

<label>Password</label>

<input
name="password"
type="password"
placeholder="Enter Password"
required>

<button type="submit">
Login
</button>

</form>

<div class="footer">

Secure Checkout • Powered by Kubernetes

</div>

</div>

<div class="right">

<img
src="{{ url_for('static', filename='shopping-bg.png') }}"
alt="Shopping">

</div>

</div>

</body>

</html>

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    response = requests.post(
        "http://user-service/login",
        json={
            "email": email,
            "password": password
        }
    )

    if response.status_code != 200:
        return """
        <h2>Login Failed</h2>

        <a href="/">
            Try Again
        </a>
        """

    user = response.json()

    return f"""
    <h1>Welcome {user['name']}</h1>

    <h2>Wallet Balance : ₹ {user['wallet']}</h2>

    <br>

    <a href="/">
        Logout
    </a>
    """

@app.route("/")
def home():
    
    APP_NAME = os.getenv("APP_NAME", "Paypal")
    ENV_NAME = os.getenv("ENV_NAME", "DEV")

    API_KEY = os.getenv("API_KEY")
    if API_KEY:
        API_KEY_MASKED = API_KEY[:5] + "*****"
    else:
        API_KEY_MASKED = "NOT_SET"

    DB_PASSWORD = os.getenv("DB_PASSWORD", "dummy-password")

    return render_template_string(HOME_PAGE, 
                                    APP_NAME=APP_NAME, 
                                        ENV_NAME=ENV_NAME, 
                                            API_KEY=API_KEY_MASKED)

@app.route("/users")
def users():

    response = requests.get(
        "http://user-service/users"
    )

    return response.json()
                               
@app.route("/health")
def health():
    return {"status": "UP"}, 200


@app.route("/ready")
def ready():
    return {"status": "READY"}, 200
    #return "NOT READY", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)