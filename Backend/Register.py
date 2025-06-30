import os
from flask import Flask, request, jsonify, render_template # Added render_template
from firebase_admin import credentials, firestore, initialize_app
import re # Import regex for PIN validation
from flask_cors import CORS # Import CORS for handling cross-origin requests

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, adjust as needed for production

# --- Firebase Initialization ---
# Ensure serviceAccountKey.json is in the same directory or provide its path
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    # Initialize Firebase Admin SDK
    firebase_app = initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # Exit or handle the error appropriately if Firebase fails to initialize
    exit()

# --- Configuration ---
# This mimics the appId used in the frontend's Firestore path.
# In a real scenario, appId might come from an environment variable or config.
# For demonstration, we'll use a placeholder.
# You might want to match this with __app_id from your frontend environment if public data path matters.
FLASK_APP_ID = "default-app-id" # Match this with your frontend's __app_id if possible
USERS_COLLECTION_PATH = "users"

# --- Helper Function for PIN Validation ---
def validate_pin(pin):
    """
    Validates if the PIN is exactly 4 digits.
    """
    return bool(re.fullmatch(r'^\d{4}$', pin))

# --- API Endpoints ---

@app.route('/') # New route to serve the HTML file
def index():
    """
    Serves the main HTML page.
    """
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    """
    Registers a new user with partner names and a 4-digit PIN.
    """
    try:
        data = request.get_json()
        partner1 = data.get('partner1')
        partner2 = data.get('partner2')
        pin = data.get('pin')

        # Input validation
        if not all([partner1, partner2, pin]):
            return jsonify({"message": "Please fill in all fields."}), 400

        if not validate_pin(pin):
            return jsonify({"message": "PIN must be exactly 4 numbers."}), 400

        users_ref = db.collection(USERS_COLLECTION_PATH)

        # Check if a user with these partners already exists
        query_result = users_ref.where('partner1', '==', partner1).where('partner2', '==', partner2).limit(1).get()
        if len(query_result) > 0:
            return jsonify({"message": "Account with these partners already exists. Please sign in."}), 409

        # Add new user to Firestore
        user_data = {
            'partner1': partner1,
            'partner2': partner2,
            'pin': pin, # Store PIN as string
            'registeredAt': firestore.SERVER_TIMESTAMP # Use server timestamp
        }
        users_ref.add(user_data)
        return jsonify({"message": "Registration successful! You can now sign in."}), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login_user():
    """
    Authenticates a user with partner names and a 4-digit PIN.
    """
    try:
        data = request.get_json()
        partner1 = data.get('partner1')
        partner2 = data.get('partner2')
        pin = data.get('pin')

        # Input validation
        if not all([partner1, partner2, pin]):
            return jsonify({"message": "Please fill in all fields."}), 400

        if not validate_pin(pin):
            return jsonify({"message": "PIN must be exactly 4 numbers."}), 400

        users_ref = db.collection(USERS_COLLECTION_PATH)

        # Query for the user by partner names
        query_result = users_ref.where('partner1', '==', partner1).where('partner2', '==', partner2).limit(1).get()

        if len(query_result) == 0:
            return jsonify({"message": "No account found with these partner names. Please register."}), 404

        user_doc = query_result[0]
        user_data = user_doc.to_dict()

        if user_data.get('pin') == pin:
            return jsonify({"message": "Login successful! Welcome to the house."}), 200
        else:
            return jsonify({"message": "Invalid PIN. Please try again."}), 401

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"message": f"Login failed: {str(e)}"}), 500

# --- Run the Flask App ---
if __name__ == '__main__':
    # Flask defaults to 127.0.0.1:5000
    # For production, consider gunicorn or similar WSGI server
    # For development, you can run with `flask run` or `python register.py`
    app.run(debug=True) # debug=True for development, set to False for production
