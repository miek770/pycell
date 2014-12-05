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

import argparse, logging, sys, time, re
from multiprocessing import Process, Pipe
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from modules import keys
from modules.fona import Fona
from modules.SSD1306 import SSD1306
from modules.phone import Phone

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
                    phone.shutdown()

                elif key == '#':
                    phone.home()
                    time.sleep(2)
                    phone.refresh()
 
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

