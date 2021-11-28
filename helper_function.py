import pandas as pd
import numpy as np

def prepare_olympic_dataset( olympic_file_name, region_file_name):
    """
    This function prepares the required olympics dataframe for analysis from the dataset at
    https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results

    To obtain the country name from country code, the olympic dataframe is merged with noc data
    (contains country code to country name mapping).

    :param olympic_file_name:
    :param region_file_name:
    :return:
    """
    dff = pd.read_csv(olympic_file_name)
    noc = pd.read_csv(region_file_name)
    dff["Team"] = dff["Team"].str.upper()
    noc["region"] = noc["region"].str.upper()
    dff_noc = dff.merge(noc, left_on="NOC", right_on="NOC", how="inner")
    dff_noc = pd.get_dummies(dff_noc, columns=["Sex", "Medal"])
    final_df = dff_noc.groupby(['region', 'Year', 'NOC', 'City', 'Sport'
                                ]).agg({"Age": np.mean,
                                        "Name": 'count',
                                        'Sex_F': 'sum',
                                        'Sex_M': 'sum',
                                        'Medal_Bronze': 'sum',
                                        'Medal_Silver': 'sum',
                                        'Medal_Gold': 'sum'}).reset_index()
    return final_df, noc

def prepare_polity_dataset(polity_file_name, noc_df):
    polity = pd.read_excel(polity_file_name, )
    polity = polity[polity.year >= 1890]
    polity["country"] = polity["country"].str.upper()
    polity_dff = polity.merge(noc_df, left_on="country", right_on="region", how="left")
    polity_dff1 = polity_dff.merge(noc_df, left_on="scode", right_on="NOC", how="left")
    polity_dff1['region_z'] = np.where(polity_dff1['region_x'].isnull(), polity_dff1['region_y'],
                                       polity_dff1['region_x'])
    polity_dff1['NOC_z'] = np.where(polity_dff1['NOC_x'].isnull(), polity_dff1['NOC_y'], polity_dff1['NOC_x'])
    polity_dff1[(polity_dff1['region_x'] != polity_dff1['region_y'])
                & (~polity_dff1['NOC_y'].isnull()) & (polity_dff1['region_x'].isnull())]
    cols = ["scode", "country", "year", "polity", "polity2", "durable", "region_z", "NOC_z"]
    poltiy_dff2 = polity_dff1[cols]
    polity_dff2 = poltiy_dff2.rename(columns={"region_z": "alternate_region", "NOC_z": "alternate_noc"})
    return polity_dff2

def map_polity_region_dataset(country_dict, polity_df):
    polity_df.loc[polity_df['alternate_noc'].isnull(), "alternate_noc"] = polity_df['country'].map(
        country_dict)
    polity_dff3 = polity_df[~(polity_df['country'] == 'ORANGE FREE STATE')]
    polity_dff3 = polity_dff3[~(polity_dff3.polity == -66)]
    return polity_dff3



