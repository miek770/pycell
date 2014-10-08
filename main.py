#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  main.py
#
#  Copyright 2014 Michel Lavoie <lavoie.michel@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import argparse, logging, sys
from multiprocessing import Process, Pipe
#from random import randint
from modules.pins import *
import time
from datetime import datetime

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont
from modules import keys
from modules import fona

from lxml import etree

POWER_KEY = 'P9_12'
POWER_STATUS = 'P9_15'
NETWORK_STATUS = 'P9_23'
RING = 'P9_27'

#===============================================================================
# Classe :      Oled
# Description : 
#===============================================================================
class Oled:

    # Initialisation
    #================
    def __init__(self, args, menufile='ressources/menu.xml'):
        self.args = args

        RST = 'P9_13'
        DC = 'P9_14'
        SPI_PORT = 1
        SPI_DEVICE = 0

        # 128x64 display with hardware SPI:
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Initialisation du menu
        self.maxlines = 6
        self.menufile = menufile

        # Initialize keypad
        self.keypad_parent_conn, self.keypad_child_conn = Pipe()
        self.keypad_sub = Process(target=keys.loop, args=(self.keypad_child_conn, ))
        self.keypad_sub.start()

        # Initialisation du module Fona
        self.phone = fona.Fona()

        set_output(POWER_KEY, self.args)
        set_high(POWER_KEY, self.args)
        set_input(POWER_STATUS, self.args)
        set_input(NETWORK_STATUS, self.args)
        set_input(RING, self.args)

        self.pwr = get_input(POWER_STATUS, self.args)
        #self.ntk = get_input(NETWORK_STATUS, self.args)
        self.rng = get_input(RING, self.args)

        # Demarre le Fona s'il ne l'est pas deja
        if not self.pwr:
            msg('Demarrage du module Fona...', self.args)
            set_low(POWER_KEY, self.args)
            time.sleep(2)
            set_high(POWER_KEY, self.args)

        msg('Power Status: ' + str(self.pwr), self.args)
        #msg('Network Status: ' + str(self.ntk), self.args)
        msg('Ring Indicator: ' + str(self.rng), self.args)

    # Initialisation du menu
    #========================
    def init_menu(self):
        # Initialise le menu
        self.menu = etree.parse(self.menufile).getroot()
        self.buff = list()
        self.cursor = 0

        for m in self.menu:
            self.buff.append(m.find('Title').text)

        self.refresh()

    # Générateurs (associés à ressources/menu.xml)
    #==============================================
    def gen_msg(self):
        msg = self.phone.get_all_sms()

        msg = msg.split('\r\n+CMGL: ')
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
            when = datetime.strptime('{} {}'.format(a, a1).strip('"')[:-3], '%y/%m/%d %H:%M%S')

            message = b[:-2]

    # Cette fonction va devoir créer des sous-menus à partir d'une liste de tuples bâtie ainsi :
    # [('Nom', 'Titre', 'Action', 'Commande'), ...] où :
    #
    #   Nom = Nom de l'élément (interne)
    #   Titre = Titre de l'élément du menu à afficher
    #   Action = "Exec" ou "Generator"
    #   Commande = Nom de la fonction à appeler

    def create_submenus(self, generator):

        # Génère les sous-menus à partir du générateur
        submenus = eval('self.{}()'.format(generator))

        # Commence par effacer les sous-menus actuels
        self.menu.remove(self.menu[self.cursor].find('Submenu'))

        # Popule le nouveau sous-menu
        self.menu.SubElement(self.menu[self.cursor], 'Submenu')
        for menu in submenus:
            self.menu.SubElement(self.menu[self.cursor].find('Submenu'), menu[0])

            self.menu.SubElement(self.menu[self.cursor].find('Submenu').find(menu[0], 'Title'))
            self.menu[self.cursor].find('Submenu').find(menu[0]).find('Title').text = menu[1]

            self.menu.SubElement(self.menu[self.cursor].find('Submenu').find(menu[0], menu[2]))
            self.menu[self.cursor].find('Submenu').find(menu[0]).find('Title').text = menu[3]

    def go_child(self):
        if self.menu[self.cursor].find('Generator'):
            self.create_submenus(self.menu[self.cursor].find('Generator').text)
            self.menu = self.menu[self.cursor].find('Submenu')
            self.buff = list()
            self.cursor = 0

            for m in self.menu:
                try:
                    self.buff.append(m.find('Title').text)
                except AttributeError:
                    msg('[Erreur] Aucun champ Title pour {}'.format(m.tag), self.args)

            self.refresh()

        elif self.menu[self.cursor].find('Submenu'):
            self.menu = self.menu[self.cursor].find('Submenu')
            self.buff = list()
            self.cursor = 0

            for m in self.menu:
                try:
                    self.buff.append(m.find('Title').text)
                except AttributeError:
                    msg('[Erreur] Aucun champ Title pour {}'.format(m.tag), self.args)

            self.refresh()

        elif self.menu[self.cursor].find('Exec'):
            msg('[Debug] Exécution de : {}'.format(self.menu[self.cursor].find('Exec').text), self.args)

        else:
            msg('[Erreur] Aucune action de définie pour {}'.format(self.menu[self.cursor].tag), self.args)
        
    def go_parent(self):
        try:
            self.menu = self.menu.find('..').find('..')
            self.buff = list()
            self.cursor = 0

            for m in self.menu:
                self.buff.append(m.find('Title').text)

            self.refresh()
        except AttributeError:
            msg('[Debug] Aucun menu parent pour {}'.format(self.menu.tag), self.args)

    def refresh(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height

        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        #font = ImageFont.load_default()
        font = ImageFont.truetype('ressources/Minecraftia-Regular.ttf', 8)

        i = 0
        for l in range(self.cursor, len(self.buff)):
            if i < self.maxlines:
                if i == 0:
                    draw.text((0, 10*i), '> {}'.format(self.buff[l]), font=font, fill=255)
                else:
                    draw.text((0, 10*i), self.buff[l], font=font, fill=255)
                i += 1

        # Display image.
        self.disp.image(image)
        self.disp.display()

    def scroll_down(self):
        if self.cursor < len(self.buff) - 1:
            self.cursor += 1
            self.refresh()

    def scroll_up(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.refresh()

    def update_fona_status(self):
            tmp = get_input(POWER_STATUS, self.args)
            if tmp != self.pwr:
                self.pwr = tmp
                msg('Power Status: ' + str(self.pwr), self.args)
            #tmp = get_input(NETWORK_STATUS, self.args)
            #if tmp != self.ntk:
                #self.ntk = tmp
                #msg('Network Status: ' + str(self.ntk), self.args)
            tmp = get_input(RING, self.args)
            if tmp != self.rng:
                self.rng = tmp
                msg('Ring Indicator: ' + str(self.rng), self.args)

#===============================================================================
# Fonction :    main
# Description : Routine principale
#===============================================================================
def main():
    parser = argparse.ArgumentParser(description='PyCell')

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='Imprime l\'aide sur l\'exécution du script.')
    
    parser.add_argument('-l',
                        '--logfile',
                        action='store',
                        help='Spécifie le chemin du journal d\'événement.')

    args = parser.parse_args()

    if args.logfile:
        logging.basicConfig(filename=args.logfile,
                            format='%(asctime)s[%(levelname)s] %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S ',
                            level=logging.DEBUG)

        msg('Logger initié : ' + args.logfile, args)

    msg('Programme lancé.', args)

    # Lancement des sous-routines
    #=============================

    oled = Oled(args)
    oled.init_menu()

    # Boucle principale
    #===================

    # J'ai créé des compteurs indépendants pour pouvoir les redémarrer à zéro
    # sans affecter les autres (pour ne pas atteindre des chiffres inutilement
    # élevés).
    count_10ms = 0
    count_100ms = 0
    count_1000ms = 0

    while True:

        # S'exécute toutes les 10ms
        if count_10ms == 10:
            count_10ms = 0

            oled.update_fona_status()

        # S'exécute toutes les 100ms
        if count_100ms == 100:
            count_100ms = 0

            if oled.keypad_parent_conn.poll():
                key = oled.keypad_parent_conn.recv()
                if key == '1':
                    pass
                elif key == '2':
                    oled.scroll_up()
                elif key == '3':
                    pass
                elif key == '4':
                    oled.go_parent()
                elif key == '5':
                    oled.go_child()
                elif key == '6':
                    oled.go_child()
                elif key == '7':
                    pass
                elif key == '8':
                    oled.scroll_down()
                elif key == '9':
                    pass
                elif key == '0':
                    pass
                elif key == '*':
                    pass
                elif key == '#':
                    pass
 
        # S'exécute toutes les 1s
        if count_1000ms == 1000:
            count_1000ms = 0

            pass

        count_10ms += 1
        count_100ms += 1
        count_1000ms += 1
        time.sleep(0.001)

    return 0

if __name__ == '__main__':
    main()

