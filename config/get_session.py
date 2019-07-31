from mitmproxy import ctx
import json
from logger import logger
import socket
import sys

exit_on_success = True
print_cookie = False  # we recommend only turning this on if debugging


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr


class CookieLogger:

    def __init__(self):
        logger.info("Running proxy on {} (Port: 8080)".format(get_ip()))
        logger.info(
            "Head to the network settings on your iOS / Android device (or emulator), and set this as this as the proxy")
        logger.info(
            "New users: make sure to head to setup.ink in your browser to install certificates so we get your cookie")

        self.session = {"api_key": "", "cookie": "", "friend_code": "",
                        "session_token": "skip", "user_lang": ""}

    def steal_token(self, flow):
        try:
            self.session['cookie'] = flow.request.cookies['iksm_session']
            if print_cookie:
                logger.info("Got new cookie {}".format(
                    self.session['cookie']))
            else:
                logger.info("Got new cookie")
            with open("config/config.txt", "w") as session_f:
                session_f.write(json.dumps(self.session, indent=4))
                if exit_on_success:
                    sys.exit(0)
        except KeyError:
            pass

    def request(self, flow):
        self.steal_token(flow)


addons = [
    CookieLogger()
]
