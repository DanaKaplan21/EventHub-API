import uuid

from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import os

# Load environment variables
load_dotenv()

port = os.getenv('PORT', 5000)  # Default to 5000 if PORT is not defined
db_uri = os.getenv('DB_URI', 'mongodb://localhost:27017')

app = Flask(__name__)

# Connect to MongoDB
try:
    client = MongoClient(db_uri)
    db = client['mydatabase']
    users = db['users']
    events = db['events']
    guests = db['guests']
    reminders = db['reminders']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db = None
    users = None
    events = None
    guests = None
    reminders = None



@app.route('/', methods=['GET'])
def home():
    return "API is running!"

### **Users Routes**

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        all_users = list(users.find({}, {'_id': False}))
        return jsonify(all_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        users.insert_one(data)
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<email>', methods=['PUT'])
def update_user(email):
    try:
        data = request.json
        result = users.update_one({"email": email}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<email>', methods=['DELETE'])
def delete_user(email):
    try:
        result = users.delete_one({"email": email})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **Events Routes**

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        all_events = list(events.find())
        return jsonify(all_events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.json
        data["_id"] = str(uuid.uuid4())
        if "date" in data:
            data["date"] = data["date"]
        if "invitees" in data and isinstance(data["invitees"], list):
            data["invitees"] = data["invitees"]
        events.insert_one(data)
        return jsonify({"message": "Event created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        data = request.json
        result = events.update_one({"_id": event_id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"message": "Event updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        object_id = ObjectId(event_id)
        result = events.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"message": "Event deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **Guests Routes**
@app.route('/api/guests/<event_id>', methods=['GET'])
def get_guests(event_id):
    try:
        event = events.find_one({"_id": event_id})
        if not event or "invitees" not in event:
            return jsonify([]), 200

        invitees = event["invitees"]
        processed_invitees = [
            {"email": invitee, "status": "Invited"} if isinstance(invitee, str) else invitee
            for invitee in invitees
        ]

        return jsonify(processed_invitees), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/guests', methods=['POST'])
def add_guest():
    try:
        data = request.json
        event_id = data["event_id"]
        email = data["email"]
        status = data.get("status", "Invited")

        event = events.find_one({"_id": event_id})
        if not event:
            return jsonify({"error": "Event not found"}), 404

        invitees = event.get("invitees", [])
        if any(invitee.get("email") == email for invitee in invitees):
            return jsonify({"error": "Guest already exists"}), 400

        invitees.append({"email": email, "status": status})
        events.update_one({"_id": event_id}, {"$set": {"invitees": invitees}})
        return jsonify({"message": "Guest added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_invitees_format():
    try:
        for event in db.events.find():
            updated_invitees = [
                {"email": invitee["email"], "status": invitee.get("status", "Invited")}
                if isinstance(invitee, dict) else
                {"email": invitee, "status": "Invited"}
                for invitee in event.get("invitees", [])
            ]

            db.events.update_one({"_id": event["_id"]}, {"$set": {"invitees": updated_invitees}})
        print("All invitees updated successfully.")
    except Exception as e:
        print(f"Error occurred while updating invitees: {e}")

@app.route('/api/guests/<event_id>/<email>', methods=['PUT'])
def update_guest_status(event_id, email):
    try:
        event = events.find_one({"_id": event_id})
        if not event:
            return jsonify({"error": "Event not found"}), 404

        invitees = event.get("invitees", [])
        guest_found = False
        for invitee in invitees:
            if invitee.get("email") == email:
                invitee["status"] = request.json.get("status", "Invited")
                guest_found = True
                break

        if not guest_found:
            return jsonify({"error": "Guest not found in the specified event"}), 404

        events.update_one({"_id": event_id}, {"$set": {"invitees": invitees}})
        return jsonify({"message": "Guest status updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/guests/<guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    try:
        object_id = ObjectId(guest_id)
        result = guests.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Guest not found"}), 404
        return jsonify({"message": "Guest deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reminders/<event_id>', methods=['GET'])
def get_reminders(event_id):
    try:
        event_reminders = list(reminders.find({"event_id": event_id}, {'_id': False}))
        return jsonify(event_reminders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    try:
        data = request.json
        reminders.insert_one(data)
        return jsonify({"message": "Reminder created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)
