#!/usr/bin/python
#-*- coding: utf-8 -*-

from ablib import Pin
from time import sleep, time

class Keypad:
    def __init__(self):

        self.row = list()
        self.col = list()

        self.row.append(Pin('J4.39', 'OUTPUT')) # Row 0
        self.row.append(Pin('J4.37', 'OUTPUT')) # Row 1
        self.row.append(Pin('J4.35', 'OUTPUT')) # Row 2
        self.row.append(Pin('J4.33', 'OUTPUT')) # Row 3

        self.col.append(Pin('J4.31', 'INPUT')) # Col 0
        self.col.append(Pin('J4.29', 'INPUT')) # Col 1
        self.col.append(Pin('J4.27', 'INPUT')) # Col 2
        self.col.append(Pin('J4.19', 'INPUT')) # Col 3 - À corriger dans le circuit, actuellement soudé sur J4.25
        self.col.append(Pin('J4.21', 'INPUT')) # Col 4

        for r in self.row:
            r.on()

        self.key = [['1', '2', '3', 'a', 'b'], ['4', '5', '6', 'c', 'd'], ['7', '8', '9', 'e', 'f'], ['*', '0', '#', 'g', 'h']]

    def read(self):

        for r in self.row:
            r.off()

            for c in self.col:
                if not c.get_value():
                    r.on()
                    return self.key[self.row.index(r)][self.col.index(c)]

            r.on()

        return None

    def test(self, f=0.005, d=0.2):
        last = None
        lasttime = 0.0

        while True:
            r = self.read()

            if r:
                if r != last or time() > lasttime + d:
                    last = r
                    lasttime = time()
                    print r
                    sleep(0.1)

            sleep(f)

def loop(conn, f=0.005, d=0.2):
    k = Keypad()
    last = None
    lasttime = 0.0

    while True:
        r = k.read()

        if r:
            if r != last or time() > lasttime + d:
                last = r
                lasttime = time()
                conn.send(r)
                sleep(0.1)

        sleep(f)

