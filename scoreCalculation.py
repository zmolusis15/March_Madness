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
    momentum_boost_set = {"North Carolina"}
    if row['team'] in momentum_boost_set:
        boost_rating += 0.1
        
    return boost_rating



#Sim Games
def simulate_game (team_name1, team_name2, df):
    
    team1_row = df[df["team"] == team_name1].iloc[0]
    team2_row = df[df['team'] == team_name2].iloc[0]

    team1_score = calculate_team_rating(team1_row)
    team2_score = calculate_team_rating(team2_row)
    
    team1_score += rating_boosts(team1_row,team2_row)
    team2_score += rating_boosts(team2_row,team1_row)
    
    rating_diff = (team1_score - team2_score) * 7.5  # Scale factor to adjust win probability distribution

    win_prob_team1 = 1 / (1 + np.exp(-rating_diff))  

    # Simulate game outcome
    random_number = np.random.rand()
    
    if random_number < win_prob_team1:
        winner = team_name1
        winning_prob = win_prob_team1
    else: 
        winner = team_name2
        winning_prob = 1-win_prob_team1
        
    return winner, winning_prob
    


def load_bracket():
    bracket = {
        "South": [
            (1, "Auburn"), (16, "Alabama St."),
            (8, "Louisville"), (9, "Creighton"),
            (5, "Michigan"), (12, "UC San Diego"),
            (4, "Texas A&M"), (13, "Yale"),
            (6, "Mississippi"), (11, "North Carolina"),
            (3, "Iowa St."), (14, "Lipscomb"),
            (7, "Marquette"), (10, "New Mexico"),
            (2, "Michigan St."), (15, "Bryant")
        ],
        "West": [
            (1, "Florida"), (16, "Norfolk St."),
            (8, "Connecticut"), (9, "Oklahoma"),
            (5, "Memphis"), (12, "Colorado St."),
            (4, "Maryland"), (13, "Grand Canyon"),
            (6, "Missouri"), (11, "Drake"),
            (3, "Texas Tech"), (14, "UNC Wilmington"),
            (7, "Kansas"), (10, "Arkansas"),
            (2, "St. John's"), (15, "Nebraska Omaha")
        ],
        "East": [
            (1, "Duke") , (16, "American"),
            (8, "Mississippi St."), (9, "Baylor"),
            (5, "Oregon"), (12, "Liberty"),
            (4, "Arizona"), (13, "Akron"),
            (6, "BYU"), (11, "VCU"),
            (3, "Wisconsin"), (14, "Montana"),
            (7, "Saint Mary's"), (10, "Vanderbilt"),
            (2, "Alabama"), (15, "Robert Morris")
        ],
        "Midwest": [
            (1, "Houston"), (16, "SIUE"),
            (8, "Gonzaga"), (9, "Georgia"),
            (5, "Clemson"), (12, "McNeese"),
            (4, "Purdue"), (13, "High Point"),
            (6, "Illinois"), (11, "Texas"),
            (3, "Kentucky"), (14, "Troy"),
            (7, "UCLA"), (10, "Utah St."),
            (2, "Tennessee"), (15, "Wofford")
        ]
    }
    return bracket


def print_bracket(bracket, old_bracket, game_prob):
    for region in old_bracket.keys():
        print(f"🌎 {region} Region:\n")

        # Extract winners from the current bracket
        current_winners = {team[1] for team in bracket[region]}  # Store only the team names in a set

        for idx, matchup in enumerate(old_bracket[region]):# Loop through the previous round's matchups
            
            spacing = (idx % 2 != 0) and (idx < len(old_bracket[region]) - 1)
            
            seed, team = matchup

            if team in current_winners:  
                winning_prob = game_prob[team]
                print(f"{seed} {team} ✅ --- {winning_prob}%")
            else: 
                print(f"{seed} {team} ❌")

            if spacing:
                print("\n")
        
        print("-"*30)


def print_final_four(teams, winners, game_prob):
    print("\n🏆 Final Four 🏆\n")
    if teams[0][0][1] == winners[0][1]:
        winning_prob = game_prob[teams[0][0][1]]
        print(f"{teams[0][0][0]} {teams[0][0][1]} ✅ ---{winning_prob}%")
        print(f"{teams[1][0][0]} {teams[1][0][1]} ❌")
    else:
        winning_prob = game_prob[teams[1][0][1]]
        print(f"{teams[0][0][0]} {teams[0][0][1]} ❌")
        print(f"{teams[1][0][0]} {teams[1][0][1]} ✅ ---{winning_prob}%")
    print('\n')
    if teams[2][0][1] == winners[1][1]:
        winning_prob = game_prob[teams[2][0][1]]
        print(f"{teams[2][0][0]} {teams[2][0][1]} ✅ ---{winning_prob}%")
        print(f"{teams[3][0][0]} {teams[3][0][1]} ❌")
    else:
        winning_prob = game_prob[teams[3][0][1]]
        print(f"{teams[2][0][0]} {teams[2][0][1]} ❌")
        print(f"{teams[3][0][0]} {teams[3][0][1]} ✅ ---{winning_prob}%")
    print("\n" + "-"*30)


def print_chip(teams, champ, game_prob):
    print("\n🏆 National Championship 🏆\n")
    if teams[0][1] == champ:
        winning_prob = game_prob[teams[0][1]]
        print(f"{teams[0][0]} {teams[0][1]} ✅ --- {winning_prob}%")
        print(f"{teams[1][0]} {teams[1][1]} ❌")
    else:
        winning_prob = game_prob[teams[1][1]]
        print(f"{teams[0][0]} {teams[0][1]} ❌")
        print(f"{teams[1][0]} {teams[1][1]} ✅ --- {winning_prob}%")
    print("\n" + "-"*30)
    print("\n🏀🏆 Champion 🏆🏀\n")
    print(champ)


def madness_sim(bracket, df):
    print("🏀 NCAA March Madness Bracket 🏀\n")
    regions = ['West','East' , 'Midwest', 'South']
    
    round_names = ["First Round", "Round of 32", "Sweet 16", "Elite 8"]
    round_winners_list = []
    for round_index, round_name in enumerate(round_names):
        game_prob = {}
        print(f"\n🏀 {round_name} 🏀\n")
        old_bracket = copy.deepcopy(bracket)
        for region in regions:
            winners_list = []
            step = 16 // (2 ** round_index)
    
            for i in range(0, step, 2):
                team1 = bracket[region][i][1]
                team2 = bracket[region][i+1][1]
                winner, winning_prob = simulate_game(team1, team2, df)

                game_prob[winner] = round(winning_prob*100) #game probability dictionary - team:prob
                if team1 == winner:
                    winners_list.append(bracket[region][i])
                else:
                    winners_list.append(bracket[region][i+1])
            
            bracket[region] = winners_list  # Update the bracket
            round_winners_list.append(winners_list)
        print_bracket(bracket, old_bracket, game_prob)

    game_prob = {}
    final_four = []
    for region in regions:
        final_four.append(bracket[region])
        
    #Final Four
    winners_list = []
    for i in range(0,4,2):
        team1 = final_four[i][0][1]
        team2 = final_four[i+1][0][1]
        winner, winning_prob = simulate_game(team1,team2, df)
        game_prob[winner] = round(winning_prob*100) #game probability dictionary - team:prob
        if team1 == winner:
            winners_list.append(final_four[i][0])
        else:
            winners_list.append(final_four[i+1][0])
    print_final_four(final_four, winners_list, game_prob)

    #Championship
    game_prob = {}
    champion, winning_prob = simulate_game(winners_list[0][1], winners_list[1][1], df)
    game_prob[champion] = round(winning_prob*100) #game probability dictionary - team:prob
    print_chip(winners_list, champion, game_prob)

    return bracket
