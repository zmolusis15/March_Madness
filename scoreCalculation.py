import pandas as pd
import copy
import numpy as np

df = pd.read_csv("ratings.csv")

def calculate_team_rating(row):
    # Calculate Adjusted Efficiency Margin (normalized)
    adj_em = row["off_eff_adj"] - row["def_eff_adj"]

    # Weights for each stat
    weights = {
        "AdjEM": 0.40,   # Overall efficiency
        "SOS": 0.15,     # Strength of Schedule
        "tempo_adj": 0.05,  # Tempo/Pace
        "Off-eFG%": 0.07,  # Offensive Shooting Efficiency
        "Def-eFG%": 0.07,  # Defensive Shooting Efficiency
        "Off-TO%": -0.05,  # Turnovers (negative impact)
        "Def-TO%": 0.05,   # Defensive Turnovers Forced
        "Off-OR%": 0.05,   # Offensive Rebounding
        "Def-OR%": -0.05,  # Opponent Offensive Rebounding (lower is better)
        "Off-FTRate": 0.03,  # Getting to the FT line
        "Def-FTRate": -0.03,  # Opponent getting to the FT line (lower is better)
        "Experience": 0.10,  # Veteran teams perform better
        "Continuity": 0.05,  # Returning players help chemistry
        "Bench": 0.03,  # Bench depth
        "3P%": 0.05,   # 3-point shooting
        "FT%": 0.03,   # Free throw shooting
        "3PA%": 0.03,  # Volume of 3-pointers taken
        "EffHgt": 0.03,  # Effective height
        "C-Hgt": 0.00  # Center height
    }

    # Compute team rating as a weighted sum
    rating = (
        weights["AdjEM"] * adj_em +
        weights["SOS"] * row["SOS"] +
        weights["tempo_adj"] * row["tempo_adj"] +
        weights["Off-eFG%"] * row["Off-eFG%"] +
        weights["Def-eFG%"] * row["Def-eFG%"] +
        weights["Off-TO%"] * row["Off-TO%"] +
        weights["Def-TO%"] * row["Def-TO%"] +
        weights["Off-OR%"] * row["Off-OR%"] +
        weights["Def-OR%"] * row["Def-OR%"] +
        weights["Off-FTRate"] * row["Off-FTRate"] +
        weights["Def-FTRate"] * row["Def-FTRate"] +
        weights["Experience"] * row["Experience"] +
        weights["Continuity"] * row["Continuity"] +
        weights["Bench"] * row["Bench"] +
        weights["3P%"] * row["3P%"] +
        weights["FT%"] * row["FT%"] +
        weights["3PA%"] * row["3PA%"] +
        weights["EffHgt"] * row["EffHgt"] +
        weights["C-Hgt"] * row["C-Hgt"]
    )

    return rating


def rating_boosts (row, opponent):
    boost_rating = 0

    #Momentum Boost
    momentum_boost_set = {"Kansas","Auburn","North Carolina"}
    if row['team'] in momentum_boost_set:
        boost_rating += 0.1
        
    return boost_rating



def simulate_game (team_name1, team_name2, df):
    np.random.seed(None)  
    team1_row = df[df["team"] == team_name1].iloc[0]
    team2_row = df[df['team'] == team_name2].iloc[0]

    team1_score = calculate_team_rating(team1_row)
    team2_score = calculate_team_rating(team2_row)

    team1_score += rating_boosts(team1_row,team2_row)
    team2_score += rating_boosts(team1_row,team2_row)

    rating_diff = (team1_score - team2_score) * 6  # Scale factor to adjust win probability distribution
    win_prob_team1 = 1 / (1 + np.exp(-rating_diff))  

    # Simulate game outcome
    random_number = np.random.rand()
    if random_number < win_prob_team1:
        winner = team_name1
    else: 
        winner = team_name2
    return winner


def load_bracket():
    bracket = {
        "East": [
            (1, "Duke") , (16, "Marist"),
            (8, "New Mexico"), (9, "Connecticut"),
            (5, "Missouri"), (12, "Yale"),
            (4, "Purdue"), (13, "Lipscomb"),
            (6, "UCLA"), (11, "UC San Diego"),
            (3, "Texas Tech"), (14, "Towson"),
            (7, "Memphis"), (10, "Arkansas"),
            (2, "Tennessee"), (15, "Norfolk St.")
        ],
        "West": [
            (1, "Houston"), (16, "Nebraska Omaha"),
            (8, "BYU"), (9, "Utah St."),
            (5, "Oregon"), (12, "Drake"),
            (4, "St. John's"), (13, "Liberty"),
            (6, "Saint Mary's"), (11, "Indiana"),
            (3, "Wisconsin"), (14, "Chattanooga"),
            (7, "Louisville"), (10, "West Virginia"),
            (2, "Florida"), (15, "Central Connecticut")
        ],
        "South": [
            (1, "Auburn"), (16, "American"),
            (8, "Illinois"), (9, "Vanderbilt"),
            (5, "Clemson"), (12, "Ohio St."),
            (4, "Michigan"), (13, "High Point"),
            (6, "Marquette"), (11, "VCU"),
            (3, "Kentucky"), (14, "James Madison"),
            (7, "Mississippi St."), (10, "San Diego St."),
            (2, "Iowa St."), (15, "Montana")
        ],
        "Midwest": [
            (1, "Alabama"), (16, "Bryant"),
            (8, "Creighton"), (9, "Gonzaga"),
            (5, "Maryland"), (12, "McNeese"),
            (4, "Arizona"), (13, "Akron"),
            (6, "Kansas"), (11, "Nebraska"),
            (3, "Texas A&M"), (14, "Utah Valley"),
            (7, "Mississippi"), (10, "Baylor"),
            (2, "Michigan St."), (15, "Robert Morris")
        ]
    }
    return bracket


def print_bracket(bracket, old_bracket):
    
    for region in old_bracket.keys():
        print(f"🌎 {region} Region:")
        
        # Extract winners from the current bracket
        current_winners = {team[1] for team in bracket[region]} 
        
        for matchup in old_bracket[region]:  # Loop through the previous round's matchups
            seed, team = matchup
            
            if team in current_winners:  
                print(f"{seed} {team} ✅")
            else: 
                print(f"{seed} {team} ❌")
        
        print("\n" + "-"*30)


def print_final_four(teams, winners):
    print("\n🏆 Final Four 🏆\n")
    if teams[0][0][1] == winners[0][1]:
        print(teams[0][0][0], teams[0][0][1], "✅")
        print(teams[1][0][0], teams[1][0][1], "❌")
    else:
        print(teams[0][0][0], teams[0][0][1], "❌")
        print(teams[1][0][0], teams[1][0][1], "✅")
    print('\n')
    if teams[2][0][1] == winners[1][1]:
        print(teams[2][0][0], teams[2][0][1], "✅")
        print(teams[3][0][0], teams[3][0][1], "❌")
    else:
        print(teams[2][0][0], teams[2][0][1], "❌")
        print(teams[3][0][0], teams[3][0][1], "✅")
    print("\n" + "-"*30)


def print_chip(teams, champ):
    print("\n🏆 National Championship 🏆\n")
    if teams[0][1] == champ:
        print(teams[0][0],teams[0][1], "✅")
        print(teams[1][0],teams[1][1], "❌")
    else:
        print(teams[0][0],teams[0][1], "❌")
        print(teams[1][0],teams[1][1], "✅")
    print("\n" + "-"*30)
    print("\n🏀🏆 Champion 🏆🏀\n")
    print(champ)


def madness_sim(bracket, df):
    print("🏀 NCAA March Madness Bracket 🏀\n")
    regions = ['East', 'West', 'South', 'Midwest']
    
    round_names = ["First Round", "Round of 32", "Sweet 16", "Elite 8"]
    round_winners_list = []
    for round_index, round_name in enumerate(round_names):
        print(f"\n🏀 {round_name} 🏀\n")
        old_bracket = copy.deepcopy(bracket)
        for region in regions:
            winners_list = []
            step = 16 // (2 ** round_index)
    
            for i in range(0, step, 2):
                team1 = bracket[region][i][1]
                team2 = bracket[region][i+1][1]
                winner = simulate_game(team1, team2, df)  
                if team1 == winner:
                    winners_list.append(bracket[region][i])
                else:
                    winners_list.append(bracket[region][i+1])
                
            
            bracket[region] = winners_list.copy() #UPDATING BRACKET
            round_winners_list.append(winners_list)
        print_bracket(bracket, old_bracket)
            
    final_four = []
    for region in regions:
        final_four.append(bracket[region])
    #Final Four
    winners_list = []
    for i in range(0,4,2):
        team1 = final_four[i][0][1]
        team2 = final_four[i+1][0][1]
        winner = simulate_game(team1, team2, df)
     
        if team1 == winner:
            winners_list.append(final_four[i][0])
        else:
            winners_list.append(final_four[i+1][0])
    print_final_four(final_four, winners_list)

    #Championship
    champion = simulate_game(winners_list[0][1], winners_list[1][1], df)
    print_chip(winners_list, champion)
    return bracket
