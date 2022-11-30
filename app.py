# Required imports
import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from firebase_admin import credentials, firestore, initialize_app
from haversine import haversine

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
data_ref = db.collection("data")


@app.route("/")
def main():
    return jsonify({"message": "Welcome to v1 of RoadAI's api!"})


@app.route("/api/v1/obstructions", methods=["POST"])
def obstructions():
    if request.method == "POST":
        try:
            data_ref.add(json.loads(request.data))
            return jsonify({"success": True}), 200
        except Exception as e:
            return f"An Error Occurred: {e}"


@app.route("/api/v1/obstructions/near", methods=["GET"])
def get_nearby():
    # Query Args
    latitude = request.args.get("latitude", default=None, type=float)
    longitude = request.args.get("longitude", default=None, type=float)
    radius = request.args.get("radius", default=3, type=float)
    unit = request.args.get("unit", default="mi", type=str)

    try:
        if (longitude == None) or (latitude == None):
            raise Exception("both a longitude and latitude must be provided")
        if radius < 0:
            raise Exception("the desired radius must be a positive value")

        valid_units = set(["km", "mi", "m", "nmi", "ft", "in"])
        if unit not in valid_units:
            raise Exception(f"{unit} is not a valid unit")

        location = (latitude, longitude)
        obstructions = list(data_ref.stream())
        nearby = []

        for obstruction in obstructions:
            obstruction = obstruction.to_dict()
            obstruction_lat = obstruction["location"]["latitude"]
            obstruction_long = obstruction["location"]["longitude"]
            obstruction_location = (obstruction_lat, obstruction_long)
            distance = haversine(location, obstruction_location, unit=unit)
            if distance <= radius:
                nearby.append(obstruction)

        return jsonify(nearby), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route("/api/v1/obstructions/batch", methods=["GET"])
def get_batch():
    batch_size = request.args.get("size", default=5, type=int)
    try:
        obstructions = list(data_ref.stream())
        batch = []
        if (batch_size <= 0) or batch_size > len(obstructions):
            raise Exception(f"the provided batch size {batch_size} is invalid")
        for _ in range(batch_size):
            rand_idx = random.randrange(len(obstructions))
            batch.append(obstructions[rand_idx].to_dict())
            obstructions.pop(rand_idx)
        return jsonify(batch), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route("/delete", methods=["GET", "DELETE"])
def delete():
    """
    delete() : Delete a document from Firestore collection.
    """
    try:
        # Check for ID in URL query
        data_id = request.args.get("id")
        data_ref.document(data_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


port = int(os.environ.get("PORT", 8080))
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=port)
