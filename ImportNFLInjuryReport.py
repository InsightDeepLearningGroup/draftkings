#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 21:17:54 2017

@author: staples
"""
from datetime import datetime
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import numpy as np
    
def ImportNFLInjuryReport(): 

    SeasonStartDate = datetime.strptime("2017-09-07","%Y-%m-%d").date()
        
    url = 'http://www.rotoworld.com/teams/injuries/nfl/all/'
    
    opener = urllib.FancyURLopener({})
    request = str(opener.open(url).read())#str(urlopen(url).read())
    
    # Need to test for successful request here
    
    # Beautify the xmal data
    soup = BeautifulSoup(request, "html5lib")
    
    # Find all tables
    injurydata = soup.find_all("div", class_="pb")
    
    #print(r)
    PlayerData = []
    for teams in injurydata:
        TeamName = teams.find(class_="player").get_text()
        TeamAbv  = teams.find(class_="player").find('a')['href'].split("/")[3].upper()
    
        # Get table of player injuries
        Players  = teams.find('table').find_all('tr') [1:]
        
        for Player in Players:
            PlayerItems = Player.find_all("td")
            
            # Get  The Player Info
            #PlayerName       = PlayerItems[0].get_text().partition(" ") # Parsed into first and last name
            PlayerFullName   = PlayerItems[0].get_text()
            PlayerReport     = PlayerItems[1].find(class_="report").get_text() # Get report portion only. The rest is a repeat of other col data
            PlayerReportDate = PlayerItems[1].find(class_="date").get_text().replace(u'\xa0', u' ') # Remove unicode 
            PlayerPosition   = PlayerItems[2].get_text()
            PlayerStatus     = PlayerItems[3].get_text()
            PlayerInjuryDate = PlayerItems[4].get_text().replace(u'\xa0', u' ') # Remove unicode 
            PlayerInjury     = PlayerItems[5].get_text()
            PlayerReturns    = PlayerItems[6].get_text()
            
            # format dates and get week since season started
            PlayerReportDate = datetime.strptime(PlayerReportDate, '%b %d').replace(year=SeasonStartDate.year)
            PlayerInjuryDate = datetime.strptime(PlayerInjuryDate, '%b %d').replace(year=SeasonStartDate.year)
            
            
            
            # Catch any injuries that happened in a previous season
            if((datetime.now().date()-PlayerReportDate.date()).days<0):
                PlayerReportDate = PlayerReportDate.replace(year=SeasonStartDate.year-1)
            
            if((datetime.now().date()-PlayerInjuryDate.date()).days<0):
                PlayerInjuryDate = PlayerInjuryDate.replace(year=SeasonStartDate.year-1)
                
            
            PlayerReportWeek = np.ceil((datetime.now().date() - PlayerReportDate.date()).days/7.0).astype(int)
            PlayerInjuryWeek = np.ceil((datetime.now().date() - PlayerInjuryDate.date()).days/7.0).astype(int)
            CurrentWeek      = np.ceil((datetime.now().date() - SeasonStartDate).days/7.0).astype(int)
            
            
       
            # Store Player data
            PlayerData.append([PlayerFullName, PlayerPosition, TeamName, TeamAbv, CurrentWeek, 
                               PlayerReport, PlayerReportDate, PlayerReportWeek, 
                               PlayerStatus, PlayerInjuryDate,  PlayerInjuryWeek, PlayerInjury, PlayerReturns])
    
    # convert to a dataframe
    injury_df = pd.DataFrame(PlayerData,columns=["Name","Pos","FullTeamName","Team","CurrentWeek", "Report","ReportDate","ReportWeeksAgo","Status","InjuryDate","InjuryWeeksAgo","Injury","Return"])
    
    # Add Flag for Play (1) or No Play (0)
    injury_df['PlayFlag'] = injury_df["Return"].str.contains("will play",case=False)*1
    return(injury_df)

    
