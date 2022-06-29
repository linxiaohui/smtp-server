import sys

from .smtp_server import SMTPServer

if __name__ == '__main__':
    port = 25
    if len(sys.argv) == 2:
        # noinspection PyBroadException
        try:
            port = int(sys.argv[1])
        except:
            pass
    print(f"Starting Simple SMTP Server on {port}")
    server = SMTPServer(port)
    server.socket_accept()
