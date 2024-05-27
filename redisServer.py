import socket
import threading
import time
import redis

groups = redis.Redis(host='localhost', port=6379)
messages = redis.Redis(host='localhost', port=6379)
messages.select(1)
print(groups.ping())
print(messages.ping())
#groups.flushall() 
#messages.flushall()

host = '127.0.0.1' # localhost
port = 55555

user_client = {} # a dictionary username -> client

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

def broadcast(message, groupname, username, client):
    if message.endswith("#list"): # to see list of groups
        msg = ""
        keys = groups.keys('*') # get all keys
        for i in keys:
            ii = i.decode('utf-8')
            m = groups.hget(ii, "members").decode('utf-8')
            print(m)
            msg += "Group: " + ii + " | Admin: " + groups.hget(ii, "creator").decode('utf-8')
            msg += " | Members: " + m + " | Created at: " + groups.hget(ii, "created_at").decode('utf-8')+ "\n"
        client.send(msg.encode('utf-8'))
    elif "#bio" in message: # to set a bio for group
        admin_username = groups.hget(groupname, "creator").decode('utf-8')
        if admin_username == username:
            bio = message[message.index("bio") + 4 : ]
            groups.hset(groupname, "bio", bio)
            msg = "Bio: " + bio + " | Group: " + groupname
            members = groups.hget(groupname, "members").decode('utf-8').split(' ')
            for member in members:
                if member in user_client:
                    c = user_client.get(member)
                    c.send(msg.encode('utf-8'))
        else: # if the user is 
            client.send("You Are Not Admin".encode('utf-8'))
    elif "#load" in message: # to see chat history
        hour = int(message[message.index("last") + 5 : message.index("_hour")]) # get user time
        local_time = time.localtime()
        h = local_time.tm_hour
        h = h - hour
        if h >= 0:
            while h <= local_time.tm_hour:
                format_time = time.strftime("%Y-%m-%d", time.localtime())
                format_time_2 = str(format_time) + " " + str(h)
                load_messages = messages.lrange(groupname + "Messages", 0, -1)
                for m in sorted(load_messages):
                    message_decoded = m.decode('utf-8')
                    if format_time_2 in message_decoded:
                        client.send(message_decoded.encode('utf-8'))
                h += 1
        else:
            client.send("Wrong Time! You Can See Today's Messages".encode('utf-8'))
    else:
        if groups.hexists(groupname, "creator"): #to see group
            members = groups.hget(groupname, "members").decode('utf-8').split(' ')
            if username in members: #to send message
                if message.endswith('#left'): # to left the group
                    t_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    msg = "[" + t_string + "] Member: " + username + " Has Left | Group: " + groupname + "\n"
                    messages.lpush(groupname + "Messages", msg)
                    for member in members:
                        if member in user_client:
                            c = user_client.get(member)
                            c.send(msg.encode('utf-8'))
                    members.remove(username)
                    s = ' '.join(map(str, members))
                    groups.hset(groupname, "members", s)
                else:
                    t_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    message = "[" + t_string + "] " + message + "\n"
                    messages.lpush(groupname + "Messages", message)
                    for member in members:
                        if member in user_client:
                            c = user_client.get(member)
                            c.send(message.encode('utf-8'))
            else: # to send message and join the group
                members = groups.hget(groupname, "members").decode('utf-8').split(' ')
                members.append(username)
                s = ' '.join(map(str, members))
                groups.hset(groupname, "members", s)
                t_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg = "[" + t_string + "] New Member: " + username + " | Group: " + groupname + "\n"
                message = "[" + t_string + "] " + message + "\n"
                messages.lpush(groupname + "Messages", msg)
                messages.lpush(groupname + "Messages", message)
                message = msg + message
                members = groups.hget(groupname, "members").decode('utf-8').split(' ')
                for member in members:
                    if member in user_client:
                        c = user_client.get(member)
                        c.send(message.encode('utf-8'))
        else: # make new group
            groups.hset(groupname, "creator", username)
            groups.hset(groupname, "members", username)
            t_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            groups.hset(groupname, "created_at", t_string)
            msg = "[" + t_string + "] New Group: " + groupname + " | Admin: " + username + "\n"
            message = "[" + t_string + "] " + message + "\n"
            messages.lpush(groupname + "Messages", msg)
            messages.lpush(groupname + "Messages", message)
            message = msg + message
            client.send(message.encode('utf-8'))

def handle(client): # handles client's messages
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.endswith("#list"):
                broadcast(message, '.', '..', client)
            else:
                groupname = message[message.index('(') + 1:message.index(')')]
                username = message[0:message.index('(') - 1]
                broadcast(message, groupname, username, client)
        except:
            client.close()
            break

def receive(): # accept client and receive client's messages 
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('Username'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')

        user_client.update({username : client})

        print(f'Username of the client is {username}')
        client.send('Welcome to RPG_Chatroom!\nSend #list to See List of Groups'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
print("Server is listening...")
receive()