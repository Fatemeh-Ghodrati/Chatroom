import socket
import threading

host = '127.0.0.1'
port = 55555

username = input("\033[94m{}\033[00m" .format("Please Enter Your Username: ")) # blue
print("\033[94m{}\033[00m" .format("Guidance:")) # a guidance of hsending message
print("\033[94m{}\033[00m" .format("To Send or Join in Group -> (groupname) : message"))
print("\033[94m{}\033[00m" .format("To See List of Groups -> #list"))
print("\033[94m{}\033[00m" .format("To Write a Bio for Group -> (groupname) : #bio bio"))
print("\033[94m{}\033[00m" .format("To See Chat History -> (groupname) : #load_last_n_hour_message"))
print("\033[94m{}\033[00m" .format("To Left from a Group -> (groupname) : #left"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "Username":
                client.send(username.encode('utf-8'))
            elif message == "Welcome to RPG_Chatroom!\nSend #list to See List of Groups":
                print("\033[92m{}\033[00m" .format(message)) # green
            else:
                print("\033[93m{}\033[00m" .format(message)) # yellow
        except:
            print("\033[91m{}\033[00m" .format("An Error Occured")) # red
            client.close()
            break

def write():
    while True:
        message = f'{username} {input("")}'
        if message.endswith("#list") :
            client.send(message.encode('utf-8'))
        elif (message[message.index(':') - 2] != ')' or message.index(')') + 1 <= message.index('(')):
            print("\033[91m{}\033[00m" .format("Invalid Input"))
        else:
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

# guidance is blue
# error is red
# joining to chatroom is green
# group'messages are yello
# input is white