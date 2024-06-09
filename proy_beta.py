import pandas as pd
import random
import numpy as np
from scipy.stats import spearmanr
import math
import matplotlib.pyplot as plt


# Load data from teams
def load_data(s_date, e_date):
    # Load the CSV file
    games = pd.read_csv('games.csv')

    # Modify the Date column to be in the correct format by removing every character after the 9th
    games['Date'] = games['Date'].str[:10]

    # Filter the DataFrame to only include games from the 2021 season and the first half of 2021 season
    games_filtered = games[(games['Date'] >= s_date) & (games['Date'] <= e_date)]

    # Create a dictionary to store the results
    results = {}

    # Iterate over the rows of the DataFrame
    for index, row in games_filtered.iterrows():
        home_team = row['home']
        away_team = row['away']
        home_score = row['home-score']
        away_score = row['away-score']

        # Determine the winning team and the losing team
        if home_score > away_score:
            winning_team = home_team
            losing_team = away_team
        else:
            winning_team = away_team
            losing_team = home_team

        # Update the dictionary with the results
        if winning_team not in results:
            results[winning_team] = {}
        if losing_team not in results:
            results[losing_team] = {}
        if losing_team not in results[winning_team]:
            results[winning_team][losing_team] = {'total_games': 0, 'victories': 0}
        if winning_team not in results[losing_team]:
            results[losing_team][winning_team] = {'total_games': 0, 'victories': 0}
        results[losing_team][winning_team]['total_games'] += 1
        results[winning_team][losing_team]['total_games'] += 1
        results[winning_team][losing_team]['victories'] += 1

    # Convert the results to the desired format
    # Esto va a ser un diccionario donde la clave es el nombre del equipo y el valor es una lista de tuplas. Cada tupla
    # contiene el nombre del equipo contra el que jugó, la cantidad de juegos jugados y la cantidad de juegos ganados.

    # Por ejemplo:
    # results['LAD'] = [('SD', 10, 6), ('SF', 12, 8), ...]
    # results['SD'] = [('LAD', 10, 4), ('SF', 11, 6), ...]
    # En este caso, LAD jugó 10 juegos contra SD y ganó 6 de ellos, y 12 juegos contra SF y ganó 8 de ellos. SD jugó
    # 10 juegos contra LAD y ganó 4 de ellos, y 11 juegos contra SF y ganó 6 de ellos.

    final_results = {}
    for team, opponents in results.items():
        for opponent, stats in opponents.items():
            if team not in final_results:
                final_results[team] = []
            final_results[team].append((opponent, stats['total_games'], stats['victories']))

    return final_results


# Get the historical game results between the two teams
def get_history(team1, team2, results):
    # The get method is used to retrieve the list of tuples for team1 from the results'
    # dictionary. If team1 is not in results, an empty list is returned. Then, a generator expression is used to
    # iterate over the list of tuples and find the tuple where the first element is team2. If such a tuple is found,
    # its second and third elements (the number of games played and won) are returned. If no such tuple is found, (0,
    # 0) is returned. This is done using the next function with a default value.
    return next(((gp, gw) for t, gp, gw in results.get(team1, []) if t == team2), (0, 0))


# Simulate if there are any injured players using binomial distribution
def simulate_injured_players(p=0.5):
    # Run a binomial trial 5 times
    injured_players = np.random.binomial(1, p)
    return injured_players


# Simulate a game
def simulate_game(team1, team2, results, game_simulations, count):
    # Initialize win counters
    wins_team1 = 0
    wins_team2 = 0

    # Get the historical game results between the two teams
    games_played, games_won = get_history(team1, team2, results)

    # Simulate if there are injured players in each team
    injured_players_team1 = simulate_injured_players()
    injured_players_team2 = simulate_injured_players()

    # Calculate the win rate of team1 against team2
    if games_played > 0:
        numerator = games_won + injured_players_team2 - injured_players_team1
        if numerator < 0:
            numerator = 0
        win_rate = numerator / games_played
    else:
        win_rate = 0.5  # Assume a 50% win rate if there are no historical game results

    # Run the Monte Carlo simulation
    for _ in range(game_simulations):
        # Simulate a game based on the win rate
        if random.random() < win_rate:
            wins_team1 += 1
        else:
            wins_team2 += 1
    current_volatility = ((win_rate * (1 - win_rate)) / (math.sqrt(count)))
    if wins_team1 > wins_team2:
        return team1, current_volatility
    else:
        return team2, current_volatility


# Simulate a season
def simulate_season(statistics, game_simulations, count):
    resultados = []
    rate = 0.0

    # For each possible matchup between two teams
    for team1 in statistics.keys():
        for team2 in statistics.keys():
            if team1 != team2:
                # Simulate the game and save the result
                ganador, rate = simulate_game(team1, team2, statistics, game_simulations, count)
                resultados.append(ganador)

    return resultados, rate


# Convert results to table format
def create_results_table(total_wins):
    # Convert the total wins dictionary into a DataFrame
    df_total_wins = pd.DataFrame(list(total_wins.items()), columns=['Team', 'Total Wins'])

    # Sort the DataFrame by the number of total wins in descending order
    df_total_wins = df_total_wins.sort_values('Total Wins', ascending=False)

    # Reset the index of the DataFrame
    df_total_wins.reset_index(drop=True, inplace=True)

    return df_total_wins


# Print the DataFrame in a table-like format
def print_results_table(table):
    print(table.to_string(index=False))


# Creates a histogram for the first team in the statistics dictionary
# using the total_spots data.
# The histogram displays the frequency of each spot for the team.
def create_histogram(statistics, total_spots):
    """
    Parameters:
    statistics (dict): A dictionary containing team statistics.
    total_spots (dict): A dictionary containing the total spots for each team.

    """
    # Get the first team from the statistics dictionary
    team0 = list(statistics.keys())[0]

    # Create a histogram
    plt.figure(figsize=(10, 6))  # Increase the size of the figure
    plt.bar(total_spots[team0].keys(), total_spots[team0].values(), color='b', label='Frequency of Spots')

    # Add labels and title
    plt.xlabel('Spot', fontsize=14)  # Increase the font size
    plt.ylabel('Frequency', fontsize=14)  # Increase the font size
    plt.title('Histogram of Team Spots for ' + team0, fontsize=16)  # Add the team name to the title and increase the font size

    # Add grid for better readability
    plt.grid(True)

    # Add legend
    plt.legend()

    # Show the plot
    plt.show()


# Get simulation results
def get_sim_results(epsilon, game_simulations=100, show_table=False, show_histogram=False):
    statistics = load_data('2021-01-01', '2021-06-31')
    # Initialize a dictionary to store the total number of wins for each team
    total_wins = {}
    rate = 2
    # Run the simulation 'num_simulations' times
    # for _ in range(num_simulations):

    count = 0
    while epsilon < rate:
        # Run the simulation
        count += 1
        simulation_results, rate = simulate_season(statistics, game_simulations, count)
        # Add the results to the total wins
        for team in simulation_results:
            if team not in total_wins:
                total_wins[team] = 0
            total_wins[team] += 1

    table = create_results_table(total_wins)
    if show_table:
        print_results_table(table)
    if show_histogram:
        create_histogram(statistics, total_wins)
    return table


# Get real results
def get_real_results():
    # Load the data
    results = load_data('2021-01-01', '2021-12-31')

    total_wins = {}

    # Add the results to the total wins
    for team1 in results:
        for team2 in results:
            if team1 != team2:
                games_played, games_won = get_history(team1, team2, results)

                if team1 not in total_wins:
                    total_wins[team1] = 0
                if team2 not in total_wins:
                    total_wins[team2] = 0
                total_wins[team1] += games_won
                total_wins[team2] += games_played - games_won

    return create_results_table(total_wins)


###############
### METRICS ###
###############

# Calculate the average distance between the real and simulated positions of each team over multiple runs.
def position_distances(df_real, df_simulated):
    # Reset the index of both DataFrames to get the positions
    df_real = df_real.reset_index().rename(columns={'index': 'Real Position'})
    df_simulated = df_simulated.reset_index().rename(columns={'index': 'Simulated Position'})

    # Merge the two DataFrames on the 'Team' column
    df_merged = pd.merge(df_real, df_simulated, on='Team')

    # Calculate the absolute difference between the positions in both results
    df_merged['Position Distance'] = abs(df_merged['Real Position'] - df_merged['Simulated Position'])

    distance = df_merged['Position Distance'].sum()
    return distance


def exact_positions(df_real, df_simulated):
    # Reset the index of both DataFrames to get the positions
    df_real = df_real.reset_index().rename(columns={'index': 'Real Position'})
    df_simulated = df_simulated.reset_index().rename(columns={'index': 'Simulated Position'})

    # Merge the two DataFrames on the 'Team' column
    df_merged = pd.merge(df_real, df_simulated, on='Team')

    # Create a new column that is True when the positions are the same and False otherwise
    df_merged['Same Position'] = df_merged['Real Position'] == df_merged['Simulated Position']

    # Count the number of True values in the 'Same Position' column
    same_positions = df_merged['Same Position'].sum()

    return same_positions


# Count how many of the first n teams match their positions in the real and simulated results.
def top_n(df_real, df_simulated, n):
    # Reset the index of both DataFrames to get the positions
    df_real = df_real.reset_index().rename(columns={'index': 'Real Position'})
    df_simulated = df_simulated.reset_index().rename(columns={'index': 'Simulated Position'})

    # Merge the two DataFrames on the 'Team' column
    df_merged = pd.merge(df_real, df_simulated, on='Team')

    # Filter the merged DataFrame to only include the first n teams
    df_filtered = df_merged[df_merged['Real Position'] < n]

    # Count the number of teams where the real and simulated positions match
    matching_positions = sum(df_filtered['Real Position'] == df_filtered['Simulated Position'])

    return matching_positions


# Calculate the Spearman correlation between the real and simulated positions of each team.
def spearman_correlation(df_real, df_simulated):
    # Reset the index of both DataFrames to get the positions
    df_real = df_real.reset_index().rename(columns={'index': 'Real Position'})
    df_simulated = df_simulated.reset_index().rename(columns={'index': 'Simulated Position'})

    # Merge the two DataFrames on the 'Team' column
    df_merged = pd.merge(df_real, df_simulated, on='Team')

    # Calculate the Spearman correlation between the positions in both results
    correlation, _ = spearmanr(df_merged['Real Position'], df_merged['Simulated Position'])

    return correlation


# Run the simulation
def run_simulation(epsilon, game_simulations, show_table=False):
    real_results = get_real_results()  # Get the real results
    simulated_results = get_sim_results(epsilon, game_simulations, show_table, True)  # Get the simulated results

    # Calculate the position distances between the real and simulated results

    pos_dist = position_distances(real_results, simulated_results)
    ex_pos = exact_positions(real_results, simulated_results)
    top = top_n(real_results, simulated_results, 8)
    sp_corr = spearman_correlation(real_results, simulated_results)

    results = [pos_dist, ex_pos, top, sp_corr]

    return results


epsilon = 0.010206207261596576
game_simulations = 200
show_table = False

result = run_simulation(epsilon, game_simulations, show_table)

print("\nResultados obtenidos con los parametros epsilon =", epsilon, " y simulaciones de juegos =", game_simulations)
print("Position distances:", result[0])
print("Exact positions:", result[1])
print("Top-n:", result[2])
print("Spearman correlation:", result[3])
