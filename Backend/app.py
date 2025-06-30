from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app
import re

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Firebase Initialization ---
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    exit()

# --- Helper Function for PIN Validation ---
def validate_pin(pin):
    return bool(re.fullmatch(r'^\d{4}$', pin))

USERS_COLLECTION_PATH = "users" 

# --- HTML Page Routes ---
@app.route('/')
def landing_page():
    return render_template('homepage.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/landing-page')
def landing_page_route():
    return render_template('landingpage.html')

# --- API Endpoints ---

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        partner1 = data.get('partner1')
        partner2 = data.get('partner2')
        pin = data.get('pin')

        print(f"Received registration data: {partner1}, {partner2}, {pin}")

        if not all([partner1, partner2, pin]):
            print("Some fields are empty.")
            return jsonify({"message": "Please fill in all fields."}), 400

        if not validate_pin(pin):
            print("Invalid PIN format.")
            return jsonify({"message": "PIN must be exactly 4 numbers."}), 400

        # Create a unique document ID by combining partner names
        # It's good practice to normalize this (e.g., lowercase, remove spaces/special chars)
        doc_id = f"{partner1.lower()}_{partner2.lower()}"
        
        users_ref = db.collection(USERS_COLLECTION_PATH)
        
        # Check if a user with this specific document ID (combination of partners) already exists
        # This check is now redundant if you are overwriting with .set(), but good for uniqueness check logic
        existing_doc = users_ref.document(doc_id).get()
        if existing_doc.exists:
            print(f"User with ID {doc_id} already exists.")
            return jsonify({"message": "Account with these partners already exists. Please sign in."}), 409

        # --- IMPORTANT CHANGE HERE ---
        # Use .document(doc_id).set() to specify the document ID
        user_data = {
            'partner1': partner1,
            'partner2': partner2,
            'pin': pin,
            'registeredAt': firestore.SERVER_TIMESTAMP
        }
        users_ref.document(doc_id).set(user_data) # Using set() with custom ID
        print(f"User {doc_id} added successfully to Firestore.")
        return jsonify({"message": "Registration successful!"}), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        partner1 = data.get('partner1')
        partner2 = data.get('partner2')
        pin = data.get('pin')

        if not all([partner1, partner2, pin]):
            return jsonify({"message": "Please fill in all fields."}), 400

        if not validate_pin(pin):
            return jsonify({"message": "PIN must be exactly 4 numbers."}), 400

        # Reconstruct the doc_id to fetch the specific document for login
        doc_id = f"{partner1.lower()}_{partner2.lower()}"
        users_ref = db.collection(USERS_COLLECTION_PATH)
        
        # Fetch the document directly using the custom ID
        user_doc = users_ref.document(doc_id).get()

        if not user_doc.exists: # Check if the document exists
            return jsonify({"message": "No account found. Please register."}), 404

        user_data = user_doc.to_dict()

        if user_data.get('pin') == pin:
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"message": "Invalid PIN."}), 401

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"message": f"Login failed: {str(e)}"}), 500

# --- Run the Flask App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
