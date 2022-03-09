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

def generate_statistics(dataframe:pd.DataFrame) -> pd.DataFrame:
    # Meta Data (n_rows)
    # Percentage Female/Male
    # Percentage first names in A-M vs N-Z
    # Percentage last names in A-M vs N-Z
    # Percentage of people in top 10 populous states
    # Percentage of females in each top 10 populous states
    # Percentage of males in each top 10 populous states
    # Percentage of age ranges 0-20 21-40 41-60 61-80 81-100 100+


    pass
