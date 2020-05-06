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
            if new_poll.explanation is not None:
                sql = "INSERT INTO `polls` (`Subject`, `Question`,`Chat_Id`,`Correct_answer`,`User_Id`,`Answers`, `Explanation`) VALUES (" \
                      "%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (
                    new_poll.subject, new_poll.question, new_poll.chat_id, new_poll.correct_answer, new_poll.user_id,
                    json.dumps(new_poll.answers), new_poll.explanation))
            else:
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
                sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`  FROM `polls` WHERE " \
                      "`Subject`=%s AND `Impug`=0 ORDER BY RAND()"
                cursor.execute(sql, (subject))
                results = cursor.fetchmany(quantity)
                for result in results:
                    try:
                        poll_result = PollDto(result[0], result[1], json.loads(result[2]), result[3], result[4], result[5], result[6], result[7])
                    except:
                        poll_result = PollDto(0, '', '', 0, 0, '', '',  -1)
                    finally:
                        agregated_poll.append(poll_result)

    except cnx.DataError as e:
        print('ERROR: ', e)
        return [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        cnx.close()
        return agregated_poll



def get_pendents_db(first_id:int, last_id:int) -> List[PollDto]:
    cnx = pymysql.connect(user=DB_CONFIG.get('user'), passwd=DB_CONFIG.get('password'), host=DB_CONFIG.get('host'),
                          db='poll_bot')
    agregated_poll = []
    first_row = int(first_id)-1
    last_row = int(last_id)-int(first_id) +1
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`, `Impug`  FROM `polls` LIMIT " \
                  "%s , %s"
            cursor.execute(sql, (first_row, last_row))
            results = cursor.fetchall()
            for result in results:
                if result[8] == 0:
                    try:
                        poll_result = PollDto(result[0], result[1], json.loads(result[2]), result[3], result[4], result[5],
                                              result[6], result[7])
                    except:
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
        for subject, quantity in request.items():
            try:
                with cnx.cursor() as cursor:
                    sql = "SELECT COUNT(*) FROM `polls` WHERE `Subject`=%s AND `Impug`=0 "
                    cursor.execute(sql, subject)
                    subject_total = cursor.fetchone()
                    result.append((subject, subject_total[0]))
            except:
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
    try:
        with cnx.cursor() as cursor:
            sql = "SELECT `Chat_Id`, `Question`, `Answers`, `Correct_Answer`,`User_Id`, `Subject`, `Explanation`, `ID`  FROM `polls` WHERE " \
                  "`ID`=%s "
            cursor.execute(sql, poll_id)
            result = cursor.fetchone()
            poll_result = PollDto(result[0], result[1], json.loads(result[2]), result[3], result[4], result[5],
                                  result[6], result[7])
    except cnx.DataError as e:
        print('ERROR: ' + e)
        poll_result = [PollDto(0, '', '', 0, 0, '', -1)]
    finally:
        return poll_result
        cnx.close()


