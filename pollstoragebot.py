#!/usr/bin/env python
import logging
from telegram.error import TimedOut, BadRequest
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, PollHandler, PollAnswerHandler
from Dtos import PollDto, userDto
from config import TOKEN, GROUP_ID
from dataLayer import add_poll, get_poll, get_stats
from dataPresenter import get_subject_poll, get_simul


# from telegram.ext import PollHandler


def manage_users(context, user_id, group_id):
    try:
        member_of_group = context.bot.get_chat_member(group_id, user_id)
    except BadRequest:
        return False
    except TimedOut:
        return False
    else:
        return True


def start(update, context):
    print('Command' + str(update))
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def echo(update, context):
    print('Echo' + str(update))
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def poll_received_handler(update, context):
    print('Poll' + str(update))
    if update.message.poll.type == 'quiz' and update.message.poll.correct_option_id is not None:
        # subject = 'none'
        question = update.message.poll.question
        question_splitted = question.split(':', 1)
        if len(question_splitted) > 1:
            question = question_splitted[1]
            subject = question_splitted[0].upper()
        else:
            subject = 'none'
            question = update.message.poll.question

        poll_answers = []
        for option in update.message.poll.options:
            poll_answers.append(option.text)

        new_poll = PollDto(GROUP_ID, question, poll_answers,
                           update.message.poll.correct_option_id, update.message.from_user.id, subject)
        poll_array = [new_poll, new_poll, new_poll]
        add_poll(new_poll)
        if manage_users(context, update.message.from_user.id, GROUP_ID):
            context.bot.send_poll(GROUP_ID, new_poll.question, type='quiz', is_anonymous=True,
                                  allows_multiple_answers=False, options=new_poll.answers,
                                  correct_option_id=new_poll.correct_answer)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Enquesta Publicada!")
            print('Poll added')
        else:
            print("An exception occurred")
            context.bot.send_message(chat_id=update.effective_chat.id, text="No eres del grup necessari")

    else:
        #        context.bot.send_message(chat_id=update.effective_chat.id, text='Poll not added')
        print('Poll not added')


def test(update, context):
    message_parts = update.message.text.split()
    user_request = userDto(update.message.from_user.id, GROUP_ID)
    if manage_users(context, update.message.from_user.id, GROUP_ID):
        """
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You are allowed')
        """
        # requested_poll = get_poll(user_request, 1)
        requested_polls = get_subject_poll(message_parts[1], message_parts[2])
        for requested_poll in requested_polls:
            context.bot.send_poll(update.effective_user.id, requested_poll.question, type='quiz', is_anonymous=True,
                                  allows_multiple_answers=False, options=requested_poll.answers,
                                  correct_option_id=requested_poll.correct_answer)

    # subject = message_parts[1]
    # test_length = message_parts[2]
    # context.bot.send_message(chat_id=update.effective_chat.id, text='subject: ' + subject + ' ; length: ' + test_length)


def stats(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='STATS: ')
    # TODO


def simulacre(update, context):
    message_parts = update.message.text.split()
    if manage_users(context, update.message.from_user.id, GROUP_ID):
        requested_polls = get_simul(message_parts[1], message_parts[2])
        for requested_poll in requested_polls:
            context.bot.send_poll(update.effective_user.id, requested_poll.question, type='quiz', is_anonymous=True,
                                  allows_multiple_answers=False, options=requested_poll.answers,
                                  correct_option_id=requested_poll.correct_answer)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    test_handler = CommandHandler('test', test)
    stats_handler = CommandHandler('stats', stats)
    simulacre_handler = CommandHandler('simulacre', simulacre)
    poll_handler = MessageHandler(Filters.poll, poll_received_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(simulacre_handler)
    dispatcher.add_handler(poll_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

    """
            for inner_poll in poll_array:
                context.bot.send_poll(update.effective_user.id, new_poll.question, type='quiz', is_anonymous=True,
                                      allows_multiple_answers=False, options=inner_poll.answers,
                                      correct_option_id=inner_poll.correct_answer)

            context.bot.send_message(chat_id=update.effective_chat.id, text='Poll added: ' + str(new_poll.question) + ' ; subject: ' + str(new_poll.subject))
            # context.bot.send_poll(update.effective_user.id, new_poll.question, type='quiz', is_anonymous=False,
            # allows_multiple_answers=False, options= new_poll.answers, correct_option_id = new_poll.correct_answer) Save
            # some info about the poll the bot_data for later use in receive_poll_answer
            print(new_poll.subject)
    """
