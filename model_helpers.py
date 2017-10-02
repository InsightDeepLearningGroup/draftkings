import pandas as pd
import numpy as np


def get_salary(team=None):
    '''
    Calculate total salary of a team
    :param team: dataframe with team members
    :return: total salary
    '''
    return np.sum(team['Salary'])



def get_performance(team=None, point_col='DK points'):
    '''
    Calculate performance of a team
    :param team: dataframe with team members
    :param point_col: column with performance points
    :return: total performance
    '''
    return np.sum(team[point_col])



def sample_team(df=None, seed=0):
    '''
    Draws a random teams from the input df that fulfills the conditions
    Conditions: 1xQB, 2xRB, 3xWR, 1xTE, 1xFLEX, 1xDST, TotalSalary 50k
    :param df: dataframe with all teams / players and their salaries
    :param seed: random seed
    :return: list of 9 GIDs = 1 team
    '''
    team = pd.DataFrame(columns=['GID', 'DK points', 'Salary'])
    team = team.append(
        df.loc[df.Position == 'QB', ['GID', 'DK points', 'Salary']]
            .sample(n=1, replace=False, random_state=seed), ignore_index=True)
    team = team.append(
        df.loc[df.Position == 'RB', ['GID', 'DK points', 'Salary']]
            .sample(n=2, replace=False, random_state=seed), ignore_index=True)
    team = team.append(
        df.loc[df.Position == 'WR', ['GID', 'DK points', 'Salary']]
            .sample(n=3, replace=False, random_state=seed), ignore_index=True)
    team = team.append(
        df.loc[df.Position == 'TE', ['GID', 'DK points', 'Salary']]
            .sample(n=1, replace=False, random_state=seed), ignore_index=True)
    team = team.append(
        df.loc[df.Position.isin(['WR', 'TE', 'RB']) & ~df.GID.isin(team), ['GID', 'DK points', 'Salary']]
            .sample(n=1, replace=False, random_state=seed), ignore_index=True)
    team = team.append(
        df.loc[df.Position == 'DST', ['GID', 'DK points', 'Salary']]
            .sample(n=1, replace=False, random_state=seed), ignore_index=True)

    return team

def multi_draw(df=None, n=1000, point_col='DK points'):
    bestlist = []

    for i in range(n):
        team = sample_team(df=df, seed=i)
        if get_salary(team) < 50000.0:
            perf = get_performance(team, point_col=point_col)
            bestlist.append([perf, i])

    bestlist.sort(reverse=True)

    return bestlist