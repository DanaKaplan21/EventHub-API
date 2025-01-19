from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId  # הוספת יבוא ל-ObjectId
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

# פונקציה לפירוש תאריכים
def parse_date(date_str):
    formats = ["%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date format not supported: {date_str}")

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        all_events = list(events.find({}, {'_id': False}))
        return jsonify(all_events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.json
        # שמירת הנתונים כפי שהם, כולל התאריך
        events.insert_one(data)
        return jsonify({"message": "Event created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        # ניסיון להמיר את ה-ID ל-ObjectId
        try:
            object_id = ObjectId(event_id)
        except Exception:
            return jsonify({"error": "Invalid event ID format"}), 400

        # עדכון האירוע
        data = request.json
        result = events.update_one({"_id": object_id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"message": "Event updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        result = events.delete_one({"_id": event_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"message": "Event deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **Guests Routes**

@app.route('/api/guests/<event_id>', methods=['GET'])
def get_guests(event_id):
    try:
        event_guests = list(guests.find({"event_id": event_id}, {'_id': False}))
        return jsonify(event_guests), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/guests', methods=['POST'])
def add_guest():
    try:
        data = request.json
        guests.insert_one(data)
        return jsonify({"message": "Guest added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/guests/<email>', methods=['PUT'])
def update_guest_status(email):
    try:
        data = request.json
        result = guests.update_one({"email": email}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "Guest not found"}), 404
        return jsonify({"message": "Guest status updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/guests/<guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    try:
        result = guests.delete_one({"_id": guest_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Guest not found"}), 404
        return jsonify({"message": "Guest deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **Reminders Routes**

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
