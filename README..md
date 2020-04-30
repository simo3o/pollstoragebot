# Poll storage Telegram Bot
## Description
Telegram bot that stores the polls from a group in a Mariadb db, and is able to return them to individual users from the group.

## Dependencies
Depends on PyMySQL and Python-telegram-bot pip packages

## Config file
It uses a file named config.py on the root folder with the following content:
````python
TOKEN = 'TOKEN'
GROUP_ID = 'ID' 
DB_CONFIG = {
    'host': 'IP',
    'user': 'User',
    'password': 'PWD',
}
PRODUCTION_BUILD = False
IMPUGNATORS = 'tuple of ID'

````