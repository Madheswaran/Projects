from flask import Flask, render_template_string
from flask import request
#from app import app
#import subprocess
import os
import requests

app = Flask(__name__)

#user_input = input()

#os.system(user_input)

HOME_PAGE = """
<!DOCTYPE html>
<html>

<head>
    <title>PayPal Frontend Service</title>
</head>

<body>

<h1>{{ APP_NAME }}</h1>

<h2>Environment : {{ ENV_NAME }}</h2>

<h3>Welcome</h3>

<form method="POST" action="/login">

<label>Email</label>

<br>

<input
    type="email"
    name="email"
    placeholder="Enter Email"
    required>

<br><br>

<label>Password</label>

<br>

<input
    type="password"
    name="password"
    placeholder="Enter Password"
    required>

<br><br>

<button type="submit">
    Login
</button>

</form>

</body>

</html>
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