import gspread
from oauth2client.service_account import ServiceAccountCredentials
from auto_results import get_game_result
from datetime import datetime

def check_missing_results(sheet_name, column_name):
    # Set up Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("SportsDataTracker\credentials.json", scope)
    client = gspread.authorize(credentials)

    # Open the specified sheet
    sheet = client.open(sheet_name).sheet1

    # Get all the rows in the sheet
    rows = sheet.get_all_values()
    currDay = datetime.today().strftime('%Y-%m-%d')
    # Iterate over each row
    for i, row in enumerate(rows[1:], start=2):  # Skip the header row
        # Check the length of the row
        if len(row) >= int(column_name):
            # Get the corresponding values in "Team," "Against," and "Date" columns
            team = row[0]
            against = row[2]
            date = row[5]
            result = row[int(column_name)-1]  # Adjust column index to 0-based index
            date1 = datetime.strptime(date, '%Y-%m-%d')
            currDay1 = datetime.strptime(currDay, '%Y-%m-%d')
            diff = date1 - currDay1
            # Check if there are values in the "Team," "Against," and "Date" columns
            if team and against and date:
                # Check if the result is missing
                if result == "" and int(diff.days) <= -1:
                    # Get the winner
                    winner = get_game_result(f"{team} vs {against} score {date}")
                    
                    # Update the "Result" column based on the winner
                    if winner in team:
                        sheet.update_cell(i, int(column_name), "TRUE")
                    elif winner != "":
                        sheet.update_cell(i, int(column_name), "FALSE")

# Example usage
sheet_name = "Bet Picks"
column_name = "8"  # Update with the column name or index where "Result" is located

check_missing_results(sheet_name, column_name)
