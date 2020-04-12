from dataLayer import get_poll_by_subject


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
}

def get_subject_poll(subject, poll_number):
    request = {
        subject: int(poll_number)
    }
    subjects = [subject.upper()]
    quantity = [int(poll_number)]
    polls = get_poll_by_subject(request)
    return polls

def get_simul(poll_number):
    simulacre = dict(SIMUL_SCHEMA)
    for subject, quantity in simulacre.items():
        simulacre[subject] = (quantity*int(poll_number))/90
    polls = get_poll_by_subject(simulacre)
    return polls


def check_user(user_name):
    pass


def get_stats():
    pass


