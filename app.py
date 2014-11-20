from flask import Flask, request, render_template, url_for, redirect, flash, session, g, send_file, abort
from flask import jsonify
import json
import os
import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.seasurf import SeaSurf #for csrf protection
from flask_mail import Mail, Message 
from threading import Thread
app = Flask(__name__)
app.config.from_object('config')
import pytz

import operator #for sorting attrgetter

from models import db
from models import User, Event, Registration

from xhtml2pdf import pisa
from cStringIO import StringIO
from flask_weasyprint import HTML, render_pdf


csrf = SeaSurf(app)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
    return render_template('index.html',page="home")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('index'))
        return render_template('login.html',page="login")

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.pwdhash, password):
                user.authenticated = True
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))
            flash('Username or Password is invalid' , 'warning')
            return render_template("login.html",page="login")
        else:
            flash('Username or Password is invalid' , 'warning')
            return render_template("login.html",page="login")


@app.route('/register',methods=['GET','POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('index'))

    error = False
    if request.method == 'GET':
        return render_template('register.html',page="register")

    
    elif request.method == 'POST':
        #app.logger.info(repr(request.form))
        name = request.form['name']
        email = request.form['email']
        college = request.form['college']
        mobilenumber = request.form['mobilenumber']
        
        password = request.form['password']
        passwordconfirm = request.form['password-confirm']

        user = User.query.filter_by(email=email).first()
        if user:
            
            error = True
            flash('Email already registered','warning')
        
        if password != passwordconfirm:
            error = True
            flash("Passwords don't match",'warning')
        if len(mobilenumber) != 10 or not mobilenumber.isdigit():
            error = True
            flash("Mobile number is invalid",'warning')

        #app.logger.info("Error = ", str(error))
        if error:
            return render_template('register.html',page="register")
        else:
            newuser = User(name,college,email,password,mobilenumber)
            newuser.authenticated = True
            db.session.add(newuser)
            db.session.commit()
            newuser.gamayaid = "GM%04d" %newuser.id
            db.session.commit()
            login_user(newuser)
            return redirect(url_for('index'))

@app.route('/workshops', methods=['GET','POST'])
@login_required
def workshops():
    if request.method == 'GET':
        printparam  = request.args.get('print')
        if printparam:
            n = 0
            html = render_template('printregistrationdetails.html',
            enumerate=enumerate,len=len,utc_to_local=utc_to_local,
            datetime=datetime,workshops=app.config['WORKSHOPS'],page="workshops")
            return render_pdf(HTML(string=html))

        return render_template('workshops.html',workshops=app.config['WORKSHOPS'],page="workshops")
    else:
        register = request.form.get('register')
        unregister = request.form.get('unregister')
        #app.logger.info('Unregister: {}'.format(unregister))
        if register:
            if register+'_registered' in User.__dict__:
                if g.user.__dict__[register+'_registered'] == False:
                    setattr(g.user,register+'_registered',True)
                    setattr(g.user,register+'_registered_on',datetime.datetime.utcnow())
                    db.session.commit()
            
        elif unregister:
            if unregister+'_registered' in User.__dict__:
                if g.user.__dict__[unregister+'_registered'] == True:
                    setattr(g.user,unregister+'_registered',False)
                    setattr(g.user,unregister+'_registered_on',None)
                    db.session.commit()

        return render_template('workshops.html',workshops=app.config['WORKSHOPS'],page="workshops")

@app.route('/events', methods=['GET','POST'])
@login_required
def events():
    if request.method == 'GET':
        printparam  = request.args.get('print')
        if printparam:
            n = 0
            html = render_template('printregistrationdetails.html',
            enumerate=enumerate,len=len,utc_to_local=utc_to_local,
            datetime=datetime,workshops=app.config['WORKSHOPS'])
            return render_pdf(HTML(string=html))

        events = Event.query.all()
        userevents = g.user.events.all()
        


        return render_template('events.html',events=events, userevents=userevents, 
            eventtypes=app.config['EVENT_TYPES'],mod=mod,enumerate=enumerate,page="events",
            removed_events=app.config['REMOVED_EVENTS'],past_events = app.config['PAST_EVENTS'])
    else:
        register = request.form.get('register')
        unregister = request.form.get('unregister')

        #app.logger.info('Unregister: {}'.format(unregister))
        if register:
            if Event.query.filter_by(id=register).first():
                if not g.user.events.filter_by(id=register).first():
                    r = Registration(g.user.id,register)
                    db.session.add(r)
                    db.session.commit()


        elif unregister:
            
            if Event.query.filter_by(id=unregister).first():
                e = g.user.events.filter_by(id=unregister).first()

                if e:
                    r = Registration.query.filter_by(event_id=unregister).filter_by(user_id = g.user.id).first()

                    db.session.delete(r)
                    db.session.commit()

        return redirect(url_for('events'))



@app.route('/admin/')
@login_required
def admin():
    if g.user.is_admin == True:
        return render_template('admin.html',page="admin")
    else:
        return abort(403)

@app.route('/admin/allusers')
@login_required
def allusers():
    if g.user.is_admin == True:
        userslist = User.query.order_by(User.gamayaid).all()
        return render_template('allusers.html',userslist = userslist,page="admin",
            utc_to_local=utc_to_local)
    else:
        return abort(403)


@app.route('/admin/allevents')
@login_required
def allevents():
    if g.user.is_admin == True:
        userslist = User.query.all()
        return render_template('allevents.html',eventtypes = app.config['EVENT_TYPES'],
            events = Event.query.all(),page="admin")
    else:
        return abort(403)


@app.route('/admin/searchuser/', methods=['GET','POST'])
@login_required
def searchuser():
    if g.user.is_admin == True:
        userslist = []
        if request.method == 'POST':
            #app.logger.info(request.form)
            if 'gmid' in request.form:
                userslist = User.query.filter(User.gamayaid.like('%%{}%%'.format(request.form['gmid'])))
                app.logger.info(userslist)
                if userslist == []:
                    flash('No user found with id ' + request.form['gmid'], 'warning')
            elif 'name' in request.form:
                userslist = User.query.filter(User.name.ilike('%%{}%%'.format(request.form['name']))).all()
                if userslist == []:
                    flash('No user(s) found with name like ' + request.form['name'], 'warning')
            elif 'email' in request.form:
                userslist = User.query.filter(User.email.ilike('%%{}%%'.format(request.form['email']))).all()
                if userslist == []:
                    flash('No user(s) found with email like ' + request.form['email'], 'warning')
        return render_template('searchuser.html',userslist=userslist,page="admin")
    else:
        return abort(403)
@app.route('/admin/user/<gamayaid>')
@login_required
def user(gamayaid):
    if g.user.is_admin == True:
        user = User.query.filter_by(gamayaid = gamayaid).first()
        if user:
            return render_template('user.html',user=user,utc_to_local=utc_to_local,
                workshops=app.config['WORKSHOPS'], enumerate=enumerate,page="admin")
        else:
            flash('No user found with id ' + gamayaid, 'warning')
            return redirect(url_for('searchuser'))
    else:
        return abort(403)

@app.route('/admin/allworkshops/')
@login_required
def allworkshops():
    if g.user.is_admin == True:
        return render_template('allworkshops.html',workshops=app.config['WORKSHOPS'],page="admin")
    else:
        return abort(403)


@app.route('/admin/workshop/<workshopid>')
@login_required
def workshop(workshopid):
    if g.user.is_admin == True:
        if workshopid+'_registered' in User.__dict__:
            users = User.query.all()
            workshopinfo = [user for user in users if user.__dict__[workshopid+'_registered']==True ]
            workshopinfo = sorted(workshopinfo,key=operator.attrgetter('gamayaid'))
            printparam  = request.args.get('print')
            if printparam:

                html = render_template('printworkshop.html',workshopinfo=workshopinfo, 
                enumerate=enumerate,len=len,workshopid=workshopid,utc_to_local=utc_to_local,
                datetime=datetime,workshops=app.config['WORKSHOPS'])
                return render_pdf(HTML(string=html))


            return render_template('workshop.html',workshopinfo=workshopinfo, 
                enumerate=enumerate,len=len,workshopid=workshopid,utc_to_local=utc_to_local,
                workshops=app.config['WORKSHOPS'],datetime=datetime,page="admin")
        else:
            flash("No such workshop",'warning')
            return redirect(url_for('allworkshops'))
    else:
        return abort(403)

@app.route('/admin/event/<eventid>')
@login_required
def event(eventid):
    if g.user.is_admin == True:
        event = Event.query.filter_by(id=eventid).first()

        if event:
            printparam  = request.args.get('print')
            if printparam:

                html = render_template('printevent.html',event=event,utc_to_local=utc_to_local,
                datetime=datetime, enumerate=enumerate,page="admin",User=User)
                return render_pdf(HTML(string=html))

            

            return render_template('event.html',event=event,utc_to_local=utc_to_local,
                datetime=datetime, enumerate=enumerate,page="admin",User=User)
        else:
            flash("No such event",'warning')
            return redirect(url_for('allevents'))
    else:
        return abort(403)

@app.route('/admin/desk', methods=['GET','POST'])
@login_required
def regdesk():
    if g.user.is_admin == True:
        if request.method == 'GET':
            userslist = User.query.all()
            return render_template('regdesk.html',eventtypes = app.config['EVENT_TYPES'],
                events = Event.query.all(),page="admin")
        else:
            app.logger.info(request.form)
            name = request.form['name']
            mobilenumber = request.form['mobilenumber']
            college = request.form['college']
            user = User.query.filter_by(mobilenumber=mobilenumber).first()
            error = False  
            if user:
                error = True
                flash('Mobile number already registered','warning')

            if len(mobilenumber) != 10 or not mobilenumber.isdigit():
                error = True
                flash("Mobile number is invalid",'warning')

            if error:
                return render_template('regdesk.html',page="admin",eventtypes = app.config['EVENT_TYPES'],
                    events = Event.query.all())
            else:
                newuser = User(name,college,mobilenumber+'-Registered-offline',mobilenumber[:-4],mobilenumber)
                db.session.add(newuser)
                db.session.commit()
                newuser.gamayaid = "GM%04d" %newuser.id
                db.session.commit()

                for i in request.form.keys():
                    if 'event' in i:
                        if i[5:].isdigit():
                            if Event.query.filter_by(id=int(i[5:])).first():
                                r = Registration(newuser.id,int(i[5:]))
                                db.session.add(r)
                                db.session.commit()
                    if 'workshop' in i:
                        if i+'_registered' in User.__dict__:
                            setattr(newuser,i+'_registered',True)
                            setattr(newuser,i+'_registered_on',datetime.datetime.utcnow())
                            db.session.commit()

                
            flash('User created with gamaya id: ' + newuser.gamayaid, 'success')
            return render_template('regdesk.html',eventtypes = app.config['EVENT_TYPES'],
                events = Event.query.all(),page="admin")
    else:
        return abort(403)


@app.route('/logout')
def logout():
    g.user.authenticated = False
    db.session.commit()
    logout_user()
    return redirect(url_for('index')) 


def utc_to_local(utc_dt):
    local_tz = pytz.timezone('Asia/Kolkata')
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def mod(a,b):
    return a % b

@csrf.exempt
@app.route('/extauth', methods=['POST'])
def extauth():
    app.logger.info(repr(request.form))
    email = request.form['email']
    password = request.form['password']
    eid = int(request.form['eid'])
    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.pwdhash, password):
            d = dict(user.__dict__)
            d.pop('_sa_instance_state')
            d['success'] = True
            e = user.events.all()
            eids = [i.id for i in e]
            if eid in eids:
                d['event_registered'] = True
            else:
                d['event_registered'] = False
                r = Registration(user.id,eid)
                db.session.add(r)
                db.session.commit()

            return jsonify(d)
        else:
            return jsonify({'success':False})
    else:
        return jsonify(success = False)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5050)
