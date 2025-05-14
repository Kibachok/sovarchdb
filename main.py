# --Base--
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
# --Database--
from data import db_session as db
from data.__all_models import Users, Series, TypeTable, Material, Period
from data.validate import validate_periods, validate_materials
# --API--
import api.user as api_usr
# --Additional components--
from forms import RegisterForm, LoginForm, UprofileForm, SerieForm
# from requests import get, post, put, delete
from tools import passwd_hash, img_validator
from os.path import isfile
from os import listdir

# --Init--
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nAHEILbKU-T4YNoK3Y'

# --API_Init--
api = Api(app)

# --UserAPI--
api.add_resource(api_usr.UsrRes, '/api/usr/<int:uid>')
api.add_resource(api_usr.UsrLoginRes, '/api/usr/bylogin/<un>')
api.add_resource(api_usr.UsrListRes, '/api/usr')

# --Login system
login_mg = LoginManager()
login_mg.init_app(app)

LOCAL = 'http://localhost:8080'


# --Index page--
@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html', pgtitle="Index")


# --Account work--
@login_mg.user_loader
def load_user(uid):
    db_sess = db.create_session()
    usr = db_sess.query(Users).get(uid)
    if usr:
        return usr
    else:
        return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    # when form is sent
    if form.validate_on_submit():
        # checks for password criteria
        pswd = str(form.passwd.data)
        c_0 = pswd.isalnum() and not(pswd.isalpha() or pswd.isdigit())
        c_1 = pswd.lower() != pswd
        if not(c_0 or c_1):
            form.passwd.errors.append("Password doesn't match a criteria: to have both upper- and lowercase chars " +
                                      "or to have both digits and letters")
            return render_template('account/register.html', pgtitle="Register", form=form)
        # wraps the data
        data = {
            'login': form.uname.data,
            'password': passwd_hash(form.passwd.data),
            'nickname': form.nickname.data
        }
        db_sess = db.create_session()
        try:
            req = Users(**data)
        except Exception:
            form.uname.errors.append('Username is already in use')
            return render_template('account/register.html', pgtitle="Register", form=form)
        db_sess.add(req)
        db_sess.commit()
        login_user(req, remember=False)
        return redirect('/')
    # default page render
    return render_template('account/register.html', pgtitle="Register", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    # when form is sent
    if form.validate_on_submit():
        db_sess = db.create_session()
        # gets user by username
        req = db_sess.query(Users).filter(Users.login == str(form.uname.data)).first()
        if req:
            if passwd_hash(form.passwd.data) == req.password:
                login_user(req, remember=form.rmmb.data)
                return redirect('/')
            form.passwd.errors.append("Password doesn't match")
            return render_template('account/login.html', pgtitle="Log in", form=form)
        form.passwd.errors.append("No user with given username found")
        return render_template('account/login.html', pgtitle="Log in", form=form)
    # default page render
    return render_template('account/login.html', pgtitle="Log in", form=form)


@app.route('/uprofile/<int:uid>')
def user_profile(uid):
    db_sess = db.create_session()
    usr = db_sess.get(Users, uid)
    if isfile(f'static/img/u_pfps/{uid}.jpg'):
        imgp = str(uid) + '.jpg'
    else:
        imgp = 'default.png'
    return render_template('account/uprofile.html', pgtitle=f"UserProfile #{uid}", usr=usr, imgp=imgp)


@app.route('/uprofile/<int:uid>/edit', methods=['POST', 'GET'])
def user_profile_edit(uid):
    if current_user.id != uid:
        abort(403)
    form = UprofileForm()
    db_sess = db.create_session()
    usr = db_sess.get(Users, uid)
    if isfile(f'static/img/u_pfps/{uid}.jpg'):
        imgp = str(uid) + '.jpg'
    else:
        imgp = 'default.png'
    if form.validate_on_submit():
        if form.save.data:
            usr.nickname = form.nickname.data
            # avatar checker
            if request.files['avatar']:
                resp = img_validator(request.files['avatar'], size_limit=0.5, endname='static/img/u_pfps/' + str(uid),
                                     do_square=True, resize_bounds=(256, 256))
                if resp != 'Success':
                    return render_template('account/uprofile.html', pgtitle=f"UserProfile #{uid}", usr=usr, imgp=imgp,
                                           form=form, imge=resp)
            # delete checker
            if form.delete.data:
                if isfile(f'static/img/u_pfps/{uid}.jpg'):
                    with open(f'static/img/u_pfps/default.png', mode='rb') as da:
                        defav = da.read()
                    with open(f'static/img/u_pfps/{uid}.jpg', mode='wb') as av:
                        av.write(defav)
                logout_user()
                db_sess.delete(usr)
                db_sess.commit()
                return redirect('/')
            db_sess.commit()
        return redirect(f'/uprofile/{uid}')
    form.nickname.data = usr.nickname

    return render_template('account/uprofile.html', pgtitle=f"UserProfile #{uid}", usr=usr, imgp=imgp, form=form)


# --Series--
@app.route('/series')
def series_tab():
    page = request.args.get('page', default=1, type=int)
    elems = request.args.get('elems', default=50, type=int)
    db_sess = db.create_session()
    req_all = len(db_sess.query(Series).all())
    serlist = []
    if req_all == 0:
        return render_template('series/series.html', pgtitle="Series table", serlist=serlist)
    elif req_all <= (page - 1) * elems:
        return redirect(f'/series?elems={elems}&page={req_all // elems + (1 if req_all % elems != 0 else 0)}')
    else:
        req_ltd = db_sess.query(Series).filter(Series.id.between((page - 1) * elems + 1, page * elems)).all()
        for _ in req_ltd:
            dct = dict()
            dct['id'] = _.id
            dct['name'] = _.name
            dct['period'] = db_sess.get(Period, _.period).name
            dct['material'] = db_sess.get(Material, _.material).name
            dct['description'] = _.description
            dct['types'] = db_sess.query(TypeTable).filter(TypeTable.base_series == _.id).all()
            dct['img'] = isfile(f'static/img/series/{_.id}/0.jpg')
            serlist.append(dict(dct))
    return render_template('series/series.html', pgtitle="Series table", serlist=serlist)


@app.route('/series/new', methods=['POST', 'GET'])
def series_new():
    if not current_user.is_authenticated:
        abort(403)
    form = SerieForm()
    # when form is sent
    if form.validate_on_submit():
        db_sess = db.create_session()
        serie = Series(name=form.name.data,
                       period=db_sess.query(Period).filter(Period.name == str(form.period.data)).first().id,
                       material=db_sess.query(Material).filter(Material.name == str(form.mat.data)).first().id,
                       description=form.desc.data
                       )
        db_sess.add(serie)
        db_sess.commit()
        return redirect('/series')
    # default page render
    return render_template('series/serie_maker.html', pgtitle="Serie - new", form=form)


@app.route('/series/<int:sid>', methods=['POST', 'GET'])
def series_specific(sid):
    db_sess = db.create_session()
    s = db_sess.get(Series, sid)
    serie = {
        'id': s.id,
        'name': s.name,
        'period': db_sess.get(Period, s.period).name,
        'material': db_sess.get(Material, s.material).name,
        'description': s.description
    }
    try:
        files = list(map(lambda x: x.split('.')[0], listdir(f'static/img/series/{sid}/')))
        print(files)
    except FileNotFoundError:
        files = None
    if request.method == 'POST':
        try:
            p = f'static/img/series/{sid}/{len(listdir(f'static/img/series/{sid}'))}'
        except FileNotFoundError:
            p = f'static/img/series/{sid}/0'
        resp = img_validator(request.files['img'], 5, p)
        if resp != 'Success':
            return render_template('series/serie.html', pgtitle=f"Series table - {sid}", serie=serie, imge=resp)
        else:
            return redirect(f'/series/{sid}')
    return render_template('series/serie.html', pgtitle=f"Series table - {sid}", serie=serie, files=files)


@app.route('/series/<int:sid>/types')
def types_tab(sid):
    sid = int(sid)
    page = request.args.get('page', default=1, type=int)
    elems = request.args.get('elems', default=50, type=int)
    db_sess = db.create_session()
    serie = db_sess.get(Series, sid).name
    req_all = len(db_sess.query(TypeTable).filter(TypeTable.base_series == sid).all())
    typelist = []
    if req_all == 0:
        return render_template('series/types.html', pgtitle=f"{serie} types table", typelist=typelist, serie=serie, sid=sid)
    elif req_all <= (page - 1) * elems:
        return redirect(
            f'/series/{sid}/types?elems={elems}&page={req_all // elems + (1 if req_all % elems != 0 else 0)}'
        )
    else:
        req_ltd = db_sess.query(TypeTable).filter(TypeTable.id.between((page - 1) * elems + 1, page * elems),
                                                  TypeTable.base_series == sid).all()
        for _ in req_ltd:
            dct = dict()
            dct['id'] = _.id
            dct['name'] = _.name
            if _.override_period:
                dct['override_period'] = db_sess.get(Period, _.override_period).name
            else:
                dct['override_period'] = '-'
            dct['description'] = _.description
            if _.region:
                dct['region'] = _.region
            else:
                dct['region'] = '-'
            typelist.append(dict(dct))
    return render_template('series/types.html', pgtitle=f"{serie} types table", typelist=typelist, serie=serie, sid=sid)


@app.route('/series/<int:sid>/types/<int:tid>')
def type_specific(sid, tid):
    db_sess = db.create_session()
    serie = db_sess.get(Series, sid)
    try:
        t = db_sess.query(TypeTable).filter(TypeTable.base_series == serie.id).all()[tid]
    except IndexError:
        abort(404)
    serie = serie.name
    typ = {
        'id': t.id,
        'name': t.name,
        'period': db_sess.get(Period, t.override_period).name,
        'region': t.region,
        'description': t.description
    }
    return render_template('series/type.html', pgtitle=f"{serie}-{typ['name']}", sid=sid, serie=serie, type=typ)


# --Error parsers--
@app.errorhandler(404)
def notfound(e):
    return render_template('error.html', pgtitle="E404", error=404, desc='URL not found', img='notfound')


@app.errorhandler(400)
def badrequest(e):
    return render_template('error.html', pgtitle="E400", error=400, desc='Bad request', img='badrequest')


@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', pgtitle="E401", error=401, desc='Unauthorized', img='unauth')


@app.errorhandler(500)
def internal(e):
    return render_template('error.html', pgtitle="E500", error=500, desc='Internal error', img='internal')


@app.errorhandler(403)
def adenied(e):
    return render_template('error.html', pgtitle="E403", error=403, desc='Access denied', img='accessdenied')


if __name__ == "__main__":
    app.run(port=8080, host='127.0.0.1')
    validate_periods()
    validate_materials()
