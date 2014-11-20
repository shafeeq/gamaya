from werkzeug import generate_password_hash
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Registration(db.Model):
    __tablename__ = 'registration'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'),primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gamayauser.id'),primary_key=True)
    registered_on = db.Column(db.DateTime)

    def __init__(self,userid, eventid):
        self.user_id = userid
        self.event_id = eventid
        self.registered_on = datetime.datetime.utcnow()

    def __repr__(self):
        return '<user: %r - event: %r - reg:%r>' %(self.user_id, self.event_id, self.registered_on)




class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    participants = db.relationship('User',secondary='registration',
        backref=db.backref('events',lazy='dynamic'),lazy='dynamic')

    def __init__(self,name,department):
        self.name = name
        self.department = department

    def __repr__(self):
        return '<event: %r - name: %r - dept:%r>' %(self.id, self.name, self.department)


class User(db.Model):
    __tablename__ = "gamayauser"

    id = db.Column(db.Integer, primary_key=True)
    gamayaid = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False,unique=True , index=True)
    college = db.Column(db.String, nullable=False)
    mobilenumber = db.Column(db.String, nullable=False)
    pwdhash = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime)

    authenticated = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)

    is_admin = db.Column(db.Boolean, default=False)

    registrations = db.relationship('Registration',backref='user',lazy='dynamic')
    
    
    workshop1_registered = db.Column(db.Boolean, default=False)
    workshop1_registered_on = db.Column(db.DateTime)

    workshop2_registered = db.Column(db.Boolean, default=False)
    workshop2_registered_on = db.Column(db.DateTime)

    workshop3_registered = db.Column(db.Boolean, default=False)
    workshop3_registered_on = db.Column(db.DateTime)

    workshop4_registered = db.Column(db.Boolean, default=False)
    workshop4_registered_on = db.Column(db.DateTime)

    workshop5_registered = db.Column(db.Boolean, default=False)
    workshop5_registered_on = db.Column(db.DateTime)

    
    def __init__(self,name,college,email,password,mobilenumber):
        self.name = name
        self.email = email
        self.college = college
        self.mobilenumber = mobilenumber
        self.pwdhash = generate_password_hash(password)
        self.registered_on = datetime.datetime.utcnow()


    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<id: %r - email: %r>' %(self.id, self.email)
