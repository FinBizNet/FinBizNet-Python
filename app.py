# this is the main class used to create a web application
from flask import Flask
from flask_cors import CORS

from routes.smartapi_routes import smartapi_bp

# creates an instance of a class
app = Flask(__name__)  
CORS(app) 

app.register_blueprint(smartapi_bp, url_prefix="/api") 

if __name__ == "__main__":
    print("Flask server is starting on http://localhost:5001")
    app.run(debug=True, port=5001)
