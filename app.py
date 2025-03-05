from flask import Flask, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000",'https://symmetricitservicespvtltd.netlify.app/']}})

# Initialize Firebase Admin
cred = credentials.Certificate('ServiceAccountViewer.json')
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

@app.route('/data_get', methods=['GET'])
def get_data():
    print("Getting data")
    try:
        # Example: Get all documents from a 'users' collection
        users_ref = db.collection('Building-Technology-Products')
        docs = users_ref.stream()
        
        users = []
        for doc in docs:
            users.append({
                'id': doc.id,
                **doc.to_dict()
            })
        
        return jsonify({
            'status': 'success',
            'data': users
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        print("Getting stats")
        # Example: Get statistics from a 'statistics' collection
        stats_ref = db.collection('Building-Technology-Products')
        docs = stats_ref.stream()
        
        stats = []
        for doc in docs:
            stats.append({
                'id': doc.id,
                **doc.to_dict()
            })
        
        print(stats)
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting server")
    app.run(debug=True, port=5001) 