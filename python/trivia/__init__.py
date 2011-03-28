# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game, inspired by IRC's Trivia bots.

@since: 0.1
"""


import datetime
import logging

from twisted.python import log
from twisted.web.resource import Resource

from rtmpy.server import Application, Client

from pyamf.versions import Version
from pyamf.remoting import RemotingError
from pyamf.remoting.client import RemotingService


# application version
__version__ = Version(0, 1)

# python/actionscript base-alias
namespace = 'com.collab.rtmptrivia'


class TriviaClient(Client):
    """
    Remote methods that are exposed to the client.
    """

    def printData(self, d):
        """
        Data handling function to be added as a callback: handles the
        data by printing the result
        """
        print d


    def invokeOnClient(self, data):
        """
        Invokes some method on the connected clients.
        """
        print 'invokeOnClient: %s' % data
        for i, client in self.application.clients.items():
            #client.call('some_method', data)
            d = client.call('some_method', data, notify=True)
            d.addCallback(self.printData)

        return data


class TriviaApplication(Application):
    """
    Trivia server-side application.
    """

    client = TriviaClient
    service_path = 'trivia'
    appAgent = 'CollabTrivia/%s' % str(__version__)
    questions = []
    newQuestion_Interval = 4000
    hint_interval = 12000
    total_hints = 3
    current_hint = 0
    totalNrQuestions = 26380
    startup_time = 0


    def __init__(self, gateway='http://localhost:8000/gateway'):
        self.gateway = gateway
        Application.__init__(self)


    def onConnect(self, client):
        """
        """
        log.msg( "Accepted connection for '%s' from client: %s" % (self.name, client.id))
        log.msg( "Flash Player: %s" % client.agent )
        log.msg( "URI: %s" % client.uri )

        return True


    def onDisconnect(self, client):
        """
        """
        log.msg("Client '%s' has been disconnected from the application" % client.id)


    def onAppStart(self):
        """
        @note `onAppStart` is not fully implemented in RTMPy, see #138
        """
        #started = datetime.fromtimestamp(server.getStartTime() / 1000)

        log.msg(60 * "=")
        #log.msg("Server version: %s." % server.getVersion())
        #log.msg("Server started on: %s" % started)
        log.msg("Trivia Gateway: %s" % self.gateway)
        log.msg(60 * "=")

        # create Mr. Trivia
        if self.name == "trivia":
            # XXX: no shared object support yet (#46)
            #self.questions = self.getAttribute("askedQuestions")

            # setup logging
            logging.basicConfig(
                level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S%z',
                format='%(asctime)s [%(name)s] %(message)s'
            )

            # create AMF client
            self.remoting = RemotingService(self.gateway, logger=logging,
                                            user_agent=self.appAgent)
            self.service = self.remoting.getService(self.service_path)

            # is it the first time
            if len(self.questions) == 0:
                # load the questions from database
                logging.info("Loading Trivia questions...")

                try:
                    # load startup questions
                    self.questions = self.service.getQuestions()
                except RemotingError, e:
                    pass

                # save the array in sharedobject (#46)
                #self.setAttribute("askedQuestions", self.questions)
            else:
                # start Mr. Trivia
                self._start_game();


    def _start_game(self):
        """
        Start the game.
        """
        log.msg("start game")

        if self.questions and len(self.questions) > 0:
            # store startup time
            self.startup_time = datetime.now()

            log.msg("Started Mr. Trivia with %s questions." % len(self.questions))

            # load response record data
            #self.responseTimeRecord = result[1].items[0]
            #self.responseTimeRecord.username = result[2].items[0].username

            #traceMsg("Current world record by '%s", 3,
            #         self.responseTimeRecord.username + "' with " +
            #         self.responseTimeRecord.responseTime + " seconds.", 38)

            # start with first question
            #self._next_question()
        else:
            log.err("Error loading questions! Returned: %s" % (str(self.questions)))


class TriviaSite(Resource):
    """
    """
    isLeaf = True

    def render_GET(self, request):
        return "<html><body>rtmp-trivia %s</body></html>" % str(__version__)
