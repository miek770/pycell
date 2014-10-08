# Projet de téléphone portable

## Sommaire

L'idée est de faire un téléphone portable (cellulaire) avec un système Linux complet (incluant un gestionnaire de paquets) et les fonctionalités cellulaires essentielles.

Problème : J'ai oublié de commander un régulateur de tension step-up dc-dc pour monter à 5V (requis par le Arietta G25). Par contre j'ai lu sur internet qu'on peut l'alimenter a 3.3V (meme le module Wifi) en enlevant une petite résistance pour désactiver le régulateur. Ça vaut la peine d'essayer!

### 2014-10-07 22:05

Je suis en train de développer le générateur pour les SMS, mais ce n'est pas fini. Par contre je crois que ma méthode d'extraction de l'information va fonctionner quel que soit le contenu du message texte, sauf naturellement si celui-ci contient la chaîne de contrôle. Ça ne me semble pas être un problème très plausible étant donné l'état de prototype, mais c'est clair qu'à grande échelle ça ne serait pas sécuritaire...

Je me demande si l'heure retournée par le message texte est en format 24h ou en format 12h.

Je ne crois pas qu'il soit pertinent de sauvegarder les messages dans une base de données. Je ne risque pas de faire beaucoup de manipulation et vais peut-être donc les conserver dans la carte SIM jusqu'à ce que le développement soit plus avancé.

## Matériel envisagé

### Ordinateur

- [Atmel Arietta G25](http://www.acmesystems.it/arietta)
- [WIFI-2-IA](http://www.acmesystems.it/WIFI-2)
- Carte µSD 32Go

### Module GSM/GPRS

- [Adafruit FONA - Mini Cellular GSM Breakout uFL Version](http://www.adafruit.com/products/1946)
- [Slim Sticker-type GSM/Cellular Quad-Band Antenna - 3dBi uFL](http://www.adafruit.com/products/1991)
- Carte SIM Rogers

### Périphériques
- [Electret Microphone - 20Hz-20KHz Omnidirectional](https://www.adafruit.com/product/1064)
- [Mini Metal Speaker w/ Wires - 8 ohm 0.5W](https://www.adafruit.com/product/1890)
- [Monochrome 1.3" 128x64 OLED graphic display](http://www.adafruit.com/products/938)
- [Membrane 3x4 Matrix Keypad + extras](http://www.adafruit.com/products/419)
- [Vibrating Mini Motor Disc](https://www.adafruit.com/product/1201)
- [Lithium Ion Polymer Battery - 3.7v 500mAh](http://www.adafruit.com/products/1578)

## Réseaux utilisables

- [Rogers (incluant Fido)](http://en.wikipedia.org/wiki/List_of_mobile_network_operators_of_the_Americas#Canada)

