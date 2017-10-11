import pandas as pd
import numpy as np
from pulp import *



def get_salary(team=None, df=None):
    '''
    Calculate total salary of a team
    :param team: array with team GIDs
    :param df: dataframe with team data
    :return: total salary
    '''
    return np.sum(df.loc[df.GID.isin(team), 'Salary'])



def get_performance(team=None, df=None, point_col='DK points'):
    '''
    Calculate performance of a team
    :param team: array with team GIDs
    :param df: dataframe with team data
    :param point_col: column with performance points
    :return: total performance
    '''
    return np.sum(df.loc[df.GID.isin(team), point_col])



def single_draw(df=None, seed=0):
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

    return team.GID.values



def multi_draw(df=None, n=1000, point_col='DK points'):
    bestlist = []

    for i in range(n):
        team = single_draw(df=df, seed=i)
        if get_salary(team=team, df=df) < 50000.0:
            perf = get_performance(team=team, df=df, point_col=point_col)
            bestlist.append([perf, i])

    bestlist.sort(reverse=True)

    return bestlist



def optimal_draw(df=None, points_col='DK points'):

    # Create variables for all players
    QB_ID = df[df['Position'] == 'QB']['GID'].values.tolist()
    TE_ID = df[df['Position'] == 'TE']['GID'].values.tolist()
    RB_ID = df[df['Position'] == 'RB']['GID'].values.tolist()
    WR_ID = df[df['Position'] == 'WR']['GID'].values.tolist()
    DST_ID = df[df['Position'] == 'DST']['GID'].values.tolist()
    POS_ID = QB_ID + TE_ID + RB_ID + WR_ID + DST_ID

    # create dictionaries for salaries and performance
    x = LpVariable.dicts("%s", POS_ID, 0, 1, LpInteger)
    points = pd.Series(df[points_col].values, index=df['GID']).to_dict()
    salary = pd.Series(df['Salary'].values, index=df['GID']).to_dict()

    dk_solve = LpProblem("ILP", LpMaximize)

    # ****************************************************************
    # Objective
    # ****************************************************************
    dk_solve += sum([points[i] * x[i] for i in sorted(POS_ID)])

    # ****************************************************************
    # Constraints
    # ****************************************************************

    # Salary Cap at $50k
    dk_solve += sum([salary[i] * x[i] for i in sorted(POS_ID)]) <= 50000

    # Only 1 Quaterback
    dk_solve += sum([x[i] for i in sorted(QB_ID)]) == 1

    # Between 1 and 2 Tight Ends
    dk_solve += sum([x[i] for i in sorted(TE_ID)]) <= 2
    dk_solve += sum([x[i] for i in sorted(TE_ID)]) >= 1

    # Between 3 and 4 Wide Receivers
    dk_solve += sum([x[i] for i in sorted(WR_ID)]) <= 4
    dk_solve += sum([x[i] for i in sorted(WR_ID)]) >= 3
    # dk_solve += sum([x[i] for i in sorted(WR_ID)])  == 3

    # Between 2 and 3 Running Backs
    dk_solve += sum([x[i] for i in sorted(RB_ID)]) <= 3
    dk_solve += sum([x[i] for i in sorted(RB_ID)]) >= 2

    # Only 1 Defence / Special Teams
    dk_solve += sum([x[i] for i in sorted(DST_ID)]) == 1

    # Require 9 players
    dk_solve += sum([x[i] for i in sorted(POS_ID)]) == 9

    # ****************************************************************
    # Solve
    # ****************************************************************
    LpSolverDefault.msg = 1
    dk_solve.solve()

    # ****************************************************************
    # Results
    # ****************************************************************

    print("Solution Status: " + LpStatus[dk_solve.status])

    # Get Selected Player IDs
    team = [v.name for v in dk_solve.variables() if v.varValue == 1]

    return team