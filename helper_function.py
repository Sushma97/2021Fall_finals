"""
Helper function is a module containing functions to assist the olympic data analysis performed in the jupyter notebook.
"""
from multiprocessing import Process
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import constants
warnings.filterwarnings('ignore')

# TODO: LEGEND off, add constants file


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

    >>> prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    (             region  Year  NOC  ... Medal_Gold Season_Summer Season_Winter
    0       AFGHANISTAN  1936  AFG  ...          0           1.0             0
    1       AFGHANISTAN  1936  AFG  ...          0           1.0             0
    2       AFGHANISTAN  1936  AFG  ...          0           1.0             0
    3       AFGHANISTAN  1936  AFG  ...          0          13.0             0
    4       AFGHANISTAN  1948  AFG  ...          0          11.0             0
    ...             ...   ...  ...  ...        ...           ...           ...
    114145     ZIMBABWE  2016  ZIM  ...          0           1.0             0
    114146     ZIMBABWE  2016  ZIM  ...          0           1.0             0
    114147     ZIMBABWE  2016  ZIM  ...          0           1.0             0
    114148     ZIMBABWE  2016  ZIM  ...          0           1.0             0
    114149     ZIMBABWE  2016  ZIM  ...          0           1.0             0
    <BLANKLINE>
    [114150 rows x 15 columns],      NOC       region                 notes
    0    AFG  AFGHANISTAN                   NaN
    1    AHO      CURACAO  Netherlands Antilles
    2    ALB      ALBANIA                   NaN
    3    ALG      ALGERIA                   NaN
    4    AND      ANDORRA                   NaN
    ..   ...          ...                   ...
    225  YEM        YEMEN                   NaN
    226  YMD        YEMEN           South Yemen
    227  YUG       SERBIA            Yugoslavia
    228  ZAM       ZAMBIA                   NaN
    229  ZIM     ZIMBABWE                   NaN
    <BLANKLINE>
    [230 rows x 3 columns])

    >>> prepare_olympic_dataset("athlete.csv", "noc_regions.csv")
    File not found. Please enter the correct file name
    """
    try:

        olympic_df = pd.read_csv(olympic_file_name)
        noc_df = pd.read_csv(region_file_name)
    except FileNotFoundError:
        print("File not found. Please enter the correct file name")
        return
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

    >>> noc = pd.read_csv("noc_regions.csv")
    >>> prepare_polity_dataset("p5v2018.xls", noc)
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
              scode      country  year  ...  durable  alternate_region alternate_noc
    0       AFG  AFGHANISTAN  1890  ...      NaN       Afghanistan           AFG
    1       AFG  AFGHANISTAN  1891  ...      NaN       Afghanistan           AFG
    2       AFG  AFGHANISTAN  1892  ...      NaN       Afghanistan           AFG
    3       AFG  AFGHANISTAN  1893  ...      NaN       Afghanistan           AFG
    4       AFG  AFGHANISTAN  1894  ...      NaN       Afghanistan           AFG
    ...     ...          ...   ...  ...      ...               ...           ...
    13413   ZIM     ZIMBABWE  2014  ...        1          Zimbabwe           ZIM
    13414   ZIM     ZIMBABWE  2015  ...        2          Zimbabwe           ZIM
    13415   ZIM     ZIMBABWE  2016  ...        3          Zimbabwe           ZIM
    13416   ZIM     ZIMBABWE  2017  ...        4          Zimbabwe           ZIM
    13417   ZIM     ZIMBABWE  2018  ...        5          Zimbabwe           ZIM
    <BLANKLINE>
    [13418 rows x 8 columns]

    >>> prepare_polity_dataset("p5v2013.xls", noc)
    File not found. Please enter the correct file name
    """
    try:
        polity = pd.read_excel(polity_file_name, )
    except FileNotFoundError:
        print("File not found. Please enter the correct file name")
        return
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
    cols = ["scode", "country", "year", "polity", "polity2", "durable", "region_z", "NOC_z"]  # Filter columns
    poltiy_dff2 = polity_dff1[cols]
    # Rename columns
    polity_dff2 = poltiy_dff2.rename(columns={"region_z": "alternate_region", "NOC_z": "alternate_noc"})
    return polity_dff2


def handle_countries_that_split(countries: dict, olympic_df: pd.DataFrame, noc_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function corrects the olympic dataset for countries that have split up during the war
    :param countries: Dictionary of countries that have split up with key as the country code and value as the
    country name
    :param olympic_df: Olympic dataset
    :param noc_df: Country code dataset
    :return: Corrected olympic dataset

    >>> olympic_df_test = pd.read_csv("athlete_events.csv")
    >>> countries_test = {"GDR":"GERMANY EAST"}
    >>> noc_df_test = pd.read_csv("noc_regions.csv")
    >>> handle_countries_that_split(countries_test, olympic_df_test, noc_df_test)
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
                    ID                      Name  ... Medal  region
    0            1                 A Dijiang  ...   NaN     NaN
    1            2                  A Lamusi  ...   NaN     NaN
    2            3       Gunnar Nielsen Aaby  ...   NaN     NaN
    3            4      Edgar Lindenau Aabye  ...  Gold     NaN
    4            5  Christine Jacoba Aaftink  ...   NaN     NaN
    ...        ...                       ...  ...   ...     ...
    271111  135569                Andrzej ya  ...   NaN     NaN
    271112  135570                  Piotr ya  ...   NaN     NaN
    271113  135570                  Piotr ya  ...   NaN     NaN
    271114  135571        Tomasz Ireneusz ya  ...   NaN     NaN
    271115  135571        Tomasz Ireneusz ya  ...   NaN     NaN
    <BLANKLINE>
    [271116 rows x 16 columns]
    """
    for key, value in countries.items():
        olympic_df.loc[olympic_df["NOC"] == key, "region"] = value
        noc_df.loc[noc_df["NOC"] == key, "region"] = value
    return olympic_df


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
    >>> mapper = { 'BIH': 'BOSNIA AND HERZEGOVINA'}
    >>> noc_df = pd.read_csv("noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> country_dict_test = {'BOSNIA': 'BIH'}
    >>> polity_df_test = map_polity_region_dataset(country_dict_test, polity_df_test, mapper)
    >>> polity_df_test[polity_df_test.country == 'BOSNIA']
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
             scode country  year  ...  durable        alternate_region alternate_noc
    1378   BOS  BOSNIA  1992  ...        0  BOSNIA AND HERZEGOVINA           BIH
    ...
    1404   BOS  BOSNIA  2018  ...        0  BOSNIA AND HERZEGOVINA           BIH
    <BLANKLINE>
    [27 rows x 8 columns]

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

    >>> olympic_df, noc = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> sport_dict_test = {'Rugby': True, \
    'Alpinism':False, 'Speed Skating':False, 'Ice Hockey':True, 'Nordic Combined':False, \
    'Rhythmic Gymnastics':False, 'Short Track Speed Skating':False, 'Baseball':True, \
    'Softball':True, 'Tug-Of-War':True, 'Ski Jumping':False, 'Lacrosse':True, 'Curling':True, \
       'Military Ski Patrol':True, 'Cricket':True, 'Croquet':False, 'Motorboating':True, \
     'Basque Pelota':False, 'Aeronautics':False, 'Jeu De Paume':False, 'Racquets':False, \
       'Roque':False, 'Athletics':False, 'Hockey':True, 'Football':True, 'Wrestling': False, 'Boxing':False, \
       'Judo':False, \
     'Taekwondo':False, 'Shooting':False, 'Weightlifting':False, 'Swimming':True, 'Cycling':False, \
   'Alpine Skiing':False, 'Gymnastics':False, 'Fencing':False, 'Handball':True, 'Tennis':True, \
  'Volleyball':True, 'Rowing':True, 'Table Tennis':True, 'Trampolining':False, \
 'Cross Country Skiing':False, 'Badminton':False, 'Sailing':True, 'Bobsleigh':True, \
 'Archery':False, 'Canoeing':False, 'Snowboarding':False, 'Biathlon':False, 'Basketball':True, \
      'Beach Volleyball':True, 'Figure Skating':False, 'Polo':True, 'Equestrianism':True, \
  'Water Polo':True, 'Art Competitions':False, 'Modern Pentathlon':False, 'Diving':False, \
     'Luge':False, 'Freestyle Skiing':False, 'Triathlon':False, 'Skeleton':False, \
      'Synchronized Swimming':True, 'Golf':False, 'Rugby Sevens':True    }
    >>> olympic_df = correct_team_medals_won(olympic_df, sport_dict_test)
    >>> olympic_df[olympic_df.Sport == 'Rugby']
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
                   region  Year  NOC  ... Season_Summer Season_Winter TeamGame
    2671    AUSTRALIA  1908  ANZ  ...          15.0             0     True
    ...
    107476        USA  1924  USA  ...          19.0             0     True
    <BLANKLINE>
    [12 rows x 16 columns]

    """
    olympics_df['TeamGame'] = olympics_df.apply(
        lambda x: True if ((sport_dict[x.Sport]) & ('Single' not in x.Event) & ('One' not in x.Event) | (
                'Relay' in x.Event)) else False, axis=1)
    olympics_df.loc[((olympics_df.TeamGame == True) & (
            olympics_df.Medal_Bronze > 0)), "Medal_Bronze"] = olympics_df.Medal_Bronze / olympics_df.Name
    olympics_df.loc[
        (olympics_df.TeamGame == True) & (
                olympics_df.Medal_Gold > 0), 'Medal_Gold'] = olympics_df.Medal_Gold / olympics_df.Name
    olympics_df.loc[(olympics_df.TeamGame == True) & (
            olympics_df.Medal_Silver > 0), 'Medal_Silver'] = olympics_df.Medal_Silver / olympics_df.Name
    olympics_df[['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']] = olympics_df[
        ['Medal_Bronze', 'Medal_Gold', 'Medal_Silver']].astype('uint8')
    return olympics_df


def plot_country_medal_polity(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                              start_year: int, end_year: int, flag):
    """
    This function plots the medals won by the given country for each year, between the given year range.
    This plot is overlapped with the political score of the given country for each year, between the given year range
    for easy analysis.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of country medal polity for the two countries in the list.

    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> plot_country_medal_polity(olympic_df_test, polity_df_test, ['UK', 'FRANCE'], 1929, 2010, 'GDP')
    =================================================================================================
    >>> plot_country_medal_polity(olympic_df_test, polity_df_test, 'UK', 1929, 2010, 'Polity score')
    =================================================================================================
    >>> plot_country_medal_polity(olympic_df_test, polity_df_test, 'UK', 1929, 2010, 'Polity score')
    =================================================================================================

    """
    if type(country) == str:
        country = [country]
    label = constants.NUMBER_LABEL
    agg_dict = {"Medal_Bronze": 'sum', 'Medal_Silver': 'sum', 'Medal_Gold': 'sum', 'polity2': np.mean, 'value': np.mean}
    input_list = [["Bronze", "Year", "Medal_Bronze"], ["Silver", "Year", "Medal_Silver"],
                  ["Gold", "Year", "Medal_Gold"]]
    details = ["Medals Won vs "+flag.upper(), "Year", "Medals Won"]
    plot_df1 = modify_data_for_plot(olympic_df, polity_df, country[0], start_year, end_year, agg_dict)
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(olympic_df, polity_df, country[1], start_year, end_year, agg_dict)
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list, plot_df1, plot_df2, details, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list, plot_df1, plot_df2, details, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list, plot_df1, details, label, flag)
    print("=================================================================================================")


def modify_data_for_plot(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                         start_year: int, end_year: int, agg_dict: dict) -> pd.DataFrame:
    """
    This function prepares the model to be plotted based on the aggregations mentioned in agg_dict
    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param agg_dict: The values to aggregate the dataset on
    :return: The dataset with values to be plotted
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> modify_data_for_plot(olympic_df_test, polity_df_test, 'KOREA', 1929, 2010, {})
    ... # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError
    """
    if country not in olympic_df.region.unique():
        print("The given string country does not exist in the list")
        raise ValueError
    temp_df = olympic_df.copy(deep=True)
    temp_politify = polity_df[polity_df['alternate_region'] == country]
    plot_df = temp_politify.merge(temp_df, left_on="year", right_on="Year", how="left")
    plot_df = plot_df[(plot_df.region == country) & ((plot_df.Year >= start_year) &
                                                     (plot_df.Year <= end_year))].groupby(
        ['Year']).agg(agg_dict) \
        .reset_index()

    return plot_df


def plot_perc_of_medals_to_participant(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                                       start_year: int, end_year: int, flag: str):
    """
    This function plots the % of medals won by total participant in each country by each year.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of % of medals won by total participant for the two countries in the list.
    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    """
    if type(country) == str:
        country = [country]
    label = constants.PERCENTAGE_LABEL
    agg_dict1 = {"Medal_Bronze": 'sum', "Medal_Silver": 'sum', "Medal_Gold": 'sum', "Name": 'sum', 'polity2': np.mean,
                 'value': np.mean}
    input_list1 = [["Bronze", "Year", "Bronze_perc"], ["Silver", "Year", "Silver_perc"],
                   ["Gold", "Year", "Gold_perc"]]
    details1 = ["Medals Won as a % of Total Participants vs "+flag.upper(), "Year", "Medals Won"]
    temp_df = olympic_df.copy(deep=True)
    plot_df1 = modify_data_for_plot(temp_df, polity_df, country[0], start_year, end_year, agg_dict1)
    plot_df1["Bronze_perc"] = round((plot_df1["Medal_Bronze"] / plot_df1["Name"]), 2)
    plot_df1["Silver_perc"] = round((plot_df1["Medal_Silver"] / plot_df1["Name"]), 2)
    plot_df1["Gold_perc"] = round((plot_df1["Medal_Gold"] / plot_df1["Name"]), 2)
    cols = ["Year", "Bronze_perc", "Silver_perc", "Gold_perc", "polity2", "value"]
    plot_df3 = plot_df1[cols]
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(olympic_df, polity_df, country[1], start_year, end_year, agg_dict1)
        plot_df2["Bronze_perc"] = round((plot_df2["Medal_Bronze"] / plot_df2["Name"]), 2)
        plot_df2["Silver_perc"] = round((plot_df2["Medal_Silver"] / plot_df2["Name"]), 2)
        plot_df2["Gold_perc"] = round((plot_df2["Medal_Gold"] / plot_df2["Name"]), 2)
        plot_df4 = plot_df2[cols]
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list1, plot_df3, plot_df4, details1, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list1, plot_df3, plot_df4, details1, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list1, plot_df3, details1, label, flag)
    print("=================================================================================================")


def plot_country_medal_to_participants_ratio(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                                             start_year: int, end_year: int, flag: str):
    """
    This function plots the medals won to the participant ratio of the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of medals won to participant ratio for the two countries in the list.

    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> plot_country_medal_to_participants_ratio(olympic_df_test, polity_df_test, ['UK', 'FRANCE'], 1929, 2010,\
    'POLITY SCORE')
    =================================================================================================
    """
    if type(country) == str:
        country = [country]
    label = constants.NUMBER_LABEL
    agg_dict = {"TotalMedals": 'sum', "Name": 'sum', 'polity2': np.mean, 'value': np.mean}
    temp_df = olympic_df.copy(deep=True)
    temp_df['TotalMedals'] = olympic_df.Medal_Bronze + olympic_df.Medal_Silver + olympic_df.Medal_Gold
    plot_df1 = modify_data_for_plot(temp_df, polity_df, country[0], start_year, end_year, agg_dict)
    plot_df1['medalParticipantRatio'] = round((plot_df1.TotalMedals / plot_df1.Name) * 100, 2)
    input_list = [["Medal to Participants Ratio", "Year", "medalParticipantsRatio"]]
    details = ["Medal to Participants Ratio", "Year", "Medal to Participants Ratio"]
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(temp_df, polity_df, country[1], start_year, end_year, agg_dict)
        plot_df2['medalParticipantRatio'] = round((plot_df2.TotalMedals / plot_df2.Name) * 100, 2)
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list, plot_df1, plot_df2, details, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list, plot_df1, plot_df2, details, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list, plot_df1, details, label, flag)
    print("=================================================================================================")


def plot_country_age_polity(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                            start_year: int, end_year: int, flag: str):
    """
    This function plots the average age of the participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of country age for the two countries in the list.


    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> plot_country_age_polity(olympic_df_test, polity_df_test, 'UK', 1929, 2010, 'GDP')
    =================================================================================================
    """
    if type(country) == str:
        country = [country]
    label = constants.NUMBER_LABEL
    agg_dict = {"Age": 'mean', 'polity2': np.mean, 'value': np.mean}
    plot_df1 = modify_data_for_plot(olympic_df, polity_df, country[0], start_year, end_year, agg_dict)
    input_list = [["Average Age", "Year", "Age"]]
    details = ["Average Age vs "+flag.upper(), "Year", "Average Age"]
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(olympic_df, polity_df, country[1], start_year, end_year, agg_dict)
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list, plot_df1, plot_df2, details, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list, plot_df1, plot_df2, details, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list, plot_df1, details, label, flag)
    print("=================================================================================================")


def plot_country_season_wise_participants(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                                          start_year: int, end_year: int, flag: str):
    """
    This function plots the season wise participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of season wise for the two countries in the list.

    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> plot_country_season_wise_participants(olympic_df_test, polity_df_test, ['UK','FRANCE'], 1929, 2010, 'dummy')
    ENTER THE CORRECT METRIC !
    =================================================================================================
    """
    if type(country) == str:
        country = [country]
    label = constants.NUMBER_LABEL
    agg_dict = {"Name": 'sum', 'polity2': np.mean,
                'Season_Summer': 'sum', 'Season_Winter': 'sum', 'value': np.mean}
    plot_df1 = modify_data_for_plot(olympic_df, polity_df, country[0], start_year, end_year, agg_dict)
    input_list = [["Summer Season", "Year", "Season_Summer"], ["Winter Season", "Year", "Season_Winter"]]
    details = ["Number of Participants vs "+flag.upper(), "Year", "Number of Participants"]
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(olympic_df, polity_df, country[1], start_year, end_year, agg_dict)
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list, plot_df1, plot_df2, details, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list, plot_df1, plot_df2, details, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list, plot_df1, details, label, flag)
    print("=================================================================================================")


def country_male_female_ratio(olympic_df: pd.DataFrame, polity_df: pd.DataFrame, country,
                              start_year: int, end_year: int, flag: str):
    """
    This function plots the male to female ratio of the participants in olympic from the given country for each year,
    between the given year range. This plot is overlapped with the political score of the given country for each year,
    between the given year range for easier analysis.
    The flag varaible controls if it's GDP plot along with polity plot.
    The plot can be for a single country or two countries can be compared together. If the country variable is a list,
    it plots subplot of male to female ratio for the two countries in the list.


    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> country_male_female_ratio(olympic_df_test, polity_df_test, 'UK', 1929, 2010, 'Polity score')
    =================================================================================================
    """
    if type(country) == str:
        country = [country]
    label = constants.NUMBER_LABEL
    agg_dict = {"Sex_F": 'sum', 'Sex_M': 'sum', 'polity2': np.mean, 'value': np.mean}
    plot_df1 = modify_data_for_plot(olympic_df, polity_df, country[0], start_year, end_year, agg_dict)
    input_list = [["Female Participants", "Year", "Sex_F"], ["Male Participants", "Year", "Sex_M"]]
    details = ["Participating Gender vs "+flag.upper(), "Year", "Gender of participation"]
    if len(country) > 2:
        print("YOU CAN GIVE ONLY TWO COUNTRIES AT A TIME")
        raise
    if len(country) == 2:
        plot_df2 = modify_data_for_plot(olympic_df, polity_df, country[1], start_year, end_year, agg_dict)
        if flag.upper() == constants.GDP:
            plot_gdp_subplot(input_list, plot_df1, plot_df2, details, country, label)
        elif flag.upper() == constants.POLITY_SCORE:
            plot_subplot(input_list, plot_df1, plot_df2, details, country, label)
        else:
            print(constants.CORRECT_METRIC_ERROR)
    else:
        plot_figure(input_list, plot_df1, details, label, flag)
    print("=================================================================================================")


def plot_figure(input_list: list, plot_df: pd.DataFrame, details: list, axis: str, flag: str):
    """
    This function plots the figure using plotly library. For the given values in input list,
    it adds a trace in the plot. The plot details like title, x axis and y axis names are fetched from the details list.
    :param input_list: List of values that need to be added as a trace in the graph
    :param plot_df: The dataframe containing values to be plotted
    :param details: List of plot details like title and so on.
    :param axis: Variable to indicate if y axis is a count or a percentage
    :param flag: Variable to indicate if it's polity score plot or GDP plot
    :return:
    >>> input_list_test = [["Female Participants", "Year", "Sex_F"], ["Male Participants", "Year", "Sex_M"]]
    >>> details_test = ["Participating gender vs Polity Score", "Year", "Gender of participation"]
    >>> plot_df_test = pd.read_csv("noc_regions.csv")
    >>> plot_figure(input_list_test, plot_df_test, details_test, 'percentage', 'GDP')
    There was an error in plotting graph
    """
    if flag == constants.GDP:
        fig = make_subplots(rows=1, cols=2, specs=[[{"secondary_y": True}, {"secondary_y": True}]])
    else:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ['#ffa500', '#3cb371', '#4169e1', '#abe5f0']
    try:
        for index, value in enumerate(input_list):
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df[value[1]],
                       y=plot_df[value[2]], marker_color=color_list[index]), row=1, col=1,
                secondary_y=False
            )
            if flag == constants.GDP:
                fig.add_trace(
                    go.Bar(name=value[0],
                           x=plot_df[value[1]],
                           y=plot_df[value[2]], marker_color=color_list[index], showlegend=False), row=1, col=2,
                    secondary_y=False
                )
        fig.add_trace(
            go.Line(x=plot_df["Year"], y=plot_df["polity2"], name="Polity (-10 to +10)", marker_color='#051c2c'),
            row=1, col=1, secondary_y=True
        )
        if flag == constants.GDP:
            fig.add_trace(
                go.Line(x=plot_df["Year"], y=plot_df["value"], name="GDP x 10^9 USD", marker_color='#051c2c'),
                row=1, col=2, secondary_y=True
            )
        # Add figure title
        fig.update_layout(
            title_text=details[0])

        # Set x-axis title
        fig.update_xaxes(title_text=details[1])
        if axis == constants.PERCENTAGE_LABEL:
            fig['layout']['yaxis1']['tickformat'] = ',.0%'
        else:
            pass
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>"+details[2]+"</b>", secondary_y=False)
        fig['layout']['yaxis2']['title'] = '<b>Polity</b>'
        if flag == constants.GDP:
            fig['layout']['yaxis4']['title'] = '<b>GDP measure</b>'
        fig.show()
    except Exception:
        print("There was an error in plotting graph")


def plot_subplot(input_list: list, plot_df: pd.DataFrame, plot_df2: pd.DataFrame, details: list,
                 name_of_countries: list, axis: str):
    """
    This function plots the two figure side by side for each country using plotly library. For the given values in input
    list, it adds a trace in the plot. The plot details like title, x axis and y axis names are fetched from the details
    list.
    :param input_list: List of values that need to be added as a trace in the graph
    :param plot_df: The dataframe containing values to be plotted
    :param plot_df2: The dataframe for another country, containing values to be plotted
    :param details: List of plot details like title and so on.
    :param name_of_countries: List of countries to be plot side by side for better comparison
    :param axis: Variable to indicate if y axis is a count or a percentage
    :return:
    """
    fig = make_subplots(rows=1, cols=2, subplot_titles=(name_of_countries[0], name_of_countries[1]),
                        specs=[[{"secondary_y": True}, {"secondary_y": True}]])
    color_list = ['#8b4513', '#808080', '#ffd700', '#abe5f0']
    try:
        for index, value in enumerate(input_list):
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df[value[1]],
                       y=plot_df[value[2]], marker_color=color_list[index]), row=1, col=1,

                secondary_y=False
            )
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df2[value[1]],
                       y=plot_df2[value[2]], marker_color=color_list[index], showlegend=False), row=1, col=2,

                secondary_y=False
            )
        fig.add_trace(
            go.Line(x=plot_df["Year"], y=plot_df["polity2"], name="Polity", marker_color='#051c2c'),
            row=1, col=1,
            secondary_y=True
        )
        fig.add_trace(
            go.Line(x=plot_df2["Year"], y=plot_df2["polity2"], name="Polity", marker_color='#051c2c', showlegend=False),
            row=1, col=2,
            secondary_y=True
        )

        # Add figure title
        fig.update_layout(
            title_text=details[0], width=1050, height=400
        )

        # Set x-axis title
        fig.update_xaxes(title_text=details[1])
        if axis == constants.PERCENTAGE_LABEL:
            fig['layout']['yaxis1']['tickformat'] = ',.0%'
            fig['layout']['yaxis3']['tickformat'] = ',.0%'
        else:
            pass

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>" + details[2] + "</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Polity Score</b>", secondary_y=True)
        fig.show()
    except Exception:
        print("There was an error in plotting graph")


def plot_graphs_for_country(olympic_df, polity_df, country, start_year, end_year, flag):
    """
    This function plots details regarding olympics, politics and GDP for different metrics like Medals, Geneder ratio,
    Number of participants etc., It employs parallel processing to make the plots perform better.
    >>> olympic_df_test, noc_df = prepare_olympic_dataset("athlete_events.csv", "noc_regions.csv")
    >>> polity_df_test = prepare_polity_dataset("p5v2018.xls", noc_df)
    >>> polity_df_test = map_polity_gdp(polity_df_test, "Mapper_GDP.xlsx", "WEOOct2021all_new.xlsx")
    >>> plot_graphs_for_country(olympic_df_test, polity_df_test, 'UK', 1929, 2010, 'Polity score')
    ... # doctest: +ELLIPSIS
    =================================================================================================
    ...
    =================================================================================================

    :param olympic_df: Olympics dataset
    :param polity_df: Political dataset
    :param country: Country for which the results to be plotted
    :param start_year: The start year for the plot
    :param end_year: The end year for the plot
    :param flag: variable to indicate if it's polity score plot or GDP plot
    :return:
    """
    perform_parallel(plot_country_medal_polity(olympic_df, polity_df, country, start_year, end_year, flag),
                     plot_perc_of_medals_to_participant(olympic_df, polity_df, country, start_year, end_year, flag),
                     plot_country_medal_to_participants_ratio(olympic_df, polity_df, country, start_year, end_year,
                                                              flag),
                     plot_country_age_polity(olympic_df, polity_df, country, start_year, end_year, flag),
                     country_male_female_ratio(olympic_df, polity_df, country, start_year, end_year, flag),
                     plot_country_season_wise_participants(olympic_df, polity_df, country, start_year, end_year, flag))


def plot_gdp_subplot(input_list: list, plot_df: pd.DataFrame, plot_df2: pd.DataFrame, details: list,
                     name_of_countries: list, axis: str):
    """
    This function plots the two figure side by side for each country using plotly library. For the given values in input
    list, it adds a trace in the plot. The plot details like title, x axis and y axis names are fetched from the details
     list.
    :param input_list: List of values that need to be added as a trace in the graph
    :param plot_df: The dataframe containing values to be plotted
    :param plot_df2: The dataframe for second country
    :param details: List of plot details like title and so on.
    :param name_of_countries: List of countries to plot side by side
    :param axis: Variable to indicate if y axis is a count or a percentage
    :return:
    """
    fig = make_subplots(rows=1, cols=2, subplot_titles=(name_of_countries[0], name_of_countries[1]),
                        specs=[[{"secondary_y": True}, {"secondary_y": True}]])
    color_list = ['#8b4513', '#808080', '#ffd700', '#abe5f0']
    try:
        for index, value in enumerate(input_list):
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df[value[1]],
                       y=plot_df[value[2]], marker_color=color_list[index]), row=1, col=1,

                secondary_y=False
            )
            fig.add_trace(
                go.Bar(name=value[0],
                       x=plot_df2[value[1]],
                       y=plot_df2[value[2]], marker_color=color_list[index], showlegend=False), row=1, col=2,

                secondary_y=False
            )
        fig.add_trace(
            go.Line(x=plot_df["Year"], y=plot_df["value"], name="GDP x 10^9 USD", marker_color='#051c2c'),
            row=1, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Line(x=plot_df2["Year"], y=plot_df2["value"], name="GDP x 10^9 USD", marker_color='#051c2c', showlegend=False),
            row=1, col=2, secondary_y=True
        )

        # Add figure title
        fig.update_layout(
            title_text=details[0], width=1050, height=400
        )

        # Set x-axis title
        fig.update_xaxes(title_text=details[1])
        if axis == constants.PERCENTAGE_LABEL:
            fig['layout']['yaxis1']['tickformat'] = ',.0%'
            fig['layout']['yaxis3']['tickformat'] = ',.0%'
        else:
            pass

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>" + details[2] + "</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>GDP Measure</b>", secondary_y=True)
        fig.show()
    except Exception:
        print("There was an error in plotting graph")


# This function was inspired from:
# https://stackoverflow.com/questions/18864859/python-executing-multiple-functions-simultaneously
def perform_parallel(*functions):
    """
    This functions parallel processes the functions passed to it.

    :param functions: List of functions to be executed in parallel
    :return:
    """
    process_list = []
    for func in functions:
        process = Process(target=func)
        process.start()
        process_list.append(process)
    for process in process_list:
        process.join()


def map_polity_gdp(polity_df: pd.DataFrame, mapper: str, gdp_string: str) -> pd.DataFrame:
    """
    Prepares the dataset to include GDP data. GDP data is combined with politics data based on country column.

    :param polity_df: Politics Dataframe
    :param mapper: name of the mapper dataset file
    :param gdp_string: name of the GDP dataset file
    :return: Final dataset with GDP column added.
    """
    # Importing GDP Data and doing preprocessing
    gdp = pd.read_excel(gdp_string)
    df1 = gdp[(gdp.Scale == "Billions") & (gdp["WEO Subject Code"] == "NGDPD")]
    df1 = df1.drop(
        columns={'WEO Country Code', 'WEO Subject Code', 'Subject Descriptor', 'Subject Notes', 'Scale', 'Units',
                 'Country/Series-specific Notes', 'Estimates Start After'})
    df2 = df1.melt(id_vars=['ISO', 'Country'])
    df2['Country'] = df2['Country'].str.upper()

    # Importing Mapping File
    mapp = pd.read_excel(mapper)
    mapp['country'] = mapp['country'].str.strip().str.upper()
    mapp['Map'] = mapp['Map'].str.strip().str.upper()

    # Final polity with GDP data
    polity_map = polity_df.merge(mapp, left_on=['country'], right_on=['country'], how='left')
    gdp_with_polity = polity_map.merge(df2, left_on=['Map', 'year'], right_on=['Country', 'variable'], how="left")
    gdp_with_polity['value'] = gdp_with_polity['value'].astype(float)
    gdp_with_polity['value'] = gdp_with_polity['value'] / 1000

    return gdp_with_polity
