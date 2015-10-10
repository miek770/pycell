#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging, csv
from cPickle import *

class AddressBook:
    """Carnet d'adresse pour le projet pycell. Importe les contacts d'un fichier
    CSV généré par Google en format UTF-8 (pour être compatible avec Outlook).
    """

    def __init__(self, data_file="contacts.pkl"):
        self.contacts = list()
        self.data_file = data_file
        self.retreive()

    def retreive(self):
        try:
            with open(self.data_file, "rb") as f:
                try:
                    self.contacts = load(f)
                except EOFError:
                    logging.error("Fichier vide : {}".format(self.data_file))

        except IOError as e:
            logging.info("Échec d'ouverture de {} : {}".format(self.data_file, e))

    def save(self):
        if len(self.contacts):
            try:
                with open(self.data_file, "w") as f:
                    try:
                        dump(self.contacts, f)
                    except TypeError as e:
                        logging.error("Échec d'écriture dans {} : {}".format(self.data_file, e))

            except IOError as e:
                logging.error("Échec d'ouverture de {} : {}".format(self.data_file, e))

    def import_from_csv(self, csvfile):

        tags = list()
        contacts = list()

        try:
            with open(csvfile, "rb") as f:
                reader = csv.reader(f, delimiter=",", quotechar='"')

                first_line = True
                for row in reader:
                    if first_line:
                        header = row
                        first_line = False
                        tags.append(("First Name", header.index("First Name")))
                        tags.append(("Last Name", header.index("Last Name")))
                        tags.append(("Primary Phone", header.index("Primary Phone")))
                        tags.append(("Home Phone", header.index("Home Phone")))
                        tags.append(("Mobile Phone", header.index("Mobile Phone")))
                        tags.append(("Home Phone 2", header.index("Home Phone 2")))
                        tags.append(("Pager", header.index("Pager")))
                        tags.append(("Company Main Phone", header.index("Company Main Phone")))
                        tags.append(("Business Phone", header.index("Business Phone")))
                        tags.append(("Business Phone 2", header.index("Business Phone 2")))
                        tags.append(("Assistant's Phone", header.index("Assistant's Phone")))
                        tags.append(("Other Phone", header.index("Other Phone")))
                        tags.append(("Car Phone", header.index("Car Phone")))

                    else:
                        contact = dict()
                        for tag in tags:
                            contact[tag[0]] = row[tag[1]]
                        contacts.append(contact)

            return contacts

        except IOError as e:
            logging.error("Échec d'ouverture de {} : {}".format(csvfile, e))

    def merge_contacts(self, csvfile):
        contacts = self.import_from_csv(csvfile)

        for new in contacts:
            if new["First Name"] != "" and new["Last Name"] != "":
                match = False

                for old in self.contacts:
                    if new["First Name"] == old["First Name"] and new["Last Name"] == old["Last Name"]:
                        #logging.debug("Nouveau contact déjà présent, à fusionner : {} {}".format(new["First Name"], new["Last Name"]))
                        match = True

                        for key in new.keys():
                            if new[key] != "" and new[key] != old[key]:
                                logging.debug("Mise à jour du champ {} pour {} {} : {}".format(key, new["First Name"], new["Last Name"], new[key]))
                                old[key] = new[key]

                if not match:
                    logging.debug("Nouveau contact : {} {}".format(new["First Name"], new["Last Name"]))
                    self.contacts.append(new)

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Logger configuré")

    a = AddressBook()
    a.merge_contacts("outlook.csv")
    a.save()

    for c in a.contacts:
        print "{} {} :".format(c["First Name"], c["Last Name"])
        for

if __name__ == "__main__":
    main()
