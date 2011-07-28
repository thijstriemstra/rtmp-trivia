# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
twistd plugin for Trivia game.

@since: 0.1
"""


import logging

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application import internet, service
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.static import File

from rtmpy import __version__ as rtmpy_version
from rtmpy.server import ServerFactory

from pyamf import version as pyamf_version, register_class
from pyamf.remoting.gateway.twisted import TwistedGateway

from plasma.version import version as plasma_version

from sqlalchemy import __version__ as sqlalchemy_version
from sqlalchemy import create_engine, MetaData

from trivia.site import TriviaSite
from trivia.services import TriviaRemotingService, Question
from trivia import TriviaApplication, __version__, namespace



class RTMPServer(ServerFactory):
    """
    RTMP server.
    """

    def __init__(self, app):
        ServerFactory.__init__(self, app)


class WebServer(Site):
    """
    Webserver serving an AMF gateway and crossdomain.xml file.
    """

    def __init__(self, site, services, logLevel=logging.ERROR,
                 gateway_path='gateway', crossdomain='crossdomain.xml',
                 debug=False):
        """
        @type site: L{trivia.site.TriviaSite}
        @type services: dict
        """

        # Map ActionScript classes to Python
        register_class(Question, namespace + '.Question')

        # remoting gateway
        gateway = TwistedGateway(services, expose_request=False,
                                 logger=logging, debug=debug)

        root = Resource()
        root.putChild('', site)
        root.putChild(gateway_path, gateway)
        root.putChild('crossdomain.xml', File(crossdomain,
                      defaultType='application/xml'))

        Site.__init__(self, root)


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
        log.msg('       Plasma:       %s' % plasma_version)
        log.msg('       SQLAlchemy:   %s' % str(sqlalchemy_version))
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
        log.msg('')


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
        ['database', None, 'mysql+mysqldb://trivia:trivia@localhost/trivia', 'Database connection string.'],
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
        
        logging.basicConfig(
            level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S%z',
            format='%(asctime)s [%(name)s] %(message)s'
        )

        amf_host = '%s://%s:%s/gateway' % (options['amf-transport'],
                                           options['amf-host'],
                                           options['amf-port'])
        
        # rtmp
        app = TriviaApplication(amf_host, options['amf-service'])
        rtmp_apps = {
            options['rtmp-app']: app
        }

        rtmp_server = RTMPServer( rtmp_apps )
        rtmp_service = internet.TCPServer(int(options['rtmp-port']), rtmp_server,
                                         interface=options['rtmp-host'])
        rtmp_service.setServiceParent(top_service)

        # db connection
        engine = create_engine(options['database'])
        engine.connect()
        meta = MetaData()
        meta.bind = engine
        logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

        # site
        trivia_site = TriviaSite()

        # amf
        amf_service = TriviaRemotingService(meta)
        amf_port = int(options['amf-port'])
        amf_services = {
            options['amf-service']: amf_service
        }

        amf_server = WebServer( trivia_site, amf_services, logging.INFO,
                                crossdomain=options['crossdomain'])

        web_service = internet.TCPServer(amf_port, amf_server,
                                         interface=options['amf-host'])
        web_service.setServiceParent(top_service)

        return top_service


# entry point for twistd plugin system
service_maker = TriviaServiceMaker()
