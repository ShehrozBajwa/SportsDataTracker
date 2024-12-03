import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import getGames
import re
from datetime import datetime


# Define the scope and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

# Authorize the client
client = gspread.authorize(credentials)

# Open the spreadsheet by its title
spreadsheet = client.open('Bet Picks')

# Select a specific worksheet
worksheet = spreadsheet.get_worksheet(0)
header = ['Team', 'Odds', 'Against', 'Bookkeeper', 'Sport', 'Date', 'Bet Amount' , 'Result', 'Return']
picks = getGames()

existing_data = worksheet.get_all_values()
start_row = len(existing_data) + 1
existing_entries = [(row[0], row[2], row[5], row[6]) for row in existing_data[1:]]  # Skip the header row


for pick in picks:
    match = re.match(r'Take (.+) for (-?\d+) vs (.+) at (.+?) \((.+)\)', pick[0])
    if match:
        team1 = match.group(1)
        odds = int(match.group(2))
        team2 = match.group(3) 
        bookmaker = match.group(4)
        sport = match.group(5).replace("-liveOdds", "")
    entry = (team1, team2, pick[2], '${:.2f}'.format(pick[1]))
    if entry not in existing_entries:
        worksheet.append_row([team1, odds, team2, bookmaker, sport, pick[2], pick[1]], value_input_option='USER_ENTERED')
        existing_entries.append(entry)
    

# Adjust column widths
column_count = len(worksheet.get_all_values()[0])
for i in range(1, column_count + 1):
    worksheet.format(f'{chr(64 + i)}:1', {'wrapStrategy': 'WRAP', 'horizontalAlignment': 'LEFT'})

print("Picks added to the spreadsheet.")