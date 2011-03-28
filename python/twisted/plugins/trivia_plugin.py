# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
twistd plugin for Trivia game.
"""


import logging

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application import internet, service
from twisted.web import server, resource, static

from rtmpy import __version__ as rtmpy_version
from rtmpy.server import ServerFactory

from pyamf import version as pyamf_version
from pyamf.remoting.gateway.twisted import TwistedGateway

from trivia import TriviaApplication, __version__, \
                   namespace


class RTMPServer(ServerFactory):
    """
    RTMP server.
    """

    def __init__(self, app):
        ServerFactory.__init__(self, app)


class WebServer(server.Site):
    """
    Webserver serving an AMF gateway and crossdomain.xml file.
    """

    def __init__(self, services, logLevel=logging.ERROR,
                 crossdomain='crossdomain.xml', debug=False):

        logging.basicConfig(
            level=logLevel, datefmt='%Y-%m-%d %H:%M:%S%z',
            format='%(asctime)s [%(name)s] %(message)s'
        )

        # Map ActionScript classes to Python
        #register_class(data.RemoteClass, ns + '.RemoteClass')
        #register_class(data.ExternalizableClass, ns + '.ExternalizableClass')

        gateway = TwistedGateway(services, expose_request=False,
                                 logger=logging, debug=debug)

        root = resource.Resource()
        root.putChild('', gateway)
        root.putChild('crossdomain.xml', static.File(crossdomain,
                      defaultType='application/xml'))

        server.Site.__init__(self, root)


class TriviaService(service.Service):
    """
    Service monitor.
    """

    def startService(self):
        service.Service.startService(self)

        log.msg('')
        log.msg('Trivia %s' % str(__version__))
        log.msg(80 * '=')
        log.msg('')
        log.msg('AMF')
        log.msg(80 * '-')
        log.msg('')
        log.msg('       Gateway:      %s://%s:%s' % (self.options['amf-transport'],
                                                     self.options['amf-host'],
                                                     self.options['amf-port']))
        log.msg('       Service:      %s' % self.options['amf-service'])
        log.msg('       Base alias:   %s' % namespace)
        log.msg('       PyAMF:        %s' % str(pyamf_version))
        log.msg('')
        log.msg('RTMP')
        log.msg(80 * '-')
        log.msg('')
        log.msg('       Server:       %s://%s:%s' % (self.options['rtmp-protocol'],
                                                  self.options['rtmp-host'],
                                                  self.options['rtmp-port']))
        log.msg('       Application:  %s' % self.options['rtmp-app'])
        log.msg('       RTMPy:        %s' % str(rtmpy_version))
        log.msg('')
        log.msg('Trivia service completed startup.')


class Options(usage.Options):
    """
    Command-line options.
    """

    optParameters = [
        ['amf-transport', None, 'http', 'Run the AMF server on HTTP or HTTPS transport.'],
        ['amf-host', None, 'localhost', 'The interface for the AMF gateway to listen on.'],
        ['amf-service', None, 'trivia', 'The remote service name.'],
        ['amf-port', None, 8000, 'The port number for the AMF gateway to listen on.'],
        ['rtmp-port', None, 1935, 'The port number for the RTMP server to listen on.'],
        ['rtmp-protocol', None, 'rtmp', 'Version of the RTMP protocol that the server should use.'],
        ['rtmp-host', None, 'localhost', 'The interface for the RTMP server to listen on.'],
        ['rtmp-app', None, 'trivia', 'The RTMP application name.'],
        ['crossdomain', None, 'crossdomain.xml', 'Path to a crossdomain.xml file.'],
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
            options['rtmp-app']: app
        }

        rtmp_server = RTMPServer( rtmp_apps )
        rtmp_service = internet.TCPServer(int(options['rtmp-port']), rtmp_server,
                                         interface=options['rtmp-host'])
        rtmp_service.setServiceParent(top_service)

        # amf
        amf_port = int(options['amf-port'])
        amf_services = {
            options['amf-service']: app
        }

        amf_server = WebServer(amf_services, logging.INFO,
                               crossdomain=options['crossdomain'])

        web_service = internet.TCPServer(amf_port, amf_server,
                                         interface=options['amf-host'])

        return top_service


# entry point for twistd plugin system
service_maker = TriviaServiceMaker()
