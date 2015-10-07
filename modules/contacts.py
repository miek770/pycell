#!/usr/bin/python
# -*- coding: utf-8 -*-

from cPickle import *
import logging

class AddressBook:

    def __init__(self, data_file="contacts.pkl"):
        self.data_file = data_file
        self.retreive_data()

    def retreive_data(self):
        try:
            with open(self.data_file, 'r') as fichier:
                try:
                    self.contacts = load(fichier)
                except UnpicklingError as e:
                    logging.error("Échec de récupération du carnet d'adresse : {}".format(e.strerror))

        except IOError as e:
            logging.info("Échec de l'ouverture de {} : {}".format(self.data_file, e.strerror))
            self.contacts = dict()

    def save_data(self):
        try:
            with open(self.data_file, 'w') as fichier:
                try:
                    dump(self.contacts, fichier)
                except PicklingError as e:
                    logging.error("Échec de sauvegarde du carnet d'adresse : {}".format(e.strerror))

        except IOError as e:
            logging.error("Échec de l'ouverture de {} : {}".format(self.data_file, e.strerror))

    def new_contact(self, firstname, lastname, mobile_number=None, home_number=None, work_number=None, main=0):
        try:
            firstname = unicode(firstname)
            lastname = unicode(lastname)
            c = Contact(firstname, lastname, mobile_number, home_number, work_number, main)
            self.contacts["{} {}".format(firstname, lastname)] = c
            logging.debug("Nouveau contact créé : {}".format(c.get_name()))

        except UnicodeDecodeError as e:
            logging.error("Contact entré en format non-unicode : {} {}".format(firstname, lastname))

    def get_contact(self, name):
        return self.contacts[name]

class Contact:

    # Main : 0=mobile, 1=home, 2=work
    def __init__(self, firstname, lastname, mobile_number=None, home_number=None, work_number=None, main=0):
        try:
            self.firstname = unicode(firstname)
            self.lastname = unicode(lastname)

        except UnicodeDecodeError as e:
            logging.error("Contact entré en format non-unicode : {} {}".format(firstname, lastname))

        self.mobile_number = int(mobile_number)
        self.home_number = int(home_number)
        self.work_number = int(work_number)
        self.main = main

    def get_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def get_number(self, which=None):
        if which is None:
            which = self.main

        if which == 0:
            return self.mobile_number
        elif which == 1:
            return self.home_number
        elif which == 2:
            return self.work_number
        else:
            return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    a = AddressBook()
    a.new_contact(u"Michel", u"Lavoie", 15819951258, 14183532092, 14188713414, 0)

    logging.debug("Contacts : {}".format(a.contacts))

    logging.debug(a.get_contact(u"Michel Lavoie").get_number())

