import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def prepare_olympic_dataset(olympic_file_name, region_file_name):
    """
    This function prepares the required olympics dataframe for analysis from the dataset at
    https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results

    To obtain the country name from country code, the olympic dataframe is merged with noc data
    (contains country code to country name mapping).

    :param olympic_file_name:
    :param region_file_name:
    :return:
    """
    olympic_df = pd.read_csv(olympic_file_name)
    noc_df = pd.read_csv(region_file_name)
    olympic_df["Team"] = olympic_df["Team"].str.upper()
    noc_df["region"] = noc_df["region"].str.upper()
    olympic_noc = olympic_df.merge(noc_df, left_on="NOC", right_on="NOC", how="inner")
    olympic_noc = pd.get_dummies(olympic_noc, columns=["Sex", "Medal"])
    final_df = olympic_noc.groupby(['region', 'Year', 'NOC', 'City', 'Sport', 'Event'
                                    ]).agg({"Age": np.mean,
                                            "Name": 'count',
                                            'Sex_F': 'sum',
                                            'Sex_M': 'sum',
                                            'Medal_Bronze': 'sum',
                                            'Medal_Silver': 'sum',
                                            'Medal_Gold': 'sum'}).reset_index()
    return final_df, noc_df


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


def correct_team_medals_won(olympics_df, sport_dict):
    olympics_df['TeamGame'] = olympics_df.apply(
        lambda x: True if sport_dict[x.Sport] & ('Single' not in x.Event) & ('One' not in x.Event) & (
                'Relay' in x.Event) else False, axis=1)
    olympics_df.loc[(olympics_df.TeamGame == True) & (
            olympics_df.Medal_Bronze > 0), 'Medal_Bronze'] = olympics_df.Medal_Bronze / olympics_df.Name
    olympics_df.loc[
        (olympics_df.TeamGame == True) & (
                    olympics_df.Medal_Gold > 0), 'Medal_Gold>'] = olympics_df.Medal_Gold / olympics_df.Name
    olympics_df.loc[(olympics_df.TeamGame == True) & (
            olympics_df.Medal_Silver > 0), 'Medal_Silver'] = olympics_df.Medal_Silver / olympics_df.Name
    olympics_df[['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']] = olympics_df[
        ['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']].astype('uint8')
    return olympics_df


def plot_country_medal_polity(olympic_df, polity_df, country, start_year, end_year):
    temp_df = olympic_df[(olympic_df.region == country) & ((olympic_df.Year >= start_year) &
                                                           (olympic_df.Year <= end_year))].groupby(
        ['Year'])['Medal_Bronze', 'Medal_Silver', 'Medal_Gold'].agg('sum').reset_index()
    temp_politify = polity_df[polity_df['country'] == country]
    plot_df = temp_politify.merge(temp_df, left_on="year", right_on="Year", how="left")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=plot_df["Year"], y=plot_df["Medal_Bronze"], name="Bronze"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=plot_df["Year"], y=plot_df["Medal_Silver"], name="Silver"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=plot_df["Year"], y=plot_df["Medal_Gold"], name="Gold"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Line(x=plot_df["year"], y=plot_df["polity2"], name="Polity"),
        secondary_y=False,
    )
    fig.update_layout(
        title_text="Medals Won vs Polity Score",
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Year")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Medals Won</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Polity Score</b>", secondary_y=True)
    fig.show()
