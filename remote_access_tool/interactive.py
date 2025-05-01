import sys
import os
import select
import termios
import tty

def establecer_sesion_interactiva(stdin, stdout):
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        while True:
            r, w, e = select.select([sys.stdin, stdout.channel], [], [])
            if sys.stdin in r:
                data = os.read(sys.stdin.fileno(), 1024)
                if not data:
                    break
                stdin.write(data)
                stdin.flush()
            if stdout.channel in r:
                if stdout.channel.recv_ready():
                    output = stdout.channel.recv(1024)
                    if not output:
                        break
                    os.write(sys.stdout.fileno(), output)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
