from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_refresh_token_required, get_jwt_identity,
                                jwt_required, get_raw_jwt)
from models.user import UserModel
from blacklist import BLACKLIST


__parser__ = reqparse.RequestParser()
__parser__.add_argument(
    'username',
    type=str,
    required=True,
    help='This field cannot be blank'
)

__parser__.add_argument(
    'password',
    type=str,
    required=True,
    help='This field cannot be blank'
)


class UserRegister(Resource):
    def post(self):
        data = __parser__.parse_args()
        if UserModel.find_by_username(data['username']):
            return {"message": "user existed"}, 400
        user = UserModel(**data)
        user.save_to_db()
        return {"message": "user created successfully"}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.delete_from_db()
        return {"message": "User deleted"}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = __parser__.parse_args()

        # find user in database
        user = UserModel.find_by_username(data["username"])

        # check password
        # This is what the "authenticate()" function used to do
        if user and safe_str_cmp(user.password, data["password"]):
            # identity= is what the "identity()" function used to do
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200

        return {"message": "Invalid credentials"}, 401

        # create access token
        # create refresh token
        # return


class UserLogout(Resource):
    @jwt_required
    def post(self):
        # jti is "JWT ID", a unique identifier for JWT
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
