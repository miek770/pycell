#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import subprocess as sub
from msg import msg

re_connected = re.compile(r'ESSID:"(.*)"')
re_disconnected = re.compile(r'ESSID:off/any')
re_quality = re.compile(r'Link Quality=([0-9]{1,2})/70')
re_signal = re.compile(r'Signal level=(-{0,1}[0-9]{1,2}) dBm')

class Wifi:
    def __init__(self, args=None, iface="wlan0"):
        self.args = args
        self.iface = iface
        self.essid = None
        self.quality = None
        self.signal = None

    def get_status(self):
        status = sub.check_output(("iwconfig", self.iface))
        m = re_connected.search(status)
        if m:
            self.essid = m.group(1)
            self.quality = int(re_quality.search(status).group(1))
            self.signal = int(re_signal.search(status).group(1))

        elif re_disconnected.search(status):
            self.essid = None
            self.quality = None
            self.signal = None

        else:
            msg("[Erreur] État wifi non-reconnu.", self.args)
            
# Sample output (connected / disconnected)

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

if __name__ == '__main__':

    w = Wifi()
    w.get_status()

    print w.essid
    print w.quality
    print w.signal

