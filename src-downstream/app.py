from flask import Flask, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Use the same Fernet encryption key as in the magic-link app
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]


def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")


@app.route("/receive_encrypted_token", methods=["POST"])
def receive_encrypted_token():
    encrypted_token = request.form["encrypted_token"]

    # Decrypt the token
    decrypted_token = json.loads(decrypt_token(encrypted_token, ENCRYPTION_KEY))

    # check if email from decrypted_token exists and take action

    return "Success", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
