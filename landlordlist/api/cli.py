import requests, click, csv, datetime

from xml.etree import ElementTree as ET
from flask import Blueprint
from sqlalchemy import exc

from landlordlist import db
from landlordlist.models import Party, Person


bp = Blueprint('ll', __name__)

# URLs
PARTIES_URL = 'http://data.parliament.uk/membersdataplatform/services/mnis/ReferenceData/Parties/'
HOC_URL     = 'http://data.parliament.uk/membersdataplatform/services/mnis/members/query/House=Commons%7CIsEligible=true/'
HOL_URL     = 'http://data.parliament.uk/membersdataplatform/services/mnis/members/query/House=Lords%7CIsEligible=true/Interests'

KEY_WORDS = [
    'rental', 'rent', 'tenant', 'tenancy', 'tenancies', 'short hold'
]


@bp.cli.command('get:parties')
def get_parties():
    # Initial loading message
    print('Loading political party data...')

    # Load data from Parliament API
    r = requests.get(PARTIES_URL)

    if r.status_code != 200:
        print('Error: Unable to get data from API. Table not updated.')
        return

    xml_raw = r.text
    print('Loaded XML...')

    parties = ET.fromstring(xml_raw)

    for party in parties:
        if party.find('IsCommons').text == 'False' and party.find('IsLords').text == 'False':
            continue

        new_party = Party(
            name=party.find('Name').text,
            colour=party.find('Colour').text,
            abbreviation=party.find('Abbreviation').text,
            pk=int(party.find('Party_Id').text)
        )

        new_party.text_color = party.find('TextColour').text

        try:
            db.session.add(new_party)
            db.session.commit()
            print(new_party)
        except exc.IntegrityError:
            db.session.rollback()


    print('Done.')


@bp.cli.command('get:hoc')
def get_commons():
    # Initial loading message
    print('Loading House of Commons member data...')

    # Load data from Parliament API
    r = requests.get(HOC_URL)

    if r.status_code != 200:
        print('Error: Unable to get data from API. Table not updated.')
        return

    xml_raw = r.text
    print('Loaded XML...')

    members = ET.fromstring(xml_raw)

    i = 0
    for m in members:
        i += 1

        id = int(m.get('Member_Id'))
        new = False

        person = Person.query.get(id)
        if person is None:
            person = Person(id)
            new = True

        person.name = m.find('DisplayAs').text
        person.list_as = m.find('ListAs').text
        person.body = m.find('House').text
        person.party_id = int(m.find('Party').get('Id'))
        person.represents = m.find('MemberFrom').text

        try:
            if new:
                db.session.add(person)

            db.session.commit()
            if i % 100 == 0:
                print(i, person)
        except exc.IntegrityError:
            db.session.rollback()
            print('Integrity Error:', id, person)


@bp.cli.command('get:hol')
def get_lords():
    # Initial loading message
    print('Loading House of Lords member data...')

    # Load data from Parliament API
    r = requests.get(HOL_URL)

    if r.status_code != 200:
        print('Error: Unable to get data from API. Table not updated.')
        return

    xml_raw = r.text
    print('Loaded XML...')

    members = ET.fromstring(xml_raw)

    y = 0
    for m in members:
        y += 1

        id = int(m.get('Member_Id'))
        new = False

        person = Person.query.get(id)
        if person is None:
            person = Person(id)
            new = True

        person.name = m.find('DisplayAs').text
        person.list_as = m.find('ListAs').text
        person.body = m.find('House').text
        person.party_id = int(m.find('Party').get('Id'))
        person.represents = m.find('MemberFrom').text

        interests = m.findall("./Interests/Category[@Id='5']/Interest")
        for i in interests:
            text = i.find('RegisteredInterest').text
            if not any(words in text for words in KEY_WORDS):
                continue

            person.is_landlord = True
            if person.expl_txt is None:
                person.expl_txt = text
            else:
                person.expl_txt = person.expl_txt + '. ' + text

        try:
            if new:
                db.session.add(person)

            db.session.commit()
            if y % 100 == 0:
                print(y, person)
        except exc.IntegrityError:
            db.session.rollback()
            print('Integrity Error:', id, person)


@bp.cli.command('get:override')
@click.argument('url')
@click.argument('house')
def get_override(url, house=None):
    # Initial loading message
    print('Loading override member data from URL...')

    # Load data from specified URL
    r = requests.get(url)
    csv_string = r.text

    # Parse CSV
    print('Parsing CSV')
    lines      = csv_string.splitlines()
    reader     = csv.reader(lines)
    csv_parsed = list(reader)

    x = 0
    for row in csv_parsed:
        if row[0] == 'ID':
            continue

        if house is not None and house != row[1]:
            continue

        member = Person.query.get(row[0])
        if member is None:
            continue

        member.is_landlord = bool(row[3])
        member.expl_txt    = row[4]
        member.updated_at  = datetime.datetime.utcnow()

        db.session.commit()

        x += 1
        if x % 100 == 0:
            print(x, member)
