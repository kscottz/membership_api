from flask import request, Response, jsonify
from flask import Flask
from flask_cors import CORS
from membership.web.members import member_api

app = Flask(__name__)
CORS(app)
app.register_blueprint(member_api)


@app.route('/health', methods=["GET"])
def health_check():
    return jsonify({'health': True})