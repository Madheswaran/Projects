from flask import Flask, render_template_string
#from app import app
import subprocess

app = Flask(__name__)

subprocess.call("ls", shell=True)
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PayPal Checkout</title>
</head>
<body>

<h1>PayPal Checkout</h1>

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


#def test_home():
#    client = app.test_client()
#    response = client.get("/")
#    assert response.status_code == 200
