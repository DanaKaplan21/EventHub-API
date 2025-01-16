
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
    """
    Retrieve all users from the database with a limit to avoid timeouts.
    ---
    responses:
      200:
        description: Returns a list of users
      500:
        description: Internal server error
    """
    try:
        # בדיקת חיבור למסד הנתונים
        if users is None:
            print("[ERROR] Database connection failed")
            return jsonify({"error": "Database connection failed"}), 500

        print("[INFO] Querying users collection...")

        # הגבלת מספר המשתמשים המוחזרים ל-10
        all_users = list(users.find({}, {'_id': False}).limit(10))

        # בדיקה אם אין משתמשים במסד הנתונים
        if not all_users:
            print("[INFO] No users found in the database")
            return jsonify({"message": "No users found"}), 200

        print(f"[INFO] Successfully retrieved {len(all_users)} users")
        return jsonify(all_users), 200

    except Exception as e:
        # טיפול בשגיאה כללית
        print(f"[ERROR] Error while querying users: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500



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

