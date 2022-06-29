import os
import sys
import threading
import socket

import dns.resolver


def find_RR_MX(host):
    MX = dns.resolver.resolve(host, 'MX')
    for i in MX:
        print('MX preference=',i.preference,'mail exchanger=',i.exchange)
        return i.exchange.to_text()
    raise Exception(f"CAN NOT RESOLVE MX OF {host}")

class Forward:
    def __init__(self):
        self.login = ''
        self.password = ''
        self.host = ''
        self.recipient = ''


class Recipient:
    def __init__(self):
        self.login = ''
        self.host = ''


class SMTPServerCore(object):

    STATE_INIT = 0
    STATE_HELO = 1
    STATE_EHLO = 2
    STATE_MAIL = 3
    STATE_RCPT = 4
    STATE_DATA = 5
    STATE_QUIT = 6
    STATE_LOGIN = 7

    def __init__(self, conn):
        self.state = SMTPServerCore.STATE_INIT
        self.socket = conn
        self.forward = Forward()
        self.recipient = Recipient()

    def session(self):
        self.socket.sendall(b'220 Python Simple/Demo SMTP Server is glad to see you!\n')
        while True:
            data = bytearray()
            complete_line = 0

            while not complete_line:
                part = self.socket.recv(1024)
                if part:
                    data += part
                    if len(data) >= 2:
                        complete_line = 1
                        if self.state != SMTPServerCore.STATE_DATA:
                            code, keep_connection = self.do_command(data)
                            print(code)
                        else:
                            code = self.do_data(data)
                            keep_connection = 1
                            if code is None:
                                continue
                        self.socket.sendall(code + b"\n")
                        if not keep_connection:
                            self.socket.close()
                else:
                    # EOF
                    return

    def send_command(self, sock, command, buffer=1024):
        """
        发送SMTP命令给目标邮件服务器，返回对方服务器响应
        """
        sock.sendall(command + b'\n')
        return sock.recv(buffer).decode()

    def send_mail(self, mail_exchanger, data, recipient):
        throw_answer = ''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((mail_exchanger, 25))
            print(sock.recv(1024).decode())
            try:
                domain = os.environ.get("PYSMTP_SERVER_DOMAIN", "python.smtp.server")
                self.send_command(sock, b'EHLO ' + domain.encode())
                self.send_command(sock, b'MAIL FROM:<' + f'smtp@{domain}'.encode() + b'>')
                recipient = recipient.login
                throw_answer += self.send_command(sock, b'RCPT TO:<' + recipient.encode() + b'>')
                throw_answer += self.send_command(sock, b'DATA')
                # print(data)
                throw_answer += self.send_command(sock, data.encode())
                if self.send_command(sock, b'QUIT'):
                    sock.close()
                    print('OK: connection to forward server closed')
            except Exception as e:
                throw_answer += 'Error: {}'.format(e)

            finally:
                sock.close()
                print('Answer server:\n{}'.format(throw_answer))
                return throw_answer.encode()

    def do_data(self, data):
        data = data.decode()
        self.detect_host(self.recipient.login)
        print(f'Finding Recipient SMTP [{self.recipient.host}]')
        mail_exchanger = find_RR_MX(self.recipient.host)
        return self.send_mail(mail_exchanger, data, self.recipient)

    def detect_host(self, name):
        print(f"detect_host... {name}")
        host = name[name.find('@') + 1:]
        self.recipient.host = host


    def do_command(self, data):
        """
        """
        data = data.decode()
        cmd = data[0:4]
        cmd = cmd.upper()
        keep_connection = 1
        info_log = '[{}]'.format(cmd)

        if cmd == 'HELO':
            self.state = SMTPServerCore.STATE_HELO

        elif cmd == 'EHLO':
            self.state = SMTPServerCore.STATE_EHLO

        elif cmd == 'AUTH':
            self.state = SMTPServerCore.STATE_LOGIN

        elif cmd == "MAIL":
            self.forward.login = data[11:-2]
            info_log += self.forward.login
            # if self.state != SMTPServerCore.STATE_LOGIN:
            # return (b"503 Bad command sequence", 1)
            self.state = SMTPServerCore.STATE_MAIL

        elif cmd == "RCPT":
            if self.state != SMTPServerCore.STATE_MAIL:
                return b"503 Bad command sequence", 0

            print(f"debug info RCPT[{data}]")
            self.recipient.login = data.strip()[9:-1]
            info_log += self.recipient.login
            self.state = SMTPServerCore.STATE_RCPT

        elif cmd == "DATA":
            if self.state != SMTPServerCore.STATE_RCPT:
                return b"503 Bad command sequence", 0
            self.state = SMTPServerCore.STATE_DATA
            return b"354 OK, Enter data, terminated with a \\r\\n.\\r\\n", keep_connection

        elif cmd == "QUIT":
            return b"221 remsha.online Service closing ", 0

        elif cmd == "RSET":
            self.state = SMTPServerCore.STATE_INIT

        elif cmd == "NOOP":
            return b"250 I Can Fly", keep_connection

        else:
            return b"505 Bad command", 0

        return b"250 OK" + info_log.encode(), keep_connection


class SMTPServer(object):
    def __init__(self, port=25, listeners=5):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen(listeners)

    def socket_accept(self):
        while True:
            conn, addr = self.socket.accept()
            print(f"Connection From {addr}")
            engine = SMTPServerCore(conn)
            t = threading.Thread(target=engine.session())
            t.start()


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
