# Copyright (c) The rtmp-trivia Project.
# See LICENSE.txt for details.

"""
@since: 0.1
"""

from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor

from trivia import __version__


def application(environ, start_response):
    """
    """
    start_response('200 OK', [('Content-type', 'html')])

    return ["<html><body>rtmp-trivia %s</body></html>" % str(__version__)]


class TriviaSite(WSGIResource):
    """
    """
    def __init__(self, *args):
        WSGIResource.__init__(self, reactor, reactor.getThreadPool(),
                              application)
