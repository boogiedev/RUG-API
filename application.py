import os
from os.path import exists
import pandas as pd
from process import calculate
from flask import Flask, Response, jsonify, request
import requests


application = Flask(__name__)

VERSION = 0
API_ROUTE = f'/api/v{VERSION}'

def get_data(n_results:int=5000):
    """
    Route requests data from RUG API and stores processed data (persists until new call)
    """
    # Request from Random User API https://randomuser.me
    response = requests.get(f"https://randomuser.me/api/?results={n_results}")
    data = calculate.convert_data(response.json())
    return data

# Before Request Wrapper
@application.before_request
def create_data():
    path = 'data.pkl'
    file_exists = exists(path)
    global DATA
    if not file_exists:
        DATA = get_data()
        DATA.to_pickle(path)
    else:
        DATA = pd.read_pickle(path)
# Reset Data
@application.route(API_ROUTE + '/reset_data')
def reset_data():
    """
    Resets pickled data
    """
    path = 'data.pkl'
    file_exists = exists(path)
    if file_exists:
        os.remove(path)
    return 'data reset'

# View for data as HTML
@application.route(API_ROUTE + '/view_data')
def view_data():
    """
    Retrieves previous RUG API request and displays cleaned data for verification
    """
    # Retrieve DF Data
    return DATA.to_html()

# Route to get stats in different formats
@application.route(API_ROUTE + '/get_statistics')
def get_statistics():
    """
    Returns statistics generated from data in user specified format (default=json)
    """
    # Generate Stats from Saved DF
    stats = calculate.generate_statistics(DATA)
    # Retrieve ACCEPT
    accept = request.headers.get('Accept')
    print(accept)
    "application/json"
    "text/xml"
    "text/plain"
    "406" # Does not support any other type for accept header
    return data



if __name__ == '__main__':
    application.run(debug=True)
