import pandas as pd
import os
import numpy as np


def import_data():
    '''
    Reads in all csvs with data in directory ./data/
    :return: dataframes with join dictionary, salaries, and points
    '''

    # get list of all csvs in the data directory
    csvs = os.listdir("data/")

    # read in team dictionary
    teamdict_csv = [csv for csv in csvs if 'TeamDict' in csv]
    df_dict = pd.DataFrame()
    for csv in teamdict_csv:
        df_in = pd.read_csv('data/' + str(csv))
        df_dict = pd.concat([df_dict, df_in], axis=0)


    # read in the current DK salaries csv
    salaries_csvs = [csv for csv in csvs if 'Salaries' in csv]
    df_salaries = pd.DataFrame()
    for csv in salaries_csvs:
        df_in = pd.read_csv('data/' + str(csv))
        df_in['Week'] = np.int(str(csv).replace('.csv', '').split('Week')[1])
        df_salaries = pd.concat([df_salaries, df_in], axis=0)

    # lots of NaN's to be filled
    df_salaries = df_salaries.fillna(value=0)


    # read in the historical and DK points csvs
    points_csvs = [csv for csv in csvs if 'Points' in csv]
    df_points = pd.DataFrame()
    for csv in points_csvs:
        df_in = pd.read_csv('data/'+str(csv))
        df_points = pd.concat([df_points, df_in], axis=0)

    # lots of NaN's to be filled
    df_points = df_points.fillna(value=0)


    return df_dict, df_salaries, df_points



def clean_and_merge(df_dict=None, df_salaries=None, df_points=None):

    # prepare points dataframe for merging
    df_points.Pos = df_points.Pos.apply(lambda x: x.replace('Def', 'DST'))

    df_points = df_points.set_index('Team').join(
        df_dict.set_index('Abbreviation2')).reset_index()

    # Split name into first and last name
    dfpart = pd.DataFrame(df_points['Name'].apply(lambda x: x
                                                  .replace('.', '')
                                                  .replace(' Jr', '')
                                                  .replace(' Sr', '')
                                                  .replace('-', '')
                                                  .replace('\'', '')
                                                  .replace('Benjamin', 'Ben')
                                                  .replace('Danny', 'Dan')
                                                  .replace(' II', '').upper().split(', ', maxsplit=1)[
                                                            ::-1]).values.tolist(),
                          columns=['Firstname', 'Lastname'])

    df_points = pd.concat([df_points, dfpart], axis=1)


    # prepare salaries dataframe for merging
    df_salaries = df_salaries.set_index('teamAbbrev').join(
        df_dict.set_index('Abbreviation1')).reset_index()

    # Split name into first and last name
    dfpart = pd.DataFrame(df_salaries['Name'].apply(lambda x: x.replace('.', '')
                                                    .replace(' Jr', '')
                                                    .replace(' Sr', '')
                                                    .replace('-', '')
                                                    .replace('\'', '')
                                                    .replace('Benjamin', 'Ben')
                                                    .replace('Danny', 'Dan')
                                                    .replace(' II', '').upper().split(' ', maxsplit=1)).values.tolist(),
                          columns=['Firstname', 'Lastname'])

    df_salaries = pd.concat([df_salaries, dfpart], axis=1)


    # check length of dataframes before merge
    print("Entries in salary dataframe: {0}\nEntries in points dataframe: {1}".format(len(df_salaries), len(df_points)))

    # merge players first
    df = df_salaries.loc[~(df_salaries.Position == 'DST')]\
        .set_index(['TeamID'])\
        .join(df_points.loc[~(df_points.Pos == 'DST')].set_index(['TeamID']), lsuffix='_salaries')\
        .reset_index()
    df = df.loc[(df.Lastname == df.Lastname_salaries) & (df.Firstname == df.Firstname_salaries)]
    print("Merged {0} player entries".format(len(df)))

    # merge the teams separately
    df_teams = df_salaries.loc[df_salaries.Position == 'DST']\
        .set_index(['TeamID'])\
        .join(df_points.loc[df_points.Pos == 'DST'].set_index(['TeamID']), lsuffix='_salaries')\
        .reset_index()
    print("Merged {0} team entries".format(len(df_teams)))

    # concatenate team and player entries where salary week -1 = points week
    df = pd.concat([df.loc[df.Week_salaries-1 == df.Week], df_teams.loc[df_teams.Week_salaries-1 == df_teams.Week]], axis=0)
    print("Merged {0} entries total".format(len(df)))

    return df