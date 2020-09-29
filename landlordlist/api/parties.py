import json

from flask import (
    Blueprint, g, request, abort, jsonify
)

from landlordlist import db
from landlordlist.models import Party

bp = Blueprint('parties', __name__, url_prefix='/api/parties')

@bp.route('/')
def list():
    parties = Party.query.all()

    array = []
    for party in parties:
        array.append({
            '_id': party.id,
            'name': party.name,
            'colour': party.colour,
            'abbr': party.abbreviation,
            'txt_colour': party.text_color
        })

    return jsonify(array), 200


@bp.route('/<int:party_id>')
def single(party_id):
    party = Party.query.get(party_id)

    if party is None:
        return abort(404)

    return {
        'name': party.name,
        'colour': party.colour,
        'abbr': party.abbreviation,
        'txt_colour': party.text_color
    }, 200