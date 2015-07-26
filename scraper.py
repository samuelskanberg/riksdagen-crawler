from lxml import html
import requests

# Socialdemokraterna
page = requests.get('http://www.riksdagen.se/sv/ledamoter-partier/Socialdemokraterna/Ledamoter/')
tree = html.fromstring(page.text)


names = tree.xpath('//section//dl/dt/a/text()')

print 'names: '
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

