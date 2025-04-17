from flask import jsonify, request
from db import tambah_data, ambil_semua_data
import os
import requests
from dotenv import load_dotenv
load_dotenv()

def init_routes(app):

    UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
    DEVICE_LABEL = "sensor_suhu"  # Sesuaikan dengan device di Ubidots

    def send_to_ubidots(data):
        """Helper function untuk mengirim data ke Ubidots"""
        url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
        headers = {
            "X-Auth-Token": UBIDOTS_TOKEN,
            "Content-Type": "application/json"
        }
        
        try:
            payload = {
                "temperature": {"value": data.get("temperature")},
                "humidity": {"value": data.get("humidity")}
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending to Ubidots: {str(e)}")
            return False


    @app.route("/")
    def home():
        return "Backend Flask + MongoDB!"

    @app.route("/tambah", methods=["POST"])
    def tambah():
        data = request.json
        ubidots_status = send_to_ubidots(data)
        print(ubidots_status)
        id_baru = tambah_data(data)
        return jsonify({"status": "sukses", "id": id_baru})

    @app.route("/data", methods=["GET"])
    def data():
        semua_data = ambil_semua_data()
        return jsonify(semua_data)