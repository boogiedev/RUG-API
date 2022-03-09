from process import calculate
from flask import Flask, Response, jsonify, request
import requests


application = Flask(__name__)

VERSION = 0
API_ROUTE = f'/api/v{VERSION}'


# @application.route(API_ROUTE + '/fill_data', methods=['GET'])
def fill_data(n_results:int=5000):
    """
    Route requests data from RUG API and stores processed data (persists until new call)
    """
    # Request from Random User API https://randomuser.me
    response = requests.get(f"https://randomuser.me/api/?results={n_results}")
    data = calculate.convert_data(response.json())
    return data

@application.route(API_ROUTE + '/view_data')
def view_data():
    """
    Retrieves previous RUG API request and displays cleaned data
    """
    # Retrieve DF Data
    data = fill_data()
    return data.to_html()

@application.route(API_ROUTE + '/get_statistics')
def get_statistics():
    """
    Returns statistics generated from data in user specified format (default=json)
    """
    data = 'get from DB'
    # Retrieve ACCEPT
    accept = request.headers.get('Accept')
    print(accept)
    "application/json"
    "text/xml"
    "text/plain"
    "406" # Does not support any other type for accept header
    return data

@application.route(API_ROUTE + '/view_statistics')
def view_statistics():
    """
    Statistics Viewable online
    """
    # Retrieve DF Data
    return 'view statistics'


if __name__ == '__main__':
    application.run(debug=True)
