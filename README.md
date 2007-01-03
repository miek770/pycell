# Projet de téléphone portable

## Sommaire

L'idée est de faire un téléphone portable (cellulaire) avec un système Linux complet (incluant un gestionnaire de paquets) et les fonctionalités cellulaires essentielles.

### 2014-11-14 12:57

J'ai posé une question sur le Google Group par rapport au SPI, il n'apparaît pas dans /dev et ça semble être une erreur du côté de Acme Systems.

Ce site indique comment contrôler le bouton P1 sur le Arietta G25 : [Arietta on-board button](http://www.acmesystems.it/arietta_p1_button). Je pourrais faire des tests avec ce bouton et le raccorder sur inotify pour générer des interrupts. Ça va être très pratique pour l'utilisation normale du téléphone (mise en veille / réveil).

### 2014-10-08 20:01

J'ai des problèmes avec l'encodage du texte lu du Fona (pour messages textes). L'arbre XML ne l'accepte pas, mais je ne parviens pas à le décoder ou à l'encoder correctement. Il va falloir que je fasse quelques recherches.

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

