# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Remoting services used to update the database.

@since: 0.1
"""

from sqlalchemy import Table


class Question(object):
    """
    Trivia question.
    """
    def __init__(self, id=None, question=None):
        self.question = question
        self.id = id


class TriviaRemotingService(object):
    """
    Trivia AMF service.
    """

    def __init__(self, meta):
        self.questions = Table('questions', meta, autoload=True)


    def getQuestions(self):
        """
        Load all questions with answers.
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
