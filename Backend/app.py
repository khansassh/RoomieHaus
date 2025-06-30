from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to call the backend from different origin (e.g., port 8080)

@app.route('/')
def home():
    return jsonify({"message": "RoomieHaus backend is running!"})

@app.route('/api/greeting', methods=['GET'])
def greeting():
    return jsonify({"greeting": "Hello from RoomieHaus backend!"})

# Example POST endpoint
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    # Process data here
    return jsonify({"received": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
