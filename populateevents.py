from app import app
from models import db, Event
db.init_app(app)

events=[
('Sign the Wall','general'),
('Mr/Ms Gamaya','general'),
('Esprit de corps','general'),
('Encuesta','general'),
('X-QUIZit','general'),
('CADit','general'),
('Sherlocked!','general'),
('Xtrico','general'),
('ADventure','online'),
('Can the shots!','online'),
('Shoot at sight!','online'),
('Junkyard Wars','me'),
('Rocket Singh','me'),
('RoboSoccer','me'),
('Contrapto','me'),
('Mr.Mechanical','me'),
('Lathe Master','me'),
('Tech Wizard','ic'),
('Chip Master','ic'),
('CodeName MatLab','ic'),
('Make It Easy','ic'),
('Wave Trazer','ic'),
('Wire Sprint','ee'),
('Wind Trap','ee'),
('Bomb Diffusing','ee'),
('RoboWar','ee'),
('Solder magnus','ee'),
('B The Droid','cs'),
('Code Sprint','cs'),
("Bash 'em up",'cs'),
('Intrude n Exploit','cs'),
('Haze Vista','ec'),
('Track n Crack','ec'),
('Desafioder','ec'),
('Bug The Bash','ec'),
('Kramajwala','ec'),
('Master Builder','civil'),
('Chasse Au tresor','civil'),
('Greenvelope','civil'),
('conCreate','civil'),
('Ruban Ville','civil'),
('Counter Strike','gaming'),
('NFS','gaming'),
('FIFA','gaming')]

with app.app_context():
	for eventname,dept in events:
		e = Event(eventname,dept)
		db.session.add(e)
	db.session.commit()