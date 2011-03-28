# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Remoting services.

@since: 0.1
"""

from sqlalchemy.sql import select, and_


class TriviaRemotingService(object):
    """
    Trivia AMF service.

    :ivar connection: The SQLAlchemy engine used to query the database.
    :type connection: `Engine`
    """

    def __init__(self, conn=None):
        self.connection = conn
