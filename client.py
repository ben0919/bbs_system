import socket
import sys
import threading
import time
import select
from collections import deque
HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (HOST, PORT)

chatroom_records = deque(maxlen = 3)

class client():
    def __init__(self):
        self.login_id = 0
        self.chatroom_history = 0
        self.chatroom_status = 0
        self.name = ''
        self.chatroom_address = None
    def connect(self, address):
        self.address = address
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp.connect(address)
        welcome_message = str(self.tcp.recv(1000), encoding = 'utf-8')
        print(welcome_message)
    def read_command(self):
        input_command = input("% " )
        self.command = input_command.split()
        if self.command[0] == 'login':
            message = input_command + ' ' + str(self.login_id)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            splitted_message = message.split()
            if splitted_message[0].isdigit():
                self.login_id = int(splitted_message[0])
                splitted_message.remove(splitted_message[0])
                name = splitted_message[1]
                self.name = name.replace('.', '')
                message = ' '.join(splitted_message)
            print(message)
        elif self.command[0] == 'logout':
            message = input_command + ' ' + str(self.login_id) + ' ' + str(self.chatroom_status)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            if('Bye' in message):
                self.login_id = 0
            print(message)
        elif self.command[0] == 'list-user':
            self.tcp.sendall(input_command.encode('utf-8'))
            message = str(self.tcp.recv(100000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'exit':
            self.tcp.sendall(input_command.encode('utf-8'))
        elif self.command[0] == 'register':
            self.udp.sendto(input_command.encode('utf-8'), self.address)
            message, addr = self.udp.recvfrom(1000)
            message = message.decode('utf-8')
            print(message)
        elif self.command[0] == 'whoami':
            message = input_command + ' ' + str(self.login_id)
            self.udp.sendto(message.encode('utf-8'), self.address)
            message, addr = self.udp.recvfrom(1000)
            message = message.decode('utf-8')
            print(message)
        elif self.command[0] == 'create-board':
            message = input_command + ' ' + str(self.login_id)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'create-post':
            message = input_command + '¬' + str(self.login_id) ##因為post的content有可能有空格 所以隨邊挑一個特殊符號來用
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'list-board':
            message = input_command
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(10000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'list-post':
            message = input_command
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(10000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'read':
            message = input_command
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(10000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'delete-post':
            message = input_command + ' ' + str(self.login_id)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'update-post':
            message = input_command + '¬' + str(self.login_id) ##因為update的內容有可能有空格 所以隨邊挑一個特殊符號來用
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'comment':
            message = input_command + '¬' + str(self.login_id)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            print(message)
        elif self.command[0] == 'create-chatroom':
            message = input_command + ' ' + str(self.login_id) + ' ' + str(self.chatroom_history)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            if 'start' in message:
                self.chatroom_history = 1
                self.chatroom_status = 1
                message = message.split()
                address = (message[-2], int(message[-1]))
                self.chatroom_address = address
                print('start to create chatroom...')
                self.chatroom_server = chatroom_server()
                self.chatroom_server.start(self.chatroom_address)
                self.join_chatroom(address, True)
            else:
                print(message)
        elif self.command[0] == 'list-chatroom':
            input_command = input_command + ' ' + str(self.login_id)
            self.udp.sendto(input_command.encode('utf-8'), self.address)
            message, addr = self.udp.recvfrom(10000)
            message = message.decode('utf-8')
            print(message)
        elif self.command[0] == 'join-chatroom':
            message = input_command + ' ' + str(self.login_id)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            if 'Action' in message:
                message = message.split()
                address = (message[-2], int(message[-1]))
                self.join_chatroom(address, False)
            else: 
                print(message)
        elif self.command[0] == 'attach':
            if len(self.command) != 1:
                print('Usage: attach') 
            elif self.login_id == 0:
                print('Please login first.')
            elif self.chatroom_history == 0:
                print('Please create-chatroom first.')
            elif self.chatroom_status == 0:
                print('Please restart-chatroom first.')
            else:
                self.join_chatroom(self.chatroom_address, True)
        elif self.command[0] == 'restart-chatroom':
            message = input_command + ' ' + str(self.login_id) + ' ' + str(self.chatroom_history)
            self.tcp.sendall(message.encode('utf-8'))
            message = str(self.tcp.recv(1000), encoding = 'utf-8')
            if 'start' in message:
                self.chatroom_history = 1
                self.chatroom_status = 1
                message = message.split()
                address = (message[-2], int(message[-1]))
                self.chatroom_address = address
                print('start to create chatroom...')
                self.chatroom_server = chatroom_server()
                self.chatroom_server.start(self.chatroom_address)
                self.join_chatroom(address, True)
            else:
                print(message)
        else:
            print('Unsupported command!')

    def join_chatroom(self, address, owner):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(address)
        welcome_message = str(connection.recv(1000), encoding = 'utf-8')
        print(welcome_message)
        if owner:
            while True:
                try:
                    sockets_list = [sys.stdin, connection]
                    read_sockets,write_sockets, error_sockets = select.select(sockets_list,[],[])
                    for mysocket in read_sockets:
                        if mysocket == connection:
                            message = str(connection.recv(1000), encoding = 'utf-8')
                            if message == 'close':
                                print('Welcome back to BBS')
                                connection.close()
                                break
                            else:
                                print(message)
                        else:
                            input_command = sys.stdin.readline().strip('\n')
                            if input_command == 'leave-chatroom':
                                input_command = input_command + ' ' + '1'
                                connection.sendall(input_command.encode('utf-8'))
                                message = 'chatroom-closed' + ' ' + str(self.login_id)
                                self.tcp.sendall(message.encode())
                                self.chatroom_status = 0
                                break
                            if input_command == 'detach':
                                connection.sendall(input_command.encode('utf-8'))
                                break
                            else:
                                now = time.strftime('[%H:%M]', time.localtime())
                                message = self.name + now + ':' + input_command
                                connection.sendall(message.encode('utf-8'))
                except:
                    break
        else:
            join_message = 'sys' + self.name + ' join us.'
            connection.sendall(join_message.encode('utf-8'))
            while True:
                try:
                    sockets_list = [sys.stdin, connection]
                    read_sockets,write_sockets, error_sockets = select.select(sockets_list,[],[])
                    for mysocket in read_sockets:
                        if mysocket == connection:
                            message = str(connection.recv(1000), encoding = 'utf-8')
                            if message == 'close':
                                print('Welcome back to BBS')
                                connection.close()
                                break
                            else:
                                print(message)
                        else:
                            input_command = sys.stdin.readline().strip('\n')
                            if input_command == 'leave-chatroom':
                                input_command = input_command + ' ' + '0' + ' ' + self.name 
                                connection.sendall(input_command.encode('utf-8'))
                                break
                            else:
                                now = time.strftime('[%H:%M]', time.localtime())
                                message = self.name + now + ':' + input_command
                                connection.sendall(message.encode('utf-8'))
                except:
                    break


class chatroom_server():
    def __init__(self):
        self.connections = []
        self.flag = False
        self.record_lock = threading.Lock()
    def start(self, address):
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(0.1)
        self.server.bind(address)
        self.server.listen(10)
        threaded_handler = threading.Thread(target = self.connection_handler)
        threaded_handler.start()

    def connection_handler(self):
        while True:
            if self.flag:
                break
            try:
                conn, addr = self.server.accept()
                self.connections.append(conn)
                welcome_message = '******************************\n** Welcome to the chatroom. **\n******************************'
                for i in chatroom_records:
                    welcome_message += ('\n' + i) 
                conn.sendall(welcome_message.encode('utf-8'))
                threaded_client_receiver = threading.Thread(target = self.client_receiver, args = (conn, addr))
                threaded_client_receiver.start()
            except socket.timeout:
                pass
        self.server.close()

    def client_receiver(self, conn, addr):
        while True:
            try:
                message = str(conn.recv(1000), encoding = 'utf-8')
                splitted_message = message.split()
                if message == 'detach':
                    conn.sendall('close'.encode('utf-8'))
                    conn.close()
                    self.reomove_clients(conn)
                    break
                elif splitted_message[0] == 'leave-chatroom':
                    if splitted_message[1] == '0':
                        conn.sendall('close'.encode('utf-8'))
                        conn.close()
                        now = time.strftime('[%H:%M]', time.localtime())
                        sys_message = 'sys' + now + ':' + splitted_message[2] + ' leave us'
                        self.broadcast(sys_message, conn)
                        self.reomove_clients(conn)
                        break
                    if splitted_message[1] == '1':
                        conn.sendall('close'.encode('utf-8'))
                        conn.close()
                        now = time.strftime('[%H:%M]', time.localtime())
                        sys_message = 'sys' + now + ':' + 'the chatroom is close.'
                        self.broadcast(sys_message, conn)
                        self.flag = True
                        time.sleep(0.1)
                        self.broadcast('close', conn)
                        self.reomove_clients(conn)
                        for i in range(len(self.connections)):
                            self.connections[i].close()
                        break
                elif 'sys' in message:
                    if 'join us' in message:
                        now = time.strftime('[%H:%M]', time.localtime())
                        sys_message = message.replace('sys', str('sys' + now + ':'))
                        self.broadcast(sys_message, conn)
                else:
                    self.record_lock.acquire()
                    chatroom_records.append(message)
                    self.record_lock.release()
                    self.broadcast(message, conn)
            except:
                break

    def broadcast(self, message, connection):
        for i in range(len(self.connections)):
            if self.connections[i] != connection:
                self.connections[i].sendall(message.encode('utf-8'))

    def reomove_clients(self, connection):
        for i in range(len(self.connections)):
            if self.connections[i] == connection:
                del self.connections[i]

client = client()
client.connect(ADDR)
while True:
    client.read_command()
    if client.command[0] == 'exit':
        client.tcp.close()
        client.udp.close()
        break
