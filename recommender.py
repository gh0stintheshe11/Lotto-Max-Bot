import pandas as pd
import random
from collections import Counter
from itertools import combinations
from datetime import datetime

def get_historical_data():
    """Get historical data and analyze patterns"""
    df = pd.read_csv('lottery_results.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] >= '2019-07-01']  # RNG era
    
    # Get individual number frequencies
    all_numbers = []
    for i in range(1, 8):
        numbers = df[f'Main Numbers {i}'].astype(int).tolist()
        all_numbers.extend(numbers)
    number_freq = Counter(all_numbers)
    
    # Get pair frequencies
    pair_freq = Counter()
    for _, row in df.iterrows():
        numbers = [int(row[f'Main Numbers {i}']) for i in range(1, 8)]
        pairs = list(combinations(sorted(numbers), 2))
        pair_freq.update(pairs)
    
    # Analyze gaps and consecutive patterns
    gaps = []
    consecutive_pairs = Counter()
    for _, row in df.iterrows():
        numbers = sorted([int(row[f'Main Numbers {i}']) for i in range(1, 8)])
        for i in range(len(numbers)-1):
            gap = numbers[i+1] - numbers[i]
            gaps.append(gap)
            if gap == 1:
                consecutive_pairs.update([(numbers[i], numbers[i+1])])
    
    avg_gap = sum(gaps) / len(gaps)
    
    return {
        'number_freq': number_freq,
        'pair_freq': pair_freq,
        'consecutive_pairs': consecutive_pairs,
        'avg_gap': avg_gap,
        'total_draws': len(df)
    }

def calculate_scores(remaining, selected=[], history_weight=0.5, balance_weight=0.3, pattern_weight=0.2):
    scores = {}
    data = get_historical_data()
    
    # If all weights are high, prioritize historical patterns more strongly
    all_high = all(w >= 0.7 for w in [history_weight, balance_weight, pattern_weight])
    
    # Get historical high/low patterns
    high_nums = [n for n, f in data['number_freq'].items() if n > 25]
    low_nums = [n for n, f in data['number_freq'].items() if n <= 25]
    high_freq = sum(data['number_freq'][n] for n in high_nums) / len(high_nums)
    low_freq = sum(data['number_freq'][n] for n in low_nums) / len(low_nums)
    historical_high_ratio = high_freq / (high_freq + low_freq)
    
    for num in remaining:
        # Get normalized frequency score
        freq_score = data['number_freq'].get(num, 0) / data['total_draws']
        
        if all_high:
            # Adjust frequency score based on historical high/low balance
            if num > 25:
                freq_score *= historical_high_ratio
            else:
                freq_score *= (1 - historical_high_ratio)
        
        if selected:
            # Calculate current and new ratios
            new_count = len(selected) + 1
            new_high_count = sum(1 for x in selected if x > 25) + (1 if num > 25 else 0)
            new_ratio = new_high_count / new_count
            
            # Base balance score using historical ratio as target
            balance_score = 1.0 - abs(historical_high_ratio - new_ratio) * 2
            
            # Add severe penalty for extreme ratios
            numbers_remaining = 7 - new_count
            potential_max_high = new_high_count + (numbers_remaining if num > 25 else 0)
            potential_min_high = new_high_count
            
            if potential_max_high == 7 or potential_min_high == 0:
                balance_score *= 0.1  # 90% penalty for extreme ratios
            
            # Even/Odd balance
            new_even_count = sum(1 for x in selected if x % 2 == 0) + (1 if num % 2 == 0 else 0)
            even_odd_ratio = new_even_count / new_count
            even_odd_score = 1.0 - abs(0.5 - even_odd_ratio) * 2
            
            # Combine balance scores
            balance_score = (balance_score + even_odd_score) / 2
        else:
            # For first number, prefer middle range
            balance_score = 1.0 - abs(25.5 - num) / 25
        
        # Pattern score based on historical patterns
        pattern_score = freq_score if all_high else 0.5
        
        # Final score combines all factors
        scores[num] = {
            'frequency': freq_score,
            'balance': balance_score,
            'pattern': pattern_score
        }
    
    return scores

def generate_smart_numbers(history_weight=0.5, balance_weight=0.3, pattern_weight=0.2):
    """
    Generate 7 numbers using comprehensive analysis
    """
    data = get_historical_data()
    total_draws = data['total_draws']
    
    # Normalize frequencies
    number_weights = {num: count/total_draws for num, count in data['number_freq'].items()}
    max_pair_freq = max(data['pair_freq'].values())
    
    def calculate_scores(remaining, selected=[]):
        scores = {}
        for num in remaining:
            # 1. Historical frequency score
            freq_score = number_weights.get(num, 0)
            
            # 2. Pair relationship score
            if selected:
                pair_scores = []
                for existing in selected:
                    pair = tuple(sorted([existing, num]))
                    pair_freq = data['pair_freq'].get(pair, 0)
                    pair_scores.append(pair_freq / max_pair_freq)
                pair_score = sum(pair_scores) / len(pair_scores)
            else:
                pair_score = 0.5
            
            # Enhanced balance factors
            if selected:
                # Count high/low numbers in current selection
                high_count = sum(1 for x in selected if x > 25)
                low_count = len(selected) - high_count
                
                # Calculate ideal ratios based on how many numbers we still need
                numbers_left = 7 - len(selected)
                ideal_high = 3 - high_count  # We want about 3 high numbers total
                
                # Strongly prefer high numbers if we're below target, low numbers if above
                if num > 25:
                    balance_score = 1.0 if high_count < 3 else 0.2
                else:
                    balance_score = 1.0 if high_count >= 3 else 0.2
                
                # Even/Odd balance remains the same
                even_odd_ratio = sum(1 for x in selected if x % 2 == 0) / len(selected)
                even_odd_score = (0.5 - abs(0.5 - even_odd_ratio))
                
                # Combine balance scores
                balance_score = (balance_score + even_odd_score) / 2
            else:
                balance_score = 0.5
            
            # 3. Balance factors
            if selected:
                high_low_ratio = sum(1 for x in selected if x > 25) / len(selected)
                even_odd_ratio = sum(1 for x in selected if x % 2 == 0) / len(selected)
                
                # Target 50/50 distributions
                balance_score = (
                    (0.5 - abs(0.5 - high_low_ratio)) +
                    (0.5 - abs(0.5 - even_odd_ratio))
                ) / 2
                
                # Gap analysis
                if len(selected) > 0:
                    last_num = max(selected)
                    gap = abs(num - last_num)
                    gap_score = 1.0 if abs(gap - data['avg_gap']) < 3 else 0.5
                else:
                    gap_score = 1.0
            else:
                balance_score = 0.5
                gap_score = 1.0
            
            # 4. Pattern score (including gaps and consecutive numbers)
            pattern_score = (pair_score + gap_score) / 2
            
            # Combine all scores with weights
            scores[num] = (
                freq_score * history_weight +
                balance_score * balance_weight +
                pattern_score * pattern_weight +
                random.random() * 0.1  # Small random factor
            )
        
        return scores
    
    def generate_combination():
        numbers = []
        remaining = list(range(1, 51))
        
        while len(numbers) < 7:
            scores = calculate_scores(remaining, numbers)
            chosen = max(scores.items(), key=lambda x: x[1])[0]
            numbers.append(chosen)
            remaining.remove(chosen)
        
        return sorted(numbers)
    
    return generate_combination()

def main():
    # Define high and low weights
    HIGH = 0.7
    LOW = 0.2
    
    # All possible combinations of weights
    strategies = [
        ("Historical-High Balance-High Pattern-High", HIGH, HIGH, HIGH),
        ("Historical-High Balance-High Pattern-Low", HIGH, HIGH, LOW),
        ("Historical-High Balance-Low Pattern-High", HIGH, LOW, HIGH),
        ("Historical-High Balance-Low Pattern-Low", HIGH, LOW, LOW),
        ("Historical-Low Balance-High Pattern-High", LOW, HIGH, HIGH),
        ("Historical-Low Balance-High Pattern-Low", LOW, HIGH, LOW),
        ("Historical-Low Balance-Low Pattern-High", LOW, LOW, HIGH),
        ("Historical-Low Balance-Low Pattern-Low", LOW, LOW, LOW)
    ]
    
    print("\nLotto Max Smart Number Generator")
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    for strategy_name, hist_w, bal_w, pat_w in strategies:
        print(f"\n{strategy_name}")
        print(f"Weights - History: {hist_w:.1f}, Balance: {bal_w:.1f}, Patterns: {pat_w:.1f}")
        print("-" * 50)
        
        for i in range(5):
            numbers = generate_smart_numbers(hist_w, bal_w, pat_w)
            high_count = sum(1 for x in numbers if x > 25)
            even_count = sum(1 for x in numbers if x % 2 == 0)
            
            print(f"\nSet {i+1}: {numbers}")
            print(f"High/Low: {high_count}/{7-high_count}, Even/Odd: {even_count}/{7-even_count}")

if __name__ == "__main__":
    main() 