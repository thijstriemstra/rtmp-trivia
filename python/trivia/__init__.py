# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game, inspired by IRC's Trivia bots.

@since: 0.1
"""

import logging
from copy import copy
from random import randint, sample
from datetime import datetime

from twisted.python import log
from twisted.internet.task import LoopingCall

from pyamf.versions import Version

from plasma.client import HTTPRemotingService

from rtmpy.server import Application, Client


# application version
__version__ = Version(0, 1)

# Python/Actionscript base class alias
namespace = 'com.collab.rtmptrivia'


class TriviaClient(Client):
    """
    Remote methods that are exposed to the trivia client.
    """

    def playTrivia(self, join):
        """
        Join or leave the trivia game.
        
        @param join: Boolean indicating whether the user wants to join or
                     leave the game.
        @type join: C{bool}
        """
        self.trivia = join

        #log.msg('playTrivia: %s' % self.trivia)


    def giveAnswer(self, answer, username, highscore, myResponseTime=None,
                   record=False):
        """
        Answer to question or send chat message.

        @param answer: Answer to question or chat message.
        @type answer: C{str}
        @param username: User's name.
        @type username: C{str}
        @param highscore: Highscore for this client.
        @type highscore: C{int}
        @param myResponseTime:
        @type myResponseTime:
        @param record:
        @type record:
        """
        myAnswer = answer.lower() == self.application.answer.lower()

        # XXX: its a time record, but maybe not the first person to give the
        #      right answer
        #if record:
        #    # world record?
        #    if myResponseTime < self.application.responseTimeRecord.responseTime:
        #        recordType = "world"
        #    else:
        #        recordType = "personal"
        #else:
        #    recordType = "none"

        # check if it's an correct answer and if you can still win this round
        if myAnswer == True and self.application.winner == False:
            for i, client in self.application.clients.items():
                if client.trivia == True:
                    # calculate rewarded points for this round
                    points = 250 - ((self.application.current_hint + 1) * 50)

                    # return the user's (correct) answer as normal response
                    client.call("chatMessage", answer, username)

                    # return the user's correct answer including the points
                    # that were rewarded
                    client.call("correctAnswer", answer, username, points +
                                highscore, points, myResponseTime ) # recordType)

        # check if you're still able to win this round and somebody hasn't already
        # given the correct answer
        if self.application.winner == False:
            # check if it's the right answer
            if myAnswer == True:
                log.msg("Winner: %s answered in %s seconds." % (
                        username, myResponseTime))

                # you are the winner
                self.application.winner = True

                # store the response time
                #self.application.responseTimeRecord.time = myResponseTime

                # add points to personal highscore
                highscore += (250 - (self.application.current_hint + 1) * 50)

                # check personal response time record
                if record == True:
                    # update time record in database
                    #call = self.application.service.setResponseTimeRecord(username, myResponseTime)
                    #call.addCallback(self._gotStartupData)
                    #call.addErrback(self._gotStartupError)

                    # world record?
                    #if myResponseTime < self.application.responseTimeRecord.responseTime:
                        # update record holder data
                        #self.application.responseTimeRecord.responseTime = myResponseTime
                        #self.application.responseTimeRecord.username = username
                        #recordType = "world"
                    #else:
                        #recordType = "personal"

                    #log.msg("New %s record by %s with %s seconds." % (
                    #        recordType, username, myResponseTime))

                    # update responseTimeRecord on winning client
                    newClient.call("updateResponseRecord", myResponseTime)

                # update highscore in database
                #call = self.application.service.setHighscore(username, highscore)
                #call.addCallback(self._gotStartupData)
                #call.addErrback(self._gotStartupError)

                # update highscore on winning client
                newClient.call("updateHighscore", highscore)

                # clear old intervals
                #clearInterval(self.application.theHints)

                # start new question after few seconds
                #self.application.startupQuestion = setInterval(startNewQuestion, newQuestion_Interval)

            # the answer is not correct
            else:
                # send clients the incorrect answer
                for i, client in self.application.clients.items():
                    if client.trivia == True:
                        client.call("chatMessage", answer, username)

        # answered too late
        else:
            # but it's the right answer
            if myAnswer == True:
                # the amount of seconds the answer came late
                difference = 0 #String(myResponseTime-self.application.responseTimeRecord.time).substr(0, 5)

                # add difference to message
                answer += "    <b>(+%s sec.)</b>" % difference

                #log.msg("LATE: %s gave the right answer but %s seconds too late." % (
                #        username, difference))

            # send clients the late (in)correct answer
            for i, client in self.application.clients.items():
                if client.trivia == True:
                    client.call("chatMessage", answer, username)


    def invokeOnClient(self, data):
        """
        Invokes some method on the connected clients.
        
        Note: for debugging, to be removed.
        """
        log.msg('invokeOnClient: %s' % data)

        for i, client in self.application.clients.items():
            #client.call('some_method', data)
            d = client.call('some_method', data, notify=True)
            d.addCallback(self.printData)

        return data


class TriviaApplication(Application):
    """
    Server-side Trivia application.
    """

    client = TriviaClient
    appAgent = 'RTMP-Trivia/%s' % str(__version__)

    question_interval = 4 # sec
    hint_interval = 12 # sec
    total_hints = 3

    def __init__(self, gateway='http://localhost:8000/gateway',
                 service_path='trivia'):
        """
        @param gateway: Remoting gateway URL.
        @type gateway: C{str}
        @param service_path: Remoting service path.
        @type service_path: C{str}
        """
        self.gateway = gateway
        self.service_path = service_path
        self.questions = []
        self.to_ask_questions = []
        self.winner = False
        self.current_hint = 0
        self.startup_time = 0

        Application.__init__(self)


    def onConnect(self, client, username):
        """
        Invoked when the client connects to the application for the first time.
        
        @param client: Reference to the connecting RTMP client.
        @type client: L{rtmpy.server.Client}
        @param username: User's name.
        @type username: C{str}
        """
        log.msg("")
        log.msg(60 * "-")
        log.msg("New client connection for '%s' application from client: %s" % (
                self.name, client.id))
        log.msg("Flash Player: %s" % client.agent)
        log.msg("URI: %s" % client.uri)
        log.msg("Username: %s" % username)
        log.msg("")

        accepted_client = False

        # configure Trivia client
        if self.name.startswith("trivia"):
            # check for duplicate username
            if self._checkDuplicateName(username) == False:
                client.username = username
                client.trivia = False
                client.highscore = 0

                # load questions, returns a Deferred
                accepted_client = self._load_questions()

        return accepted_client


    def onDisconnect(self, client):
        """
        Invoked when the client disconnects from the application.
        
        @param client: Reference to the connecting RTMP client.
        @type client: L{rtmpy.server.Client}
        """
        log.msg("Client '%s' has been disconnected from the application." % client.id)


    def onAppStart(self):
        """
        @note: `onAppStart` is not fully implemented in RTMPy, see ticket #138
        """
        # create Mr. Trivia
        if self.name.startswith("trivia"):
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


    def _gotStartupData(self, result):
        """
        Handle loading of startup data.
        
        @param result: Remoting data returned from the server.
        @type result: C{list}
        @return: Boolean indicating whether the startup data was successfully
                 loaded or not.
        @rtype: C{bool}
        """
        self.questions = result

        # XXX: save the array in sharedobject (rtmpy ticket #46)
        #self.setAttribute("askedQuestions", self.questions)

        accepted = False

        if len(self.questions) > 0:
            # start Mr. Trivia
            self._start_game()

            # tell the client it's ok to connect
            accepted = True

        # XXX: include rejection message for client (could not load startup
        #      questions)
        return accepted


    def _gotStartupError(self, failure):
        """
        Handle errors while loading startup data.

        @param failure:
        @type failure: 
        """
        failure.printDetailedTraceback()

        # XXX: this currently returns 'NetConnection.Connect.Rejected' with
        # status message 'Authorization is required'. This should say something
        # like 'Error starting Mr. Trivia` instead (and possibly include the
        # failure). See rtmpy ticket #141.
        return False


    def _load_questions(self):
        """
        Load questions at startup.
        
        @return: Either a Deferred (when loading the questions) or True (when
                 the questions have previously been loaded into the application).
        """
        # is it the first time
        if len(self.questions) == 0:
            # load the questions from database
            log.msg("Loading Trivia questions...")

            # load startup questions
            call = self.service.getQuestions()
            call.addCallback(self._gotStartupData)
            call.addErrback(self._gotStartupError)

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
        if len(self.to_ask_questions) == 0:
            #log.msg("Restarting...")
            self.to_ask_questions = self.questions[:]

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
        new_question = copy(current_question)
        del new_question.answer
        self._send_trivia_crew("newQuestion", new_question)
        del new_question

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

        # check which clients need the answer
        self._send_trivia_crew("showAnswer", self.answer)

        # Mr. Trivia is the winner
        self.winner = True

        # stop giving hints
        self.hint_generator.stop()

        # start new question after few seconds
        self.question_generator = LoopingCall(self._start_new_question)
        self.question_generator.start(self.question_interval)


    def _send_trivia_crew(self, method, object1, object2=None):
        """
        """
        # check which clients need a question
        for client in self.clients:
            """
            if self.clients[i].trivia:
                log.msg("client '%s' is playin trivia: '%s'" %s (
                        self.clients[i].id,
                        self.clients[i].trivia))
            """
            # give the client a new question
            if object2:
                self.clients[client].call(method, object1, object2)
            else:
                self.clients[client].call(method, object1)


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


    def _checkDuplicateName(self, name):
        """
        Check for duplicate username among the application's connected clients.
        
        @return: Boolean indicating whether or not a client has a duplicate
                 username.
        @rtype: C{bool}
        """
        duplicate = False
        log.msg('Checking duplicate username for: %s' % name)

        for i, client in self.clients.items():
            if client.username and client.username == name:
                log.msg("Found duplicate username for '%s'" % client.username)
                duplicate = True
                break

        return duplicate
