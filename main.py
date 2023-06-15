import requests
from bs4 import BeautifulSoup
from datetime import datetime



url = "https://www.covers.com/sport/odds"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

sports= [("nfl-liveOdds", 13, 4), ("ncaaf-liveOdds", 13, 4) , ("nba-liveOdds", 13, 4), ("ncaab-liveOdds", 13, 4), ("nhl-liveOdds", 13, 3), ("mlb-liveOdds", 13, 3), ("bundesliga-liveOdds", 13, 2), ("champions-leagueLiveOdds", 13, 2) 
         , ("europa-league-liveOdds", 13, 2), ("serie-a-liveOdds", 13, 2), ("la-liga-liveOdds", 13, 2), ("ligue-1-liveOdds", 13, 2), ("mls-liveOdds", 9, 2), ("premier-league-liveOdds", 13, 2), ("cfl-liveOdds", 13, 3), ("wnba-liveOdds", 13, 2)]

picks = []


def isOverpriced(findOdds):
    added = False
    length = len(findOdds)
    temp2 = {}
    temp1 = []
    for i in findOdds.keys():
        string = i
        split_string = string.split() 
        value = split_string[-1]
        if int(value) > 0:
            value = value[1:]
        temp2[value] = i
        temp1.append(int(value))
    temp1 = [int(numeric_string) for numeric_string in temp1]
    temp1 = sorted(temp1) 
    avg = int(sum(temp1)/length)
    bestValue = temp1[length - 1]
    if abs(bestValue - avg) > 20:
        pick = f"Take {findOdds[str(temp2[str(bestValue)])][1]} for {bestValue} vs {findOdds[str(temp2[str(bestValue)])][2]} at {findOdds[str(temp2[str(bestValue)])][0]} ({findOdds[str(temp2[str(bestValue)])][3]})"
        added = True
    pick = f"Take {findOdds[str(temp2[str(bestValue)])][1]} for {bestValue} vs {findOdds[str(temp2[str(bestValue)])][2]} at {findOdds[str(temp2[str(bestValue)])][0]} ({findOdds[str(temp2[str(bestValue)])][3]})"
    return pick, bestValue, added

def calculate_implied_probability(american_odds):
    if american_odds >= 0:
        implied_probability = 100 / (american_odds + 100)
    else:
        implied_probability = -american_odds / (-american_odds + 100)
    return implied_probability



def check_arbitrage_opportunity(odds1, odds2):
    implied_probability1 = calculate_implied_probability(odds1)
    implied_probability2 = calculate_implied_probability(odds2)
    combined_probability = implied_probability1 + implied_probability2

    if combined_probability < 1:
        return True  # Arbitrage opportunity exists
    else:
        return False  # No arbitrage opportunity

def optimal_bets(odds1, odds2):
    implied_probability1 = calculate_implied_probability(odds1)
    implied_probability2 = calculate_implied_probability(odds2)
    bet1 = implied_probability1 / implied_probability2
    bet2 = implied_probability2 / implied_probability1
    return bet1, bet2

def getGames():
    finalPicks = {}
    picks.clear()
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html5lib')
    time = datetime.now()
    time = time.strftime("%b %d")
    time =  datetime.strptime(time, '%b %d')
    added = False
    added1 = False
    for i in range(0,len(sports)):
            counter1 = 0
            sport = soup.find(id=sports[i][0])
            currSport = sport.find('a')
            if currSport != None:
                sportURL = currSport.get("href")
                specificSport = requests.get("https://www.covers.com" + sportURL, headers=headers)
                soup2 = BeautifulSoup(specificSport.text, 'html5lib')
                teams_div = soup2.find_all('div', class_='__teams __awaiting')
                date_div = soup2.find_all('div', class_='__date')
                odds_table = soup2.find_all('td', class_='covers-CoversOdss-oddsTd')
                for j in range(0, len(teams_div)//sports[i][2]):
                    homeOdds = {}
                    awayOdds = {}
                    # Find all the team elements within the __teams container
                    team_elements = teams_div[j].find_all('div', class_='__away')


                    # Extract the full team names by accessing the desired index
                    away_team_name = team_elements[0].find('a').find('div', class_='__teamLogo').find('img')['title']

                    home_team_name = teams_div[j].find('div', class_='__home').find('a').find('div', class_='__teamLogo').find('img')['title']
                    try:
                        date = date_div[j].text.strip()[:-1]
                    except:
                        date = "Today"
                    for k in range(0, sports[i][1]):
                        if int(odds_table[counter1].get('data-date')) > 0:
                            bookmaker = odds_table[counter1].get('data-book')
                            checkMoneyLine = odds_table[counter1].find('div', {'class':'__awayOdds'}).find('div', {'class': '__american'}).text.strip().split()
                            if len(checkMoneyLine) == 1:
                                awayOdds[odds_table[counter1].find('div', {'class':'__awayOdds'}).find('div', {'class': '__american'}).text.strip()] = [bookmaker, away_team_name, home_team_name, sports[i][0]]
                                homeOdds[odds_table[counter1].find('div', {'class':'__homeOdds'}).find('div', {'class': 'American __american'}).text.strip()] = [bookmaker, home_team_name, away_team_name, sports[i][0]]
                        counter1 = counter1 + 1
                    if len(homeOdds) >= 1:
                        homeARB, arbOdd, added = isOverpriced(homeOdds)
                        awayARB, arbOdd1, added1 = isOverpriced(awayOdds)
                    
                    if (check_arbitrage_opportunity(arbOdd, arbOdd1)):
                        if date == "Today":
                            formatted_date = datetime.today().strftime('%Y-%m-%d')
                        else:
                            formatted_date = datetime.strptime(f"2023 {date}", "%Y %b %d").strftime("%Y-%m-%d")
                        optimal_odd1, optimal_odd2 = optimal_bets(arbOdd, arbOdd1)
                        picks.append([homeARB, optimal_odd1, formatted_date])
                        picks.append([awayARB, optimal_odd2, formatted_date])
                    if (date == "Today"):
                        formatted_date = datetime.today().strftime('%Y-%m-%d')
                        if added == True:
                            picks.append([homeARB, 1, formatted_date]) 
                        if added1 == True:
                            picks.append([awayARB, 1, formatted_date])  
                    awayOdds.clear()
                    homeOdds.clear()
            else:
                continue
    return picks
