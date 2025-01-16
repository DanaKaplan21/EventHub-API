class EventCollection:
    def __init__(self, db):
        self.collection = db['events']

    def get_all_events(self):
        return list(self.collection.find({}, {'_id': False}))

    def add_event(self, event_data):
        return self.collection.insert_one(event_data).inserted_id
