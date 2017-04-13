# Python animation objects

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1

from Queue import Empty, Queue
from os import system
from threading import Thread
from time import sleep


class Handler(object):

    pipe = Queue()

    def __init__(self):

        pass

    def Start(self, string):

        self.string = string
        self.animation = Thread(target=self.Execute)

        self.animation.start()
        system('setterm -cursor off')

    def Stop(self, error=None, proceed=False):

        if error:
            self.pipe.put('error', block=True)
        else:
            self.pipe.put(True, block=True)

        self.animation.join()
        system('setterm -cursor on')

        if error and not proceed:
            exit(-1)

    def Execute(self):

        data = False

        while not data:
            for char in ['|', '/', '-', '\\']:
                print '', char, ':', self.string, '\033[F'
                sleep(0.12)

                try:
                   data = self.pipe.get(data)
                except Empty:
                    pass

                if data == 'error':
                    self.Error(self.string)
                    break
                elif data:
                    self.Success(self.string)
                    break

    def Error(self, string):

        print("\033[31mFailed\033[0m: {0}\033[K".format(string))

    def Success(self, string):

        print("\033[32mSuccess\033[0m: {0}\033[K".format(string))

    def Warning(self, string):

        print("\033[33mWarning\033[0m: {0}\033[K".format(string))

    def Info(self, string):

        print("\033[36mInfo\033[0m: {0}\033[K".format(string))
