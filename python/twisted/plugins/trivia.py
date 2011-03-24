# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
Trivia game.
"""


import logging
import sys

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application import internet, service

from rtmpy import __version__
from rtmpy.server import ServerFactory, Application, Client


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
    host = 'collab.dev/gateway'
    address = 'http://%s' % (host)
    appAgent = 'CollabTrivia/1.0.0'
    newQuestion_Interval = 4000
    hint_interval = 12000
    total_hints = 3
    current_hint = 0
    totalNrQuestions = 26380
    startup_time = 0


    def onAppStart(self):
        """
        Buggy, see #138
        """
        #server = self.module_context.getServer()
        #started = datetime.fromtimestamp(server.getStartTime() / 1000)

        #log.msg(60 * "=")
        #log.msg("Server version: %s." % server.getVersion())
        #log.msg("Server started on: %s" % started)
        log.msg(60 * "=")

        log.msg("Trivia Gateway: %s" % self.address)


    def onConnect(self, client):
        """
        """
        log.msg( "Accepted connection for '%s' from client: %s" % (self.name, client.id))
        log.msg( "Flash Player: %s" % client.agent )
        log.msg( "URI: %s" % client.uri )

        """
        self.service_path = trivia_namespace
        self.client = TriviaAMFClient(self.address, self.service_path,
                                      logger=self.log, user_agent=self.appAgent)
        self.log.msg(60 * "-")
        """
        return True


    def onDisconnect(self, client):
        """
        """
        print "Client '%s' has been disconnected from the application" % client.id


class RTMPServer(ServerFactory):
    """
    RTMP server.
    """

    def __init__(self, app):
        ServerFactory.__init__(self, app)


class TriviaService(service.Service):
    """
    Service monitor.
    """

    def startService(self):
        service.Service.startService(self)

        log.msg('')
        log.msg('Trivia 1.0')
        log.msg(80 * '=')
        log.msg('')
        log.msg('       Server:       %s://%s:%s' % (self.options['protocol'],
                                                  self.options['host'],
                                                  self.options['port']))
        log.msg('       Application:  %s' % self.options['app'])
        log.msg('       RTMPy:        %s' % '.'.join([str(x) for x in __version__]))
        log.msg('')
        log.msg('Trivia service completed startup.')


class Options(usage.Options):
    """
    Command-line options.
    """

    optParameters = [
        ['port', None, 1935,           'The port number for the RTMP server to listen on.'],
        ['protocol', None, 'rtmp',     'Version of the RTMP protocol that the server should use.'],
        ['host', None, 'localhost',    'The interface for the RTMP server to listen on.'],
        ['app', None, 'trivia',       'The RTMP application name.'],
    ]


class TriviaServiceMaker(object):
    """
    Object which knows how to construct Trivia services.
    """

    implements(service.IServiceMaker, IPlugin)

    tapname = "trivia"
    description = "RTMP trivia game"
    options = Options

    def makeService(self, options):
        top_service = service.MultiService()
        trivia_service = TriviaService()
        trivia_service.options = options
        trivia_service.setServiceParent(top_service)
        
        # rtmp
        app = TriviaApplication()
        rtmp_apps = {
            options['app']: app
        }
        
        rtmp_server = RTMPServer( rtmp_apps )
        rtmp_service = internet.TCPServer(int(options['port']), rtmp_server,
                                         interface=options['host'])
        rtmp_service.setServiceParent(top_service)

        return top_service


# entry point for twistd plugin system
service_maker = TriviaServiceMaker()
