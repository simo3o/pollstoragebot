import random
from math import floor, ceil
from typing import List, Tuple
from Dtos import PollDto
from config import MIN_WEEKLY_POLLS
import dataLayer

SIMUL_SCHEMA = {
    'MECANICA': 7,
    'FOC': 7,
    'ESTRUC': 8,
    'ELEC': 6,
    'RISC': 6,
    'HIDRA': 7,
    'SANITARI': 6,
    'MOTOR': 6,
    'CARTO': 6,
    'QUIMICA': 3,
    'PCI': 6,
    'FISICA': 3,
    'METEO': 5,
    'AGENTS': 3,
    'CIVIL': 2,
    'SPEIS': 1,
    'TERRI': 2,
    'CONSTI': 1,
    'EAC': 2,
    'EBEP': 3,
    'PRL': 3,
    'GUARDIA': 2,
    'INTERIOR': 1,
    'DONA': 1,
    'VLA': 1,
    'HIBRID': 1,
    'FOREST': 1
}


def randomize_answers(answers: List[str], correct_id: int) -> Tuple[List[str], int]:
    correct_answer = answers[correct_id]
    randomized_answers = answers
    random.shuffle(randomized_answers)
    new_correct_id = randomized_answers.index(correct_answer)
    return randomized_answers, new_correct_id


def get_subject_poll(subject: str, poll_number: int) -> List[PollDto]:
    request = {
        subject: int(poll_number)
    }
   # subjects = [subject.upper()]
   # quantity = [int(poll_number)]
    polls = dataLayer.get_poll_by_subject(request)
    return polls

def get_group_test(subject: str, poll_number: int) -> List[PollDto]:
    request = {
        subject: int(poll_number)
    }
    polls = dataLayer.get_poll_by_group(request)
    return polls


def get_simul(poll_number: int) -> List[PollDto]:
    simulacre = dict(SIMUL_SCHEMA)
    for subject, quantity in simulacre.items():
        if ((quantity * poll_number) / 100) < 1:
            simulacre[subject] = 1
        else:
            simulacre[subject] = floor((quantity * poll_number) / 100)
    polls = dataLayer.get_poll_by_subject(simulacre)
    random.shuffle(polls)
    return polls


def get_stats():
    return dataLayer.get_stats_db(SIMUL_SCHEMA)


def poll_impugnation(poll_id: int, value: bool) -> bool:
    result = dataLayer.poll_impugnation_db(value, poll_id)
    return result


def add_poll(poll: PollDto) -> int:
    return dataLayer.add_poll_db(poll)


def get_pendents(first_id: int, last_id: int) -> List[PollDto]:
    return dataLayer.get_pendents_db(first_id, last_id)
    

def get_single_poll(poll_id: int) -> PollDto:
    return dataLayer.get_single_poll_db(poll_id)


def get_user_stats():
    users = dataLayer.get_user_list()
    result = []
    for user in users:
        ranking = dataLayer.get_user_ranking(user)
        result.append((user, ranking))
    return sorted(result, key=lambda x: x[1], reverse=True)


def is_banned(user_id: int):
    return dataLayer.check_ban(user_id)


def is_impugnator(user_id: int):
    return dataLayer.check_impugnator(user_id)


def ban_new_user(ban: bool, user_id: int):
    return dataLayer.ban_user(ban, user_id)


def set_new_impugnator(impugnator: bool, user_id: int):
    return dataLayer.set_impugnator(impugnator, user_id)


def check_users_weekly():
    old_total = dict(list(dataLayer.get_users_old_total()))
    new_totals = dict(get_user_stats())
    weekly = {}
    weekly_fails = {'strikes':{}, 'bans':{}}
    for user, new in new_totals.items():
        weekly[user] = new - old_total[user]
        if weekly[user] < MIN_WEEKLY_POLLS and not is_impugnator(user) and not dataLayer.check_old(user):
            strike_number= dataLayer.strike_user(user)
            weekly_fails['strikes'][user] = 'Strike'
            if strike_number > 1:
                dataLayer.ban_user(True, user)
                weekly_fails['bans'][user] = 'Ban'
        else:
            dataLayer.restart_user(user)
        dataLayer.set_users_old_total(user, new)
    return weekly_fails


def strike_user_weekly(user: int):
    return dataLayer.strike_user(user)


def delete_strikes(user: int):
    return dataLayer.restart_user(user)

def get_user_list():
    return dataLayer.get_users_old_total()

def set_old(old:bool, userid:int):
    return dataLayer.set_old_member(old, userid)

def add_member(userid:int)->bool :
    return dataLayer.new_member(userid)

def check_user(userid:int)->bool :
    user_total = dataLayer.get_user_ranking(userid)
    user_info = dataLayer.get_user_info(userid)
    user_info["Weekly Polls"] = int(user_total) - int(user_info["Total_polls"])
    user_info.pop("Id")
    if user_info["Banned"] == 1:
        user_info["Banned"] = "Sí"
    else:
        user_info["Banned"] = "No"

    if user_info["Impugnator"] == 1:
        user_info["Impugnator"] = "Sí"
    else:
        user_info["Impugnator"] = "No"

    if user_info["Old_member"] == 1:
        user_info["Old_member"] = "Sí"
    else:
        user_info["Old_member"] = "No"    

    return user_info
    

    # return dataLayer.new_member(userid)
