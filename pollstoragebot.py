#!/usr/bin/env python
import logging
import random
import time
from typing import List, Tuple

from telegram.error import TimedOut, BadRequest
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from Dtos import PollDto
from config import TOKEN, GROUP_ID, PRODUCTION_BUILD, IMPUGNATORS, TEST_GROUP
from dataManager import get_subject_poll, get_simul, poll_impugnation, add_poll, get_stats, get_single_poll, \
    get_pendents, get_group_test

UNAUTHORIZED_JOKES = [
    "No tens permisos per fer res a aquest bot, que t'has pensat...",
    "Perqué tú ho digues!!",
    "No tens permís, pardal",
    "Jo no sempre faig el que tu vols eh!!",
    "Sempre demanant sempre demanant, ara no vull...",
    "Com dius, no t'he entes bé, pots repetir...",
    "Ja estas marejant...",
    "Espera que m'ho pense....., NO",
    "Si vols tindre permís has de dir-me que va ser primer l'ou o la gallina",
    "Jo no vaig a ajudar-te, demana-li al OJT a veure si t'ajuda...",
    "Mira-ho a la wiki, com diu un conegut...",
    "https://www.youtube.com/watch?v=rX7wtNOkuHo",
    "https://media.giphy.com/media/wYyTHMm50f4Dm/giphy.gif",
    "https://media.giphy.com/media/d1E1msx7Yw5Ne1Fe/giphy.gif",
    "https://media.giphy.com/media/ftqLysT45BJMagKFuk/giphy.gif",
    "https://media.giphy.com/media/6Q2KA5ly49368/giphy.gif",
    "https://media.giphy.com/media/1iTIu7WtSfPqMDbW/giphy.gif"
]
POLL_PROBLEM = 'Hi ha hagut un problema la enquesta d"ID: {}'
POLL_PROBLEM_USER = 'Hi ha hagut un problema la enquesta d"ID: {} feta per {}'


def manage_users(context, user_id, group_id) -> bool:
    try:
        member_of_group = context.bot.get_chat_member(group_id, user_id)
    except BadRequest:
        return False
    except TimedOut:
        return False
    else:
        if PRODUCTION_BUILD:
            if member_of_group.status == 'administrator' or member_of_group.status == 'member' or member_of_group.status == 'creator':
                return True
            else:
                return False
        else:
            return True


def randomize_answers(answers: List[str], correct_id: int) -> Tuple[List[str], int]:
    correct_answer = answers[correct_id]
    randomized_answers = answers
    random.shuffle(randomized_answers)
    new_correct_id = randomized_answers.index(correct_answer)
    return randomized_answers, new_correct_id


def send_polls(context, user_id, polls):
    for requested_poll in polls:
        if requested_poll.poll_id == -1:
            context.bot.send_message(chat_id=user_id,
                                     text=POLL_PROBLEM.format(requested_poll.poll_id))
        else:
            try:
                if PRODUCTION_BUILD:
                    # On Production
                    try:
                        member_username = context.bot.get_chat_member(GROUP_ID, requested_poll.user_id)
                    except BadRequest:
                        member_username.user.full_name = 'Error'
                else:
                    # Testing
                    True
            except:
                context.bot.send_message(chat_id=user_id, text=POLL_PROBLEM.format(
                    requested_poll.poll_id))
            else:
                requested_poll.answers, requested_poll.correct_answer = randomize_answers(requested_poll.answers, int(
                    requested_poll.correct_answer))
                # Production
                if PRODUCTION_BUILD:
                    try:
                        context.bot.send_poll(user_id, str(
                            requested_poll.poll_id) + '-' + member_username.user.full_name + ':' + requested_poll.question,
                                              type='quiz', is_anonymous=True,
                                              allows_multiple_answers=False, options=requested_poll.answers,
                                              correct_option_id=requested_poll.correct_answer,
                                              explanation=requested_poll.explanation)
                    except BadRequest:
                        context.bot.send_message(chat_id=user_id,
                                                 text=POLL_PROBLEM_USER.format(
                                                     requested_poll.poll_id, member_username.user.full_name))
                else:
                    # Testing
                    context.bot.send_poll(user_id, str(requested_poll.poll_id) + ':' + requested_poll.question,
                                          type='quiz', is_anonymous=True,
                                          allows_multiple_answers=False, options=requested_poll.answers,
                                          correct_option_id=requested_poll.correct_answer,
                                          explanation=requested_poll.explanation)
            finally:
                # To Avoid Telegram Flood exception on large requests
                time.sleep(0.2)


def start(update, context):
    print('Command' + str(update))
    print('Group_ID: ', str(update.effective_chat.id), 'Group_Name: ', str(update.effective_chat.username))
    # user_allowed = manage_users(context, update.from_user.id, GROUP_ID)
    if manage_users(context, update.message.from_user.id, GROUP_ID):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Comencem a estudiar?")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def poll_received_handler(update, context):
    print('Poll' + str(update))
    if update.message.poll.type == 'quiz' and update.message.chat.type == 'private' and update.message.poll.correct_option_id is not None:
        question = update.message.poll.question
        question_splitted = question.split(':', 1)
        if len(question_splitted) < 2:
            subject = 'none'
            question = update.message.poll.question
            context.bot.send_message(chat_id=update.effective_chat.id, text="Enquesta sense el format correcte")
        else:
            question = question_splitted[1].strip()
            subject = question_splitted[0].upper().strip()
            if subject[-1] in TEST_GROUP:
                group_test = TEST_GROUP.get(subject[-1])
                subject = subject[:-1]
            else:
                group_test = None

            poll_answers = []
            for option in update.message.poll.options:
                poll_answers.append(option.text)

            new_poll = PollDto(chat_id=GROUP_ID, question=question, answers=poll_answers,
                               correct_answer=int(update.message.poll.correct_option_id),
                               user_id=update.message.from_user.id, subject=subject,
                               explanation=update.message.poll.explanation, group_test=group_test)
            poll_id = add_poll(new_poll)
            new_poll.poll_id = poll_id
            if manage_users(context, update.message.from_user.id, GROUP_ID):
                send_polls(context, GROUP_ID, [new_poll])
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Enquesta {} Publicada!".format(new_poll.poll_id))
                print('Poll added')
            else:
                print("An exception occurred")
                context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))

    else:
        if update.message.chat.type == 'private':
            context.bot.send_message(chat_id=update.effective_chat.id, text="L'enquesta no era Concurs")
        print('Poll not added')


def test(update, context):
    # if update.effective_chat.type == 'private':
    message_parts = update.message.text.split()
    if manage_users(context, update.message.from_user.id, GROUP_ID):
        try:
            total_test = int(message_parts[2])
        except (ValueError, TypeError):
            total_test = 0
            context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')

        requested_polls = get_subject_poll(message_parts[1].strip(), total_test)
        if update.effective_chat.type == 'private':
            send_polls(context, update.effective_user.id, requested_polls)
        else:
            if update.message.from_user.id in IMPUGNATORS:
                send_polls(context, GROUP_ID, requested_polls)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=random.choice(UNAUTHORIZED_JOKES))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def recull(update, context):
    # if update.effective_chat.type == 'private':
    message_parts = update.message.text.split()
    if manage_users(context, update.message.from_user.id, GROUP_ID):
        try:
            total_test = int(message_parts[2])
        except (ValueError, TypeError):
            total_test = 0
            context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')
        requested_polls = get_group_test(message_parts[1].strip(), total_test)
        if update.effective_chat.type == 'private':
            if len(requested_polls) < 1:
                context.bot.send_message(chat_id=update.effective_chat.id, text="No hi han enquestes d'aquest recull")
            else:
                send_polls(context, update.effective_user.id, requested_polls)
        else:
            if update.message.from_user.id in IMPUGNATORS:
                if len(requested_polls) < 1:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="No hi han enquestes d'aquest recull")
                else:
                    send_polls(context, GROUP_ID, requested_polls)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=random.choice(UNAUTHORIZED_JOKES))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def stats(update, context):
    if update.effective_chat.type == 'private' or update.message.from_user.id in IMPUGNATORS:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Enquestes per tema: ")
        stats_result = get_stats()
        message = ""
        total_polls = 0
        for subject in stats_result:
            message += "\n " + str(subject[0]) + ": " + str(subject[1]) + ' enquestes'
            total_polls += subject[1]
        message += "\n \n TOTAL: " + str(total_polls) + ' enquestes'
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def xulla(update, context):
    if (manage_users(context, update.message.from_user.id, GROUP_ID)):
        if update.effective_chat.type == 'private' or update.message.from_user.id in IMPUGNATORS:
            message = ''
            for sim, name in TEST_GROUP.items():
                message += "\n {0} : {1} ".format(sim, name)
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def simulacre(update, context):
    # if update.effective_chat.type == 'private':
    message_parts = update.message.text.split()
    if (manage_users(context, update.message.from_user.id, GROUP_ID)):
        try:
            total_sim = int(message_parts[1])
        except (ValueError, TypeError):
            total_sim = 0
            context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')

        requested_polls = get_simul(total_sim)
        if len(requested_polls) > 0:
            if update.effective_chat.type == 'private':
                send_polls(context, update.effective_user.id, requested_polls)
            else:
                if update.message.from_user.id in IMPUGNATORS:
                    send_polls(context, GROUP_ID, requested_polls)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=random.choice(UNAUTHORIZED_JOKES))

        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='No hi ha enquestes de les seleccionades ')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def impgunation(update, context):
    if update.message.from_user.id in IMPUGNATORS:
        message_parts = update.message.text.split()
        if manage_users(context, update.message.from_user.id, GROUP_ID):
            try:
                impugnate_poll = int(message_parts[1])
            except (ValueError, TypeError):
                impugnate_poll = 0
                context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')
            impugnated_poll = poll_impugnation(impugnate_poll, True)
            if impugnated_poll:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Enquesta {} impugnada!'.format(str(impugnate_poll)))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Hi ha hagut algun error')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def restaurator(update, context):
    if update.message.from_user.id in IMPUGNATORS:
        message_parts = update.message.text.split()
        if manage_users(context, update.message.from_user.id, GROUP_ID):
            try:
                restaurate_poll = int(message_parts[1])
            except (ValueError, TypeError):
                restaurate_poll = 0
                context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')
            impugnated_poll = poll_impugnation(restaurate_poll, False)
            if impugnated_poll:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Enquesta restaurada')
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Hi ha hagut algun error')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def enquesta(update, context):
    if update.message.from_user.id in IMPUGNATORS:
        message_parts = update.message.text.split()
        requested_poll = [get_single_poll(int(message_parts[1]))]
        send_polls(context, update.effective_chat.id, requested_poll)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def pendents(update, context):
    message_parts = update.message.text.split()
    if (manage_users(context, update.message.from_user.id, GROUP_ID)):
        if len(message_parts) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Digues un número final')
        else:
            try:
                first_id = int(message_parts[1])
                last_id = int(message_parts[2])
            except (ValueError, TypeError):
                first_id = 0
                last_id = 0
                context.bot.send_message(chat_id=update.effective_chat.id, text='Error de format')

            polls_pendents = get_pendents(first_id, last_id)
            if len(polls_pendents) > 0:
                if update.effective_chat.type == 'private':
                    send_polls(context, update.effective_user.id, polls_pendents)
                else:
                    if update.message.from_user.id in IMPUGNATORS:
                        send_polls(context, GROUP_ID, polls_pendents)
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text=random.choice(UNAUTHORIZED_JOKES))

            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='No hi ha enquestes de les seleccionades ')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(UNAUTHORIZED_JOKES))


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    test_handler = CommandHandler('test', test)
    stats_handler = CommandHandler('stats', stats)
    simulacre_handler = CommandHandler('simulacre', simulacre)
    impugnation_handler = CommandHandler('impugnator', impgunation)
    restaurator_handler = CommandHandler('restaurator', restaurator)
    single_poll_handler = CommandHandler('enquesta', enquesta)
    pendents_handler = CommandHandler('pendents', pendents)
    xulla_handler = CommandHandler('xulla', xulla)
    recull_handler = CommandHandler('recull', recull)

    poll_handler = MessageHandler(Filters.poll, poll_received_handler)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(simulacre_handler)
    dispatcher.add_handler(poll_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(impugnation_handler)
    dispatcher.add_handler(restaurator_handler)
    dispatcher.add_handler(single_poll_handler)
    dispatcher.add_handler(pendents_handler)
    dispatcher.add_handler(xulla_handler)
    dispatcher.add_handler(recull_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
