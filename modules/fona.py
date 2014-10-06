#!/usr/bin/python
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

        # Mode texte pour les SMS
        self.text_mode()

        # Désactive l'écho
        self.echo_off()

    # Commandes de base et configuration
    #======================================================

    def write(self, string, delay=0.05):
        self.ser.write('{}\n'.format(string))
        sleep(delay)
        return self.ser.read(self.ser.inWaiting())

    def read(self, l=False):
        if self.new_data():
            if l<= self.ser.inWaiting():
                return self.ser.read(l)
            else:
                return self.ser.read(self.ser.inWaiting())

    def new_data(self):
        if self.ser.inWaiting():
            return True
        else:
            return False

    def get_config(self):
        return self.write('AT&V')

    def text_mode(self):
        return self.write('AT+CMGF=1')

    def echo_off(self):
        return self.write('ATE0')

    def echo_on(self):
        return self.write('ATE1')

    # Commandes liées aux SMS
    #==================================

    def send_sms(self, num, msg):
        self.ser.write('AT+CMGS="{0}"\r'.format(num))
        sleep(0.05)
        self.ser.write('{0}{1}'.format(msg, chr(26)))
        sleep(0.05)
        return self.ser.read(self.ser.inWaiting())

    def new_sms(self):
        if new_data():
            r = self.ser.read(self.ser.inWaiting())
            if '+CMTI: "SM",' in r:
                return r.split(',')[2]
            else:
                return False
        else:
            return False

    def read_sms(self, id):
        if id:
            return self.write('AT+CMGR={0}'.format(int(id)))
        else:
            return False

    def read_all_sms(self):
        return self.write('AT+CMGL="ALL"', delay=0.2)

    # Commandes liées à la voix
    #===========================

    def call(self, num):
        return self.write('ATD{0};'.format(num))

    def hang_up(self):
        return self.write('ATH')

    def redial(self):
        return self.write('ATDL')

    def answer(self):
        return self.write('ATA')

