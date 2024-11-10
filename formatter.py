import json
import csv
from datetime import datetime

def format_lottery_data(json_file):
    # Read JSON file
    with open(json_file, 'r') as f:
        data_list = json.load(f)
    
    print(f"Total records in JSON: {len(data_list)}")
    processed = 0
    skipped = []
    
    # Create single CSV file
    with open('lottery_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Date',
            'Draw Date',
            'Main Numbers 1',
            'Main Numbers 2',
            'Main Numbers 3',
            'Main Numbers 4',
            'Main Numbers 5',
            'Main Numbers 6',
            'Main Numbers 7',
            'Bonus Number',
            'Jackpot',
            'Prize Breakdown',
            'Total Sales',
            'Tickets Sold',
            'Total Winners',
            'Winning Ratio',
            'Sales Difference',
            'Millions Count',
            'Max Millions Numbers',
            'Max Millions Next Draw',  
        ])
        
        # Write each result as a row
        for index, data in enumerate(data_list):
            try:
                # Format max millions numbers
                max_millions_numbers = '|'.join([
                    ','.join(result['numbers']) 
                    for result in data.get('max_millions', {}).get('results', [])
                ]) if data.get('max_millions', {}).get('results') else ''
                
                # Get statistics with default values
                statistics = data.get('statistics', {})
                
                main_row = [
                    data.get('date', ''),                                         # Date
                    data.get('main_draw', {}).get('draw_date', ''),              # Draw Date
                    data.get('main_draw', {}).get('main_numbers', [''])[0],      # Main Numbers 1
                    data.get('main_draw', {}).get('main_numbers', ['', ''])[1],  # Main Numbers 2
                    data.get('main_draw', {}).get('main_numbers', ['', '', ''])[2],  # Main Numbers 3
                    data.get('main_draw', {}).get('main_numbers', ['', '', '', ''])[3],  # Main Numbers 4
                    data.get('main_draw', {}).get('main_numbers', ['', '', '', '', ''])[4],  # Main Numbers 5
                    data.get('main_draw', {}).get('main_numbers', ['', '', '', '', '', ''])[5],  # Main Numbers 6
                    data.get('main_draw', {}).get('main_numbers', [''] * 7)[6],  # Main Numbers 7
                    data.get('main_draw', {}).get('bonus_number', ''),           # Bonus Number
                    data.get('main_draw', {}).get('jackpot', ''),               # Jackpot
                    json.dumps(data.get('prize_breakdown', [])),                 # Prize Breakdown
                    statistics.get('Total Sales', {}).get('main_stat', 'N/A'),   # Total Sales
                    statistics.get('Tickets Sold', {}).get('main_stat', 'N/A'),  # Tickets Sold
                    statistics.get('Total Winners', {}).get('main_stat', 'N/A'), # Total Winners
                    statistics.get('Winning Ratio', {}).get('main_stat', 'N/A'), # Winning Ratio
                    statistics.get('Sales Difference (From previous draw)', {}).get('main_stat', 'N/A'),  # Sales Difference
                    data.get('max_millions', {}).get('count', '0'),             # Millions Count
                    max_millions_numbers,                                        # Max Millions Numbers
                    statistics.get('Max Millions for the next draw:', {}).get('main_stat', '0')  # Max Millions Next Draw
                ]
                writer.writerow(main_row)
                processed += 1
            except Exception as e:
                skipped.append({
                    'index': index,
                    'date': data.get('date', 'Unknown'),
                    'error': str(e)
                })
    
    print(f"\nProcessing Summary:")
    print(f"Total processed: {processed}")
    print(f"Total skipped: {len(skipped)}")
    if skipped:
        print("\nSkipped entries:")
        for entry in skipped:
            print(f"Index {entry['index']}, Date: {entry['date']}, Error: {entry['error']}")

# Usage
format_lottery_data('lottery_results_final.json')