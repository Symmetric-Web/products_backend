from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://symmetricitservicespvtltd.netlify.app",'https://www.symmetricit.in/','https://symmetricit.in/']}})


@app.route('/get_products', methods=['POST'])
def get_data():
    print("Getting data")
    try:
        # Get product type from request body
        request_data = request.get_json()
        product_type = request_data.get('product_type')
        with open(f"json_data/{product_type}.json","r") as filename:
            result = json.load(filename)
        print("hi")
        
        
        return jsonify({
            'status': 'success',
            'data': result
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
    app.run(host='0.0.0.0', port=8080)