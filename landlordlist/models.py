import datetime

from landlordlist import db


class Party(db.Model):
    __tablename__ = 'parties'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(150))
    abbreviation = db.Column(db.String(50))
    colour       = db.Column(db.String(10))
    text_color   = db.Column(db.String(10))

    members = db.relationship("Person", back_populates="party")


    def __init__(self, name, colour, abbreviation, pk=None):
        if pk is not None:
            self.id = pk

        self.name         = name
        self.colour       = colour
        self.abbreviation = abbreviation


    def __repr__(self):
        return '<Party [%s]>' % self.abbreviation,

    def __str__(self):
        return self.name


class Person(db.Model):
    __tablename__ = 'people'

    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.String(50))
    party_id    = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=True)
    name        = db.Column(db.String(200))
    list_as     = db.Column(db.String(200))
    represents  = db.Column(db.String(200), nullable=True)
    is_landlord = db.Column(db.Boolean, nullable=True)
    expl_txt    = db.Column(db.Text, nullable=True, default=None)
    updated_at  = db.Column(db.Date, default=datetime.datetime.utcnow)

    party = db.relationship("Party", back_populates="members")


    def __init__(self, pk):
        self.id = pk

    def __repr__(self):
        return '<Person [%s]>' % self.list_as,

    def __str__(self):
        return self.name

    @property
    def avatar_url(self):
        return str('https://data.parliament.uk/membersdataplatform/services/images/MemberPhoto/%s/' % self.id,)



