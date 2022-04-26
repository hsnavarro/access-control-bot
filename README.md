# Access Control Bot
Telegram Bot to manage RFID access control

### Setup Instructions

1 - Creating Telegram Bot

- Go to BotFather
- Insert `/newbot`
- Give the bot a `name`
- Give the bot a `username`
- You should have now succesfully created a Telegram Bot and should receive a `token`

![image](https://user-images.githubusercontent.com/42014408/165408479-cd7f360e-4bba-49da-b370-647a6bc6ad35.png)

2 - Download dependencies (Ubuntu 20.04 LTS)
```
$ sudo apt install python3 python3-pip python3-venv
```

3 - Cloning repository
```
$ git clone <this-repo>
$ cd access-control-bot
```

4 - Python and database setup

- Run virtualenv

```
$ python3 -m venv venv
$ source venv/bin/activate
```

(To deactivate virtualenv just run `deactivate`)

- Install requirements

```
$ pip install -r requirements.txt
```

- Setup database

```
$ bash setup.sh
```

5 - Configure Token

Create a file `.ENV` to store your token

```
$ echo "export TOKEN=<YOUR_TOKEN_HERE>" > .ENV
```

6 - Run the bot
```
$ sudo ./run.sh
```
