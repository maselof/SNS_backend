import hashlib


def hash_password(username, password):
    return hashlib.sha256(username.encode() + password.encode()).hexdigest()

