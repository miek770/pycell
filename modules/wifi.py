#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, logging
import subprocess as sub

re_connected = re.compile(r'ESSID:"(.*)"')
re_disconnected = re.compile(r'ESSID:off/any')
re_quality = re.compile(r'Link Quality=([0-9]{1,2})/70')
re_signal = re.compile(r'Signal level=(-{0,1}[0-9]{1,2}) dBm')

class Wifi:

    def __init__(self, iface="wlan0"):
        self.iface = iface
        self.essid = None
        self.quality = None
        self.signal = None
        self.on = True

    def get_status(self):
        """Vérifie l'état de l'interface et mets les variables internes
        à jour, mais ne retourne rien directement.
        """

        # L'interface est désactivée
        with open("/sys/class/net/{}/operstate".format(self.iface), "r") as f:
            if f.read() == "down\n":
                logging.debug("{} désactivée.".format(self.iface))
                self.on = False
                return

        try:
            status = sub.check_output(("iwconfig", self.iface))

        except sub.CalledProcessError:
            status = None

        # L'interface est déconnectée
        if re_disconnected.search(status):
            logging.debug("{} déconnecté.".format(self.iface))
            self.essid = None
            self.quality = None
            self.signal = None
            self.on = True

        # L'interface est connectée
        else:
            m = re_connected.search(status)
            logging.debug("{} connecté.".format(self.iface))
            self.essid = m.group(1)
            self.on = True

            m = re_quality.search(status)
            if m:
                self.quality = int(m.group(1))
            else:
                self.quality = 0

#            m = re_signal.search(status)
#            if m:
#                self.signal = int(m.group(1))
#            else:
#                self.signal = 0

           
# Sample output (connected / disconnected / off)

# wlan0     IEEE 802.11abgn  ESSID:"Michel et Sophie"  
#           Mode:Managed  Frequency:2.412 GHz  Access Point: 00:14:D1:9C:DC:28   
#           Bit Rate=1 Mb/s   Tx-Power=20 dBm   
#           Retry  long limit:7   RTS thr:off   Fragment thr:off
#           Power Management:on
#           Link Quality=70/70  Signal level=-39 dBm  
#           Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
#           Tx excessive retries:22  Invalid misc:382   Missed beacon:0

# wlan0     IEEE 802.11abgn  ESSID:off/any  
#           Mode:Managed  Access Point: Not-Associated   Tx-Power=20 dBm   
#           Retry  long limit:7   RTS thr:off   Fragment thr:off
#           Power Management:on

# wlan0     IEEE 802.11bgn  ESSID:off/any
#           Mode:Managed  Access Point: Not-Associated   Tx-Power=20 dBm
#           Retry short limit:7   RTS thr:off   Fragment thr:off
#           Encryption key:off
#           Power Management:off
                                        
if __name__ == '__main__':

    w = Wifi()
    w.get_status()

    print w.essid
    print w.quality
    print w.signal

