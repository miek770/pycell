#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  main.py
#
#  Copyright 2015 Michel Lavoie <lavoie.michel@gmail.com>
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
import subprocess as sub

KEYS_FAST = 0.05
KEYS_SLOW = 0.5

def main():
    """Routine principale du Pycell. Les arguments sont traités, le journal est
    initié, les sous-routines sont lancées et la boucle principale est
    exécutée.

    C'est dans cette boucle que les modes sont contrôlés (ex.: composition,
    appel en cours, menus).
    """

    parser = argparse.ArgumentParser(description='PyCell')

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help="Imprime l'aide sur l'exécution du script.")
    
    parser.add_argument('-l',
                        '--logfile',
                        action='store',
                        default=None,
                        help="Spécifie le chemin du journal d'événement.")

    args = parser.parse_args()

    log_frmt = '%(asctime)s[%(levelname)s] %(message)s'
    date_frmt = '%Y-%m-%d %H:%M:%S '

    if args.verbose:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.WARNING

    logging.basicConfig(filename=args.logfile, format=log_frmt, datefmt=date_frmt, level=log_lvl)
    logging.info("Logger initié : {}".format(args.logfile))

    logging.info('Programme lancé.')

    # Lancement des sous-routines
    #=============================

    phone = Phone()

    # Boucle principale
    #===================

    # J'ai créé des compteurs indépendants pour pouvoir les redémarrer à zéro
    # sans affecter les autres (pour ne pas atteindre des chiffres inutilement
    # élevés).
    count_10 = 0
    count_100 = 0

    # La période de la boucle principale équivaut à 1s divisée par le diviseur
    # ici-bas. Donc avec diviseur=100 la période est de 10ms.
    diviseur = 100

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

    delai_veille = 1000 # En ticks, 10s avec diviseur=100
    count_delai = 0
    delai = True

    # Pour la composition
    numero = ""
    dtmf_dur = 2

    while True:

        # S'exécute à chaque fois (tous les 10ms par défaut)
        if mode == 0: # Veille

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()

                if key == 'o':
                    logging.debug("Passage au mode 1 (Accueil).")
                    mode = 1 # Accueil
                    diviseur = 100
                    phone.keypad_parent_conn.send(KEYS_FAST)
                    phone.home()
                    delai = True
                    count_delai = 0

            # Vérifier si ça marche bien, si oui mettre en premier
            elif phone.fona.ring.get():
                #logging.debug("Passage au mode 12 (appel entrant)")
                pass

        elif mode == 1: # Accueil

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()

                if key == 'e':
                    logging.debug("Passage au mode 0 (Veille).")
                    mode = 0 # Veille
                    diviseur = 10
                    phone.clear_display()
                    phone.keypad_parent_conn.send(KEYS_SLOW)
                    delai = False

                elif key in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#'):
                    logging.debug("Passage au mode 11 (composition).")
                    mode = 11 # Composition
                    phone.clear_display()
                    delai = False
                    numero = key
                    phone.fona.gen_dtmf(duration=dtmf_dur, string=key)
                    phone.draw_text(numero)

                elif key in ('o', 'l', 'r', 'u', 'd'):
                    logging.debug("Passage au mode 2 (Menu).")
                    mode = 2 # Menu
                    phone.refresh_display()
                    count_delai = 0

            # Vérifier si ça marche bien, si oui mettre en premier
            elif phone.fona.ring.get():
                #logging.debug("Passage au mode 12 (appel entrant)")
                pass

        elif mode == 2: # Menu

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()

                if key == 'e':
                    logging.debug("Passage au mode 1 (Accueil).")
                    mode = 1 # Accueil
                    phone.home()
                    count_delai = 0

                elif key == 'u':
                    count_delai = 0
                    phone.scroll_up()

                elif key == 'd':
                    count_delai = 0
                    phone.scroll_down()

                elif key == 'l':
                    count_delai = 0
                    phone.go_parent()

                elif key in ('r', 'o'):
                    count_delai = 0
                    phone.go_child()

            # Vérifier si ça marche bien, si oui mettre en premier
            elif phone.fona.ring.get():
                #logging.debug("Passage au mode 12 (appel entrant)")
                pass

        elif mode == 10: # Appel en cours

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()

                if key == 'e':
                    logging.debug("Raccroche. Retour au mode 1 (Accueil).")
                    phone.fona.hang_up()
                    mode = 1 # Accueil
                    phone.home()
                    delai = True
                    count_delai = 0

        elif mode == 11: # Composition

            if phone.keypad_parent_conn.poll():
                key = phone.keypad_parent_conn.recv()

                if key == 'o':

                    if phone.fona.get_call_ready():
                        logging.debug("Passage au mode 10 (Appel en cours).")
                        phone.fona.call(numero)
                        mode = 10 # Appel en cours
                    else:
                        phone.popup("E: Pas prêt!")
                        time.sleep(3)

                elif key == 'e':
                    logging.debug("Annule l'appel. Retour au mode 1 (Accueil).")
                    mode = 1 # Accueil
                    phone.home()
                    delai = True
                    count_delai = 0

                elif key in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#'):
                    numero += key
                    phone.fona.gen_dtmf(duration=dtmf_dur, string=key)
                    phone.draw_text(numero)

                elif key == 'l':
                    numero = numero[:-1]
                    phone.draw_text(numero)

        # S'exécute toutes les 10 ticks (tous les 100ms par défaut)
        if count_10 >= 10:
            count_10 = 0

        # S'exécute tous les 100 ticks (tous les 1s par défaut)
        if count_100 >= 100:
            count_100 = 0

            # Rafraichissement de l'accueil
            if mode == 1: # Accueil
                phone.home()

            #logging.debug("Batterie : {}".format(phone.fona.get_battery()))

        # S'exécute après un certain delai
        if delai and count_delai >= delai_veille:
            count_delai = 0

            if mode == 1: # Accueil
                logging.debug("Passage au mode 0 (Veille).")
                delai = False
                mode = 0 # Veille
                diviseur = 10
                phone.clear_display()
                phone.keypad_parent_conn.send(KEYS_SLOW)

            elif mode == 2: # Menu
                logging.debug("Passage au mode 1 (Accueil).")
                mode = 1 # Accueil
                phone.home()
                count_delai = 0

            else:
                delai = False

        count_10 += 1
        count_100 += 1

        if delai:
            count_delai += 1

        time.sleep(1.0/diviseur)

    return 0

if __name__ == '__main__':

    while True:

        try:
            main()

        except KeyboardInterrupt:
            logging.info("Interruption du programme.")
            sys.exit(2)

        except:
            sub.check_call(("ifup", "wlan0"))
            print "Erreur imprévue : ", sys.exc_info()[0]
            logging.error(sys.exc_info())
            raise

