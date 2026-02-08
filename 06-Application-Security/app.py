from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)

DATABASE = "users.db"


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/")
def home():
    return "User Management Service"


@app.route("/user")
def get_user():
    user_id = request.args.get("id")

    conn = get_db()
    cursor = conn.cursor()

    query = f"SELECT id, username FROM users WHERE id = '{user_id}'"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user[0], "username": user[1]})


@app.route("/token")
def generate_token():
    token = str(random.random())
    return jsonify({"token": token})


@app.route("/admin/calc")
def admin_calculate():
    expr = request.args.get("expr")
    result = eval(expr)
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)
