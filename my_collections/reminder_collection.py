class ReminderCollection:
    def __init__(self, db):
        self.collection = db['reminders']

    def get_reminders_by_event(self, event_id):
        return list(self.collection.find({'event_id': event_id}, {'_id': False}))

    def add_reminder(self, reminder_data):
        return self.collection.insert_one(reminder_data).inserted_id
