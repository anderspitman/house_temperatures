import os
import json
from flask import Flask, send_from_directory, jsonify, request
from pymongo import MongoClient
from urllib.parse import quote_plus, unquote_plus
from datetime import datetime
from pprint import pprint


app = Flask(__name__)

class DbManager(object):
    def __init__(self):
        # For this to work make sure the following auth.json file exists:
        # {
        #   "user": "USERNAME",
        #   "pwd": "PASSWORD"
        # }
        with open('auth.json') as json_file:
            auth = json.load(json_file)

        # takes care of special characters in password
        user = quote_plus(auth['user'])
        password = quote_plus(auth['pwd'])
        server_address = 'localhost'

        uri = "mongodb://{}:{}@{}/sensors_db/?authMechanism={}&authSource={}".format(
                user, password, server_address, 'DEFAULT', 'admin')

        client = MongoClient(uri)
        self._db = client.sensors_db

    def get_db(self):
        return self._db


#client_dir = os.path.join(os.pardir, 'client')
client_dir = os.getcwd()

db = DbManager().get_db()

@app.route('/')
def index():
    return send_from_directory(client_dir, 'index.html')

@app.route('/<filename>')
def get_static_file(filename):
    return send_from_directory(client_dir, filename)

@app.route('/upload_interval/')
def upload_interval():
    return str(60) 

@app.route('/readings')
def readings_all():

    pipeline = [
        {
            # Collect readings by sensor_id
            '$group': {
                '_id': '$sensor_id',
                'readings': {
                    '$push': {
                        'temperature_celsius': '$temperature_celsius',
                        'humidity': '$humidity',
                        'datetime': '$datetime',
                    }
                }
            }
        },
        {
            # Rename _id to sensor_id
            '$project': {
                '_id': 0,
                'sensor_id': '$_id',
                'readings': 1
            }
        },
        {
            # Sort ascending by sensor_id
            '$sort': { 'sensor_id': 1 }
        }
    ]

    cursor = db.readings_collection.aggregate(pipeline)

    results = [ reading for reading in cursor ]

    return jsonify(results)

@app.route('/readings/<int:sensor_id>', methods=['GET', 'POST'])
def readings(sensor_id):

    if request.method == 'GET':

        query = {
            'sensor_id': sensor_id
        }

        cursor = db.readings_collection.find(query)

        results = []
        for reading in cursor:
            result = {
                'sensor_id': sensor_id,
                'temperature_celsius': reading['temperature_celsius'],
                'humidity': reading['humidity'],
                'datetime': reading['datetime'],
            }
            results.append(result)

        return jsonify(results)

    elif request.method == 'POST':
        #print(request.form['title'])
        print(request.json)

        data = request.json

        reading = {
            'sensor_id': sensor_id,
            'temperature_celsius': data['temperature_celsius'],
            'humidity': data['humidity'],
            'datetime': datetime.now().isoformat(),
        }
        db.readings_collection.insert_one(reading)

        return "OK"

if __name__ == '__main__':

    db.sensors_collection.find_one()

    app.run(host='0.0.0.0', port=5001)
