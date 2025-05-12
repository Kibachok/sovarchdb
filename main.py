from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegisterForm, LoginForm
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nAHEILbKU-T4YNoK3Y'

# login_mg = LoginManager()
# login_mg.init_app(app)


@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html', pgtitle="Index")


# --Account work--
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('account/register.html', pgtitle="Register", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('account/login.html', pgtitle="Log in", form=form)


@app.route('/uprofile/<int:uid>')
def user_profile(uid):
    return render_template('account/uprofile.html', pgtitle=f"UserProfile #{uid}")


# --Series--
@app.route('/series')
def series_tab():
    return render_template('series/series.html', pgtitle="Series table")


@app.route('/series/<int:sid>')
def series_specific(sid):
    return render_template('series/serie.html', pgtitle=f"Series table - {sid}", sid=sid)


@app.route('/series/<int:sid>/types')
def types_tab(sid):
    return render_template('series/types.html', pgtitle=f"{sid} types table", sid=sid)


@app.route('/series/<int:sid>/types/<int:tid>')
def type_specific(sid, tid):
    return render_template('series/type.html', pgtitle=f"{sid}-{tid}", sid=sid, tid=tid)


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
