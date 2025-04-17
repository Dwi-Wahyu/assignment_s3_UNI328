from flask import Flask
from routes import init_routes
from config import Config

# Inisialisasi Flask
app = Flask(__name__)

# Setup routes
init_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)