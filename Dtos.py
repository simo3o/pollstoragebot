class PollDto:
    def __init__(self, chat_id=0, question='', answers='', correct_answer=0, user_id=0, subject='', poll_id=0):
        self.subject = subject
        self.question = question
        self.chat_id = chat_id
        self.correct_answer = correct_answer
        self.user_id = user_id
        self.answers = answers
        self.poll_id = poll_id


class userDto:
    def __init__(self, user_id, user_group):
        self.user_id = user_id
        self.user_group = user_group
