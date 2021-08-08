import asyncio
import logging
import settings
import getpass
import ssl
from slixmpp import ClientXMPP, OptionParser



class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            self.send_message(mto=msg['from'],
                            mbody='Thanks for sending:\n%s' % msg['body'])


if __name__ == '__main__':
    
    optp = OptionParser()

    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    if opts.jid is None:
        opts.jid = input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    logging.basicConfig(
        level=opts.loglevel,
        format='%(levelname)-8s %(message)s')

    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # Ping
    xmpp.ssl_version = ssl.PROTOCOL_SSLv3 # OpenFire server config