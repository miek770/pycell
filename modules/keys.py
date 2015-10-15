#!/usr/bin/python
#-*- coding: utf-8 -*-

from ablib import Pin
from time import sleep, time

clavier = dict()
clavier["1"] = [".", ",", "1", ":", ";"]
clavier["2"] = ["a", "b", "c", "2"]
clavier["3"] = ["d", "e", "f", "3"]
clavier["4"] = ["g", "h", "i", "4"]
clavier["5"] = ["j", "k", "l", "5"]
clavier["6"] = ["m", "n", "o", "6"]
clavier["7"] = ["p", "q", "r", "s", "7"]
clavier["8"] = ["t", "u", "v", "8"]
clavier["9"] = ["w", "x", "y", "z", "9"]
clavier["0"] = [" ", "0"]
clavier["*"] = ["*", "@"]
clavier["#"] = ["!", "?", "#", "\n"]

class Keypad:

    def __init__(self, period=0.05, delay=0.3):

        self.row = list()
        self.col = list()

        self.row.append(Pin('J4.39', 'OUTPUT')) # Row 0
        self.row.append(Pin('J4.37', 'OUTPUT')) # Row 1
        self.row.append(Pin('J4.35', 'OUTPUT')) # Row 2
        self.row.append(Pin('J4.33', 'OUTPUT')) # Row 3

        self.col.append(Pin('J4.31', 'INPUT')) # Col 0
        self.col.append(Pin('J4.29', 'INPUT')) # Col 1
        self.col.append(Pin('J4.27', 'INPUT')) # Col 2
        self.col.append(Pin('J4.19', 'INPUT')) # Col 3
        self.col.append(Pin('J4.21', 'INPUT')) # Col 4

        self.period = period
        self.delay = delay

        for r in self.row:
            r.on()

        self.key = [['1', '2', '3', 'o', 'e'], ['4', '5', '6', 'd', 'u'], ['7', '8', '9', 'l', 'r'], ['*', '0', '#', 'x', 'y']]

    def read(self):

        for r in self.row:
            r.off()

            for c in self.col:
                if not c.get_value():
                    r.on()
                    return self.key[self.row.index(r)][self.col.index(c)]

            r.on()

        return None

    def test(self):
        last = None
        lasttime = 0.0

        while True:
            r = self.read()

            if r:
                if r != last or time() > lasttime + self.delay:
                    last = r
                    lasttime = time()
                    print r
                    sleep(0.1)

            sleep(self.period)

def loop(conn):
    k = Keypad()
    last = None
    lasttime = 0.0

    while True:
        r = k.read()

        if r:
            if r != last or time() > lasttime + k.delay:
                last = r
                lasttime = time()
                conn.send(r)
                sleep(0.1)

        sleep(k.period)

        if conn.poll():
            k.period = conn.recv()

