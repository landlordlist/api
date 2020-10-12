from flask import (
    Blueprint, g, request, abort, jsonify
)

from landlordlist.models import Person

bp = Blueprint('people', __name__, url_prefix='/api/people')

@bp.route('/')
def list():
    people = Person.query.order_by('list_as')

    q = request.args

    if q.get('house'):
        if q.get('house') in ('Lords', 'Commons'):
            people = people.filter_by(body=q.get('house'))

    if q.get('party_id'):
        people = people.filter_by(party_id=int(q.get('party_id')))

    if q.get('landlord'):
        people = people.filter_by(is_landlord=True)

    if q.get('search'):
        people = people.filter(Person.name.contains(q.get('search').title()))

    # This offset should be the last condition
    if q.get('offset'):
        people = people.offset(int(q.get('offset')))

    array = []
    for person in people.limit(10).all():
        array.append({
            '_id': person.id,
            'name': person.name,
            'from': person.represents,
            'party': {
                "name": person.party.name,
                "colour": person.party.colour,
                "abbr": person.party.abbreviation,
                "text_colour": person.party.text_color
            },
            'is_landlord': person.is_landlord,
            'avatar_url': person.avatar_url,
            'text': person.expl_txt
        })

    return jsonify(array), 200


@bp.route('/<int:member_id>')
def single(member_id):
    person = Person.query.get(member_id)

    if person is None:
        return abort(404)

    return {
        'name': person.name,
        'from': person.represents,
        'party': {
            "name": person.party.name,
            "colour": person.party.colour,
            "abbr": person.party.abbreviation
        },
        'is_landlord': person.is_landlord,
        'avatar_url': person.avatar_url,
        'text': person.expl_txt
    }, 200
