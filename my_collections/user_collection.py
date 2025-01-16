class UserCollection:
    def __init__(self, db):
        self.collection = db['users']

    def get_all_users(self):
        return list(self.collection.find({}, {'_id': False}))

    def add_user(self, user_data):
        return self.collection.insert_one(user_data).inserted_id
