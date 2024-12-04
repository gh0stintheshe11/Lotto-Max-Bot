import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import timedelta

def map_numbers_to_grid():
    grid = {}
    number = 1
    for row in range(1, 11):  # 10 rows
        for col in range(1, 6):  # 5 columns
            if number <= 50:
                grid[number] = (row, col)
                number += 1
    return grid

grid_positions = map_numbers_to_grid()

# First get the frequency data
def analyze_lottery_statistics():
    # Read and filter data
    df = pd.read_csv('lottery_results.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] >= '2019-07-01']
    
    # Analyze number frequencies
    all_numbers = []
    for i in range(1, 8):
        numbers = df[f'Main Numbers {i}'].tolist()
        all_numbers.extend(numbers)
    
    freq = Counter(all_numbers)
    return freq

# Get the frequency data
freq_data = analyze_lottery_statistics()

def plot_lottery_heatmap(freq_data, next_draw_date):
    """Create a heatmap using actual lottery frequency data"""
    plt.figure(figsize=(10, 5))
    
    # Create heatmap data
    heatmap_data = np.zeros((10, 5))
    max_freq = max(freq_data.values())
    
    # Fill the heatmap data
    for number, freq in freq_data.items():
        if number in grid_positions:
            row, col = grid_positions[number]
            heatmap_data[row-1, col-1] = freq
    
    # Create heatmap
    plt.imshow(heatmap_data, cmap='YlOrRd')
    plt.colorbar(label='Frequency')
    
    # Add number labels and frequencies with inverted colors
    for number, (row, col) in grid_positions.items():
        if number in freq_data:
            freq = freq_data[number]
            # Get the current color of the cell
            current_color = plt.cm.YlOrRd(heatmap_data[row-1, col-1] / max_freq)
            # Invert the color
            inverted_color = (1-current_color[0], 1-current_color[1], 1-current_color[2])
            plt.text(col-1, row-1, f'{number}\n({freq})', 
                    ha='center', va='center',
                    color=inverted_color)
    
    plt.title('Lotto Max Frequency Heatmap')
    plt.savefig(f'recommendation_history/{next_draw_date.strftime("%m-%d-%Y")}_heatmap.jpg', dpi=500, transparent=False, facecolor='white', bbox_inches='tight')
    

from datetime import datetime

def main():
    # load in the last draw date from lottery_dates.json
    with open('lottery_dates.json', 'r') as f:
        lottery_dates = json.load(f)
    # find the last draw date in lottery_dates
    # Convert the strings to datetime objects
    datetime_dates = [datetime.strptime(date, "%m-%d-%Y") for date in lottery_dates]
    # Find the latest date
    latest_date = max(datetime_dates)
    # Calculate the next draw date based on specific rules
    # For example, if draws are on Wednesdays and Saturdays:
    days_until_next_draw = (2 - latest_date.weekday()) % 7  # 2 represents Wednesday
    if days_until_next_draw == 0:
        days_until_next_draw = 3  # If today is Wednesday, next draw is Saturday
    next_draw_date = latest_date + timedelta(days=days_until_next_draw)
    
    plot_lottery_heatmap(freq_data, next_draw_date)
if __name__ == "__main__":
    main() 