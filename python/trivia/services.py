# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Remoting services used to update the database.

@since: 0.1
"""

from sqlalchemy.sql import select, and_
from sqlalchemy import Table


class TriviaRemotingService(object):
    """
    Trivia AMF service.

    :ivar connection: The SQLAlchemy connection used to query the database.
    """

    def __init__(self, meta=None):
        self.questions = Table('questions', meta, autoload=True)


    def getQuestions(self):
        """
        """
        query = self.questions.select().execute()
        result = []
        for x in query:
            result.append(x.q_id)

        return result
