import json
import csv
from datetime import datetime

def format_lottery_data(json_file_path):
    # Read JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Create main draw CSV
    with open('main_draws.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Main Numbers', 'Bonus Number', 'Jackpot', 'Total Winners'])
        
        # Format main numbers as comma-separated string
        main_numbers = ','.join(data['main_draw']['main_numbers'])
        writer.writerow([
            data['main_draw']['draw_date'],
            main_numbers,
            data['main_draw']['bonus_number'],
            data['main_draw']['jackpot'],
            data['main_draw']['total_winners']
        ])

    # Create max millions CSV
    with open('max_millions.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Draw Date', 'Numbers'])
        
        for result in data['max_millions']['results']:
            numbers = ','.join(result['numbers'])
            writer.writerow([data['main_draw']['draw_date'], numbers])

    # Create prize breakdown CSV
    with open('prize_breakdown.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Draw Date', 'Match Type', 'Prize Per Winner', 'Winners', 'Prize Fund'])
        
        for prize in data['prize_breakdown']:
            writer.writerow([
                data['main_draw']['draw_date'],
                prize['match_type'],
                prize['prize_per_winner'],
                prize['winners'].split('\n')[0],  # Take only the first line to avoid regional breakdown
                prize['prize_fund']
            ])

    # Create statistics CSV
    with open('statistics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Draw Date', 'Metric', 'Value'])
        
        for metric, value in data['statistics'].items():
            writer.writerow([
                data['main_draw']['draw_date'],
                metric,
                value['main_stat']
            ])

# Usage
format_lottery_data('lottery_results_final.json')