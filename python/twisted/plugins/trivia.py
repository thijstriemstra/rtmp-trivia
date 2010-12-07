# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

import logging

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application import internet, service

from rtmpy import __version__
from rtmpy.server import ServerFactory, Application


class TriviaApplication(Application):
    """
    Trivia game.
    """

    def acceptConnection(self, client):
        print "Accepted connection for '%s' from client: %s" % (self.name, client.id)


    def onDisconnect(self, client):
        print "Client '%s' has been disconnected from the application" % client.id


    def echo(self, data):
        #print 'echo: %s' % data
        return data


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
