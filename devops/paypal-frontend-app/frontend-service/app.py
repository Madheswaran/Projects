from flask import Flask, render_template_string
#from app import app
#import subprocess
import os

app = Flask(__name__)

#user_input = input()

#os.system(user_input)

APP_NAME = os.getenv("APP_NAME", "Paypal")
ENV_NAME = os.getenv("ENV_NAME", "DEV")

HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PayPal frontend Service</title>
</head>
<body>

<h1>{{ APP_NAME }}</h1>

<h2>Environment : {{ ENV_NAME }}</h2>

<h3>Welcome</h3>

<form>

Email

<br>

<input type="text">

<br><br>

Password

<br>

<input type="password">

<br><br>

<button>Login</button>

</form>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)