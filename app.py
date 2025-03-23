from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://symmetricitservicespvtltd.netlify.app,'https://www.symmetricit.in/','https://symmetricit.in/']}})

# Initialize Firebase Admin based on environment
if os.getenv('ENVIRONMENT') == 'prod':
    # Use default credentials in production
    firebase_admin.initialize_app()
else:
    # Use service account file in development
    cred = credentials.Certificate('../ServiceAccountViewer.json')
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

@app.route('/get_products', methods=['POST'])
def get_data():
    print("Getting data")
    try:
        # Get product type from request body
        request_data = request.get_json()
        product_type = request_data.get('product_type')
        
        if not product_type:
            return jsonify({
                'status': 'error',
                'message': 'product_type is required in request body'
            }), 400
        
        # Query the collection based on product type
        products_ref = db.collection(product_type.replace(' ', '-'))
        docs = products_ref.stream()
        
        products = []
        for doc in docs:
            products.append({
                'id': doc.id,
                **doc.to_dict()
            })
        
        return jsonify({
            'status': 'success',
            'data': products
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health_check', methods=['GET'])
def health_check():
    try:
        print("Health check log")
        return jsonify({
            'status': 'success',
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting server")
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)