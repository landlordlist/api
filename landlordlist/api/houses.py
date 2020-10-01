from flask import (
    Blueprint, g, request, abort, jsonify
)

from landlordlist import db, limiter
from landlordlist.models import Person

bp = Blueprint('houses', __name__, url_prefix='/api/houses')


@bp.route('/')
def list():
    output_array = []
    for house in db.session.execute("SELECT DISTINCT(body) FROM people"):

        member_count = db.session.execute("SELECT COUNT(*) FROM people WHERE body = '%s'" % house[0],).first()

        output_array.append({
            'name': house[0],
            'members': member_count[0]
        })

    return jsonify(output_array)


@bp.route('<string:house_name>')
def single(house_name):
    houses = db.session.execute("SELECT DISTINCT(body) FROM people")
    found = False
    for h in houses:
        if h[0] == house_name:
            found = True

    if not found:
        return abort(404)

    member_count   = db.session.execute("SELECT COUNT(*) FROM people WHERE body = '%s'" % house_name, ).first()
    landlord_count = db.session.execute("SELECT COUNT(*) FROM people WHERE body = '%s' and is_landlord = TRUE" % house_name, ).first()

    party_balance  = db.session.execute(
        """
        SELECT parties.id, parties.name, COUNT(people.id) as member_count, SUM(people.is_landlord::int), parties.abbreviation, parties.colour FROM people
          JOIN parties ON party_id = parties.id
        WHERE body = '%s'
        GROUP BY parties.id
        ORDER BY member_count DESC
        """ % house_name,
    ).fetchall()

    parties = []
    for p in party_balance:
        parties.append({
            '_id': p[0],
            'name': p[1],
            'members': p[2],
            'landlords': p[3],
            'abbr': p[4],
            'colour': p[5]
        })

    return jsonify({
        'name': house_name,
        'counts': {
            'members': member_count[0],
            'landlords': landlord_count[0]
        },
        'party_balance': parties
    }), 200
