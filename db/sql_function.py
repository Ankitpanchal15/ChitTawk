import mysql.connector
from mysql.connector import Error
from flask import session


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="admin", database="chat_app"
        )
        if connection.is_connected:
            # print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error : {e}")
        return None


def create_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO users(username,password) VALUES(%s,%s)"
        cursor.execute(query, (username, password))
        conn.commit()
        print(f"{username} has registered successfully ")

    except Error as e:
        print(f"Error Executing Query : {e}")

    finally:
        cursor.close()
        conn.close()


def get_user_by_username(username):
    conn = get_db_connection()
    user = None
    try:
        cursor = conn.cursor()
        query = "SELECT id, username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

    except Error as e:
        print(f"Error Executing Query : {e}")

    finally:
        cursor.close()
        conn.close()
    return user


def get_all_Users(userid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, type FROM users WHERE id != %s", (userid,))
        users = cursor.fetchall()
        return users

    except Error as e:
        print(f"Error Executing Query : {e}")

    finally:
        cursor.close()
        conn.close()


def get_messages(sender_id, receiver_id=None, group_id=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        if group_id:  
            print("get_messages ----- group_id", group_id)
            query = """SELECT 
                        messages.id,
                        messages.message, 
                        messages.sender_id, 
                        users.username AS sender_name
                    FROM messages
                    JOIN users ON messages.sender_id = users.id
                    WHERE messages.group_id = %s
                    ORDER BY messages.timestamp ASC;
                    """
            cursor.execute(query, (group_id,))

        elif receiver_id:  
            print("get_messages ----- receiver_id", receiver_id)
            query = """SELECT 
                        messages.id,
                        messages.message, 
                        messages.sender_id, 
                        users.username AS sender_name
                    FROM messages
                    JOIN users ON messages.sender_id = users.id
                    WHERE (messages.sender_id = %s AND messages.receiver_id = %s)
                    OR (messages.sender_id = %s AND messages.receiver_id = %s)
                    ORDER BY messages.timestamp ASC;
                    """
            cursor.execute(query, (sender_id, receiver_id, receiver_id, sender_id))

        fecthData = cursor.fetchall()
        messages = None

        if fecthData:
            messages = [
                {
                    "id": id,
                    "message": message,
                    "sender_id": sender_id,
                    "send_by": send_by,
                    "sent_by_me": sender_id == session["userId"],
                }
                for id, message, sender_id, send_by in fecthData
            ]

        return messages

    except Error as e:
        print(f"Error Executing Query : {e}")

    finally:
        cursor.close()
        conn.close()


def save_message(sender_id, receiver_id, message):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        query = "INSERT INTO messages(sender_id,receiver_id,message) values(%s,%s,%s)"
        cursor.execute(query, (sender_id, receiver_id, message))
        conn.commit()
    except Error as e:
        print(f"Error Executing Query : {e}")
    finally:
        cursor.close()
        conn.close()

def save_group_message(sender_id, group_id, message):
    print("save_group_message ......", sender_id, group_id, message)
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        query = "INSERT INTO messages(sender_id,group_id,message) values(%s,%s,%s)"
        cursor.execute(query, (sender_id, group_id, message))
        conn.commit()
    except Error as e:
        print(f"Error Executing Query : {e}")
    finally:
        cursor.close()
        conn.close()


# create_user("Mark", "1234")
# create_user("", "1234")
