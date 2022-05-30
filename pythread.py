# Python program using
# traces to kill threads

import sys
import trace
import threading
import time
class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run	
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

def func(name =1):
    while True:
        print('running in thread %s' % name)

t1 = thread_with_trace(target = func, args = (1,))
t1.start()
time.sleep(2)
t2 = thread_with_trace(target = func, args = (2,))
t2.start()
time.sleep(3)
t1.kill()
t1.join()
t2.kill()
t2.join()
if not t1.is_alive():
    print('thread1 killed')
if not t2.is_alive():
    print('thread2 killed')
