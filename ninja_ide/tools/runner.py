import code
import subprocess

from PyQt4.QtNetwork import QHostAddress
from PyQt4.QtNetwork import QTcpServer


def run_code(codes):
    interpreter = code.InteractiveInterpreter()
    interpreter.runcode(codes)


def run_code_from_file(fileName):
    subprocess.Popen(['python', fileName])


def isAvailable(port):
    server = QTcpServer()
    result = server.listen(QHostAddress("127.0.0.1"), port)
    server.close()
    return result


def start_pydoc():
    port = 6452
    retry = 10
    while retry > 0 and not isAvailable(port):
        retry -= 1
        port += 10
    proc = subprocess.Popen(['pydoc', '-p', str(port)]), \
        ('http://127.0.0.1:' + str(port) + '/')
    return proc
