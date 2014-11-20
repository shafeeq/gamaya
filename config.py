import os
basedir = os.path.abspath(os.path.dirname(__file__))


DATABASE = 'user.db'
DEBUG = False
DATABASE_PATH = os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SECRET_KEY = "some secret key"
APPSITE = "http://registrations.gamaya.org/"

WORKSHOPS={
'workshop1':{'name':'Cloud Computing','description':"Cloud computing workshop",'past' : True},
'workshop2':{'name':'Robotics','description':"Robotics workshop",'past' : False},
'workshop3':{'name':'Motion Sensing','description':"Motion Sensing workshop",'past' : False},
'workshop4':{'name':'Tall buildings design','description':"Tall buildings design workshop",'past' : True},
'workshop5':{'name':'Auto Design','description':"Auto Design workshop",'past' : True}
}
EVENT_TYPES=[('civil','Civil Engineering'),
			('cs','Computer Science & Engineering'),
			('ec','Electronics & Communication Engineering'),
			('ee','Electrical Engineering'),
			('ic','Instrumentation & Control Engineering'),
			('me','Mechanical Engineering'),
			('general','General'),
			('online','Online'),
			('gaming','Gaming')]
REMOVED_EVENTS = [19]
PAST_EVENTS = [30,31,3,28,35,41,38,17,18,24,27,6,9]

