# Projet de téléphone portable

## Sommaire

L'idée est de faire un téléphone portable (cellulaire) avec un système Linux complet (incluant un gestionnaire de paquets) et les fonctionalités cellulaires essentielles.

- corriger les pins dans le circuit et le dts (un seul UART, un CS0);
- Corriger le statut réseau (la pin est liée à la fréquence de la LED);
- Créer un mode avion avec son icône;
- Investiguer le comportement du signal RING;
- Remplacer init par systemd;
- Ajouter la synchronisation des contacts, courriels et événements;
- L'application devrait arrêter et redémarrer le système au complet;
- Tester / rechercher la veille sur WKUP;
- Intégrer les codes d'erreur du FONA dans le module fona.py.

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
