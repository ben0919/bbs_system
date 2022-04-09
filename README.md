# Board Bulletin System
## Introduction
This is a multi-threaded BBS server implemented by Python socket API, which provides fundamental BBS functions such like create board, create post, comment etc., and an additional chatroom function. Accounts information is stored in SQL database. 
## Usage
1. Run the server.
```bash
python3 server.py {port number}
```
2. Then Run the client.
```bash
python3 client.py {server IP address} {port number}
```
