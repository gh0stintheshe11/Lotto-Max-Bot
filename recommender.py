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