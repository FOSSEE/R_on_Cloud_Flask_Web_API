from config import *
import subprocess
import flask
from flask import send_file
from flask import Flask, url_for, jsonify, request
import json
import os
import os.path
import base64
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
        user_id = req_data["user_id"]
        user_dir = TEMP_DIR + user_id
        R_file_id = req_data["R_file_id"]
        code = req_data["code"]
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        file_path = user_dir + '/' + R_file_id + '.R'
        plot_path = user_dir + '/' + R_file_id + '.png'
        f = open(file_path, "w")
        #add png file path
        f.write('png("{0}");\n'.format(plot_path))
        f.write('\n')
        f.write(code)
        f.write('\n')
        f.write("while (!is.null(dev.list()))  dev.off()")
        f.close()
        processed_data = subprocess.Popen(['Rscript', file_path],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        ret_data, err = processed_data.communicate()
        is_plot = str(os.path.isfile(plot_path))
        plot_path_req = API_URL_PLOT + '?user_id=' + user_id + '&R_file_id=' + R_file_id
        response_body = {
            "data": ret_data.decode("utf-8"),
            "error": err.decode("utf-8"),
            "is_plot": is_plot,
            "plot_path_req": plot_path_req
        }
        result = jsonify(response_body)
        return result

    else:

        # The request body wasn't JSON so return a 400 HTTP status code
        return "Request was not JSON", 400

@app.route('/plot', methods=['GET', 'POST'])
def get_plot():
    user_id = request.args.get('user_id')
    R_file_id = request.args.get('R_file_id')
    user_dir = TEMP_DIR + user_id
    plot_path = user_dir + '/' + R_file_id + '.png'
    try:
        return send_file(plot_path, mimetype='image/png', as_attachment=True)
    except Exception as e:
        print("Error generated in")

if __name__ == '__main__':
    if (PRODUCTION == True):
        app.run(debug = False)
    else:
        app.run(debug = True)

    app.run(port=HTTP_PORT, host=HTTP_HOST)