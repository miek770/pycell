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
from time import sleep
from multiprocessing import Process, Pipe
#from random import randint
from modules.pins import *

power_key = 'P9_12'
power_status = 'P9_15'
network_status = 'P9_23'
ring = 'P9_27'

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

        # S'exécute toutes les 1s
        if count_1000ms == 1000:
            count_1000ms = 0

        count_10ms += 1
        count_100ms += 1
        count_1000ms += 1
        sleep(0.001)

    return 0

if __name__ == '__main__':
    main()
