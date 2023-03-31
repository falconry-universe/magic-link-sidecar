from flask import Flask, request, jsonify, render_template, redirect, url_for
from cryptography.fernet import Fernet
import requests
import os
import json
from time import time
import mailjet_rest

app = Flask(__name__)

ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]


def encrypt_token(token, key):
    fernet = Fernet(key)
    return fernet.encrypt(token.encode("utf-8"))


def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")


def send_magic_link_email(email, magic_link):
    api_key = os.environ["MAILJET_API_KEY"]
    api_secret = os.environ["MAILJET_API_SECRET"]
    mailjet = mailjet_rest.Client(auth=(api_key, api_secret), version="v3.1")
    data = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ["APP_FROM_EMAIL_ADDRESS"],
                    "Name": os.environ["APP_FROM_NAME"],
                },
                "To": [{"Email": email}],
                "Subject": f"Magic Link to login to {os.environ['APP_NAME']}",
                "TextPart": "Click on the magic link below to continue:",
                "HTMLPart": f'<a href="{magic_link}">Magic Link</a>',
            }
        ]
    }
    return mailjet.send.create(data=data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_magic_link", methods=["POST"])
def generate_magic_link():
    email = request.form["email"]
    token_dict = dict(nonce=os.urandom(32).hex(), timestamp=time.time, email=email)
    # Generate unique token

    # Encrypt the token
    encrypted_token = encrypt_token(json.dumps(token_dict), ENCRYPTION_KEY)

    # Send magic-link email using Mailjet API
    magic_link = f"{request.url_root}magic_link_callback?token={encrypted_token}"
    send_magic_link_email(email, magic_link)

    return "Magic link sent", 200


@app.route("/magic_link_callback", methods=["GET"])
def magic_link_callback():
    encrypted_token = request.args.get("token")
    try:
        decrypted_token = json.loads(decrypt_token(encrypted_token, ENCRYPTION_KEY))
    except InvalidToken:
        return "Invalid token. Unable to decrypt.", 400

    # Send the decrypted token to the downstream app
    downstream_app_url = os.environ["DOWNSTREAM_APP_URL"]
    response = requests.post(
        downstream_app_url, data={"decrypted_token": decrypted_token}
    )

    if response.status_code == 200:
        return "Success", 200
    else:
        return "Error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
