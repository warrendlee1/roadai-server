# app.py

# Required imports
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from firebase_admin import credentials, firestore, initialize_app

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
data_ref = db.collection('data')

@app.route('/')
def main():
    return 'ROAD AI API'

@app.route('/api/v1/obstructions', methods=['POST'])
def obstructions():
    if (request.method == 'POST'):
        try:
            data_ref.add(json.loads(request.data))
            return jsonify({"success": True}), 200
        except Exception as e:
            return f"An Error Occurred: {e}"

@app.route('/api/v1/obstructions/near', methods=['GET'])
def batch():
    # Query Args
    batch_size = request.args.get('batch-size', default = 1, type = int)
    radius = request.args.get('radius', default=5, type=int)
    longitude = request.args.get('longitude', default = 0.0, type = float)
    latitude = request.args.get('latitude', default = 0.0, type = float)

    # Calculated Vars
    max_longitude = longitude + (radius * 0.02) # given 5 miles = 0.1 degrees
    min_longitude = longitude - (radius * 0.02)
    max_latitude = latitude + (radius * 0.02)
    min_latitude = latitude - (radius * 0.02)
    
    try:
        filtered_longitude = data_ref.where('location.longitude', "<=", max_longitude).where('location.longitude', ">=", min_longitude).stream()
        filtered_latitude = []
        for doc in filtered_longitude:
            doc = doc.to_dict()
            if (doc['location']['latitude'] <= max_latitude and doc['location']['latitude'] >= min_latitude):
                if len(filtered_latitude) < batch_size:
                    filtered_latitude.append(doc)
        return {'success': filtered_latitude}, 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        # Check for ID in URL query
        data_id = request.args.get('id')
        data_ref.document(data_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)