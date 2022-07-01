import sys

if sys.platform=='linux':
    import termios, fcntl, os
    import atexit
    class keyboard:
        def __init__(self):
            #print("hallo")
            self.fd = sys.stdin.fileno()
            self.oldterm = termios.tcgetattr(self.fd)
            newattr = termios.tcgetattr(self.fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(self.fd, termios.TCSANOW, newattr)
            self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
            self.character=b''
            atexit.register(self.cleanup)
        def cleanup(self):
            #print("Running cleanup...")
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
        def kbhit(self):
            try:
                while True:
                    try:
                        c = sys.stdin.read(1)
                        if len(c) == 0:
                            return False
                        self.character=c # here ungetch should apply, how you do it?
                        #construction with self.character is a not good FIXME
                        return True
                    except IOError:
                        return False
            finally:
                pass
        def getch(self):
            if len(self.character):
                x=self.character
                self.character = b''
                return x
            while True:
                c = sys.stdin.read(1)
                if len(c) == 1:
                    return c
else:
    import msvcrt
    class keyboard:
        def __init__(self):
            pass
        def kbhit(self):
            return msvcrt.kbhit()
        def getch(self):
            return msvcrt.getch()
        def gets(self):
            line = b''
            while True:
                c = msvcrt.getch()
                if c==b'\r':
                    return line
                line += c        


if __name__ == '__main__':
    import time
    rrr=keyboard()
    print ("type a line!")    
    print("gets() returned",rrr.gets())