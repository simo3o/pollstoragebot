import pymysql
from Dtos import PollDto, userDto
import json
from config import DB_CONFIG


def testdb():
    cnx = pymysql.connect(user=DB_CONFIG.get('user', default=None), passwd=DB_CONFIG.get('password', default=None), host=DB_CONFIG.get('host', default=None), db='poll_bot')

    try:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `users` (`User_Id`, `User_Group`) VALUES (%s, %s)"
            cursor.execute(sql, (1, 'pepe'))
            cnx.commit()
    finally:
        cnx.close()


def add_poll(new_poll):
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'), db='poll_bot')

    try:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`) VALUES (" \
                  "%s, %s, %s, %s, %s, %s) "
            cursor.execute(sql, (
                new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer, new_poll.user_id,
                json.dumps(new_poll.answers)))
            cnx.commit()
    finally:
        cnx.close()
    pass


def get_poll(subjects, quantites):
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'), db='poll_bot')
    agregated_poll = []
    try:
        for subject, quantity in zip(subjects, quantites):
            with cnx.cursor() as cursor:
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject` FROM `polls` WHERE " \
                      "`Subject`=%s "
                cursor.execute(sql, (subject,))
                result = cursor.fetchone()
                poll_result = PollDto(result[0], result[1], result[2], result[3], result[4], result[5])
                agregated_poll.append(poll_result)
    finally:
        cnx.close()
        return agregated_poll


def get_poll_by_subject(request):
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'), db='poll_bot')
    agregated_poll = []
    try:
        for subject, quantity in request.items():
            with cnx.cursor() as cursor:
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject` FROM `polls` WHERE " \
                      "`Subject`=%s  ORDER BY RAND()"
                cursor.execute(sql, (subject))
                results = cursor.fetchmany(quantity)
                for result in results:
                    poll_result = PollDto(result[0], result[1], result[2], result[3], result[4], result[5])
                    agregated_poll.append(poll_result)

    except cnx.DataError as e:
        print('ERROR: ', e)
        agregated_poll = ['ERROR']
    finally:
        cnx.close()
        return agregated_poll


def get_stats():
    cnx = pymysql.connect(user=DB_CONFIG.user, passwd=DB_CONFIG.password, host=DB_CONFIG.host, db='poll_bot')

    pass


def check_user(user):
    cnx = pymysql.connect(user=DB_CONFIG.user, passwd=DB_CONFIG.password, host=DB_CONFIG.host, db='poll_bot')

    pass
