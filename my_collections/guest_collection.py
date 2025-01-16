class GuestCollection:
    def __init__(self, db):
        self.collection = db['guests']

    def get_all_guests(self):
        return list(self.collection.find({}, {'_id': False}))

    def add_guest(self, data):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)
