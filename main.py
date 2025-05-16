# --Base--
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
# --Database--
from data import db_session as db
from data.__all_models import Users, Series, TypeTable, Material, Period, Region
from data.validate import validate_periods, validate_materials, validate_regions
# --API--
import api.user as api_usr
# --Additional components--
from forms import RegisterForm, LoginForm, UprofileForm, SerieForm, TypeForm
# from requests import get, post, put, delete
from tools import (passwd_hash, img_validator, required_folders_validator, resort_folder_num, get_user_permission,
                   get_by_rolekey)
from os.path import isfile
from os import listdir, remove

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
@login_required
def user_profile(uid):
    db_sess = db.create_session()
    usr = db_sess.get(Users, uid)
    if isfile(f'static/img/u_pfps/{uid}.jpg'):
        imgp = str(uid) + '.jpg'
    else:
        imgp = 'default.png'
    return render_template('account/uprofile.html', pgtitle=f"UserProfile #{uid}", usr=usr, imgp=imgp)


@app.route('/uprofile/<int:uid>/edit', methods=['POST', 'GET'])
@login_required
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
                                     resize_bounds=(256, 256), proportion_coeff=1.0, prop_validate_only=False)
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
            rkd = get_by_rolekey(form.rolecode.data)
            print(passwd_hash(form.rolecode.data))
            if rkd:
                usr.role = rkd
                print(get_user_permission(usr.role))
            else:
                form.rolecode.errors.append("Such role code doesn't exist")
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
    maxpage = req_all // elems + (1 if req_all % elems != 0 else 0)
    if req_all == 0:
        return render_template('series/series.html', pgtitle="Series table", serlist=serlist, perm=get_user_permission)
    elif req_all <= (page - 1) * elems:
        return redirect(f'/series?elems={elems}&page={maxpage}')
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
    return render_template('series/series.html', pgtitle="Series table", serlist=serlist, page=page, elems=elems,
                           maxpage=maxpage, perm=get_user_permission)


@app.route('/series/new', methods=['POST', 'GET'])  # add
@login_required
def series_new():
    if 'add_data' not in get_user_permission(current_user.role):
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


@app.route('/series/<int:sid>')  # get specific
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
    except FileNotFoundError:
        files = None
    return render_template('series/serie.html', pgtitle=f"Series table - {serie['name']}", serie=serie, files=files)


@app.route('/series/<int:sid>/delete')  # delete specific serie
@login_required
def serie_delete(sid):
    if 'moderate_data' not in get_user_permission(current_user.role):
        abort(403)
    return redirect(f'/series/{sid}')


# --Series - gallery--
@app.route('/series/<int:sid>/gallery', methods=['POST', 'GET'])  # gallery of serie
def serie_gallery(sid):
    db_sess = db.create_session()
    name = db_sess.get(Series, sid).name
    try:
        items = listdir(f'static/img/series/{sid}')
    except FileNotFoundError:
        items = []
    if request.method == 'POST':
        try:
            p = f'static/img/series/{sid}/{len(listdir(f'static/img/series/{sid}'))}'
        except FileNotFoundError:
            p = f'static/img/series/{sid}/0'
        resp = img_validator(request.files['img'], 5, p, resize_bounds=('r', 384), proportion_coeff=1.25,
                             prop_fault=0.75)
        if resp != 'Success':
            return render_template('series/gallery.html', pgtitle=f"{name} - gallery", name=name, imge=resp,
                                   items=items, path=f'/static/img/series/{sid}', link=f'/series/{sid}', perm=get_user_permission)
        else:
            return redirect(f'/series/{sid}/gallery')
    return render_template('series/gallery.html', pgtitle=f'{name} - gallery', name=name, items=items,
                           path=f'/static/img/series/{sid}', link=f'/series/{sid}', perm=get_user_permission)


@app.route('/series/<int:sid>/delimg')  # delete specific image from serie
@login_required
def serie_delimg(sid):
    if 'moderate_data' not in get_user_permission(current_user.role):
        abort(403)
    resort_folder_num(f'static/img/series/{sid}', 'jpg')
    num = request.args.get('index', default=0)
    if num:
        print(listdir(f'static/img/series/{sid}'), num)
        if num in map(lambda x: x.split('.')[0], listdir(f'static/img/series/{sid}')):
            remove(f'static/img/series/{sid}/{num}.jpg')
            resort_folder_num(f'static/img/series/{sid}', 'jpg')
            return redirect(f'/series/{sid}/gallery')
        else:
            abort(404)
    else:
        abort(404)


# --Types--
@app.route('/series/<int:sid>/types')
def types_tab(sid):
    sid = int(sid)
    page = request.args.get('page', default=1, type=int)
    elems = request.args.get('elems', default=50, type=int)
    db_sess = db.create_session()
    serie = db_sess.get(Series, sid).name
    req_all = len(db_sess.query(TypeTable).filter(TypeTable.base_series == sid).all())
    maxpage = req_all // elems + (1 if req_all % elems != 0 else 0)
    typelist = []
    if req_all == 0:
        return render_template('series/types.html', pgtitle=f"{serie} types table", typelist=typelist, serie=serie,
                               sid=sid, page=page, elems=elems, maxpage=maxpage, perm=get_user_permission)
    elif req_all <= (page - 1) * elems:
        return redirect(
            f'/series/{sid}/types?elems={elems}&page={maxpage}'
        )
    else:
        req_ltd = db_sess.query(TypeTable).filter(TypeTable.id.between((page - 1) * elems + 1, page * elems),
                                                  TypeTable.base_series == sid).all()
        for i, _ in enumerate(req_ltd):
            dct = dict()
            dct['id'] = i
            dct['aid'] = _.id
            dct['name'] = _.name
            if _.override_period:
                dct['override_period'] = db_sess.get(Period, _.override_period).name
            else:
                dct['override_period'] = '-'
            dct['description'] = _.description
            if _.region:
                dct['region'] = db_sess.get(Region, _.region).name
            else:
                dct['region'] = '-'
            dct['img'] = isfile(f'static/img/series/types/{sid}-{i}/0.jpg')
            typelist.append(dict(dct))
    return render_template('series/types.html', pgtitle=f"{serie} types table", typelist=typelist, serie=serie, sid=sid,
                           page=page, elems=elems, maxpage=maxpage, perm=get_user_permission)


@app.route('/series/<int:sid>/types/new', methods=['POST', 'GET'])  # add
@login_required
def stype_new(sid):
    if 'add_data' not in get_user_permission(current_user.role):
        abort(403)
    db_sess = db.create_session()
    ser = db_sess.get(Series, sid)
    if not ser:
        db_sess.close()
        abort(404)
    ser = ser.name
    form = TypeForm()
    # when form is sent
    if form.validate_on_submit():
        stype = TypeTable(name=form.name.data,
                          base_series=sid,
                          override_period=db_sess.query(Period).filter(Period.name == str(form.period.data)).first().id,
                          region=db_sess.query(Region).filter(Region.name == str(form.region.data)).first().id,
                          description=form.desc.data
                          )
        db_sess.add(stype)
        db_sess.commit()
        return redirect(f'/series/{sid}/types')
    # default page render
    return render_template('series/type_maker.html', pgtitle=f"{ser} Type - new", form=form, serie=ser)


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
    try:
        files = list(map(lambda x: x.split('.')[0], listdir(f'static/img/series/types/{sid}-{tid}/')))
    except FileNotFoundError:
        files = None
    return render_template('series/type.html', pgtitle=f"{serie}-{typ['name']}", sid=sid, serie=serie, type=typ,
                           tid=tid, files=files)


# --Types - gallery--
@app.route('/series/<int:sid>/types/<int:tid>/gallery', methods=['POST', 'GET'])  # gallery of type
def type_gallery(sid, tid):
    db_sess = db.create_session()
    name = (db_sess.get(Series, sid).name + '-'
            + db_sess.query(TypeTable).filter(TypeTable.base_series == sid).all()[tid].name)
    path = f'static/img/series/types/{sid}-{tid}'
    try:
        items = listdir(path)
    except FileNotFoundError:
        items = []
    if request.method == 'POST':
        try:
            p = f'{path}/{len(listdir(path))}'
        except FileNotFoundError:
            p = f'{path}/0'
        resp = img_validator(request.files['img'], 5, p, resize_bounds=('r', 384), proportion_coeff=1.25,
                             prop_fault=0.75)
        if resp != 'Success':
            return render_template('series/gallery.html', pgtitle=f"{name} - gallery", name=name, imge=resp,
                                   items=items, path='/' + path, link=f'/series/{sid}/types/{tid}', perm=get_user_permission)
        else:
            return redirect(f'/series/{sid}/types/{tid}/gallery')
    return render_template('series/gallery.html', pgtitle=f'{name} - gallery', name=name, items=items,
                           path='/' + path, link=f'/series/{sid}/types/{tid}', perm=get_user_permission)


@app.route('/series/<int:sid>/types/<int:tid>/delimg')  # delete specific image from type
@login_required
def type_delimg(sid, tid):
    if 'moderate_data' not in get_user_permission(current_user.role):
        abort(403)
    path = f'static/img/series/types/{sid}-{tid}'
    resort_folder_num(path, 'jpg')
    num = request.args.get('index', default=0)
    if num:
        print(listdir(path), num)
        if num in map(lambda x: x.split('.')[0], listdir(path)):
            remove(f'{path}/{num}.jpg')
            resort_folder_num(path, 'jpg')
            return redirect(f'/series/{sid}/types/{tid}/gallery')
        else:
            abort(404)
    else:
        abort(404)


# --Discussions--
@app.route('/discussions')
@login_required
def discuss_main():
    return render_template('discs/main.html')


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
    required_folders_validator()
    validate_periods()
    validate_materials()
    validate_regions()
    app.run(port=8089, host='0.0.0.0')
