#!/usr/bin/env python
import logging
from telegram.bot import Bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, PollHandler, PollAnswerHandler
from Dtos import PollDto, userDto
from config import TOKEN, GROUP_ID
from dataLayer import add_poll, get_poll, get_stats


# from telegram.ext import PollHandler


def manage_users(user_data):
    if user_data.user_id == 120181656:
        return True
    else:
        return False


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

        new_poll = PollDto(update.message.chat.id, question, poll_answers,
                           update.message.poll.correct_option_id, update.message.from_user.id, subject)
        poll_array = [new_poll, new_poll, new_poll]
        add_poll(new_poll)
        try:
            member_of_group = context.bot.get_chat_member(GROUP_ID, update.message.from_user.id)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Funciona!")
            context.bot.send_poll(GROUP_ID, new_poll.question, type='quiz', is_anonymous=True,
                                  allows_multiple_answers=False, options=new_poll.answers,
                                  correct_option_id=new_poll.correct_answer)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Enquesta Publicada!")
            print('Poll added')

        except:
            print("An exception occurred")
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't belong here")

    else:
        #        context.bot.send_message(chat_id=update.effective_chat.id, text='Poll not added')
        print('Poll not added')


def test(update, context):
    message_parts = update.message.text.split()
    user_request = userDto(update.message.from_user.id, update.message.chat_id)
    if manage_users(user_request):
        """
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You are allowed')
        """
        requested_poll = get_poll(user_request, 1)
        context.bot.send_poll(update.effective_user.id, requested_poll.question, type='quiz', is_anonymous=True,
                              allows_multiple_answers=False, options=requested_poll.answers,
                              correct_option_id=requested_poll.correct_answer)

    subject = message_parts[1]
    test_length = message_parts[2]
    context.bot.send_message(chat_id=update.effective_chat.id, text='subject: ' + subject + ' ; length: ' + test_length)


def stats(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='STATS: ')
    # TODO


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    test_handler = CommandHandler('test', test)
    stats_handler = CommandHandler('stats', stats)
    poll_handler = MessageHandler(Filters.poll, poll_received_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(poll_handler)
    dispatcher.add_handler(stats_handler)

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
