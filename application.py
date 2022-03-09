from dict2xml import dict2xml
import os
from os.path import exists
import pandas as pd
from process import calculate
import json
from flask import abort, Flask, Response, jsonify, request
import requests


application = Flask(__name__)

VERSION = 0
API_ROUTE = f"/api/v{VERSION}"

"Helpers"
def get_data(n_results: int = 5000):
    """
    Route requests data from RUG API and stores processed data (persists until new call)
    """
    # Request from Random User API https://randomuser.me
    response = requests.get(f"https://randomuser.me/api/?results={n_results}")
    data = calculate.convert_data(response.json())
    return data


"Internal"
# Before Request Wrapper
@application.before_request
def create_data():
    path = "data.pkl"
    file_exists = exists(path)
    global DATA
    if not file_exists:
        DATA = get_data()
        DATA.to_pickle(path)
    else:
        DATA = pd.read_pickle(path)


# Reset Data
@application.route(API_ROUTE + "/reset_data")
def reset_data():
    """
    Resets pickled data
    """
    path = "data.pkl"
    file_exists = exists(path)
    if file_exists:
        os.remove(path)
    temp = f"""
    <div>
        <h2> Data Reset </h2>
        <h4> Endpoints: </h4>
        <a href="/api/v0/view_data"><p> View Data </p></a>
        <a href="/api/v0/get_statistics"><p> Get Statistics </p></a>
    </div>
    """
    return temp


"Routes"
# View for data as HTML
@application.route("/")
def home():
    """
    Home Page
    """
    base_uri = "/api/v0/"
    endpoints = ["view_data", "get_statistics", "reset_data"]
    temp = f"""
    <div>
        <h1> RUG API </h1>
        <p> Access API via {base_uri} </p>
        <p> Endpoints: {", ".join(endpoints)} </p>
        <a href="/api/v0/view_data"><p> View Data </p></a>
        <a href="/api/v0/reset_data"><p> Reset Data </p></a>
        <a href="/api/v0/get_statistics"><p> Get Statistics </p></a>
    </div>
    """
    return temp


# View for data as HTML
@application.route(API_ROUTE + "/view_data")
def view_data():
    """
    Retrieves previous RUG API request and displays cleaned data for verification
    """
    # Retrieve DF Data
    return DATA.to_html()


# Route to get stats in different formats
@application.route(API_ROUTE + "/get_statistics")
def get_statistics():
    """
    Returns statistics generated from data in user specified format (default=json)
    """
    # NOTE: Better to use decorators here for each mime-type but in lieu of time, doing hard match
    # Generate Stats from Saved DF
    stats = calculate.generate_statistics(DATA)
    print(stats)
    # Retrieve ACCEPT
    accept = request.headers.get("Accept")
    print(accept)
    res = None
    if "application/json" in accept:
        res = json.dumps(stats, indent=4)
    elif ("text/xml" in accept) or ('application/xml' in accept):
        res = dict2xml(stats, wrap ='root', indent ="   ")
        print(res)
    elif "text/plain" in accept:
        res = 'plain'
    else: # 406
        abort(406)
    return res


if __name__ == "__main__":
    application.run(debug=True)
