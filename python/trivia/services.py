# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Remoting services used to update the database.

@since: 0.1
"""

from sqlalchemy.sql import select, and_
from sqlalchemy import Table


class Question(object):
    def __init__(self, id=None, answer=None, question=None):
        self.answer = answer
        self.question = Question
        self.id = id


class TriviaRemotingService(object):
    """
    Trivia AMF service.
    """

    def __init__(self, meta=None):
        self.questions = Table('questions', meta, autoload=True)


    def getQuestions(self):
        """
        """
        query = self.questions.select().execute()
        result = []
        for obj in query:
            question = Question()
            question.id = obj.q_id
            question.answer = obj.answer
            question.question = obj.question
            result.append(question)

        return result
