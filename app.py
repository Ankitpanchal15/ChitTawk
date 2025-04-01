from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from db.sql_function import (
    get_user_by_username,
    get_all_Users,
    get_messages,
    save_message,
    save_group_message,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-app"
socketio = SocketIO(app)


@app.route("/login", methods=["GET", "POST"])
def loginpage():
    if request.method == "POST":
        username = request.form.get("username")
        user = get_user_by_username(username)
        if user:
            session["username"] = user[1]
            session["userId"] = user[0]

            return redirect(url_for("home"))
        else:
            flash("Invalid Users, Please Enter Valid User", "error")

    return render_template("login.html")


@app.route("/")
@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("loginpage"))
    userId = session["userId"]
    usersList = get_all_Users(userId)
    usersListDict = []
    if usersList:
        usersListDict = [
            {"user_id": user_id, "user_name": user_name, "type": type}
            for user_id, user_name, type in usersList
        ]
    return render_template(
        "home.html", username=session["username"], users=usersListDict
    )


user_session = {}
users_status = {}


@socketio.on("connect")
def handle_Connect():
    client_id = request.sid

    if "userId" in session:
        user_session[session["userId"]] = client_id
        print("user_session", user_session)
        emit("connection_response", {"userId": session["userId"]})


@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
        session.pop("userId", None)
    return redirect(url_for("loginpage"))


@socketio.on("disconnect")
def handle_disconnect():
    if "username" in session:
        username = session["username"]
        emit(
            "chat_message",
            {"sender": "server", "message": f"{username} has left the chat"},
            broadcast=True,
        )


@socketio.on("get_messages")
def get_all_messages(data):
    reciever_id = data.get("selected_user_id")
    group_message = data.get("chat_type") == "group"
    group_id = None

    if group_message:
        group_id = reciever_id

    sender_id = session["userId"]
    messages = get_messages(sender_id, reciever_id, group_id)
    sender_sid = user_session.get(sender_id)

    # print("sender_sid", sender_sid, user_session)

    emit("load_history_messages", {"messages": messages}, room=sender_sid)


@socketio.on("message")
def handle_message(data):
    sender = session["username"]
    message = data["message"]
    sender_id = session["userId"]
    reciever_id = data["reciever_id"]

    receiver_session_id = user_session.get(int(reciever_id), None)
    sender_session_id = user_session.get(int(session["userId"]), None)

    group_message = data.get("chat_type") == "group"

    if group_message:
        emit(
            "new_message",
            {
                "send_by": sender,
                "message": message,
                "sender_id": sender_id,
                "reciever_id": reciever_id,
            },
            broadcast=True,
        )
    else:
        emit(
            "new_message",
            {
                "send_by": sender,
                "message": message,
                "sender_id": sender_id,
                "reciever_id": reciever_id,
            },
            room=[receiver_session_id, sender_session_id],
        )

    if group_message:
        save_group_message(
            sender_id,
            reciever_id,
            message,
        )
    else:
        save_message(sender_id, reciever_id, message)


if __name__ == "__main__":
    socketio.run(app, debug=True)
