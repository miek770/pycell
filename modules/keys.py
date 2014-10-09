#!/usr/bin/python
#-*- coding: utf-8 -*-

from pins import *
from time import sleep, time

class keypad:
    def __init__(self):

        self.row = list()
        self.col = list()

        self.row.append('P8_7')
        self.row.append('P8_9')
        self.row.append('P8_11')
        self.row.append('P8_13')

        self.col.append('P8_15')
        self.col.append('P8_17')
        self.col.append('P8_19')

        for r in self.row:
            set_output(r)
            set_low(r)

        for c in self.col:
            set_input(c)

        self.key = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]

    def read(self):
        for r in self.row:
            set_high(r)

            for c in self.col:
                if get_input(c):
                    set_low(r)
                    return self.key[self.row.index(r)][self.col.index(c)]

            set_low(r)

        return None

    def loop(self, f=0.01, d=0.2):
        last = None
        lasttime = 0.0

        while True:
            r = self.read()

            if r:
                if r != last or time() > lasttime + d:
                    last = r
                    lasttime = time()
                    print r

            sleep(f)

if __name__ == '__main__':
    keypad().loop()

