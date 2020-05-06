from dataLayer import get_poll_by_subject, poll_impugnation_db, add_poll_db, get_stats_db, get_single_poll_db, get_pendents_db
from Dtos import PollDto
from math import floor
from typing import List
import random

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


def get_subject_poll(subject: str, poll_number: int) -> List[PollDto]:
    request = {
        subject: int(poll_number)
    }
    subjects = [subject.upper()]
    quantity = [int(poll_number)]
    polls = get_poll_by_subject(request)
    return polls


def get_simul(poll_number: int) -> List[PollDto]:
    simulacre = dict(SIMUL_SCHEMA)
    for subject, quantity in simulacre.items():
        simulacre[subject] = floor((quantity * poll_number) / 100)
    polls = get_poll_by_subject(simulacre)
    random.shuffle(polls)
    return polls


def get_stats():
    return get_stats_db(SIMUL_SCHEMA)


def poll_impugnation(poll_id: int, value: bool) -> bool:
    result = poll_impugnation_db(value, poll_id)
    return result


def add_poll(poll: PollDto) -> int:
    return add_poll_db(poll)

def get_pendents(first_id: int, last_id:int) -> List[PollDto]:
    return get_pendents_db(first_id, last_id)
    pass

def get_single_poll(poll_id: int) -> PollDto:
    return get_single_poll_db(poll_id)
