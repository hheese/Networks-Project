import socket

# Written by: Henry Heese
# Student ID: 16261325
# Date: Mar. 16, 2023
#
# This is the client side of the undergraduate chatroom project. 
# Coded in Python 3.11.0

HEADER = 64
PORT = 11325
SERVER = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "logout"
LOGIN_MESSAGE = "login"
NEWUSER_MESSAGE = "newuser"
SEND_MESSAGE = "send"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg) :
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

# Determines if given username and password are within given bounds.
# Used by handle_login and handle_newuser
# Returns if it is valid or not.
def validate_credentials(username, password) :
    if len(username) < 3 or len(username) > 32:
        return False, "> Denied. Username must be between 3 and 32 characters."
    if len(password) < 4 or len(password) > 8:
        return False, "> Denied. Password must be between 4 and 8 characters."
    if " " in username or " " in password:
        return False, "> Denied. Username or password cannot contain spaces."
    return True, ""

# Client receives welcome message
send("")
# Client can continue sending to server until it disconnects with the logout command
while (True) :
    text = input(">").strip()

    # Client does initial check to ensure commands are formatted within constraints
    tokens = text.split()
    if len(tokens) == 0: continue
    if tokens[0] == DISCONNECT_MESSAGE:
        send(DISCONNECT_MESSAGE)
        break
    # Check for valid name/password input
    elif tokens[0] == LOGIN_MESSAGE or tokens[0] == NEWUSER_MESSAGE:
        if len(tokens) == 3 :
            valid, reply = validate_credentials(tokens[1], tokens[2])
            if (valid) : send(text)
            else: print(reply)
        else: print("> Denied. Please use correct command format.")
    # Check message size is within bounds
    elif tokens[0] == SEND_MESSAGE:
        if len(tokens) > 1 :
            if len(text) <= 260 : send(text)
            else : print("> Denied. Message must be less than 256 characters.")
        else : print("> Denied. Please use correct command format.")
    else : print("> Denied. Invalid command.")