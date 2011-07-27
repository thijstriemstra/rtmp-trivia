# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game, inspired by IRC's Trivia bots.

@since: 0.1
"""


from datetime import datetime
import logging

from twisted.python import log

from rtmpy.server import Application, Client

from pyamf.versions import Version

from plasma.client import HTTPRemotingService


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
        log.msg(d)


    def invokeOnClient(self, data):
        """
        Invokes some method on the connected clients.
        """
        log.msg('invokeOnClient: %s' % data)
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
    appAgent = 'RTMP-Trivia/%s' % str(__version__)
    questions = []
    newQuestion_Interval = 4000
    hint_interval = 12000
    total_hints = 3
    current_hint = 0
    startup_time = 0

    def __init__(self, gateway='http://localhost:8000/gateway'):
        self.gateway = gateway
        Application.__init__(self)


    def onConnect(self, client):
        """
        """
        log.msg( "New client connection for '%s' from client: %s" % (self.name, client.id))
        log.msg( "Flash Player: %s" % client.agent )
        log.msg( "URI: %s" % client.uri )

        result = self._load_questions()

        return result


    def onDisconnect(self, client):
        """
        """
        log.msg("Client '%s' has been disconnected from the application." % client.id)


    def onAppStart(self):
        """
        @note: `onAppStart` is not fully implemented in RTMPy, see ticket #138
        """
        log.msg(60 * "=")
        #log.msg("Server version: %s." % server.getVersion())
        #log.msg("Server started on: %s" % started)
        log.msg("Trivia Gateway: %s" % self.gateway)
        log.msg(60 * "=")

        # create Mr. Trivia
        if self.name == "trivia":
            # XXX: no shared object support yet (rtmpy ticket #46)
            #self.questions = self.getAttribute("askedQuestions")

            # XXX: setup dedicated logger for remoting client
            logging.basicConfig(
                level=logging.ERROR, datefmt='%Y-%m-%d %H:%M:%S:%z',
                format='%(asctime)s %(message)s'
            )

            # create async AMF client
            self.remoting = HTTPRemotingService(self.gateway, logger=logging,
                                                user_agent=self.appAgent)
            self.service = self.remoting.getService(self.service_path)


    def _startupData(self, d):
        """
        Handle startup.
        """
        self.questions = d

        log.msg('Total questions: %s' % len(self.questions))

        # save the array in sharedobject (rtmpy ticket #46)
        #self.setAttribute("askedQuestions", self.questions)
        
        # start Mr. Trivia
        self._start_game()

        # Tell the client it's ok to connect
        return True


    def _startupError(self, failure):
        """
        Handle errors while loading startup data.
        """
        failure.printDetailedTraceback()
        
        # this returns 'NetConnection.Connect.Rejected' with status message
        # 'Authorization is required'. This should say something like
        # 'Error starting Mr. Trivia` instead (and possibly including the
        # failure). See rtmpy ticket #141.
        return False


    def _load_questions(self):
        """
        Load questions at startup.
        """
        # is it the first time
        if len(self.questions) == 0:
            # load the questions from database
            log.msg("Loading Trivia questions...")

            # load startup questions
            d = self.service.getQuestions()
            d.addCallback(self._startupData)
            d.addErrback(self._startupError)

            return d

        return True


    def _start_game(self):
        """
        Start the game.
        """
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
            log.err("No questions found! Returned: %s" % (str(self.questions)))


    def _next_question(self):
        """
        """
        to_ask_questions = self.questions[:]

        # pick a random question
        rnd_question_index = randint(1, len(to_ask_questions))-1

        # get the question index
        current_question_index = to_ask_questions[rnd_question_index]

        # get the question object
        question_obj = to_ask_questions[current_question_index]

        self.log.info("question_obj: %s" % str(question_obj))

        self.current_hint = 0
        self.winner = False
        self.question_id = question_obj.q_id
        self.question = question_obj.question
        self.answer = question_obj.answer
        #self.responseTimeRecord.time = 0

        # create hints for the answer
        scrambled_answers = self._make_hints(self.answer, self.total_hints, 70)

        self.log.info("scrambled_answers: %s" % str(scrambled_answers))

        # print current question
        #self.log.debug("TRIVIA : QUESTION: " + self.question_id + "   (" + ((len(application.questionIDs)-len(to_ask_questions)+1) + "/" + len(application.questionIDs) + ") : " + question + " | " + application.answer)

        # give a hint every x sec
        #self.the_hints = setInterval(self._give_hint, self.hint_interval)

        # send question to clients
        #self._send_trivia_crew("newQuestion", question_obj)

        # remove question from array
        #to_ask_questions.splice(rnd_question_index, 1)

        # save the array to disk
        #application.users_so.setProperty("askedQuestions", to_ask_questions)
