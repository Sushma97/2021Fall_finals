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
    Categorical variables like sex, medal, season are split into individual columns
    We then groupby the 'region', 'Year', 'NOC', 'City', 'Sport', 'Event'
    and sum up the other numeric columns for further analysis

    :param olympic_file_name: File name that contains olympics data
    :param region_file_name: File name that contains country to country code mapping
    :return: Final data set with data in required format for analysis
    """
    olympic_df = pd.read_csv(olympic_file_name)
    noc_df = pd.read_csv(region_file_name)
    olympic_df["Team"] = olympic_df["Team"].str.upper()
    noc_df["region"] = noc_df["region"].str.upper()
    olympic_noc = olympic_df.merge(noc_df, left_on="NOC", right_on="NOC", how="inner")
    olympic_noc = pd.get_dummies(olympic_noc, columns=["Sex", "Medal", "Season"])
    final_df = olympic_noc.groupby(['region', 'Year', 'NOC', 'City', 'Sport', 'Event'
                                    ]).agg({"Age": np.mean,
                                            "Name": 'count',
                                            'Sex_F': 'sum',
                                            'Sex_M': 'sum',
                                            'Medal_Bronze': 'sum',
                                            'Medal_Silver': 'sum',
                                            'Medal_Gold': 'sum', 'Season_Summer':'sum', 'Season_Winter':'sum'}).reset_index()
    return final_df, noc_df


def prepare_polity_dataset(polity_file_name, noc_df):
    """

    :param polity_file_name:
    :param noc_df:
    :return:
    """
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


def map_polity_region_dataset(country_dict, polity_df, country_mapper):
    polity_df.loc[polity_df['alternate_noc'].isnull(), "alternate_noc"] = polity_df['country'].map(
        country_dict)
    polity_dff3 = polity_df[~(polity_df['country'] == 'ORANGE FREE STATE')]
    polity_dff3 = polity_dff3[~(polity_dff3.polity == -66)]
    polity_dff3.loc[polity_dff3['alternate_region'].isnull(), "alternate_region"] = polity_dff3['alternate_noc'].map(
        country_mapper)
    return polity_dff3


def correct_team_medals_won(olympics_df, sport_dict):
    olympics_df['TeamGame'] = olympics_df.apply(
        lambda x: True if sport_dict[x.Sport] & ('Single' not in x.Event) & ('One' not in x.Event) & (
                'Relay' in x.Event) else False, axis=1)
    olympics_df.loc[(olympics_df.TeamGame == True) & (
            olympics_df.Medal_Bronze > 0), 'Medal_Bronze'] = olympics_df.Medal_Bronze / olympics_df.Name
    olympics_df.loc[
        (olympics_df.TeamGame == True) & (
                olympics_df.Medal_Gold > 0), 'Medal_Gold'] = olympics_df.Medal_Gold / olympics_df.Name
    olympics_df.loc[(olympics_df.TeamGame == True) & (
            olympics_df.Medal_Silver > 0), 'Medal_Silver'] = olympics_df.Medal_Silver / olympics_df.Name
    olympics_df[['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']] = olympics_df[
        ['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']].astype('uint8')
    return olympics_df

def get_polityshift_column(df):
    req_df = pd.DataFrame()
    for country in df.country.unique():
        df_processed = df[df['country'] == country]
        df_processed['shift'] = df_processed[df_processed['country'] == country]['polity2'] - df_processed[df_processed['country'] == country]['polity2'].shift(-1)
        req_df = pd.concat([req_df, df_processed], axis=0)
        df_processed = pd.DataFrame()
    return req_df

def get_polityshift_column(df):
    req_df = pd.DataFrame()
    for country in df.country.unique():
        df_processed = df[df['country'] == country]
        df_processed['shift'] = df_processed[df_processed['country'] == country]['polity2'] - \
                                df_processed[df_processed['country'] == country]['polity2'].shift(-1)
        req_df = pd.concat([req_df, df_processed], axis=0)
        df_processed = pd.DataFrame()
    return req_df

def plot_country_medal_polity(olympic_df, polity_df, country, start_year, end_year):
    temp_df = olympic_df[(olympic_df.region == country) & ((olympic_df.Year >= start_year) &
                                                           (olympic_df.Year <= end_year))].groupby(
        ['Year'])['Medal_Bronze', 'Medal_Silver', 'Medal_Gold'].agg('sum').reset_index()
    temp_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_politify.merge(temp_df, left_on="year", right_on="Year", how="left")
    input_list = [["Bronze","Year","Medal_Bronze"],["Silver","Year","Medal_Silver"],["Gold","Year","Medal_Gold"]]
    details = ["Medals Won vs Polity Score","Year","Medals Won"]
    plot_figure(input_list, plot_df, details)



def plot_country_medal_to_participants_ratio(olympic_df, polity_df, country, start_year, end_year):
    temp_df = olympic_df.copy(deep=True)
    temp_df['TotalMedals'] = olympic_df.Medal_Bronze + olympic_df.Medal_Silver + olympic_df.Medal_Gold
    temp_df = temp_df[(temp_df.region == country) & ((temp_df.Year >= start_year) &
                                                           (temp_df.Year <= end_year))].groupby(
        ['Year'])['TotalMedals','Name'].agg('sum').reset_index()
    temp_df['medalParticipantRatio'] = round((temp_df.TotalMedals/temp_df.Name) * 100,2)
    temp_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_politify.merge(temp_df, left_on="year", right_on="Year", how="left")
    input_list = [["Medal to Participant Ratio","Year","medalParticipantRatio"]]
    details = ["Medal to Participant Ratio","Year","Medal to Participant Ratio"]
    plot_figure(input_list, plot_df, details)


def plot_country_age_polity(olympic_df, polity_df, country, start_year, end_year):
    temp_age_df = olympic_df[(olympic_df.region == country) & ((olympic_df.Year >= start_year) &
                                                               (olympic_df.Year <= end_year))].groupby(
        ['Year'])['Age'].agg(np.mean).reset_index()

    temp_age_politify = polity_df[polity_df['alternate_region'] == country]

    plot_df = temp_age_politify.merge(temp_age_df, left_on="year", right_on="Year", how="left")
    input_list = [["Average Age", "Year", "Age"]]
    details = ["Average Age vs Polity Score", "Year", "Average Age"]
    plot_figure(input_list, plot_df, details)


def plot_country_season_wise_participants(olympic_df, polity_df, country, start_year, end_year):
    temp_season_df = olympic_df.copy(deep=True)
    temp_season_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_season_politify.merge(temp_season_df, left_on="year", right_on="Year", how="left")
    plot_df = plot_df[(plot_df.region == country) & ((plot_df.Year >= start_year) &
                                                                  (plot_df.Year <= end_year))].groupby(
        ['Year']).agg({"Name": 'sum', 'polity2': np.mean,
                       'Season_Summer': 'sum', 'Season_Winter': 'sum'}).reset_index()
    input_list = [["Summer Season", "Year", "Season_Summer"], ["Winter Season", "Year", "Season_Winter"]]
    details = ["Number of Participants vs Polity Score", "Year", "Number of Participants"]
    plot_figure(input_list, plot_df, details)


def country_male_female_ratio(olympic_df, polity_df, country, start_year, end_year):
    temp_mf_df = olympic_df.copy(deep=True)
    temp_mf_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_mf_politify.merge(temp_mf_df, left_on="year", right_on="Year", how="left")
    plot_df = plot_df[(plot_df.region == country) & ((plot_df.Year >= start_year) &
                                                     (plot_df.Year <= end_year))].groupby(
        ['Year']).agg({"Sex_F":'sum','Sex_M': 'sum', 'polity2': np.mean}).reset_index()
    input_list = [["Female Participants", "Year", "Sex_F"], ["Male Participants", "Year", "Sex_M"]]
    details = ["Participating gender vs Polity Score", "Year", "Gender of participation"]
    plot_figure(input_list, plot_df, details)

def plot_figure(input_list, plot_df, details):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # color_list = ['#051c2c','#abe5f0', '#abe5f0', '#abe5f0']
    for index,value in enumerate(input_list):
        fig.add_trace(
            go.Bar(name=value[0],
                   x=plot_df[value[1]],
                   y=plot_df[value[2]],),
                   # marker_color=color_list[index]),
            secondary_y=False
        )
    fig.add_trace(
        go.Line(x=plot_df["Year"], y=plot_df["polity2"], name="Polity"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text=details[0],
    )

    # Set x-axis title
    fig.update_xaxes(title_text=details[1])

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>"+details[2]+"</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Polity Score</b>", secondary_y=True)
    fig.show()
