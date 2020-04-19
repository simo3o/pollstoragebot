import pymysql
from Dtos import PollDto, userDto
import json
from config import DB_CONFIG
from typing import List
from typing import Dict


def add_poll_db(new_poll: PollDto) -> int:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')

    try:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`) VALUES (" \
                  "%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer, new_poll.user_id,
                json.dumps(new_poll.answers)))
            result_id = cursor.lastrowid
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ', e)
        result_id = 0
    finally:
        return result_id
        cnx.close()
    pass


def get_poll_by_subject(request: Dict[str, int]) -> List[PollDto]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    agregated_poll = []
    try:
        for subject, quantity in request.items():
            with cnx.cursor() as cursor:
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `ID`  FROM `polls` WHERE " \
                      "`Subject`=%s AND `Impug`=0 ORDER BY RAND()"
                cursor.execute(sql, (subject))
                results = cursor.fetchmany(quantity)
                for result in results:
                    poll_result = PollDto(result[0], result[1], json.loads(result[2]), result[3], result[4], result[5],
                                          result[6])
                    agregated_poll.append(poll_result)

    except cnx.DataError as e:
        print('ERROR: ', e)
        result_poll = PollDto(0, '', '', 0, 0, '', -1)
        agregated_poll.append(result_poll)
    finally:
        cnx.close()
        return agregated_poll


def get_stats():
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')

    pass


def poll_impugnation_db(impug_value: bool, pol_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `polls` SET `Impug`=%s WHERE `ID`=%s"
            if impug_value:
                query_value = 1
            else:
                query_value = 0
            cursor.execute(sql, (query_value, pol_id))
            cnx.commit()
            return True

    except cnx.DataError as e:
        print('ERROR: ' + e)
        return False
    finally:
        cnx.close()
