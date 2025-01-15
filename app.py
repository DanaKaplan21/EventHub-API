from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

port = os.getenv('PORT', 5000)  # ברירת מחדל ל-5000 אם PORT לא מוגדר
db_uri = os.getenv('DB_URI', 'mongodb://localhost:27017')

app = Flask(__name__)

# Connect to MongoDB
try:
    client = MongoClient(db_uri)
    db = client['mydatabase']
    users = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db = None
    users = None

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Return a simple static response for testing.
    """
    return jsonify({"data": "This is some data!"}), 200

@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        db_names = client.list_database_names()
        if 'mydatabase' in db_names:
            return "Connection to MongoDB is successful!", 200
        else:
            return "Database not found.", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        if users is None:  # בדיקה מפורשת
            return jsonify({"error": "Database not connected"}), 500

        all_users = list(users.find({}, {'_id': False}).limit(100))
        if not all_users:
            return jsonify({"message": "No users found"}), 200
        return jsonify(all_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        if not request.is_json:
            return jsonify({"error": "Request content type must be 'application/json'"}), 415

        data = request.json
        if not data or "name" not in data or "email" not in data:
            return jsonify({"error": "Invalid data"}), 400

        users.insert_one(data)
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<email>', methods=['PUT'])
def update_user(email):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)


# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
#
# # Load environment variables
# load_dotenv()
#
# port = os.getenv('PORT')
# db_uri = os.getenv('DB_URI')
#
# print(f"Running on port: {port}")
# print(f"Database URI: {db_uri}")
#
# app = Flask(__name__)
#
# # Connect to MongoDB
# client = MongoClient(db_uri)
# db = client['mydatabase']
#
# # Users collection
# users = db['users']
#
# # ---------------------------------------------
# # API Home Route
# # ---------------------------------------------
# @app.route('/', methods=['GET'])
# def home():
#     """
#     Check if the API is running
#     ---
#     responses:
#       200:
#         description: Returns "API is running!"
#     """
#     return "API is running!"
#
# # ---------------------------------------------
# # Test Data Route
# # ---------------------------------------------
# @app.route('/api/data', methods=['GET'])
# def get_data():
#     """
#     Get a static data response
#     ---
#     responses:
#       200:
#         description: Returns a static data object
#     """
#     return {'data': 'This is some data!'}
#
# # ---------------------------------------------
# # GET: Retrieve All Users
# # ---------------------------------------------
# @app.route('/users', methods=['GET'])
# def get_users():
#     """
#     Retrieve all users from the database
#     ---
#     responses:
#       200:
#         description: Returns a list of users
#       500:
#         description: Internal server error
#     """
#     try:
#         all_users = list(users.find({}, {'_id': False}))  # Hide _id field
#         if not all_users:
#             return jsonify({"message": "No users found"}), 200
#         return jsonify(all_users), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
# # POST: Create a New User
# # ---------------------------------------------
# @app.route('/users', methods=['POST'])
# def create_user():
#     """
#     Create a new user
#     ---
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               name:
#                 type: string
#               email:
#                 type: string
#             required:
#               - name
#               - email
#     responses:
#       201:
#         description: User added successfully
#       400:
#         description: Invalid data
#       415:
#         description: Request content type must be 'application/json'
#       500:
#         description: Internal server error
#     """
#     try:
#         if not request.is_json:
#             return jsonify({"error": "Request content type must be 'application/json'"}), 415
#
#         data = request.json
#         if not data or "name" not in data or "email" not in data:
#             return jsonify({"error": "Invalid data"}), 400
#
#         users.insert_one(data)
#         return jsonify({"message": "User added successfully"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
# # PUT: Update User by Email
# # ---------------------------------------------
# @app.route('/users/<email>', methods=['PUT'])
# def update_user(email):
#     """
#     Update user information by email
#     ---
#     parameters:
#       - name: email
#         in: path
#         required: true
#         schema:
#           type: string
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               name:
#                 type: string
#               role:
#                 type: string
#     responses:
#       200:
#         description: User updated successfully
#       400:
#         description: Invalid data
#       404:
#         description: User not found
#       500:
#         description: Internal server error
#     """
#     try:
#         data = request.json
#         if not data:
#             return jsonify({"error": "Invalid data"}), 400
#
#         result = users.update_one({"email": email}, {"$set": data})
#         if result.matched_count == 0:
#             return jsonify({"error": "User not found"}), 404
#
#         return jsonify({"message": "User updated successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
# # DELETE: Delete User by Email
# # ---------------------------------------------
# @app.route('/users/<email>', methods=['DELETE'])
# def delete_user(email):
#     """
#     Delete user by email
#     ---
#     parameters:
#       - name: email
#         in: path
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: User deleted successfully
#       404:
#         description: User not found
#       500:
#         description: Internal server error
#     """
#     try:
#         result = users.delete_one({"email": email})
#         if result.deleted_count == 0:
#             return jsonify({"error": "User not found"}), 404
#
#         return jsonify({"message": "User deleted successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
# # Test MongoDB Connection
# # ---------------------------------------------
# @app.route('/test-db', methods=['GET'])
# def test_db():
#     """
#     Test connection to MongoDB
#     ---
#     responses:
#       200:
#         description: MongoDB connection is successful
#       404:
#         description: Database not found
#       500:
#         description: Internal server error
#     """
#     try:
#         db_names = client.list_database_names()
#         if 'mydatabase' in db_names:
#             return "Connection to MongoDB is successful!", 200
#         else:
#             return "Database not found.", 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
#
# # Run the Application
# # ---------------------------------------------
# if __name__ == '__main__':
#     app.run(port=int(port), debug=True)




# from flask import Flask, request, jsonify
# from pymongo import MongoClient
#
# app = Flask(__name__)
#
# # חיבור ל-MongoDB
# connection_string = "mongodb+srv://danakaplan21:4PSIxzB1nDDWTq2m@eventcluster.c5dy4.mongodb.net/?retryWrites=true&w=majority&appName=eventcluster"
# client = MongoClient(connection_string)
# db = client['mydatabase']
#
# # יצירת הקולקציות
# users = db['users']
#
# # ---------------------------------------------
# # USERS ENDPOINTS
# # ---------------------------------------------
#
# # GET: שליפת כל המשתמשים
# @app.route('/users', methods=['GET'])
# def get_users():
#     try:
#         all_users = list(users.find({}, {'_id': False}))  # הסתרת _id
#         return jsonify(all_users), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # POST: הוספת משתמש חדש
# @app.route('/users', methods=['POST'])
# def create_user():
#     try:
#         data = request.json
#         users.insert_one(data)
#         return jsonify({"message": "User added successfully"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# @app.route('/', methods=['GET'])
# def home():
#     return "API is running"
#
# @app.route('/test-db', methods=['GET'])
# def test_db():
#     try:
#         # בדיקת מסד הנתונים
#         db_names = client.list_database_names()
#         if 'mydatabase' in db_names:
#             return "Connection to MongoDB is successful!", 200
#         else:
#             return "Database not found.", 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/users', methods=['GET'])
# def get_users():
#     try:
#         all_users = list(users.find({}, {'_id': False}))  # שליפת כל המשתמשים
#         if not all_users:
#             return jsonify({"message": "No users found"}), 200
#         return jsonify(all_users), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     try:
#         data = request.json
#         users.insert_one(data)
#         return jsonify({"message": "User added successfully"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # ---------------------------------------------
#
# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from pymongo import MongoClient
#
# app = Flask(__name__)
#
# # חיבור ל-MongoDB
# connection_string = "mongodb+srv://danakaplan21:4PSIxzB1nDDWTq2m@eventcluster.c5dy4.mongodb.net/?retryWrites=true&w=majority&appName=eventcluster"
# client = MongoClient(connection_string)
# db = client['mydatabase']
#
# # יצירת הקולקציות
# users = db['users']
# events = db['events']
# guests = db['guests']
# reminders = db['reminders']
# # ---------------------------------------------
# # USERS ENDPOINTS
# # ---------------------------------------------
#
# # GET: שליפת כל המשתמשים
# @app.route('/users', methods=['GET'])
# def get_users():
#     all_users = list(users.find({}, {'_id': False}))
#     return jsonify(all_users), 200
#
# # POST: הוספת משתמש חדש
# @app.route('/users', methods=['POST'])
# def create_user():
#     data = request.json
#     users.insert_one(data)
#     return jsonify({"message": "User added successfully"}), 201
#
# # ---------------------------------------------
# # EVENTS ENDPOINTS
# # ---------------------------------------------
#
# # GET: שליפת כל האירועים
# @app.route('/events', methods=['GET'])
# def get_events():
#     all_events = list(events.find({}, {'_id': False}))
#     return jsonify(all_events), 200
#
# # POST: יצירת אירוע חדש
# @app.route('/events', methods=['POST'])
# def create_event():
#     data = request.json
#     events.insert_one(data)
#     return jsonify({"message": "Event created successfully"}), 201
#
# # ---------------------------------------------
# # GUESTS ENDPOINTS
# # ---------------------------------------------
#
# # GET: שליפת כל המוזמנים לאירוע מסוים
# @app.route('/guests/<event_id>', methods=['GET'])
# def get_guests(event_id):
#     event_guests = list(guests.find({'event_id': event_id}, {'_id': False}))
#     return jsonify(event_guests), 200
#
# # POST: הוספת מוזמן לאירוע
# @app.route('/guests', methods=['POST'])
# def add_guest():
#     data = request.json
#     guests.insert_one(data)
#     return jsonify({"message": "Guest added successfully"}), 201
#
# # ---------------------------------------------
# # REMINDERS ENDPOINTS
# # ---------------------------------------------
#
# # GET: שליפת תזכורות לאירוע מסוים
# @app.route('/reminders/<event_id>', methods=['GET'])
# def get_reminders(event_id):
#     event_reminders = list(reminders.find({'event_id': event_id}, {'_id': False}))
#     return jsonify(event_reminders), 200
#
# # POST: יצירת תזכורת לאירוע
# @app.route('/reminders', methods=['POST'])
# def create_reminder():
#     data = request.json
#     reminders.insert_one(data)
#     return jsonify({"message": "Reminder created successfully"}), 201
#
# # ---------------------------------------------
#
# @app.route('/users', methods=['GET'])
# def get_users():
#     all_users = list(users.find({}, {'_id': False}))  # מבטיחים שהשדה _id לא ייכלל
#     return jsonify(all_users), 200
#
# if __name__ == '__main__':
#     app.run(debug=True)







# from flask import Flask, render_template
# from pymongo import MongoClient
#
# app = Flask(__name__)
#
#
# connection_string = "mongodb+srv://danakaplan21:4PSIxzB1nDDWTq2m@eventcluster.c5dy4.mongodb.net/?retryWrites=true&w=majority&appName=eventcluster"
#
# # חיבור ל-MongoDB
# client = MongoClient(connection_string)
#
# # התחברות למסד נתונים בשם 'mydatabase'
# db = client['mydatabase']
#
# # יצירת הקולקציות
# users = db['users']
# events = db['events']
# guests = db['guests']
# reminders = db['reminders']
#
# # הוספת משתמש חדש
# users.insert_one({
#     "name": "John Doe",
#     "email": "john.doe@example.com",
#     "password": "hashed_password",
#     "role": "organizer"
# })
#
# # הוספת אירוע חדש
# events.insert_one({
#     "title": "Tech Conference",
#     "description": "A conference about the latest in technology.",
#     "organizer_id": "user123",
#     "date": "2025-03-15T10:00:00",
#     "location": "Tel Aviv"
# })
#
# # הוספת מוזמן
# guests.insert_one({
#     "event_id": "event123",
#     "name": "Alice Johnson",
#     "email": "alice@example.com",
#     "status": "confirmed"
# })
#
# # הוספת תזכורת
# reminders.insert_one({
#     "event_id": "event123",
#     "sent_to": "alice@example.com",
#     "sent_at": "2025-03-14T10:00:00",
#     "status": "sent"
# })