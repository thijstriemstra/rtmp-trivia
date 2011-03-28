# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game.
"""


import datetime

from twisted.python import log

from rtmpy.server import Application, Client

from pyamf.versions import Version
from pyamf.remoting.client import RemotingService

from sqlalchemy.sql import select, and_



__version__ = Version(0, 1)


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


    def getQuestions(self):
        """
        Get all Trivia questions.
        """
        return ['todo']


class TriviaApplication(Application):
    """
    Trivia server-side application.
    """

    client = TriviaClient
    host = 'collab.dev/gateway'
    address = 'http://%s' % (host)
    appAgent = 'CollabTrivia/1.0.0'
    questions = None
    newQuestion_Interval = 4000
    hint_interval = 12000
    total_hints = 3
    current_hint = 0
    totalNrQuestions = 26380
    startup_time = 0


    def onAppStart(self):
        """
        @note `onAppStart` is not fully implemented in RTMPy, see #138
        """
        #server = self.module_context.getServer()
        #started = datetime.fromtimestamp(server.getStartTime() / 1000)

        log.msg(60 * "=")
        #log.msg("Server version: %s." % server.getVersion())
        #log.msg("Server started on: %s" % started)
        log.msg("Trivia Gateway: %s" % self.address)
        log.msg(60 * "=")
        
        # create Mr. Trivia
        if self.name == "trivia":
            # XXX: no shared object support yet (#46)
            #self.questions = self.getAttribute("askedQuestions")

            # is it the first time
            if self.questions == None:
                # load the questions from database
                print("TRIVIA : Loading Trivia questions...")

                # create AMF client
                #self.service_path = trivia_namespace
                #self.client = RemotingService(self.address, self.service_path,
                #    logger=log, user_agent=self.appAgent)

                # invoke a method on the server using an AMF client.
                #self.questions = self.client.getQuestions()

                # save the array in sharedobject (#46)
                #self.setAttribute("askedQuestions", self.questions)
            else:
                self.questions = self.questions.getValue()

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
            #application.responseTimeRecord = result[1].items[0]
            #application.responseTimeRecord.username = result[2].items[0].username

            #traceMsg("Current world record by '%s", 3, application.responseTimeRecord.username + "' with " + application.responseTimeRecord.responseTime + " seconds.", 38)

            # start with first question
            self._next_question()
        else:
            log.err("Error loading questions! Returned: %s" % (str(self.questions)))


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
        print "Client '%s' has been disconnected from the application" % client.id
