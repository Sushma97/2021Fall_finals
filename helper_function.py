"""
Helper function is a module containing functions to assist the olympic data analysis performed in the jupyter notebook.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def prepare_olympic_dataset(olympic_file_name: str, region_file_name: str) -> tuple:
    """
    This function prepares the required olympics dataframe for analysis from the dataset at
    https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results

    To obtain the country name from country code, the olympic dataframe is merged with noc data
    (contains country code to country name mapping).
    Categorical variables like sex, medal, season are split into individual columns
    We then group by the 'region', 'Year', 'NOC', 'City', 'Sport', 'Event'
    and sum up the other numeric columns for further analysis

    :param olympic_file_name: File name that contains olympics data
    :param region_file_name: File name that contains country to country code mapping
    :return: Final data set with data in required format for analysis and the country code dataset
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
                                            'Medal_Gold': 'sum', 'Season_Summer': 'sum',
                                            'Season_Winter': 'sum'}).reset_index()
    return final_df, noc_df


def prepare_polity_dataset(polity_file_name: str, noc_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function prepares the required political dataframe from the dataset at 
    https://www.systemicpeace.org/polityproject.html
    
    We merge the political data with the country code data to stay consistent with country names
    
    :param polity_file_name: File name of the polity dataset
    :param noc_df: File name of the country code dataset
    :return: Final political dataset for further analysis
    """
    polity = pd.read_excel(polity_file_name, )
    polity = polity[polity.year >= 1890]  # Olympic dataset begins from 1890 while polity dataset from 1776.
    # Hence we consider data from 1890 only
    polity["country"] = polity["country"].str.upper().str.strip()
    # Join the Olympic and polity dataset where country name is same
    polity_dff = polity.merge(noc_df, left_on="country", right_on="region", how="left")
    # Join the Olympic and polity dataset where country code is same
    polity_dff1 = polity_dff.merge(noc_df, left_on="scode", right_on="NOC", how="left")
    # If country in polity dataset is null, then map the country from olympic dataset
    polity_dff1['region_z'] = np.where(polity_dff1['region_x'].isnull(), polity_dff1['region_y'],
                                       polity_dff1['region_x'])
    polity_dff1['NOC_z'] = np.where(polity_dff1['NOC_x'].isnull(), polity_dff1['NOC_y'], polity_dff1['NOC_x'])
    polity_dff1[(polity_dff1['region_x'] != polity_dff1['region_y'])
                & (~polity_dff1['NOC_y'].isnull()) & (polity_dff1['region_x'].isnull())]
    cols = ["scode", "country", "year", "polity", "polity2", "durable", "region_z", "NOC_z"]  # Filter columns
    poltiy_dff2 = polity_dff1[cols]
    # Rename columns
    polity_dff2 = poltiy_dff2.rename(columns={"region_z": "alternate_region", "NOC_z": "alternate_noc"})
    return polity_dff2


def map_polity_region_dataset(country_dict: dict, polity_df: pd.DataFrame, country_mapper: dict) -> pd.DataFrame:
    """
    This function corrects the errors in country mapping in polity dataset and olympic dataset.
    Few country code for same country differ in polity and olympic dataset.
    Hence we correct them using dictionary which has mapping of country name in polity dataset
    to country code in olympic dataset
    :param country_dict: Dictionary of country name in polity dataset and country code of olympic dataset
    :param polity_df: Political dataset
    :param country_mapper: Dictionary of country code to region mapping in olympic dataset
    :return: Political dataset with country errors corrected.
    """
    polity_df.loc[polity_df['alternate_noc'].isnull(), "alternate_noc"] = polity_df['country'].map(
        country_dict)
    polity_dff3 = polity_df[~(polity_df['country'] == 'ORANGE FREE STATE')]
    polity_dff3 = polity_dff3[~(polity_dff3.polity2 == -66)]
    polity_dff3.loc[polity_dff3['alternate_region'].isnull(), "alternate_region"] = polity_dff3['alternate_noc'].map(
        country_mapper)
    return polity_dff3


def correct_team_medals_won(olympics_df: pd.DataFrame, sport_dict: dict) -> pd.DataFrame:
    """
    This function corrects the error in medal won for team games. When a country wins a team games like basketball,
    the olympic dataset considers it as 14 medals won, whereas its just 1 medal win. Hence we correct this issue using
    a dictionary that lists all the olympic team sports.
    :param olympics_df: Olympic dataset
    :param sport_dict: Dictionary with key as the olympic sports and values indicating if its a team sport
    :return: Corrected Olympic dataset
    """
    olympics_df['TeamGame'] = olympics_df.apply(
        lambda x: True if sport_dict[x.Sport] & ('Single' not in x.Event) & ('One' not in x.Event) & (
                'Relay' in x.Event) else False, axis=1)
    olympics_df.loc[(olympics_df.TeamGame is True) & (
            olympics_df.Medal_Bronze > 0), 'Medal_Bronze'] = olympics_df.Medal_Bronze / olympics_df.Name
    olympics_df.loc[
        (olympics_df.TeamGame is True) & (
                olympics_df.Medal_Gold > 0), 'Medal_Gold'] = olympics_df.Medal_Gold / olympics_df.Name
    olympics_df.loc[(olympics_df.TeamGame is True) & (
            olympics_df.Medal_Silver > 0), 'Medal_Silver'] = olympics_df.Medal_Silver / olympics_df.Name
    olympics_df[['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']] = olympics_df[
        ['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']].astype('uint8')
    return olympics_df


def get_polityshift_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function finds out the shift in polity score year after year for each country. A shift of more than
    3 points in polity score in consecutive years, indicate a drastic shift in the country political system.
    :param df: Political dataset
    :return: Political dataset with the shift column added.
    """
    req_df = pd.DataFrame()
    for country in df.country.unique():
        df_processed = df[df['country'] == country]
        df_processed['shift'] = df_processed[df_processed['country'] == country]['polity2'] \
                                - df_processed[df_processed['country'] == country]['polity2'].shift(-1)
        req_df = pd.concat([req_df, df_processed], axis=0)
    return req_df


def plot_country_medal_polity(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int):
    """
    This function plots the medals won by the given country for each year, between the given year range.
    This plot is overlapped with the political score of the given country for each year, between the given year range
    for easy analysis.
    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    agg_dict = {"Medal_Bronze": 'sum', 'Medal_Silver': 'sum', 'Medal_Gold': 'sum', 'polity2': np.mean}
    plot_df = modify_data_for_plot(olympic_df, polity_df, country, start_year, end_year, agg_dict)
    input_list = [["Bronze", "Year", "Medal_Bronze"], ["Silver", "Year", "Medal_Silver"],
                  ["Gold", "Year", "Medal_Gold"]]
    details = ["Medals Won vs Polity Score", "Year", "Medals Won"]
    plot_figure(input_list, plot_df, details)


def modify_data_for_plot(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int, agg_dict: dict) -> pd.DataFrame:
    """
    This function prepares the model to be plotted based on the aggregations mentioned in agg_dict
    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    temp_df = olympic_df.copy(deep=True)
    temp_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_politify.merge(temp_df, left_on="year", right_on="Year", how="left")
    plot_df = plot_df[(plot_df.region == country) & ((plot_df.Year >= start_year) &
                                                     (plot_df.Year <= end_year))].groupby(
        ['Year']).agg(agg_dict) \
        .reset_index()
    return plot_df



def plot_country_medal_to_participants_ratio(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int):
    """
    This function plots the medals won to the participant ratio of the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.

    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    agg_dict = {"TotalMedals": 'sum', "Name": 'sum','polity2': np.mean}
    temp_df = olympic_df.copy(deep=True)
    temp_df['TotalMedals'] = olympic_df.Medal_Bronze + olympic_df.Medal_Silver + olympic_df.Medal_Gold
    plot_df = modify_data_for_plot(temp_df, polity_df, country, start_year, end_year, agg_dict)
    plot_df['medalParticipantRatio'] = round((plot_df.TotalMedals / plot_df.Name) * 100, 2)
    input_list = [["Medal to Participant Ratio", "Year", "medalParticipantRatio"]]
    details = ["Medal to Participant Ratio", "Year", "Medal to Participant Ratio"]
    plot_figure(input_list, plot_df, details)


def plot_country_age_polity(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int):
    """
    This function plots the average age of the participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.


    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    agg_dict = {"Age": 'sum', 'polity2': np.mean}
    plot_df = modify_data_for_plot(olympic_df, polity_df, country, start_year, end_year, agg_dict)
    input_list = [["Average Age", "Year", "Age"]]
    details = ["Average Age vs Polity Score", "Year", "Average Age"]
    plot_figure(input_list, plot_df, details)


def plot_country_season_wise_participants(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int):
    """
    This function plots the season wise participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.


    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    agg_dict = {"Name": 'sum', 'polity2': np.mean,
                       'Season_Summer': 'sum', 'Season_Winter': 'sum'}
    plot_df = modify_data_for_plot(olympic_df, polity_df, country, start_year, end_year, agg_dict)
    input_list = [["Summer Season", "Year", "Season_Summer"], ["Winter Season", "Year", "Season_Winter"]]
    details = ["Number of Participants vs Polity Score", "Year", "Number of Participants"]
    plot_figure(input_list, plot_df, details)


def country_male_female_ratio(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country: str,
                              start_year: int, end_year: int):
    """
    This function plots the male to female ratio of the participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.


    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :return:
    """
    agg_dict = {"Sex_F": 'sum', 'Sex_M': 'sum', 'polity2': np.mean}
    plot_df = modify_data_for_plot(olympic_df, polity_df, country, start_year, end_year, agg_dict)
    input_list = [["Female Participants", "Year", "Sex_F"], ["Male Participants", "Year", "Sex_M"]]
    details = ["Participating gender vs Polity Score", "Year", "Gender of participation"]
    plot_figure(input_list, plot_df, details)


def plot_figure(input_list: list, plot_df: pd.DataFrame, details: list):
    """
    This function plots the figure using plotly library. For the given values in input list,
    it adds a trace in the plot. The plot details like title, x axis and y axis names are fetched from the details list.
    :param input_list: List of values that need to be added as a trace in the graph
    :param plot_df: The dataframe containing values to be plotted
    :param details: List of plot details like title and so on.
    :return:
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # color_list = ['#051c2c','#abe5f0', '#abe5f0', '#abe5f0']
    try:
        for index, value in enumerate(input_list):
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df[value[1]],
                       y=plot_df[value[2]]),
                       # marker_color=color_list[index]),
                secondary_y=False
            )
        fig.add_trace(
            go.Line(x=plot_df["Year"], y=plot_df["polity2"], name="Polity", marker_color='#051c2c'),
            secondary_y=True
        )
        # Add figure title
        fig.update_layout(
            title_text=details[0]
        )

        # Set x-axis title
        fig.update_xaxes(title_text=details[1])

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>"+details[2]+"</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Polity Score</b>", secondary_y=True)
        fig.show()
    except Exception:
        print("There was an error")
