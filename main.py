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

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont
from modules import keys
from modules import fona

from lxml import etree

power_key = 'P9_12'
power_status = 'P9_15'
network_status = 'P9_23'
ring = 'P9_27'

#===============================================================================
# Classe :      Oled
# Description : 
#===============================================================================
class Oled:
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

    def init_menu(self):
        # Initialise le menu
        self.menu = etree.parse(self.menufile).getroot()
        self.buff = list()
        self.cursor = 0

        for m in self.menu:
            self.buff.append(m.find('Title').text)

        self.refresh()

    def go_child(self):
        
        s = self.menu[self.cursor].find('Submenu')
        if s is not None:
            self.menu = s
            self.buff = list()
            self.cursor = 0

            for m in self.menu:
                try:
                    self.buff.append(m.find('Title').text)
                except AttributeError:
                    msg('[Debug] Aucun champ Title pour {}'.format(m.tag), self.args)

            self.refresh()
        else:
            try:
                s = self.menu[self.cursor].find('Exec').text
                msg('[Debug] Exécution de : {}'.format(s), self.args)
            except AttributeError:
                msg('[Erreur] Aucun <Submenu> ni <Exec> de défini pour {}'.format(self.menu[self.cursor].tag), self.args)

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

    def welcome(self):
        self.buff.append(u'1 Hello world!')
        self.buff.append(u'2 Mon nom est Michel.')
        self.buff.append(u'3 Ceci est un test.')
        self.buff.append(u'4 Je veux voir si ca')
        self.buff.append(u'5 marche, mais je ne')
        self.buff.append(u'6 suis pas inquieté')
        self.cursor = len(self.buff) - 6
        self.refresh()

    def loop(self):
        while True:
            if self.keypad_parent_conn.poll():
                key = self.keypad_parent_conn.recv()
                if key == '1':
                    pass
                elif key == '2':
                    self.scroll_up()
                elif key == '3':
                    pass
                elif key == '4':
                    self.go_parent()
                elif key == '5':
                    self.go_child()
                elif key == '6':
                    self.go_child()
                elif key == '7':
                    pass
                elif key == '8':
                    self.scroll_down()
                elif key == '9':
                    pass
                elif key == '0':
                    pass
                elif key == '*':
                    pass
                elif key == '#':
                    pass
            time.sleep(0.1)

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

    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Augmenter considerablement les messages.')

    args = parser.parse_args()

    if args.logfile:
        logging.basicConfig(filename=args.logfile,
                            format='%(asctime)s[%(levelname)s] %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S ',
                            level=logging.DEBUG)

        if args.debug:
            msg('Logger initié : ' + args.logfile, args)

    if args.debug:
        msg('Programme lancé.', args)

    # Configuration
    #===============

    set_output(power_key, args)
    set_high(power_key, args)
    set_input(power_status, args)
    set_input(network_status, args)
    set_input(ring, args)

    pwr = get_input(power_status, args)
    ntk = get_input(network_status, args)
    rng = get_input(ring, args)

    msg('Power Status: ' + str(pwr), args)
    msg('Network Status: ' + str(ntk), args)
    msg('Ring Indicator: ' + str(rng), args)

    # Lancement des sous-routines
    #=============================

    oled = Oled(args)
    oled.init_menu()

    phone = fona.Fona()

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

            tmp = get_input(power_status, args)
            if tmp != pwr:
                pwr = tmp
                msg('Power Status: ' + str(pwr), args)
            tmp = get_input(network_status, args)
            if tmp != ntk:
                ntk = tmp
                msg('Network Status: ' + str(ntk), args)
            tmp = get_input(ring, args)
            if tmp != rng:
                rng = tmp
                msg('Ring Indicator: ' + str(rng), args)

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

        count_10ms += 1
        count_100ms += 1
        count_1000ms += 1
        time.sleep(0.001)

    return 0

if __name__ == '__main__':
    main()

