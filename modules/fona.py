#!/usr/bin/python
#-*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import re, serial, sys
from pins import *

#===============================================================================
# Classe :      SMS
# Description : Message SMS.
#===============================================================================
class SMS:

    # Initialisation
    #================
    def __init__(self, index, status, number, when, message):
        self.index = index
        self.status = status
        self.number = number
        self.when = when
        self.message = message

#===============================================================================
# Classe :      Fona
# Description : Wrapper pour le module Fona d'Adafruit (SIM800).
#===============================================================================
class Fona:

    # Initialisation
    #================
    def __init__(self, args=None, power_key='P9_12', power_status='P9_15', network_status='P9_23', ring='P9_27'):
        self.args = args

        self.ser = serial.Serial('/dev/ttyO1')
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.parity = 'N'
        self.ser.stopbits = 1
        self.ser.timeout = 0.1
        self.ser.xonxoff = 0
        self.ser.rtscts = 0

        # Configuration des pins de contrôle
        self.power_key = power_key
        self.power_status = power_status
        self.network_status = network_status
        self.ring = ring

        set_output(self.power_key, self.args)
        set_high(self.power_key, self.args)
        set_input(self.power_status, self.args)
        set_input(self.network_status, self.args)
        set_input(self.ring, self.args)

        self.pwr = get_input(self.power_status, self.args)
        #self.ntk = get_input(self.network_status, self.args)
        self.rng = get_input(self.ring, self.args)

        # Demarre le Fona s'il ne l'est pas deja
        if not self.pwr:
            msg('Demarrage du module Fona...', self.args)
            set_low(self.power_key, self.args)
            sleep(2)
            set_high(self.power_key, self.args)

        msg('Power Status: ' + str(self.pwr), self.args)
        #msg('Network Status: ' + str(self.ntk), self.args)
        msg('Ring Indicator: ' + str(self.rng), self.args)

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

    def get_config(self, delay=0.3):
        return self.write('AT&V')

    def text_mode(self):
        return self.write('AT+CMGF=1')

    def echo_off(self):
        return self.write('ATE0')

    def echo_on(self):
        return self.write('ATE1')

    def update_status(self):
        tmp = get_input(self.power_status, self.args)
        if tmp != self.pwr:
            self.pwr = tmp
            msg('Power Status: ' + str(self.pwr), self.args)
        #tmp = get_input(self.network_status, self.args)
        #if tmp != self.ntk:
            #self.ntk = tmp
            #msg('Network Status: ' + str(self.ntk), self.args)
        tmp = get_input(self.ring, self.args)
        if tmp != self.rng:
            self.rng = tmp
            msg('Ring Indicator: ' + str(self.rng), self.args)

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
        msg = self.write('AT+CMGR={0}'.format(int(id))).split('\r\n+CMGR: ')

        index = int(id)

        (a, b) = msg[1].split(',', 1)
        status = a.strip('"')

        (a, b) = b.split(',', 1)
        number = a.strip('"+')

        (a, b) = b.split(',', 1) # a = '""'

        (a, b) = b.split(',', 1)
        (a1, b) = b.split('"\r\n', 1)
        when = datetime.strptime('{} {}'.format(a, a1).strip('"')[:-3], '%y/%m/%d %H:%M:%S')

        message = b[:-8].decode('latin-1')

        return SMS(index, status, number, when, message)

    def read_all_sms(self):
        # Plus il y aura de SMS en mémoire plus cette fonction prendra
        # de temps à s'exécuter. Il faudra éventuellement que je
        # m'arranger pour que la fonction attende le temps nécessaire,
        # ni plus ni moins. Je pourrais attendre le OK à la fin par
        # exemple.
        #
        # En fait ça pourrait être le comportement par défaut de
        # self.write().

        liste_sms = list()

        msg = self.write('AT+CMGL="ALL"', delay=0.3).split('\r\n+CMGL: ')
        msg.pop(0)

        for m in msg:
            (a, b) = m.split(',', 1)
            index = int(a)

            (a, b) = b.split(',', 1)
            status = a.strip('"')

            (a, b) = b.split(',', 1)
            number = a.strip('"+')

            (a, b) = b.split(',', 1) # a = '""'

            (a, b) = b.split(',', 1)
            (a1, b) = b.split('"\r\n', 1)
            when = datetime.strptime('{} {}'.format(a, a1).strip('"')[:-3], '%y/%m/%d %H:%M:%S')

            message = b[:-2].decode('latin-1')

            liste_sms.append(SMS(index, status, number, when, message))

        return liste_sms

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

    # Générateurs (associés à ../ressources/menu.xml)
    #==============================================
    def gen_msg(self):
        menus = list()
        msg = self.read_all_sms()

        for m in msg:
            nom = 'sms{}'.format(m.index)
            titre = '{:%y%m%d %H:%M} - {}'.format(m.when, m.number)
            action = 'Generator'
            commande = 'show("{}")'.format(m.message)

            menus.append((nom, titre, action, commande))

        return menus

