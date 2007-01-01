#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  phone.py

import argparse, logging, sys, time, re
from multiprocessing import Process, Pipe
import subprocess as sub
from datetime import datetime
from textwrap import wrap
from time import sleep

from PIL import Image, ImageDraw, ImageFont
import keys
from fona import Fona
from SSD1306 import SSD1306
from ablib import Pin

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
    def __init__(self,
                 args=None,
                 menufile="ressources/menu.xml",
                 ):

        self.args = args

        # Initialisation des boutons
        self.but_ok = Pin("J4.34", "INPUT")
        self.but_esc = Pin("J4.36", "INPUT")
#        self.but_g25 = Pin("PC17", "INPUT")

        # Initialisation du OLED
        self.disp = SSD1306(rst="J4.12", dc="J4.14", cs="J4.11")
        self.disp.begin()
        self.clear_display()
        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.image)

        # Initialisation du menu
        self.maxlines = 6
        self.menufile = menufile

        # Initialisation du clavier
        self.keypad_parent_conn, self.keypad_child_conn = Pipe()
        self.keypad_sub = Process(target=keys.loop, args=(self.keypad_child_conn, ))
        self.keypad_sub.start()

        # Initialisation du Fona
        self.fona = Fona(self.args)
        self.font = ImageFont.truetype('ressources/Minecraftia-Regular.ttf', 8)

        # Initialisation de la barre des tâches
        self.tskbr_size = 128, 6 
        self.tskbr_padding = 2

        self.tskbr_batt = True
        self.tskbr_date = True
        self.tskbr_time = True
        self.tskbr_wifi = True
        self.tskbr_fona = True
        self.tskbr_message = True
        self.tskbr_call = True

    # Général
    #=========

    def clear_display(self):
        self.disp.clear()
        self.disp.display()

    def clear_image(self):
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)

    def popup(self, message, padding=3, text_width=24):

        width, height = self.image.size

        message = wrap(message, width=text_width)

        largest = 0
        highest = 0
        for l in message:
            w = self.font.getsize(l)
            if w[0] > largest:
                largest = w[0]
            if w[1] > highest:
                highest = w[1]

        self.draw.rectangle(((width - largest)/2 - padding,
                             (height - len(message)*highest)/2 - padding,
                             (width + largest)/2 + padding,
                             (height + len(message)*highest)/2 + padding,
                             ),
                            outline=255,
                            fill=0)

        line = 0
        for l in message:
            self.draw.text(((width - largest)/2,
                            (height - len(message)*highest)/2 + line*highest,
                            ),
                           l,
                           font=self.font,
                           fill=255)
            line += 1

        self.disp.image(self.image)
        self.disp.display()

    # Actions (items Exec dans le menu)
    #===================================

    def shutdown(self):
        self.keypad_sub.terminate()
        self.fona.turn_off()
        self.clear_display()
        sys.exit()

    def shell(self, command):
        output = sub.check_output(command, shell=True)
        self.popup(output)
        sleep(3)
        self.refresh()

    # Accueil
    #=========

    def home(self):
        self.clear_image()

        # Indique la date / heure en haut à gauche
        date = datetime.strftime(datetime.now(), "%y-%m-%d %H:%M:%S")
        self.draw.text((0, 0), date, font=self.font, fill=255)

        # Affiche la barre des tâches
        self.image.paste(self.get_tskbr_image(), (0, self.image.size[1] - self.tskbr_size[1]))

        # Display image.
        self.disp.image(self.image)
        self.disp.display()

    # Menus
    #=======

    def init_menu(self):
        # Initialise le menu
        self.tree = etree.parse(self.menufile)
        self.menu = self.tree.getroot()
        self.buff = list()
        self.cursor = 0
        self.previous_cursor = 0

        for m in self.menu:
            self.buff.append(m.find('Title').text)

#        self.refresh()

    # Cette fonction crée des sous-menus à partir d'une liste de tuples bâtie ainsi :
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
            eval(u'self.{}'.format(self.menu[self.cursor].find('Exec').text))

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
        self.clear_image()

        i = 0
        for l in range(self.cursor, len(self.buff)):
            if i < self.maxlines:
                self.draw.text((0, 10*i), unicode(self.buff[l]), font=self.font, fill=255)
#                if i == 0:
#                    draw.text((0, 10*i), u'> {}'.format(self.buff[l]), font=self.font, fill=255)
#                else:
#                    draw.text((0, 10*i), unicode(self.buff[l]), font=self.font, fill=255)
                i += 1

        # Display image.
        self.disp.image(self.image)
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

    # Barre de notification
    #=======================

    def draw_batt(self, image, offset=0):
        batt_size = 13, 6
        draw = ImageDraw.Draw(image)
        width, height = image.size

        width -= offset
        offset += batt_size[0] + self.tskbr_padding

        charge = float(re.search(u"CBC: 0,([0-9]{2,3}),[0-9]?", self.fona.get_battery()).group(1))/100

        # Enveloppe batterie
        draw.rectangle((width - (batt_size[0] - 1), 0, width - 1, batt_size[1] - 1),
                       outline=255,
                       fill=0)

        draw.rectangle((width-batt_size[0], 1, width-batt_size[0], batt_size[1] - 2),
                       outline=255,
                       fill=0)

        # Niveau de charge
        draw.rectangle((width-(batt_size[0] - 2), 1, width-(batt_size[0] - 2) + charge*(batt_size[0] - 3), batt_size[1] - 2),
                       outline=255,
                       fill=255)

        return image, offset

    def get_date(self):
        return datetime.strftime(datetime.now(), "%y%m%d")

    def get_time(self):
        return datetime.strftime(datetime.now(), "%H:%M")

    def draw_wifi(self, image, offset=0):
        icon_size = 9, 6
        draw = ImageDraw.Draw(image)
        width, height = image.size

        width -= offset
        offset += icon_size[0] + self.tskbr_padding

        try:
            # 2 = Connected
            if sub.check_output("iwconfig wlan0 | grep ESSID", shell=True):
                status = 2
            # 1 = On
            else:
                status = 1
        # 0 = Off
        except sub.CalledProcessError:
            status = 0

        p = [(4, 5),
             ((4, 5), (2, 4), (3, 3), (4, 3), (5, 3), (6, 4)),
             ((4, 5), (2, 4), (3, 3), (4, 3), (5, 3), (6, 4), (0, 2), (1, 1), (2, 1), (3, 0), (4, 0), (5, 0), (6, 1), (7, 1), (8, 2)),
             ]

        # Décalage des points
        points = tuple(map(lambda x: (width - icon_size[0] + x[0], x[1]), p[status]))

        draw.point(points, fill=255)

        return image, offset

    def draw_fona(self, image, offset=0, status=2): # Corriger status
        icon_size = 8, 6
        draw = ImageDraw.Draw(image)
        width, height = image.size

        width -= offset
        offset += icon_size[0] + self.tskbr_padding

        # 2 = Connected
        if self.fona.network_status.get():
            status = 2
        # 1 = On
        elif self.fona.power_status.get():
            status = 1
        # 0 = Off
        else:
            status = 0

        rect = (width - icon_size[0], 4, width - icon_size[0] + 1, 5)
        draw.rectangle(rect, outline=255, fill=0)

        if status > 0:
            rect = (width - icon_size[0] + 3, 2, width - icon_size[0] + 4, 5)
            draw.rectangle(rect, outline=255, fill=0)

            if status > 1:
                rect = (width - icon_size[0] + 6, 0, width - icon_size[0] + 7, 5)
                draw.rectangle(rect, outline=255, fill=0)

        return image, offset

    def draw_message(self, image, offset=0):

        status = self.fona.new_sms()

        if not status:
            return image, offset

        icon_size = 10, 6
        draw = ImageDraw.Draw(image)
        width, height = image.size

        width -= offset
        offset += icon_size[0] + self.tskbr_padding

        lines = ((width - icon_size[0] + 0, 0, width - icon_size[0] + 9, 0),
                 (width - icon_size[0] + 2, 1, width - icon_size[0] + 7, 1),
                 (width - icon_size[0] + 4, 2, width - icon_size[0] + 5, 2),
                 (width - icon_size[0] + 0, 2, width - icon_size[0] + 1, 2),
                 (width - icon_size[0] + 8, 2, width - icon_size[0] + 9, 2),
                 (width - icon_size[0] + 0, 3, width - icon_size[0] + 3, 3),
                 (width - icon_size[0] + 6, 3, width - icon_size[0] + 9, 3),
                 (width - icon_size[0] + 0, 4, width - icon_size[0] + 9, 4),
                 (width - icon_size[0] + 0, 5, width - icon_size[0] + 9, 5),
                 )

        for l in lines:
            draw.line(l, fill=255)

        return image, offset

    def draw_call(self, image, offset=0):

        status = self.fona.ring.get()

        if not status:
            return image, offset

        icon_size = 14, 6
        draw = ImageDraw.Draw(image)
        width, height = image.size

        width -= offset
        offset += icon_size[0] + self.tskbr_padding

        lines = ((width - icon_size[0] + 4, 0, width - icon_size[0] + 9, 0),
                 (width - icon_size[0] + 2, 1, width - icon_size[0] + 11, 1),
                 (width - icon_size[0] + 1, 2, width - icon_size[0] + 12, 2),
                 (width - icon_size[0] + 0, 3, width - icon_size[0] + 3, 3),
                 (width - icon_size[0] + 10, 3, width - icon_size[0] + 13, 3),
                 (width - icon_size[0] + 0, 4, width - icon_size[0] + 3, 4),
                 (width - icon_size[0] + 10, 4, width - icon_size[0] + 13, 4),
                 (width - icon_size[0] + 0, 5, width - icon_size[0] + 3, 5),
                 (width - icon_size[0] + 10, 5, width - icon_size[0] + 13, 5),
                 )

        for l in lines:
            draw.line(l, fill=255)

        return image, offset

    def get_tskbr_image(self):
        image = Image.new('1', (self.tskbr_size[0], self.tskbr_size[1]))

        offset = 0

        if self.tskbr_batt:
            image, offset = self.draw_batt(image, offset)
        if self.tskbr_wifi:
            image, offset = self.draw_wifi(image, offset)
        if self.tskbr_fona:
            image, offset = self.draw_fona(image, offset)
        if self.tskbr_message:
            image, offset = self.draw_message(image, offset)
        if self.tskbr_call:
            image, offset = self.draw_call(image, offset)

        return image

