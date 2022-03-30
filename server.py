import socket
import sys
import sqlite3 as sql
import threading
import random
from dataclasses import dataclass
import datetime

HOST = '127.0.0.1'
PORT = int(sys.argv[1])
ADDR = (HOST, PORT)


class server():
    def __init__(self, address):
        self.sql_connect()
        self.start(address)
        self.random_history = []
        self.boards = []
        self.board_id = 1
        self.posts = []
        self.post_id = 1
        self.chatrooms = []
        self.board_lock = threading.Lock()
        self.post_lock = threading.Lock()
        self.comment_lock = threading.Lock()
    def sql_connect(self):
        self.db_conn = sql.connect('bbs_users.db', check_same_thread = False)
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('DROP TABLE IF EXISTS USERS;')
        self.db_conn.commit()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS USERS(
                UID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                Email TEXT NOT NULL,
                Password TEXT NOT NULL);''')
        self.db_conn.commit()
        self.cursor.execute('DROP TABLE IF EXISTS LOGIN_STATUS;')
        self.db_conn.commit()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS LOGIN_STATUS(
                LOGIN_ID INTEGER NOT NULL,
                Username TEXT NOT NULL);''')
        self.db_conn.commit()

    def start(self, address):
        self.address = address
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.bind(address)
        self.tcp.listen(10)
        self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(address)

    def tcp_connect_handler(self):
        while True:
            conn, addr = self.tcp.accept()
            print('New connection.')
            welcome_message = '''********************************\n** Welcome to the BBS server. **\n********************************'''
            conn.sendall(welcome_message.encode('utf-8'))
            threaded_tcp_receive = threading.Thread(target = self.tcp_receive, args = (conn, addr))
            threaded_tcp_receive.start()

    def tcp_receive(self, conn, addr):
        while True:
            command = str(conn.recv(1000), encoding = 'utf-8')
            splitted_command = command.split()
            if splitted_command[0] == 'login':
                message = self.login(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'logout':
                message = self.logout(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'list-user':
                message = self.list_user(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'create-board':
                message = self.create_board(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'create-post':
                if '--title' not in command or '--content' not in command:
                    message = 'Usage: create-post <board-name> --title <title> --content <content>'
                    conn.sendall(message.encode('utf-8'))
                    continue
                temp_command = command.split(' --title ')
                temp_command[0] = temp_command[0].split()
                temp_command[1] = temp_command[1].split(' --content ')
                temp_command[1][1] = temp_command[1][1].split('¬') ##因為post的content有可能有空格 所以隨邊挑一個特殊符號來用
                splitted_command = []
                splitted_command.append(temp_command[0][0])
                splitted_command.append(temp_command[0][1])
                splitted_command.append(temp_command[1][0])
                splitted_command.append(temp_command[1][1][0])
                splitted_command.append(temp_command[1][1][1])
                message = self.create_post(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'list-board':
                message = self.list_board(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'list-post':
                message = self.list_post(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'read':
                message = self.read(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'delete-post':
                message = self.delete_post(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'update-post':
                if ('--title' not in command and '--content' not in command) or ('--title' in command and '--content' in command):
                    message = 'Usage: update-post <post-S/N> --title/content <new>'
                    conn.sendall(message.encode('utf-8'))
                    continue
                temp_command = []
                temp = ''
                if ' --title '  in command:
                    temp_command = command.split(' --title ')
                    temp = 'title'
                if ' --content ' in command:
                    temp_command = command.split(' --content ')
                    temp = 'content'
                temp_command[0] = temp_command[0].split()
                temp_command[1] = temp_command[1].split('¬')
                splitted_command = []
                splitted_command.append(temp_command[0][0])
                splitted_command.append(temp_command[0][1])
                splitted_command.append(temp_command[1][0])
                splitted_command.append(temp)
                splitted_command.append(temp_command[1][1])
                message = self.update_post(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'comment':
                temp_command = command.split('¬')
                num = ''
                flag = False
                for i in range(len(temp_command[0])):
                    if temp_command[0][i].isdigit():
                        num += temp_command[0][i]
                        flag = True
                    if flag and not temp_command[0][i].isdigit():
                        break
                temp_command[0] = temp_command[0].split(str(' '+ num + ' '))
                splitted_command = []
                splitted_command.append(temp_command[0][0])
                splitted_command.append(num)
                splitted_command.append(temp_command[0][1])
                splitted_command.append(temp_command[1])
                message = self.comment(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'create-chatroom':
                message = self.create_chatroom(splitted_command, addr[0])
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'join-chatroom':
                message = self.join_chatroom(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'restart-chatroom':
                message = self.restart_chatroom(splitted_command)
                conn.sendall(message.encode('utf-8'))
            if splitted_command[0] == 'chatroom-closed':
                self.chatroom_closed(splitted_command)
            if splitted_command[0] == 'exit':
                conn.close()
                break
                
            

    def udp_receive(self):
        while True:
            command, addr = self.udp.recvfrom(1000)
            command = command.decode()
            splitted_command = command.split()
            if splitted_command[0] == 'register':
                message = self.register(splitted_command)
                self.udp.sendto(message.encode(), addr)
            if splitted_command[0] == 'whoami':
                message = self.whoami(splitted_command)
                self.udp.sendto(message.encode(), addr)
            if splitted_command[0] == 'list-chatroom':
                message = self.list_chatroom(splitted_command)
                self.udp.sendto(message.encode(), addr)
                

    def register(self, command):
        if len(command) != 4:
            return 'Usage: register <username> <email> <password>'
        self.cursor.execute(''' SELECT EXISTS(SELECT 1 FROM USERS WHERE Username = ?);''', (command[1], ))
        if self.cursor.fetchall()[0][0] == 0:
            self.cursor.execute(
                '''INSERT INTO USERS (Username, Email, Password) 
                VALUES (?, ?, ?);''', (command[1], command[2], command[3]))
            self.db_conn.commit()
            return 'Register successfully.'
        else:
            return 'Username is already used.'

    def login(self, command):
        if len(command) != 4:
            return 'Usage: login <username> <password>'
        if(command[-1] != '0'):
            return 'Please logout first.'
        self.cursor.execute('''SELECT EXISTS (SELECT 1 FROM USERS WHERE Username = ?);''', (command[1], ))
        if self.cursor.fetchall()[0][0] == 1:
            self.cursor.execute(''' SELECT Password FROM USERS WHERE Username = ?''',  (command[1], ))
            if self.cursor.fetchall()[0][0] == command[2]:
                login_id = random.randint(1,100)
                while True:
                    if login_id not in self.random_history:
                        self.random_history.append(login_id)
                        break
                    else:
                        login_id = random.randint(1,100)
                self.cursor.execute('''INSERT INTO LOGIN_STATUS (LOGIN_ID, Username) VALUES (?, ?);''', (login_id, command[1]))
                self.db_conn.commit()
                return str(login_id) + ' Welcome ' + command[1] + '.'
            else:
                return 'Login failed.'
        else:
            return 'Login failed.'
            
    def logout(self, command):
        if len(command) != 3:
            return 'Usage: logout'
        if command[-2] == '0':
            return 'Please login first.'
        if command[-1] != '0':
            return 'Please do "attach" and "leave-chatroom" first.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-2], ))
        user = self.cursor.fetchall()[0][0]
        self.cursor.execute('''DELETE FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-2], ))
        self.db_conn.commit()
        self.random_history.remove(int(command[1]))
        return 'Bye, ' + user + '.'

    def whoami(self, command):
        if len(command) != 2:
            return 'Usage: whoami'
        if command[-1] == '0':
            return 'Please login first.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        return user

    def list_user(self, command):
        if len(command) != 1:
            return 'Usage: list-user'
        self.cursor.execute('''SELECT Username, Email FROM USERS''')
        users = self.cursor.fetchall()
        if users == []:
           return ' '
        message = '%-10s%-20s\n' % ('Name', 'Email')
        for user in users:
                message += '%-10s%-20s\n' % (user[0], user[1])
        return message

    def create_board(self, command):
        if len(command) != 3:
            return 'Usage: create-board <name>'
        if command[-1] == '0':
            return 'Please login first.'
        for temp in self.boards:
            if(temp.name == command[1]):
                return 'Board already exists.'
        self.board_lock.acquire()
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        temp_board = board(self.board_id, command[1], user)
        self.board_id += 1
        self.boards.append(temp_board)
        self.board_lock.release()
        return 'Create board successfully.'

    def create_post(self, command):
        if len(command) != 5:
            return 'Usage: create-post <board-name> --title <title> --content <content>'
        if command[-1] == '0':
            return 'Please login first.'
        self.board_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.boards)):
            if(self.boards[i].name == command[1]):
                flag = True
                break
        self.board_lock.release()
        if not flag:
            return 'Board does not exist.'
        self.post_lock.acquire()
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        dt = datetime.datetime.now().strftime('%m/%d')
        temp_post = post(self.boards[i].board_id, command[2], command[3].replace('<br>', '\n'), self.post_id, user, dt, [])
        self.posts.append(temp_post)
        self.post_id += 1
        self.post_lock.release()
        return 'Create post successfully.'

    def list_board(self, command):
        if len(command) != 1:
            return 'Usage: list-board'
        self.board_lock.acquire()
        message = ('%-10s%-15s%-15s\n' % ('Index','Name','Moderator'))
        for temp_board in self.boards:
            temp = ('%-10s%-15s%-15s\n' % (temp_board.board_id, temp_board.name, temp_board.mod))
            message += temp
        self.board_lock.release()
        return message

    def list_post(self, command):
        if len(command) != 2:
            return 'Usage: list-post <board-name>'
        self.board_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.boards)):
            if(self.boards[i].name == command[1]):
                flag = True
                break
        self.board_lock.release()
        if not flag:
            return 'Board does not exist.'
        self.post_lock.acquire()
        message = '%-5s%-20s%-10s%-10s\n' % ('S/N', 'Title', 'Author', 'Date')
        for temp_post in self.posts:
            if temp_post.board_id == self.boards[i].board_id:
                temp = '%-5s%-20s%-10s%-10s\n' % (temp_post.post_id, temp_post.title, temp_post.author, temp_post.date)
                message += temp
        self.post_lock.release()
        return message
        
    def read(self, command):
        if len(command) != 2:
            return 'Usage: read <post-S/N>'
        self.post_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.posts)):
            if(self.posts[i].post_id == int(command[1])):
                flag = True
                break
        self.post_lock.release()
        if not flag:
            return 'Post does not exist.'
        self.post_lock.acquire()
        self.comment_lock.acquire()
        message = ('Author: %s\nTitle: %s\nDate: %s\n--\n%s\n--\n' % (self.posts[i].author, self.posts[i].title, self.posts[i].date, self.posts[i].content))
        for temp_comment in self.posts[i].comments:
            message += ('%s: %s\n' % (temp_comment.author, temp_comment.content))
        self.post_lock.release()
        self.comment_lock.release()
        return message

    def delete_post(self, command):
        if len(command) != 3:
            return 'Usage: delete-post <post-S/N>'
        if command[-1] == '0':
            return 'Please login first.'
        self.post_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.posts)):
            if(self.posts[i].post_id == int(command[1])):
                flag = True
                break
        self.post_lock.release()
        if not flag:
            return 'Post does not exist.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        if self.posts[i].author != user:
            return 'Not the post owner.'
        del self.posts[i]
        return 'Delete successfully.'        

    def update_post(self, command):
        if len(command) != 5:
            return 'Usage: update-post <post-S/N> --title/content <new>'
        if command[-1] == '0':
            return 'Please login first.'
        self.post_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.posts)):
            if(self.posts[i].post_id == int(command[1])):
                flag = True
                break
        self.post_lock.release()
        if not flag:
            return 'Post does not exist.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        if self.posts[i].author != user:
            return 'Not the post owner.'
        self.post_lock.acquire()
        if command[3] == 'title':
            self.posts[i].title = command[2]
        if command[3] == 'content':
            self.posts[i].content = command[2].replace('<br>', '\n')
        self.post_lock.release()
        return 'Update successfully.'
        
    def comment(self, command):
        if len(command) != 4:
            return 'Usage: comment <post-S/N> <comment>'
        if command[-1] == '0':
            return 'Please login first.'
        self.post_lock.acquire()
        flag = False
        i = 0
        for i in range(len(self.posts)):
            if(self.posts[i].post_id == int(command[1])):
                flag = True
                break
        self.post_lock.release()
        if not flag:
            return 'Post does not exist.'
        self.post_lock.acquire()
        self.comment_lock.acquire()
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        temp_comment = comment(user, command[2])
        self.posts[i].comments.append(temp_comment)
        self.post_lock.release()
        self.comment_lock.release()
        return 'Comment successfully.'

    def create_chatroom(self, command, address):
        if len(command) != 4:
            return 'Usage: create-chatroom <port>'
        if command[-2] == '0':
            return 'Please login first.'
        if command[-1] == '1':
            return 'User has already created the chatroom.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-2], ))
        user = self.cursor.fetchall()[0][0]
        temp_chatroom = chatroom(user, address, command[1], 'open')
        self.chatrooms.append(temp_chatroom)
        return 'start to create chatroom...' + ' ' + temp_chatroom.host + ' ' + temp_chatroom.port

    def list_chatroom(self, command):
        if len(command) != 2:
            return 'Usage: list-chatroom'
        if command[-1] == '0':
            return 'Please login first.'
        message = ('%-15s%-10s\n' % ('Chatroom_name','Status'))
        for temp_chatroom in self.chatrooms:
            temp = ('%-15s%-10s\n' % (temp_chatroom.name, temp_chatroom.status))
            message += temp
        return message

    def join_chatroom(self, command):
        if len(command) != 3:
            return 'Usage: join-chatroom <chatroom_name>'
        if command[-1] == '0':
            return 'Please login first.'
        flag = False
        i = 0
        for i in range(len(self.chatrooms)):
            if(self.chatrooms[i].name == command[1]):
                if(self.chatrooms[i].status == 'open'):
                    flag = True
                    break
        if not flag:
            return 'The chatroom does not exist or the chatroom is close.'
        return 'Action: connection to chatroom server.' + ' ' + self.chatrooms[i].host + ' ' + self.chatrooms[i].port
    
    def restart_chatroom(self, command):
        if len(command) != 3:
            return 'Usage: restart-chatroom'
        if command[-2] == '0':
            return 'Please login first.'
        if command[-1] == '0':
            return 'Please create-chatroom first.'
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-2], ))
        user = self.cursor.fetchall()[0][0]
        i = 0
        for i in range(len(self.chatrooms)):
            if(self.chatrooms[i].name == user):
                if(self.chatrooms[i].status == 'open'):
                    return 'Your chatroom is still running.'
        self.chatrooms[i].status = 'open'
        return 'start to create chatroom...' + ' ' + self.chatrooms[i].host + ' ' + self.chatrooms[i].port

    def chatroom_closed(self, command):
        self.cursor.execute('''SELECT Username FROM LOGIN_STATUS WHERE LOGIN_ID = ?;''', (command[-1], ))
        user = self.cursor.fetchall()[0][0]
        for i in range(len(self.chatrooms)):
            if(self.chatrooms[i].name == user):
                self.chatrooms[i].status = 'close'
                break
@dataclass
class comment():
    author: str
    content: str
    
@dataclass
class post():
    board_id: str
    title: str
    content: str
    post_id: int
    author: str
    date: str
    comments: comment

@dataclass
class board():
    board_id: int
    name: str
    mod: str
    
@dataclass
class chatroom():
    name: str
    host: str
    port: int
    status: str


server = server(ADDR)
threaded_tcp = threading.Thread(target = server.tcp_connect_handler)
threaded_tcp.start()
threaded_udp = threading.Thread(target = server.udp_receive)
threaded_udp.start()



        