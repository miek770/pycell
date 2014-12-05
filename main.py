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
from modules.phone import Phone
from lxml import etree

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

    modes = (# Général
             (0, "Veille"),
             (1, "Accueil"),
             (2, "Menu"),
             # Téléphonie
             (10, "Appel en cours"),
             (11, "Composition"),
             (12, "Appel entrant"),
             )

    mode = 1 # Accueil
    phone.home()

    delai_veille = 10000 # En ms 
    count_delai = 0
    delai = True

    while True:

        # S'exécute toutes les 10ms
        if count_10ms >= 10:
            count_10ms = 0

        # S'exécute toutes les 100ms
        if count_100ms >= 100:
            count_100ms = 0

            if mode == 0: # Veille

                if not phone.but_esc.get() or not phone.but_ok.get():
                    msg("[Debug] Passage au mode 1 (Accueil).", args)
                    mode = 1 # Accueil
                    phone.home()
                    delai = True
                    count_delai = 0
                    delai_veille = 5000

                elif phone.fona.ring.get():
                    #msg("[Debug] Passage au mode 12 (appel entrant)", args)
                    pass

            elif mode == 1: # Accueil

                if not phone.but_esc.get():
                    msg("[Debug] Passage au mode 0 (Veille).", args)
                    mode = 0 # Veille
                    phone.clear_display()
                    delai = False

                elif not phone.but_ok.get():
                    msg("[Debug] Passage au mode 2 (Menu).", args)
                    mode = 2 # Menu
                    phone.refresh()
                    count_delai = 0
                    delai_veille = 10000

                elif phone.keypad_parent_conn.poll():
                    key = phone.keypad_parent_conn.recv()

                    if key in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                        msg("[Debug] Passage au mode 11 (composition).", args)

                    elif key in ('*', '#'):
                        msg("[Debug] Passage au mode 2 (Menu).", args)
                        mode = 2 # Menu
                        phone.refresh()
                        count_delai = 0
                        delai_veille = 10000

            elif mode == 2: # Menu

                if not phone.but_esc.get():
                    msg("[Debug] Passage au mode 1 (Accueil).", args)
                    mode = 1 # Accueil
                    phone.home()
                    delai = True
                    count_delai = 0
                    delai_veille = 5000

                elif not phone.but_ok.get():
                    phone.go_child()

                elif phone.keypad_parent_conn.poll():
                    key = phone.keypad_parent_conn.recv()

                    if key == '2':
                        phone.scroll_up()
                    elif key == '4':
                        phone.go_parent()
                    elif key == '5':
                        phone.go_child()
                    elif key == '6':
                        phone.go_child()
                    elif key == '8':
                        phone.scroll_down()
 
        # S'exécute toutes les 1s
        if count_1000ms >= 1000:
            count_1000ms = 0

        # S'exécute après delai
        if delai and count_delai >= delai_veille:
            count_delai = 0

            if mode == 1: # Accueil
                msg("[Debug] Passage au mode 0 (Veille).", args)
                delai = False
                mode = 0 # Veille
                phone.clear_display()

            elif mode == 2: # Accueil
                msg("[Debug] Passage au mode 1 (Accueil).", args)
                mode = 1 # Accueil
                phone.home()
                delai_veille = 5000

            else:
                delai = False

        count_10ms += 10
        count_100ms += 10
        count_1000ms += 10

        if delai:
            count_delai += 10

        time.sleep(0.01)

    return 0

if __name__ == '__main__':
    main()

