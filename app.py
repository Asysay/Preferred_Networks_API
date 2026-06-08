from flask import Flask, request, jsonify
import re

app = Flask(__name__)

accounts = [
{
  "user_id": "TaroYamada",
  "password": "PaSSwd4TY",
  "nickname": "たろー",
  "comment": "僕は元気です"
},
{
    "user_id": "Test-",
    "password": "PaSSwd4TY",
    "nickname": "Test-",
    "comment": "Reserved testing account"
}
]

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    password = data.get("password")

    if not isinstance(user_id, str) or not isinstance(password, str):
        return jsonify({
            "message": "Account creation failed",
            "cause": "Required user_id and password"
        }), 400

    if not (6 <= len(user_id) <= 20) or not (8 <= len(password) <= 20):
        return jsonify({
            "message": "Account creation failed",
            "cause": "Input length is incorrect"
        }), 400

    if not re.fullmatch(r"^[A-Za-z0-9]+$", user_id):
        return jsonify({
            "message": "Account creation failed",
            "cause": "Incorrect character pattern"
        }), 400

    if not re.fullmatch(r"^[\x21-\x7E]+$", password):
        return jsonify({
            "message": "Account creation failed",
            "cause": "Incorrect character pattern"
        }), 400

    for account in accounts:
        if account["user_id"] == user_id:
            return jsonify({
                "message": "Account creation failed",
                "cause": "Already same user_id is used"
            }), 400

    created_account = {
        "user_id": user_id,
        "password": password,
    }

    accounts.append(created_account)

    return jsonify({
        "message": "Account successfully created",
        "account": created_account
    }), 200

def find_account_by_user_id(user_id):
    for account in accounts:
        if account["user_id"] == user_id:
            return account
    return None

def make_user_response(account):
    user = {
        "user_id": account["user_id"],
        "nickname": account.get("nickname") or account["user_id"]
    }

    if account.get("comment"):
        user["comment"] = account["comment"]

    return user

def authenticate_request():
    auth = request.authorization

    if auth is None:
        return None

    auth_account = find_account_by_user_id(auth.username)

    if auth_account is None:
        return None

    if auth.password != auth_account["password"]:
        return None

    return auth_account

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    account = find_account_by_user_id(user_id)

    if account is None:
        return jsonify({
            "message": "No user found"
        }), 404

    auth_account = authenticate_request()

    if auth_account is None:
        return jsonify({
            "message": "Authentication failed"
        }), 401

    return jsonify({
        "message": "User details by user_id",
        "user": make_user_response(account)
    }), 200

def is_valid_profile_text(value, max_length):
    if not isinstance(value, str):
        return False

    if len(value) > max_length:
        return False

    # Allows normal printable text, including Japanese.
    # Rejects control characters like newline, tab, etc.
    if not value.isprintable():
        return False

    return True


@app.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    account = find_account_by_user_id(user_id)

    if account is None:
        return jsonify({
            "message": "User not found"
        }), 404

    auth_account = authenticate_request()

    if auth_account is None:
        return jsonify({
            "message": "Authentication failed"
        }), 401

    if auth_account["user_id"] != user_id:
        return jsonify({
            "message": "No permission for update"
        }), 403

    data = request.get_json(silent=True) or {}

    if "user_id" in data or "password" in data:
        return jsonify({
            "message": "User updation failed",
            "cause": "Not updatable user_id and password"
        }), 400

    if "nickname" not in data and "comment" not in data:
        return jsonify({
            "message": "User updation failed",
            "cause": "Required nickname or comment"
        }), 400

    if "nickname" in data:
        nickname = data["nickname"]

        if not is_valid_profile_text(nickname, 30):
            return jsonify({
                "message": "User updation failed",
                "cause": "String length limit exceeded or containing invalid characters"
            }), 400

    if "comment" in data:
        comment = data["comment"]

        if not is_valid_profile_text(comment, 100):
            return jsonify({
                "message": "User updation failed",
                "cause": "String length limit exceeded or containing invalid characters"
            }), 400

    if "nickname" in data:
        if data["nickname"] == "":
            account["nickname"] = account["user_id"]
        else:
            account["nickname"] = data["nickname"]

    if "comment" in data:
        if data["comment"] == "":
            account.pop("comment", None)
        else:
            account["comment"] = data["comment"]

    return jsonify({
        "message": "User successfully updated",
        "user": make_user_response(account)
    }), 200

@app.route("/close", methods=["POST"])
def close_account():
    auth_account = authenticate_request()

    if auth_account is None:
        return jsonify({
            "message": "Authentication failed"
        }), 401

    accounts.remove(auth_account)

    return jsonify({
        "message": "Account and user successfully removed"
    }), 200

if __name__ == "__main__":
    app.run(debug=True)