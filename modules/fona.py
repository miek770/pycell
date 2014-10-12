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
        self.message = unicode(message)

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
            sleep(2)

        msg('Power Status: ' + str(self.pwr), self.args)
        #msg('Network Status: ' + str(self.ntk), self.args)
        msg('Ring Indicator: ' + str(self.rng), self.args)

        # Configuration générale
        self.set_echo(False)
        self.set_clock(when=datetime.now(), delta='-16')

        # Configuration des SMS
        self.set_text_mode(True)
        self.set_force_ascii(False)
        self.set_encoding(encoding='8859-1')

        # Active le son sur le speaker (et non le casque d'écoute)
        self.set_audio_channel(1)

    # Commandes de base et configuration
    #======================================================

    def turn_off(self):
        msg('Fermeture du module Fona...', self.args)
        set_low(self.power_key, self.args)
        sleep(2)
        set_high(self.power_key, self.args)

    def power_off(self):
        self.turn_off()

    def write(self, string):
        self.ser.write('{}\n'.format(string))
        sleep(0.1)
        return self.read(self.ser.inWaiting())

    def read(self, l=False):
        msg = u''
        while self.new_data():
            msg += unicode(self.ser.read(self.ser.inWaiting()).decode('latin-1'))
            sleep(0.05)
        return msg

    def new_data(self):
        if self.ser.inWaiting():
            return True
        else:
            return False

    def get_config(self):
        return self.write('AT&V')

    def set_text_mode(self, mode=True):
        if mode:
            return self.write('AT+CMGF=1')
        else:
            return self.write('AT+CMGF=0')

    def set_echo(self, echo):
        if echo:
            return self.write('ATE1')
        else:
            return self.write('ATE0')

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

    def get_battery(self):
        return self.write('AT+CBC')

    def get_provider(self):
        return self.write('AT+CSPN?')

    def get_clock(self):
        return self.write('AT+CCLK?')

    # delta est la différence avec GMT en quarts d'heure
    def set_clock(self, when=datetime.now(), delta='-20'):
        return self.write('AT+CCLK="{:%y/%m/%d,%H:%M:%S}{}"'.format(when, delta))

    # Commandes liées aux SMS
    #==================================

    def get_force_ascii(self):
        return self.write('AT+CMGHEX?')

    def set_force_ascii(self, force):
        if force:
            return self.write('AT+CMGHEX=0')
        else:
            return self.write('AT+CMGHEX=1')

    def get_encoding(self):
        return self.write('AT+CSCS?')

    def set_encoding(self, encoding='GSM'):
        return self.write('AT+CSCS="{}"'.format(encoding))

    def send_sms(self, num, msg):
        self.ser.write('AT+CMGS="{0}"\r'.format(num))
        sleep(0.05)
        self.ser.write('{0}{1}'.format(msg, chr(26)))
        sleep(0.05)
        return self.read(self.ser.inWaiting())

    def new_sms(self):
        if new_data():
            r = self.read(self.ser.inWaiting())
            if '+CMTI: "SM",' in r:
                return r.split(',')[2]
            else:
                return False
        else:
            return False

    def read_sms(self, id):
        sms = self.write('AT+CMGR={0}'.format(int(id))).split('+CMGR: ')
        msg('[Debug] SMS : {}'.format(sms), self.args)

        index = int(id)

        (a, b) = sms[1].split(',', 1)
        status = a.strip('"')

        (a, b) = b.split(',', 1)
        number = a.strip('"+')

        (a, b) = b.split(',', 1) # a = '""'

        (a, b) = b.split(',', 1)
        (a1, b) = b.split('"\r\n', 1)
        when = datetime.strptime('{} {}'.format(a, a1).strip('"')[:-3], '%y/%m/%d %H:%M:%S')

        message = b[:-8]

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

        msg = self.write('AT+CMGL="ALL"', delay=0.3).split('+CMGL: ')
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

            message = b[:-2]

            liste_sms.append(SMS(index, status, number, when, message))

        return liste_sms

    # Commandes liées à la voix
    #===========================

    def call(self, number):
        return self.write('ATD{0};'.format(number))

    def hang_up(self):
        return self.write('ATH')

    def redial(self):
        return self.write('ATDL')

    def answer(self):
        return self.write('ATA')

    def get_volume(self):
        return self.write('AT+CLVL?')

    def set_volume(self, volume):
        return self.write('AT+CLVL={}'.format(volume))

    def get_mute(self):
        return self.write('AT+CMUT?')

    def set_mute(self, mute):
        if mute:
            return self.write('AT+CMUT=1')
        else:
            return self.write('AT+CMUT=0')

    def get_mic_gain(self):
        return self.write('AT+CMIC?')

    def set_mic_gain(self, channel, gain):
        return self.write('AT+CMIC={},{}'.format(channel, gain))

    def get_audio_channel(self):
        return self.write('AT+CHFA?')

    def set_audio_channel(self, channel):
        return self.write('AT+CHFA={}'.format(channel))

    # Générateurs (associés à ../ressources/menu.xml)
    #==============================================
    def gen_msg(self):
        menus = list()
        msg = self.read_all_sms()

        for m in msg:
            nom = 'sms{}'.format(m.index)
            titre = '{:%y%m%d %H:%M} - {}'.format(m.when, m.number)
            action = 'Generator'
            commande = u'show("""{}""")'.format(m.message)

            menus.append((nom, titre, action, commande))

        return menus

