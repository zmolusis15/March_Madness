import pandas as pd
import copy
import numpy as np

def calculate_team_rating(row):
    # Core metric: Adjusted Efficiency Margin
    adj_em = row["off_eff_adj"] - row["def_eff_adj"]

    # Rebalanced weights (more top-heavy, less noise)
    weights = {
        "AdjEM": 0.60,        # MUCH more important (was 0.40)
        "SOS": 0.18,          # Strong signal for team quality

        # Core performance stats (still important, but secondary)
        "Off-eFG%": 0.06,
        "Def-eFG%": -0.06,
        "Off-TO%": -0.04,
        "Def-TO%": 0.04,
        "Off-OR%": 0.04,
        "Def-OR%": -0.04,

        # Situational / minor contributors
        "Off-FTRate": 0.02,
        "Def-FTRate": -0.02,
        "3P%": 0.02,
        "FT%": 0.01,

        # Team structure (keep small so they don’t dominate)
        "Experience": 0.03,
        "Continuity": 0.02,
        "Bench": 0.01,

        # Very low impact (basically tiebreakers)
        "tempo_adj": 0.01,
        "3PA%": 0.01,
        "EffHgt": 0.01,
        "C-Hgt": 0.00
    }

    # Compute rating
    rating = (
        weights["AdjEM"] * adj_em +
        weights["SOS"] * row["SOS"] +
        weights["Off-eFG%"] * row["Off-eFG%"] +
        weights["Def-eFG%"] * row["Def-eFG%"] +
        weights["Off-TO%"] * row["Off-TO%"] +
        weights["Def-TO%"] * row["Def-TO%"] +
        weights["Off-OR%"] * row["Off-OR%"] +
        weights["Def-OR%"] * row["Def-OR%"] +
        weights["Off-FTRate"] * row["Off-FTRate"] +
        weights["Def-FTRate"] * row["Def-FTRate"] +
        weights["3P%"] * row["3P%"] +
        weights["FT%"] * row["FT%"] +
        weights["Experience"] * row["Experience"] +
        weights["Continuity"] * row["Continuity"] +
        weights["Bench"] * row["Bench"] +
        weights["tempo_adj"] * row["tempo_adj"] +
        weights["3PA%"] * row["3PA%"] +
        weights["EffHgt"] * row["EffHgt"] +
        weights["C-Hgt"] * row["C-Hgt"]
    )

    return rating


def rating_boosts (row, opponent):
    boost_rating = 0

    #Momentum Boost
    momentum_boost_set = {""}
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
    
    rating_diff = (team1_score - team2_score) * 6.5  # Scale factor to adjust win probability distribution

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
        "East": [
            (1, "Duke"), (16, "Siena"),
            (8, "Ohio St."), (9, "TCU"),
            (5, "St. John's"), (12, "Northern Iowa"),
            (4, "Kansas"), (13, "Cal Baptist"),
            (6, "Louisville"), (11, "South Florida"),
            (3, "Michigan St."), (14, "North Dakota St."),
            (7, "UCLA"), (10, "UCF"),
            (2, "Connecticut"), (15, "Furman")
        ],
        "South": [
            (1, "Florida"), (16, "Lehigh"),
            (8, "Clemson"), (9, "Iowa"),
            (5, "Vanderbilt"), (12, "McNeese"),
            (4, "Nebraska"), (13, "Troy"),
            (6, "North Carolina"), (11, "VCU"),
            (3, "Illinois"), (14, "Penn"),
            (7, "Saint Mary's"), (10, "Texas A&M"),
            (2, "Houston"), (15, "Idaho")
        ],
        "West": [
            (1, "Arizona"), (16, "LIU"),
            (8, "Villanova"), (9, "Utah St."),
            (5, "Wisconsin"), (12, "High Point"),
            (4, "Arkansas"), (13, "Hawaii"),
            (6, "BYU"), (11, "N.C. State"),
            (3, "Gonzaga"), (14, "Kennesaw St."),
            (7, "Miami FL"), (10, "Missouri"),
            (2, "Purdue"), (15, "Queens")
        ],
        "Midwest": [
            (1, "Michigan"), (16, "UMBC"),
            (8, "Georgia"), (9, "Saint Louis"),
            (5, "Texas Tech"), (12, "Akron"),
            (4, "Alabama"), (13, "Hofstra"),
            (6, "Tennessee"), (11, "SMU"),
            (3, "Virginia"), (14, "Wright St."),
            (7, "Kentucky"), (10, "Santa Clara"),
            (2, "Iowa St."), (15, "Tennessee St.")
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
    regions = ['East','South','West' , 'Midwest']
    
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
