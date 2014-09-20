# Projet de telephone portable

## Sommaire

L'idee est de faire un telephone portable (cellulaire) avec un systeme Linux complet (incluant un gestionnaire de paquets) et les fonctionalites cellulaires essentielles.

Problème : J'ai oublié de commander un régulateur de tension step-up dc-dc pour monter à 5V (requis par le Arietta G25). Par contre j'ai lu sur internet qu'on peut l'alimenter a 3.3V (meme le module Wifi) en enlevant une petite resistance pour desactiver le regulateur. Ca vaut la peine d'essayer!

Probleme : J'ai beaucoup de misere a faire fonctionner le OLED. Apres avoir teste chaque pin avec l'oscilloscope, et verifie toutes les continuites des pins, je commence a croire que le probleme est un defaut du OLED. J'ai demande de l'aide sur le forum d'Adafruit.

## Materiel envisage

### Ordinateur

- [Atmel Arietta G25](http://www.acmesystems.it/arietta)
- [WIFI-2-IA](http://www.acmesystems.it/WIFI-2)
- Carte µSD 32Go

### Module GSM/GPRS

- [Adafruit FONA - Mini Cellular GSM Breakout uFL Version](http://www.adafruit.com/products/1946)
- [Slim Sticker-type GSM/Cellular Quad-Band Antenna - 3dBi uFL](http://www.adafruit.com/products/1991)
- Carte SIM Rogers

### Peripheriques
- [Electret Microphone - 20Hz-20KHz Omnidirectional](https://www.adafruit.com/product/1064)
- [Mini Metal Speaker w/ Wires - 8 ohm 0.5W](https://www.adafruit.com/product/1890)
- [Monochrome 1.3" 128x64 OLED graphic display](http://www.adafruit.com/products/938)
- [Membrane 3x4 Matrix Keypad + extras](http://www.adafruit.com/products/419)
- [Vibrating Mini Motor Disc](https://www.adafruit.com/product/1201)
- [Lithium Ion Polymer Battery - 3.7v 500mAh](http://www.adafruit.com/products/1578)

## Reseaux utilisables

- [Rogers (incluant Fido)](http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Americas#Canada)

