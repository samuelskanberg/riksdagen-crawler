#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from lxml import html
import requests
import csv, codecs, cStringIO

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



# Socialdemokraterna
page = requests.get('http://www.riksdagen.se/sv/ledamoter-partier/Socialdemokraterna/Ledamoter/')
tree = html.fromstring(page.text)
party = "Socialdemokraterna"


names = tree.xpath('//section//dl/dt/a/text()')

with open('names.csv', 'wb') as csvfile:
    fieldnames = ['first_name', 'last_name', 'email', 'party']
    writer = UnicodeWriter(csvfile)
    writer.writerow(fieldnames)

    for name in names:
        name = name.strip()
        print name
        last_name = name[0:name.find(",")].strip()
        first_name = name[name.find(",")+2:name.find("(", name.find(",")+1)].strip()
        print first_name + ","+last_name
         
        emails = tree.xpath('//section//dl[dt/a/text()[contains(., "'+name+'")]]/dd/noscript/text()')
        email = emails[0]
        before_at = email.find("riksdagen.se")
        
        formatted_email = email[0:before_at-4]+"@riksdagen.se"
        print formatted_email
        writer.writerow([first_name, last_name, formatted_email, party])

