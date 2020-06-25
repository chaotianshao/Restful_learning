from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "store not found"}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {
                'message': 'A store already exists'
            }, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except Exception:
            return {'message': 'An error occuerd while creating store'}, 500

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {'message': "store is deleted"}


class StoreList(Resource):
    def get(self):
        return {"stores": [x.json() for x in StoreModel.query.all()]}
