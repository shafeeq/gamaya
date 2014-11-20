from app import app
from models import db
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
