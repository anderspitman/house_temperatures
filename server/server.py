from flask import Flask, jsonify, request
from pymongo import MongoClient
from urllib.parse import quote_plus, unquote_plus
from datetime import datetime
import json


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


db = DbManager().get_db()

@app.route('/upload_interval/')
def upload_interval():
    return str(60) 

@app.route('/readings/<int:sensor_id>', methods=['POST'])
def reading(sensor_id):
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
