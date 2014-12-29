#!/usr/bin/python
#-*- coding: utf-8 -*-

from ablib import Pin
from time import sleep, time

class keypad:
    def __init__(self):

        self.row = list()
        self.col = list()

        self.row.append(Pin('J4.27', 'OUTPUT')) # Row 0
        self.row.append(Pin('J4.29', 'OUTPUT')) # Row 1
        self.row.append(Pin('J4.31', 'OUTPUT')) # Row 2
        self.row.append(Pin('J4.33', 'OUTPUT')) # Row 3

        self.col.append(Pin('J4.35', 'INPUT')) # Col 0
        self.col.append(Pin('J4.37', 'INPUT')) # Col 1
        self.col.append(Pin('J4.39', 'INPUT')) # Col 2

        for r in self.row:
            r.on()

        self.key = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]

    def read(self):

        for r in self.row:
            r.off()

            for c in self.col:
                if not c.get_value():
                    r.on()
                    return self.key[self.row.index(r)][self.col.index(c)]

            r.on()

        return None

def loop(conn, f=0.005, d=0.2):
    k = keypad()
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

