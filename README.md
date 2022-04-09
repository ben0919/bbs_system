# Board Bulletin System
## Introduction
This is a multi-threaded BBS server implemented by Python socket API, which provides fundamental BBS functions such like create board, create post, comment etc., and an additional chatroom function. Accounts information and bulletin board information are stored in an SQL database. 
## Usage
1. Run the server.
```bash
python3 server.py <port number>
```
2. Then run the client.
```bash
python3 client.py <server IP address> <port number>
```
## Functions
### 1. Register
```bash
register <username> <email> <password>
```
### 2. Login
```bash
login <username> <password>
```
### 3. Logout 
```bash
logout
```
### 4. List User
```bash
list-user
```
### 5. Who Am I
```bash
whoami
```
### 6. Create Board
```bash
create-board <name>
```
### 7. List Board
```bash
list-board
```
### 8. Create Post
```bash
create-post <board-name> --title <title> --content <content>
```
### 9. List Post
```bash
list-post <board-name>
```
### 10. Read
```bash
read <post-S/N>
```
### 11. Delete Post
```bash
delete-post <post-S/N>
```
### 12. Update Post
```bash
update-post <post-S/N> --title/content <new>
```
### 13. Comment
```bash
comment <post-S/N> <comment>
```
### 14. Create Chatroom
```bash
read <post-S/N>
```
### 15. List Chatroom
```bash
read <post-S/N>
```
### 16. Join Chatroom
```bash
read <post-S/N>
```
### 17. Restart Chatroom
```bash
read <post-S/N>
```
### 18. Close Chatroom
```bash
chatroom-closed
```
### 19. Exit
```bash
exit
```
