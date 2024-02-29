import socket
import threading
import os

# Written by: Henry Heese
# Student ID: 16261325
# Date: Mar. 16, 2023
#
# This is the server side of the undergraduate chatroom project. 
# Coded in Python 3.11.0

# Declare constants
HEADER = 64
PORT = 11325
# IP can be hard coded or found automatically
SERVER = "127.0.0.1" 
#SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
# encoding format
FORMAT = 'utf-8'
USERS_FILEPATH = "users.txt"
DISCONNECT_MESSAGE = "logout"
LOGIN_MESSAGE = "login"
NEWUSER_MESSAGE = "newuser"
SEND_MESSAGE = "send"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, -1)
server.bind(ADDR)

# Determines if given username and password are within given bounds.
# Used by handle_login and handle_newuser
# Returns if it is valid or not. If not, also returns the message to be sent to the client
def validate_credentials(username, password) :
    if len(username) < 3 or len(username) > 32:
        return False, "Denied. Username must be between 3 and 32 characters."
    if len(password) < 4 or len(password) > 8:
        return False, "Denied. Password must be between 4 and 8 characters."
    if " " in username or " " in password:
        return False, "Denied. Username or password cannot contain spaces."
    return True, ""

# Determines if given login credentials match a correct user in {USER_FILEPATH}.txt
# Returns username on success as well as the message for the client
def handle_login(tokens) :
    if len(tokens) != 3 :
        return False, f"Denied. Please use the format: [{LOGIN_MESSAGE} (username) (password)]"
    username = tokens[1]
    password = tokens[2]
    valid_credentials, reply = validate_credentials(username, password)
    if not valid_credentials:
        return False, reply
    
    with open(USERS_FILEPATH, "r") as file:
        lines = file.readlines()
        for line in lines:
            # name/password are separated and stripped of extra characters
            existing_user, existing_password = line.split()
            if existing_user.strip("(),") == username and existing_password.strip("(),") == password:
                current_user = username
                # On success, the username of the login is returned as well as the message
                return username, "login confirmed"
    return False, "Denied. User name or password incorrect."

# Checks that a newuser input is not already in the given users file
# returns True or False depending on success of making a new user as well as a message for the client
def handle_newuser(tokens) :
    if len(tokens) != 3 :
        return False, f"Denied. Please use the format: [{NEWUSER_MESSAGE} (username) (password)]"
    username = tokens[1]
    password = tokens[2]
    valid_credentials, reply = validate_credentials(username, password)
    if not valid_credentials:
        return False, reply
    
    valid_newuser = True
    with open(USERS_FILEPATH, "r") as file:
        lines = file.readlines()
        for line in lines:
            # usernames in given text file are split from passwords and stripped of excess characters
            existing_user, _ = line.split()
            if existing_user.strip("(),") == username:
                valid_newuser = False
    if not valid_newuser:
        return False, "Denied. User account already exists"
    
    # On success, the new name/password is written to the given users file in proper format
    with open(USERS_FILEPATH, "a") as file:
        file.write(f"({username}, {password})\n")
    return True, f"New user account created. Please login."

# Determines if a message is able to be sent
# The message tokens that were split to find the command are rejoined
# Returns status as well as a message for the client
def handle_send(tokens) :
    if len(tokens) < 2:
        return False, f"Denied. Invalid input. Try: [{SEND_MESSAGE} (message)]"
    message = " ".join(tokens[1:])

    # Is false if the message is not within given size bounds
    if len(message) < 1 or len(message) > 256:
        return False, "Denied. Message size must be between 1 and 256 characters"
    return True, message



def handle_client(conn, addr) :
    #print(f"New Connection: {addr} connected.")
    conn.send("\nMy chat room server. Version One.\n".encode(FORMAT))
    connected = True

    # Tracks current user so that their name can be displayed before chat messages
    current_user = None
    while connected:
        # Loops to keep receiving messages from the client
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length :
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            
            try: 
                reply, server_statement = "", None
                # Break up msg into tokens for handling::
                tokens = msg.split()
                if len(tokens) == 0: continue
                
                # On Disconnect the client is cut off. Works when logged in or not.
                # current user is reset, but client program exits anyways on proper logout.
                # Sends a message to both client and server.
                if tokens[0] == DISCONNECT_MESSAGE:
                    if current_user:
                        reply = f"{current_user} left."
                        server_statement = f"{current_user} logout"
                        current_user = None
                    else :
                        reply = "User left."
                        server_statement = "User logout."
                    connected = False

                # On Login the current user is updated. 
                # Sends a message to both client and server on success, otherwise tells the client what went wrong
                elif tokens[0] == LOGIN_MESSAGE:
                    new_user, reply = handle_login(tokens)
                    if new_user: 
                        current_user = new_user
                        server_statement = f"{current_user} login."

                # On success, creates a new username/password in the given users file
                # Sends a message to both client and server on success, otherwise tells the client what went wrong
                elif tokens[0] == NEWUSER_MESSAGE:
                    valid_newuser, reply = handle_newuser(tokens)
                    if valid_newuser:
                        server_statement = "New user account created."

                # On success, allows a logged in user to chat with the server. 
                # Sends a message to both client and server on success, otherwise tells the client what went wrong
                elif tokens[0] == SEND_MESSAGE:
                    if current_user == None:
                        reply = ("Denied. Please login first.")
                    else : 
                        valid_message, reply = handle_send(tokens)
                        if valid_message:
                            server_statement = reply = f"{current_user}: {reply}"

                else :
                    # Only triggers if the first token is not recognized.
                    reply = ("Invalid command.")
            
            except Exception as e:
                print(f"Error: {e}")

            #print(f"[{addr}] {current_user} {msg}")
            #conn.send(f"[ECHO] {msg}".encode(FORMAT))

            # Server messages are sent if set, client replies are always sent with proper format.
            if server_statement: print(server_statement)
            conn.send(f"> {reply}".encode(FORMAT))
    conn.close()


def start():
    # If user file is not present, it is created. It is read when needed.
    if os.path.exists(USERS_FILEPATH):
        pass
    else:
        with open(USERS_FILEPATH, "w") as f:
            pass

    server.listen()
    #print(f"Server is listening on {SERVER}")
    print("\nMy chat room server. Version One.\n")
    while True :
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        #print(f"Active Conections: {threading.active_count() - 1}")


#print("server is starting!")
start()



