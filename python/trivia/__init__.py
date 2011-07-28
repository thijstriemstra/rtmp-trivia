# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game, inspired by IRC's Trivia bots.

@since: 0.1
"""

import logging
import math
from pprint import pformat
from random import randint, sample
from datetime import datetime

from twisted.python import log
from twisted.internet.task import LoopingCall

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
    question_interval = 4
    hint_interval = 12
    current_hint = 0
    startup_time = 0
    total_hints = 3

    def __init__(self, gateway='http://localhost:8000/gateway'):
        self.gateway = gateway
        Application.__init__(self)


    def onConnect(self, client):
        """
        """
        log.msg(60 * "-")
        log.msg("New client connection for '%s' application from client: %s" % (
                self.name, client.id))
        log.msg("Flash Player: %s" % client.agent)
        log.msg("URI: %s" % client.uri)
        log.msg("")

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
        # XXX: print server version
        #log.msg("Server version: %s." % server.getVersion())
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


    def _startupData(self, result):
        """
        Handle startup.
        """
        self.questions = result
        self.to_ask_questions = self.questions[:]

        # XXX: save the array in sharedobject (rtmpy ticket #46)
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

        # XXX: this returns 'NetConnection.Connect.Rejected' with status message
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
            call = self.service.getQuestions()
            call.addCallback(self._startupData)
            call.addErrback(self._startupError)

            return call

        return True


    def _start_game(self):
        """
        Start the game.
        """
        if self.questions and len(self.questions) > 0:
            # store startup time
            self.startup_time = datetime.now()

            log.msg("Started Mr. Trivia with %s questions." % len(self.questions))

            # TODO: load response record data
            #self.responseTimeRecord = result[1].items[0]
            #self.responseTimeRecord.username = result[2].items[0].username

            #log.msg("Current world record by '%s", 3,
            #         self.responseTimeRecord.username + "' with " +
            #         self.responseTimeRecord.responseTime + " seconds.", 38)

            # start with first question
            self._next_question()
            
        else:
            log.err("No questions found! Returned: %s" % (
                str(self.questions)))


    def _next_question(self):
        """
        Picks a random new question and notifies all connected clients.
        """
        # pick a random question
        rnd_question_index = randint(1, len(self.to_ask_questions)) - 1
        current_question = self.to_ask_questions[rnd_question_index]
        #log.msg("current_question: %s" % current_question)

        self.current_hint = 0
        self.winner = False
        self.question_id = current_question.id
        self.question = current_question.question
        self.answer = current_question.answer
        #self.responseTimeRecord.time = 0
        self.scrambled_answers = self._make_hints(self.answer, self.total_hints)

        #log.msg("scrambled_answers: %s" % pformat(self.scrambled_answers))
        log.msg("TRIVIA : QUESTION ID %s - (%s/%s): %s | %s" % (
                self.question_id,
                (len(self.questions) - len(self.to_ask_questions)) + 1,
                len(self.questions),
                self.question,
                self.answer))

        # give a hint every x sec
        self.hint_generator = LoopingCall(self._give_hint)
        self.hint_generator.start(self.hint_interval)

        # send question to clients
        self._send_trivia_crew("newQuestion", current_question)

        # remove question from list
        self.to_ask_questions.pop(rnd_question_index)

        # XXX: save the list to disk (rtmpy ticket #46)
        #self.users_so.setProperty("askedQuestions", to_ask_questions)


    def _give_hint(self):
        """
        Give new hint.
        """
        if self.current_hint < self.total_hints:
            deHint = self.scrambled_answers[self.current_hint]

            self._send_trivia_crew("newHint", deHint, self.current_hint + 1)

            log.msg("TRIVIA: ///// HINT %s:      %s" %( 
                    self.current_hint + 1, deHint))

            self.current_hint += 1

        else:
            # nobody guessed the right answer
            self._show_answer()


    def _show_answer(self):
        """
        """
        log.msg("TRIVIA: ///// ANSWER: %s" % self.answer)

        # check which clients need a hint
        self._send_trivia_crew("showAnswer", self.answer)

        # mr trivia is the winner
        self.winner = True

        # stop giving hints
        self.hint_generator.stop()

        # start new question after few seconds
        self.question_generator = LoopingCall(self._start_new_question)
        self.question_generator.start(self.question_interval)


    def _send_trivia_crew(self, method, object1, object2=None):
        """
        """
        #log.msg('send trivia crew: %s' % method)

        # check which clients need a question
        """
        for i in xrange(len(self.clients)):
            if self.clients[i].trivia:
                log.msg("client '%s' is playin trivia: '%s'" %s (
                        self.clients[i].id,
                        self.clients[i].trivia))

                # give the client a new question
                self.clients[i].call(method, null, object1, object2)
        """


    def _start_new_question(self):
        """
        """
        # stop startup question generator
        self.question_generator.stop()

        # give new question
        self._next_question()


    def _make_hints(self, answer, total_hints, hint_percentage=70,
                    scrambler="*"):
        """
        Create a list of hints for the answer to a question.
        """
        chars = []
        answer_list = []
        total_chars = len(answer)

        if total_chars == 1:
            # single char answers
            return [scrambler, scrambler, answer]
        for char in range(total_chars):
            if answer[char] != " ":
                chars.append(char)

        min_chars = int(round((float(len(chars)) / 100) * float(hint_percentage)))
        selection = sample(chars, min_chars)

        #log.msg('min_chars %s' % min_chars)
        #log.msg('actual chars %s' % len(chars))

        for hint in range(total_hints):
            hint_list = range(total_chars)
            total_hint = ( total_chars / total_hints ) * hint + 1
            for p in range(total_chars):
                hint_list[p] = answer[p]
                if hint_list[p] != " ":
                    hint_list[p]= scrambler
                for s in range(total_hint):
                    try:
                        if selection[s] == p:
                            hint_list[p]= answer[p]
                    except IndexError:
                        pass
            answer_list.append("".join(hint_list))

        return answer_list

