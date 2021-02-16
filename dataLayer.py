import json
import random
from typing import Dict
from typing import List

import pymysql

from Dtos import PollDto
from config import DB_CONFIG


def add_poll_db(new_poll: PollDto) -> int:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result_id = 0
    try:
        with cnx.cursor() as cursor:
            if new_poll.explanation is not None:
                if new_poll.group_test is not None:

                    sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`, `Explanation`, `Group_test`) VALUES (" \
                          "%s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (
                        new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer,
                        new_poll.user_id,
                        json.dumps(new_poll.answers), new_poll.explanation, new_poll.group_test))
                else:
                    sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`, `Explanation`) VALUES (" \
                          "%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (
                        new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer,
                        new_poll.user_id,
                        json.dumps(new_poll.answers), new_poll.explanation))

            else:
                if new_poll.group_test is not None:
                    sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`, `Group_test`) VALUES (" \
                          "%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (
                        new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer,
                        new_poll.user_id,
                        json.dumps(new_poll.answers), new_poll.group_test))
                else:
                    sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`) VALUES (" \
                          "%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (
                        new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer,
                        new_poll.user_id,
                        json.dumps(new_poll.answers)))
            result_id = cursor.lastrowid
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ', e)
        result_id = 0
    finally:
        cnx.close()
        return result_id


def get_poll_by_subject(request: Dict[str, int]) -> List[PollDto]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    agregated_poll = []
    try:
        for subject, quantity in request.items():
            with cnx.cursor() as cursor:
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`  FROM `polls` WHERE " \
                      "`Subject`=%s AND `Impug`=0"
                cursor.execute(sql, (subject))
                results = cursor.fetchall()
                requested_results = random.sample(results, quantity)
                for result in requested_results:
                    try:
                        poll_result = PollDto(chat_id=result[0], question=result[1], answers=json.loads(result[2]),
                                              correct_answer=result[3], user_id=result[4], subject=result[5],
                                              explanation=result[6], poll_id=result[7])
                    except (ValueError, Exception):
                        poll_result = PollDto(0, '', '', 0, 0, '', '', -1)
                    finally:
                        agregated_poll.append(poll_result)

    except cnx.DataError as e:
        print('ERROR: ', e)
        return [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        cnx.close()
        return agregated_poll


def get_poll_by_group(request: Dict[str, int]) -> List[PollDto]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    agregated_poll = []
    try:
        for subject, quantity in request.items():
            with cnx.cursor() as cursor:
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`  FROM `polls` WHERE " \
                      "`Group_test`=%s AND `Impug`=0"
                cursor.execute(sql, (subject))
                results = cursor.fetchall()
                requested_results = random.sample(results, quantity)
                for result in requested_results:
                    try:
                        poll_result = PollDto(chat_id=result[0], question=result[1], answers=json.loads(result[2]),
                                              correct_answer=result[3], user_id=result[4], subject=result[5],
                                              explanation=result[6], poll_id=result[7])
                    except (ValueError, Exception):
                        poll_result = PollDto(0, '', '', 0, 0, '', '', -1)
                    finally:
                        agregated_poll.append(poll_result)

    except cnx.DataError as e:
        print('ERROR: ', e)
        return [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        cnx.close()
        return agregated_poll


def get_pendents_db(first_id: int, last_id: int) -> List[PollDto]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    agregated_poll = []
    first_row = int(first_id) - 1
    last_row = int(last_id) - int(first_id) + 1
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`, `Impug`  FROM `polls` WHERE `Impug`=0 LIMIT " \
                  "%s , %s"
            cursor.execute(sql, (first_row, last_row))
            results = cursor.fetchall()
            for result in results:
                if result[8] == 0:
                    try:
                        poll_result = PollDto(chat_id=result[0], question=result[1], answers=json.loads(result[2]),
                                              correct_answer=result[3], user_id=result[4], subject=result[5],
                                              explanation=result[6], poll_id=result[7])
                    except (ValueError, Exception):
                        poll_result = PollDto(0, '', '', 0, 0, '', '', -1)
                    finally:
                        agregated_poll.append(poll_result)
                else:
                    poll_result = PollDto(0, '', '', 0, 0, '', '', -1)
    except cnx.DataError as e:
        print('ERROR: ' + e)
        agregated_poll = [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        cnx.close()
        return agregated_poll


def get_stats_db(request: Dict[str, int]) -> Dict[str, int]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = []
    try:
        for subject in request:
            try:
                with cnx.cursor() as cursor:
                    sql = "SELECT COUNT(*) FROM `polls` WHERE `Subject`=%s AND `Impug`=0 "
                    cursor.execute(sql, subject)
                    subject_total = cursor.fetchone()
                    result.append((subject, subject_total[0]))
            except (ValueError, Exception):
                result.append(subject, 0)

    except cnx.DataError as e:
        print('ERROR: ', e)
    finally:
        cnx.close()
        return result


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


def get_single_poll_db(poll_id: int) -> PollDto:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    poll_result = PollDto()
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`  FROM `polls` WHERE " \
                  "`ID`=%s "
            cursor.execute(sql, poll_id)
            result = cursor.fetchone()
            poll_result = PollDto(chat_id=result[0], question=result[1], answers=json.loads(result[2]),
                                  correct_answer=result[3], user_id=result[4], subject=result[5], explanation=result[6],
                                  poll_id=result[7])
    #            poll_result = PollDto(result[0], result[1], json.loads(result[2]), result[3], result[4], result[5],
    #                                 result[6], result[7])
    except Exception as e:
        print('ERROR: ' + e)
        poll_result = [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        cnx.close()
        return poll_result


def get_user_list():
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = {}
    try:
        with cnx.cursor() as cursor:
            sql ="SELECT DISTINCT `User_Id` FROM `polls` "
            cursor.execute(sql)
            result = cursor.fetchall()
    except cnx.DataError as e:
        print('ERROR: ' + e)
    finally:
        cnx.close()
        return [int(str(row[0])) for row in result]


def get_user_ranking(user_id: int) -> int:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = {}
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT COUNT(`ID`) FROM `polls` WHERE `User_Id` =%s"
            cursor.execute(sql, user_id)
            result = cursor.fetchone()
    except cnx.DataError as e:
        print('ERROR: ' + e)
    finally:
        cnx.close()
        return int(str(result[0]))


def update_user_total(user_id: int, total: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result= False
    try:
        with cnx.cursor() as cursor:
            #sql = "UPDATE `users_db` SET `Total_polls` = %s, WHERE `User_Id` =%s"
            sql = "INSERT INTO `users_db` (`User_Id`, `Total_polls`, `Impugnator`,`Banned`) VALUES (" \
                          "%s, %s, %s, %s)"
            cursor.execute(sql,  (user_id, total, 0, 0))
            result = True

            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result

def set_impugnator(impugnator: bool, user_id:int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `users_db` set `Impugnator` = {} WHERE `User_Id` ={}".format(impugnator, user_id)
            cursor.execute(sql)
            result = True
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def ban_user(ban: bool, user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `users_db` set `Banned` = {} WHERE `User_Id` ={}".format(ban, user_id)
            cursor.execute(sql)
            result = True
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def check_impugnator(user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Impugnator` FROM `users_db` WHERE `User_Id` ={}".format(user_id)
            cursor.execute(sql)
            result = bool(cursor.fetchone()[0])
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def check_ban(user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Banned` FROM `users_db` WHERE `User_Id` ={}".format(user_id)
            cursor.execute(sql)
            result = bool(cursor.fetchone()[0])
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def check_old(user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Old_member` FROM `users_db` WHERE `User_Id` ={}".format(user_id)
            cursor.execute(sql)
            result = bool(cursor.fetchone()[0])
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def get_users_old_total():
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = {}
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `User_Id`, `Total_polls` FROM `users_db`"
            cursor.execute(sql)
            result = cursor.fetchall()
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return []
    finally:
        cnx.close()
        return result


def strike_user(user_id: int) -> int:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = {}
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `users_db` set `Strikes` = `Strikes` + 1 WHERE `User_Id` ={0}".format(user_id)
            cursor.execute(sql)
            sql = "SELECT `Strikes` FROM `users_db` WHERE `User_Id` ={0}".format(user_id)
            cursor.execute(sql)
            result = cursor.fetchone()
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
    finally:
        cnx.close()
        return result[0]


def restart_user(user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = {}    
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `users_db` set `Strike` = 0 WHERE `User_Id` ={}".format(user_id)
            cursor.execute(sql)
            result = cursor.fetchall()
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
    finally:
        cnx.close()
        return result


def set_old_member(old: bool, user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
            sql = "UPDATE `users_db` set `Old_member` = {} WHERE `User_Id` ={}".format(old, user_id)
            cursor.execute(sql)
            result = True
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def new_member(user_id: int) -> bool:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = False
    try:
        with cnx.cursor() as cursor:
        #    sql = "REPLACE INTO `users_db` SET `User_Id` = {}".format(user_id)
            sql ="INSERT INTO `users_db` (User_Id) VALUES ({}) ON DUPLICATE KEY UPDATE id=id".format(user_id)
            cursor.execute(sql)
            result = True
            cnx.commit()
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result


def get_user_info(user_id: int):
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    result = ""
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM `users_db` WHERE `User_Id`={}".format(user_id)
            cursor.execute(sql)
            user_row = cursor.fetchone()
            result = {"Id":user_row[0], "User_id":user_row[1],"Total_polls":user_row[2], "Strikes":user_row[3], "Impugnator": user_row[4], "Banned": user_row[5], "Old_member":user_row[6]}
    except cnx.DataError as e:
        print('ERROR: ' + e)
        return result
    finally:
        cnx.close()
        return result