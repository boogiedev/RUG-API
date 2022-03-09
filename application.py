from dict2xml import dict2xml
import os
from os.path import exists
import numpy as np
import pandas as pd
from process import calculate
from flask import abort, Flask, Response, jsonify, request, jsonify
import requests


application = Flask(__name__)

VERSION = 0
API_ROUTE = f"/api/v{VERSION}"

"Calculation"


def generate_statistics(df: pd.DataFrame) -> dict:
    print("Generating statistics")
    # Meta Data (n_rows)
    total_entries = df.shape[0]
    get_total_per = lambda x, total=total_entries: round(x / total * 100, 2)
    stats_dict = {}
    # Percentage Female/Male
    per_female, per_male = (
        get_total_per(df[df["gender"] == "female"].shape[0]),
        get_total_per(df[df["gender"] == "male"].shape[0]),
    )
    stats_dict["Percentage Female vs Male"] = {"female": per_female, "male": per_male}

    # Percentage first names in A-M vs N-Z
    first_name_AM, first_name_NZ = (
        get_total_per(df[df["first"].str.count(r"(^[a-mA-M].*)") == 1].shape[0]),
        get_total_per(df[df["first"].str.count(r"(^[n-zN-Z].*)") == 1].shape[0]),
    )
    stats_dict["Percentage first names in A-M vs N-Z"] = {
        "A-M": first_name_AM,
        "N-Z": first_name_NZ,
    }

    # Percentage last names in A-M vs N-Z
    last_name_AM, last_name_NZ = (
        get_total_per(df[df["last"].str.count(r"(^[a-mA-M].*)") == 1].shape[0]),
        get_total_per(df[df["last"].str.count(r"(^[n-zN-Z].*)") == 1].shape[0]),
    )
    stats_dict["Percentage last names in A-M vs N-Z"] = {
        "A-M": last_name_AM,
        "N-Z": last_name_NZ,
    }

    # Percentage of people in top 10 populous states
    top_s = df["state"].value_counts()[:10].index.tolist()
    state_group = df[df["state"].isin(top_s)].groupby("state")
    sorted_states = sorted(state_group, key=lambda x: x[1].shape[0], reverse=True)
    per_people_state = [
        (state, get_total_per(group.shape[0])) for state, group in sorted_states
    ]
    stats_dict["Percentage people in top 10 populous states"] = {
        state: val for state, val in per_people_state
    }

    # Percentage of females in each top 10 populous states
    females_per_top_states = [
        (
            state,
            get_total_per(group[group["gender"] == "female"].shape[0], group.shape[0]),
        )
        for state, group in sorted_states
    ]
    stats_dict["Percentage females in top 10 populous states"] = {
        state: val for state, val in females_per_top_states
    }

    # Percentage of males in each top 10 populous states
    males_per_top_states = [
        (
            state,
            get_total_per(group[group["gender"] == "male"].shape[0], group.shape[0]),
        )
        for state, group in sorted_states
    ]
    stats_dict["Percentage males in top 10 populous states"] = {
        state: val for state, val in males_per_top_states
    }

    # Percentage of age ranges 0-20 21-40 41-60 61-80 81-100 100+
    labels = ["0-20", "21-40", "41-60", "61-80", "81-100", "100+"]
    age_bins = [0, 20, 40, 60, 80, 100, np.inf]
    df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=labels)
    age_counts = df["age_group"].value_counts().sort_index()
    percent_ages = [
        (idx, get_total_per(val)) for idx, val in zip(age_counts.index, age_counts)
    ]
    stats_dict["Percentage of age ranges"] = {state: val for state, val in percent_ages}
    return stats_dict


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
    df = pd.read_pickle("data.pkl")
    stats = generate_statistics(df)
    # Retrieve ACCEPT
    accept = request.headers.get("Accept")
    res = stats
    if "application/json" in accept:
        print("Returning JSON")
        # res = json.dumps(stats, indent=4)
        res = jsonify(stats)
    elif ("text/xml" in accept) or ("application/xml" in accept):
        print("Returning XML")
        res = Response(dict2xml(stats, wrap="root", indent="   "), mimetype="text/xml")
    elif "text/plain" in accept:
        print("Returning PLAIN")
        res = Response(stats, mimetype="text/plain")
    else:  # 406
        abort(406)
    return res


if __name__ == "__main__":
    application.run(debug=True)
