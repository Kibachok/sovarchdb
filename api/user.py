import flask_restful as rest
from flask_restful import reqparse
import data.db_session as db
from data.__all_models import Users
from flask import abort, jsonify


parser = reqparse.RequestParser()
parser.add_argument('login', required=True)
parser.add_argument('password', required=True)
parser.add_argument('nickname', required=False)


def abort_if_missing(uid):
    db_sess = db.create_session()
    user = db_sess.query(Users).get(uid)
    if not user:
        abort(404, message=f"User [by ID] {uid} not found")


class UsrRes(rest.Resource):
    """Single object User Resources, includes:
    **GET** <uid>\n
    **PUT** <uid>\n
    **DELETE** <uid>"""
    def get(self, uid):
        abort_if_missing(uid)
        db_sess = db.create_session()
        usr = db_sess.query(Users).get(uid)
        return jsonify({'user': usr.to_dict()})

    def delete(self, uid):
        abort_if_missing(uid)
        db_sess = db.create_session()
        usr = db_sess.query(Users).get(uid)
        db_sess.delete(usr)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsrLoginRes(rest.Resource):
    """Single object User Resources callable using username, includes:
    **GET** <username>"""
    def get(self, un):
        db_sess = db.create_session()
        usr = db_sess.query(Users).filter(Users.login == str(un)).first()
        if not usr:
            abort(404, message=f"User [by username] {un} not found")
        return jsonify({'user': usr.to_dict()})


class UsrListRes(rest.Resource):
    """List of all User Resources, includes:
    **GET**\n
    **POST** <request's body>"""
    def get(self):
        db_sess = db.create_session()
        usr = db_sess.query(Users).all()
        return jsonify({'users': [_.to_dict() for _ in usr]})

    def post(self):
        args = parser.parse_args()
        kws = {
            'login': args['login'],
            'password': args['password']
        }
        try:
            kws['nickname'] = args['nickname']
        except KeyError:
            pass
        db_sess = db.create_session()
        try:
            usr = Users(**kws)
            db_sess.add(usr)
            db_sess.commit()
        except Exception:
            db_sess.close()
            abort(400, message=f"Login already exist")
        return jsonify({'id': usr.id})


db.global_init('db/database.db')
