#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from lxml import html
import requests
import csv, codecs, cStringIO
import sys


class Person:
    def __init__(self, party, name, email):
        self.party = party
        self.name = name
        self.email = email

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# For some very weird reason, party can contain utf-8 characters. But last_name can. Weird
party_pages = {
    'Socialdemokraterna': 'http://www.riksdagen.se/sv/ledamoter-partier/Socialdemokraterna/Ledamoter/', 
    'Moderaterna': 'http://www.riksdagen.se/sv/ledamoter-partier/Moderata-samlingspartiet/Ledamoter/', 
    'Sverigedemokraterna': 'http://www.riksdagen.se/sv/ledamoter-partier/Sverigedemokraterna/Ledamoter/',
    'Miljopartiet': 'http://www.riksdagen.se/sv/ledamoter-partier/Miljopartiet-de-grona/Ledamoter/',
    'Centerpartiet': 'http://www.riksdagen.se/sv/ledamoter-partier/Centerpartiet/Ledamoter/',
    'Vansterpartiet': 'http://www.riksdagen.se/sv/ledamoter-partier/Vansterpartiet/Ledamoter/',
    'Liberalerna': 'http://www.riksdagen.se/sv/ledamoter-partier/Folkpartiet/Ledamoter/',
    'Kristdemokraterna': 'http://www.riksdagen.se/sv/ledamoter-partier/Kristdemokraterna/Ledamoter/',
}

if __name__ == "__main__":
    all_people = []
    for party, party_page in party_pages.iteritems():

        page = requests.get(party_page)
        tree = html.fromstring(page.text)

        # Only include "ledamöter", not "partisekreterare" and such since they don't have emails
        names = tree.xpath("//*[contains(@class, 'large-12 columns alphabetical component-fellows-list')]//a[contains(@class, 'fellow-item-container')]/@href")
        root = "http://www.riksdagen.se"
        unique_name_list = []
        for name in names:
            full_url = root + name
            if full_url not in unique_name_list:
                unique_name_list.append(full_url)

        print unique_name_list
        print "unique:"
        for name_url in unique_name_list:
            print name_url
            personal_page = requests.get(name_url)

            personal_tree = html.fromstring(personal_page.text)
            email_list = personal_tree.xpath("//*[contains(@class, 'scrambled-email')]/text()")
            email_scrambled = email_list[0]
            email = email_scrambled.replace(u'[på]', '@')
            print email

            name_list = personal_tree.xpath("//header/h1[contains(@class, 'biggest fellow-name')]/text()")
            name = name_list[0]
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            name = name[:name.find("(")-1]
            name = name.strip()
            print name
            print "-----"
            person = Person(party, name, email)
            all_people.append(person)


    for person in all_people:
        print person.party + ", " + person.name + ", " + person.email

    with open('names.csv', 'wb') as csvfile:
        fieldnames = ['name', 'email', 'party']
        writer = UnicodeWriter(csvfile)
        writer.writerow(fieldnames)

        for person in all_people:
            print person.party + ", " + person.name + ", " + person.email
            writer.writerow([person.name, person.email, person.party])

