from flask import Flask, request, jsonify
from pymongo import MongoClient
from my_collections.user_collection import UserCollection
from my_collections.event_collection import EventCollection
from my_collections.guest_collection import GuestCollection
from my_collections.reminder_collection import ReminderCollection


app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017')
db = client['mydatabase']

# Initialize Collections
user_collection = UserCollection(db)
event_collection = EventCollection(db)
guest_collection = GuestCollection(db)
reminder_collection = ReminderCollection(db)

@app.route('/', methods=['GET'])
def home():
    return "API is running!", 200

# Users Routes
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = user_collection.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user_data = request.json
        user_id = user_collection.add_user(user_data)
        return jsonify({"message": f"User added with ID: {user_id}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Events Routes
@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = event_collection.get_all_events()
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        event_data = request.json
        event_id = event_collection.add_event(event_data)
        return jsonify({"message": f"Event created with ID: {event_id}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Guests Routes
@app.route('/api/guests/<event_id>', methods=['GET'])
def get_guests(event_id):
    try:
        guests = guest_collection.get_guests_by_event(event_id)
        return jsonify(guests), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/guests', methods=['POST'])
def add_guest():
    try:
        guest_data = request.json
        guest_id = guest_collection.add_guest(guest_data)
        return jsonify({"message": f"Guest added with ID: {guest_id}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reminders Routes
@app.route('/api/reminders/<event_id>', methods=['GET'])
def get_reminders(event_id):
    try:
        reminders = reminder_collection.get_reminders_by_event(event_id)
        return jsonify(reminders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    try:
        reminder_data = request.json
        reminder_id = reminder_collection.add_reminder(reminder_data)
        return jsonify({"message": f"Reminder created with ID: {reminder_id}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
