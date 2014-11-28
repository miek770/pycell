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

import argparse, logging, sys
from multiprocessing import Process, Pipe
import logging
import time

import Image
import ImageDraw
import ImageFont
from modules import keys
from modules.fona import Fona
from modules.SSD1306 import SSD1306

from lxml import etree

# Arietta G25
#=============

#'J4.7'  PA23
#'J4.8'  PA22
#'J4.10' PA21
#'J4.11' PA24   SPI1 CS0
#'J4.12' PA31   Display reset
#'J4.13' PA25
#'J4.14' PA30   Display clear
#'J4.15' PA26
#'J4.17' PA27
#'J4.19' PA28
#'J4.21' PA29
#'J4.23' PA0
#'J4.24' PA1
#'J4.25' PA8
#'J4.26' PA7    Power key
#'J4.27' PA6    Row 0
#'J4.28' PA5    Power
#'J4.29' PC28   Row 1
#'J4.30' PC27   Network
#'J4.31' PC4    Row 2
#'J4.32' PC31   Ring indicator
#'J4.33' PC3    Row 3
#'J4.34' PB11
#'J4.35' PC2    Col 0
#'J4.36' PB12
#'J4.37' PC1    Col 1
#'J4.38' PB13
#'J4.39' PC0    Col 2
#'J4.40' PB14

#===============================================================================
# Fonction :    msg(msg, args, lvl)
# Description : Cette fonction permet d'utiliser une seule fonction pour toute
#               impression (print ou log) dependamment des arguments en ligne
#               de commande. On ne devrait jamais utiliser directement 'print'
#               et 'logging.log' dans le reste du programme, toujours 'msg'.
#===============================================================================
def msg(msg, args=None, lvl=logging.INFO):
    if args is None or args.verbose:
        print msg

    elif args.logfile:
        logging.log(lvl, msg)

#===============================================================================
# Classe :      Phone
# Description : Classe d'application générale.
#===============================================================================
class Phone:

    # Initialisation
    #================
    def __init__(self, args=None, menufile='ressources/menu.xml'):
        self.args = args

        RST = 'J4.12'
        DC = 'J4.14'
        CS = 'J4.11'

        # 128x64 display with hardware SPI:
        self.disp = SSD1306(rst=RST, dc=DC, cs=CS)

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
        self.fona = Fona(self.args)
        self.font = ImageFont.truetype('ressources/Minecraftia-Regular.ttf', 8)

    # Initialisation du menu
    #========================
    def init_menu(self):
        # Initialise le menu
        self.tree = etree.parse(self.menufile)
        self.menu = self.tree.getroot()
        self.buff = list()
        self.cursor = 0
        self.previous_cursor = 0

        for m in self.menu:
            self.buff.append(m.find('Title').text)

        self.refresh()

    # Cette fonction va devoir créer des sous-menus à partir d'une liste de tuples bâtie ainsi :
    # [('Nom', 'Titre', 'Action', 'Commande'), ...] où :
    #
    #   Nom = Nom de l'élément (interne)
    #   Titre = Titre de l'élément du menu à afficher
    #   Action = "Exec" ou "Generator" ou None
    #   Commande = Nom de la fonction à appeler
    #
    # Ce sont les générateurs qui produisent ces listes.

    def create_submenus(self, generator):

        # Génère les sous-menus à partir du générateur
        msg(u'[Debug] générateur = {}'.format(generator), self.args)
        submenus = eval(u'self.{}'.format(generator))
        msg(u'[Debug] submenus = {}'.format(submenus), self.args)

        # Effacer les sous-menus actuels, si existants
        if self.menu[self.cursor].find('Submenu') is not None:
            etree.strip_elements(self.menu[self.cursor], 'Submenu')

        # Popule le nouveau sous-menu
        etree.SubElement(self.menu[self.cursor], 'Submenu')
        for menu in submenus:
            msg(u'[Debug] menu = ({}, {}, {}, {})'.format(menu[0], menu[1], menu[2], menu[3]), self.args)
            etree.SubElement(self.menu[self.cursor].find('Submenu'), menu[0])

            if menu[1] is not None:
                etree.SubElement(self.menu[self.cursor].find('Submenu').find(menu[0]), 'Title')
                self.menu[self.cursor].find('Submenu').find(menu[0]).find('Title').text = menu[1]

            if menu[2] is not None and menu[3] is not None:
                etree.SubElement(self.menu[self.cursor].find('Submenu').find(menu[0]), menu[2])
                self.menu[self.cursor].find('Submenu').find(menu[0]).find(menu[2]).text = menu[3]

    def go_child(self):
        if self.menu[self.cursor].find('Generator') is not None:
            msg('[Debug] Génération de sous-menus dans {}'.format(self.menu[self.cursor].find('Title').text), self.args)
            self.create_submenus(self.menu[self.cursor].find('Generator').text)
            self.menu = self.menu[self.cursor].find('Submenu')
            self.buff = list()
            self.previous_cursor = self.cursor
            self.cursor = 0

            for m in self.menu:
                try:
                    self.buff.append(unicode(m.find('Title').text))
                except AttributeError:
                    msg('[Erreur] Aucun champ Title pour {}'.format(m.tag), self.args)

            self.refresh()

        elif self.menu[self.cursor].find('Submenu') is not None:
            self.menu = self.menu[self.cursor].find('Submenu')
            self.buff = list()
            self.cursor = 0

            for m in self.menu:
                try:
                    self.buff.append(unicode(m.find('Title').text))
                except AttributeError:
                    msg('[Erreur] Aucun champ Title pour {}'.format(m.tag), self.args)

            self.refresh()

        elif self.menu[self.cursor].find('Exec') is not None:
            msg('[Debug] Exécution de : {}'.format(self.menu[self.cursor].find('Exec').text), self.args)

        else:
            msg('[Debug] Aucune action de définie pour {}'.format(self.menu[self.cursor].tag, ), self.args)
        
    def go_parent(self):
        try:
            self.menu = self.menu.find('..').find('..')
            self.buff = list()
            self.cursor = self.previous_cursor

            for m in self.menu:
                self.buff.append(m.find('Title').text)

            self.refresh()
        except AttributeError:
            msg('[Debug] Aucun menu parent pour {}'.format(self.menu.tag), self.args)

    def refresh(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.

        image = Image.new('1', (self.disp.width, self.disp.height))
        draw = ImageDraw.Draw(image)

        i = 0
        for l in range(self.cursor, len(self.buff)):
            if i < self.maxlines:
                if i == 0:
                    draw.text((0, 10*i), u'> {}'.format(self.buff[l]), font=self.font, fill=255)
                else:
                    draw.text((0, 10*i), unicode(self.buff[l]), font=self.font, fill=255)
                i += 1

        # Display image.
        self.disp.image(image)
        self.disp.display()

    def show(self, message):
        if message.__class__ != unicode:
            message = message.decode('utf-8')
        msg(u'[Debug] message = {}'.format(message), self.args)
        words = message.split()

        split_msg = [u'']
        current_line = 0
        line_width = 0
        space_width = self.font.getsize(' ')[0]

        # Pour chaque mot du message...
        for word in words:
            word_width = self.font.getsize(word)[0]

            # Si le mot entre dans la ligne actuelle...
            if line_width + word_width <= self.disp.width:
                split_msg[current_line] += word
                line_width += word_width

            # Sinon, si le mot n'entre pas dans un ligne vide...
            elif word_width > self.disp.width:
                current_line += 1
                split_msg.append(u'')
                line_width = 0

                # Pour chaque caractère du mot...
                for car in word:
                    car_width = self.font.getsize(car)[0]

                    # Si le caractère entre dans la ligne actuelle...
                    if line_width + car_width <= self.disp.width:
                        split_msg[current_line] += car
                        line_width += car_width

                    # Si le caractère n'entre pas dans la ligne actuelle...
                    else:
                        current_line +=1
                        split_msg.append(u'')
                        split_msg[current_line] += car
                        line_width = car_width

            # Si le mot entre dans une nouvelle ligne vide...
            else:
                current_line += 1
                split_msg.append(u'')
                split_msg[current_line] += word
                line_width = word_width

            # Ajoute un espace après chaque mot.
            if line_width + space_width <= self.disp.width:
                split_msg[current_line] += u' '
                line_width += space_width

        menu = list()

        for line in split_msg:
            menu.append((u'line' + unicode(split_msg.index(line)), line, None, None))

        return menu

    def scroll_down(self):
        if self.cursor < len(self.buff) - 1:
            self.cursor += 1
            self.refresh()
        else:
            self.cursor = 0
            self.refresh()

    def scroll_up(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.refresh()
        else:
            self.cursor = len(self.buff) - 1
            self.refresh()

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

    phone = Phone(args)
    phone.init_menu()

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

            phone.fona.update_status()

        # S'exécute toutes les 100ms
        if count_100ms == 100:
            count_100ms = 0

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()
                if key == '1':
                    pass
                elif key == '2':
                    phone.scroll_up()
                elif key == '3':
                    pass
                elif key == '4':
                    phone.go_parent()
                elif key == '5':
                    phone.go_child()
                elif key == '6':
                    phone.go_child()
                elif key == '7':
                    pass
                elif key == '8':
                    phone.scroll_down()
                elif key == '9':
                    pass
                elif key == '0':
                    pass
                elif key == '*':
                    phone.keypad_sub.terminate()
                    phone.fona.turn_off()
                    phone.disp.clear()
                    phone.disp.display()
                    sys.exit()
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

