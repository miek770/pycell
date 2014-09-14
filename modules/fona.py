#!/root/cell/bin/python
#-*- coding: utf-8 -*-

from time import sleep
import re
import serial

class Fona:
    # Initialisation
    #================
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyO1')
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.parity = 'N'
        self.ser.stopbits = 1
        self.ser.timeout = 0.1
        self.ser.xonxoff = 0
        self.ser.rtscts = 0

        # Set SMS system into text mode, as opposed to PDU mode
        self.write('AT+CMGF=1')

    def send_sms(self, num, msg, raw=False):
        self.ser.write('AT+CMGS="{0}"\r'.format(num))
        sleep(0.01)
        self.ser.write('{0}{1}'.format(msg, chr(26)))
        sleep(0.01)
        r = self.ser.read(self.ser.inWaiting())
        if not raw:
            return r.split('\n')[1].split('\r')[0]
        else:
            return r

    # Écrit une commande et retourne le résultat (nettoyé)
    #======================================================
    def write(self, s, raw=False):
        self.ser.write('{0}\n'.format(s))
        sleep(0.01)
        r = self.ser.read(self.ser.inWaiting())
        if not raw:
            return r.split('\n')[1].split('\r')[0]
        else:
            return r

