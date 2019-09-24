from config import *
import subprocess
import flask
from flask import Flask, url_for, jsonify, request
import json
import os
import re
from os.path import abspath, dirname, exists, isfile, join, splitext
import config

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

app = Flask(__name__)


@app.route('/')
def api_root():
    return 'Welcome'


@app.route('/rscript', methods=['GET', 'POST'])
def get_data():
    # Validate the request body contains JSON
    if request.is_json:

        # Parse the JSON into a Python dictionary

        req_data = json.loads(request.get_json())
        user_dir = TEMP_DIR + req_data["user_id"]
        code = req_data["code"]
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        file_path = user_dir + '/' + req_data["R_file_id"] + '.R'
        f = open(file_path, "w")
        f.write(code)
        f.close()
        processed_data = subprocess.Popen(['Rscript', file_path],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        ret_data, err = processed_data.communicate()
        response_body = {
            "data": ret_data.decode("utf-8"),
            "error": err.decode("utf-8")
        }
        result = jsonify(response_body)
        return result

    else:

        # The request body wasn't JSON so return a 400 HTTP status code
        return "Request was not JSON", 400


if __name__ == '__main__':
    app.run(debug=True)
