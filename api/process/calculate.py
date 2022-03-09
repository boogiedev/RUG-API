import numpy as np
import pandas as pd
import us

def convert_data(res_json:dict) -> pd.DataFrame:
    # Derive Results Array
    results = res_json.get('results')
    # Normalize and Flatten to DF while extracting needed columns
    fields = ['gender', 'name.first', 'name.last', 'location.state', 'dob.age']
    df = pd.json_normalize(results)[fields]
    # Filter for US States
    states = list(map(lambda x: x.name.lower(), us.states.STATES))
    df_filter = df[df['location.state'].str.lower().isin(states)].reset_index(drop=True)
    # Rename all columns for cleanliness
    new_fields = ['gender', 'first', 'last', 'state', 'age']
    df_filter.rename(columns={field:new for field, new in zip(fields, new_fields)}, inplace=True)

    # Verify
    df_filter.info()

    return df_filter

def generate_statistics(df:pd.DataFrame) -> pd.DataFrame:
    # Meta Data (n_rows)
    total_entries = df.shape[0]
    get_total_per = lambda x, total=total_entries: round(x/total * 100, 2)
    stats_dict = {}
    # Percentage Female/Male
    per_female, per_male = get_total_per(df[df['gender'] == 'female'].shape[0]), get_total_per(df[df['gender'] == 'male'].shape[0])
    stats_dict['Percentage Female vs Male'] = {
    'female' : per_female,
    'male' : per_male
    }

    # Percentage first names in A-M vs N-Z
    first_name_AM, first_name_NZ = get_total_per(df[df['first'].str.count(r'(^[a-mA-M].*)')==1].shape[0]), get_total_per(df[df['first'].str.count(r'(^[n-zN-Z].*)')==1].shape[0])
    stats_dict['Percentage first names in A-M vs N-Z'] = {
    'A-M' : first_name_AM,
    'N-Z' : first_name_NZ
    }

    # Percentage last names in A-M vs N-Z
    last_name_AM, last_name_NZ = get_total_per(df[df['last'].str.count(r'(^[a-mA-M].*)')==1].shape[0]), get_total_per(df[df['last'].str.count(r'(^[n-zN-Z].*)')==1].shape[0])
    stats_dict['Percentage last names in A-M vs N-Z'] = {
    'A-M' : last_name_AM,
    'N-Z' : last_name_NZ
    }

    # Percentage of people in top 10 populous states
    top_s = df['state'].value_counts()[:10].index.tolist()
    state_group = df[df['state'].isin(top_s)].groupby('state')
    sorted_states = sorted(state_group, key=lambda x: x[1].shape[0], reverse=True)
    per_people_state = [(state, get_total_per(group.shape[0])) for state, group in sorted_states]
    stats_dict['Percentage people in top 10 populous states'] = {
    state: val for state, val in per_people_state
    }

    # Percentage of females in each top 10 populous states
    females_per_top_states = [(state, get_total_per(group[group['gender'] == 'female'].shape[0], group.shape[0])) for state, group in sorted_states]
    stats_dict['Percentage females in top 10 populous states'] = {
    state: val for state, val in females_per_top_states
    }

    # Percentage of males in each top 10 populous states
    males_per_top_states = [(state, get_total_per(group[group['gender'] == 'male'].shape[0], group.shape[0])) for state, group in sorted_states]
    stats_dict['Percentage males in top 10 populous states'] = {
    state: val for state, val in males_per_top_states
    }

    # Percentage of age ranges 0-20 21-40 41-60 61-80 81-100 100+
    labels = ['0-20', '21-40', '41-60', '61-80', '81-100', '100+']
    age_bins = [0, 20, 40, 60, 80, 100, np.inf]
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=labels)
    age_counts = df['age_group'].value_counts().sort_index()
    percent_ages = [(idx, get_total_per(val)) for idx, val in zip(age_counts.index, age_counts)]
    stats_dict['Percentage of age ranges'] = {
    state: val for state, val in percent_ages
    }

    return stats_dict
