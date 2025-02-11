import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Tuple, Dict
import csv
from datetime import datetime
import sys
import os
import numpy as np

@dataclass(frozen=True)
class Card:
    rank: str
    suit: str
    
    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.reset()
    
    def reset(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♣', '♥', '♦']
        self.cards = []
        for _ in range(self.num_decks):
            for rank in ranks:
                for suit in suits:
                    self.cards.append(Card(rank, suit))
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        return self.cards.pop()

def is_blackjack(hand: List[Card]) -> bool:
    if len(hand) != 2:
        return False
    ranks = {card.rank for card in hand}
    return 'A' in ranks and any(rank in ranks for rank in ['10', 'J', 'Q', 'K'])

def is_suited(hand: List[Card]) -> bool:
    return len(set(card.suit for card in hand)) == 1

def is_colored(hand: List[Card]) -> bool:
    # A hand is colored if both cards are same color (red or black) but different suits
    red_suits = {'♥', '♦'}
    black_suits = {'♠', '♣'}
    suits = {card.suit for card in hand}
    
    # Must be different suits but same color
    return (suits.issubset(red_suits) or suits.issubset(black_suits)) and len(suits) == 2

def has_ace_jack(hand: List[Card]) -> bool:
    ranks = {card.rank for card in hand}
    return 'A' in ranks and 'J' in ranks

def generate_deck_and_blackjacks(num_decks=6):
    # Generate all possible cards
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['♠', '♣', '♥', '♦']
    cards = []
    for _ in range(num_decks):
        for rank in ranks:
            for suit in suits:
                cards.append(Card(rank, suit))
    
    # Pre-calculate sets for faster lookups
    red_suits = {'♥', '♦'}
    suited_aj_by_suit = {
        suit: {Card('A', suit), Card('J', suit)} 
        for suit in suits
    }
    
    return cards, red_suits, suited_aj_by_suit

def simulate_hands(num_hands: int, start_hand: int = 0, last_major_hit: int = 0, last_minor_hit: int = 0) -> tuple[dict, dict]:
    results = defaultdict(int)
    wait_times = {
        'major_prog': [],
        'minor_prog': []
    }
    
    # Generate deck and pre-calculate sets
    deck, red_suits, suited_aj_by_suit = generate_deck_and_blackjacks(6)
    
    for i in range(start_hand, start_hand + num_hands):
        if (i - start_hand) % 1_000_000 == 0:  # Print progress less frequently
            print(f"Progress: {(i - start_hand)/num_hands*100:.1f}% complete...")
            
        # Shuffle and deal
        random.shuffle(deck)
        player_hand = {deck[0], deck[2]}  # Using sets for faster operations
        dealer_hand = {deck[1], deck[3]}
        
        # Check for blackjacks (A + 10/J/Q/K)
        player_ranks = {card.rank for card in player_hand}
        dealer_ranks = {card.rank for card in dealer_hand}
        
        player_bj = 'A' in player_ranks and any(r in player_ranks for r in ['10', 'J', 'Q', 'K'])
        dealer_bj = 'A' in dealer_ranks and any(r in dealer_ranks for r in ['10', 'J', 'Q', 'K'])
        
        if player_bj and dealer_bj:
            # Check for suited A/J
            player_suited_aj = any(player_hand == s for s in suited_aj_by_suit.values())
            dealer_suited_aj = any(dealer_hand == s for s in suited_aj_by_suit.values())
            
            if player_suited_aj and dealer_suited_aj:
                results['major_prog'] += 1
                if last_major_hit > 0:
                    wait_times['major_prog'].append(i - last_major_hit)
                last_major_hit = i
            elif player_suited_aj and 'J' in dealer_ranks and 'A' in dealer_ranks and not dealer_suited_aj:
                results['minor_prog'] += 1
                if last_minor_hit > 0:
                    wait_times['minor_prog'].append(i - last_minor_hit)
                last_minor_hit = i
        elif player_bj:
            if 'J' in player_ranks and 'A' in player_ranks:
                player_suits = {card.suit for card in player_hand}
                if len(player_suits) == 1:  # Suited
                    results['suited_aj'] += 1
                elif all(s in red_suits for s in player_suits) or all(s not in red_suits for s in player_suits):  # Same color
                    results['colored_aj'] += 1
                else:  # Mixed
                    results['mixed_aj'] += 1
            else:
                results['other_bj'] += 1
    
    results['total_hands'] = num_hands
    return results, wait_times, last_major_hit, last_minor_hit

def calculate_fair_payouts(results: dict) -> tuple:
    """Calculate fair progressive payouts for 5 CHF bet."""
    total_hands = results['total_hands']
    bet_amount = 5  # CHF
    
    # Calculate total amount bet
    total_bet = total_hands * bet_amount
    
    # Calculate fixed payouts
    fixed_payouts = (
        results['suited_aj'] * 350 +
        results['colored_aj'] * 250 +
        results['mixed_aj'] * 100 +
        results['other_bj'] * 25
    )
    
    # Remaining amount that needs to be covered by progressives
    remaining = total_bet - fixed_payouts
    
    major_hits = results['major_prog']
    minor_hits = results['minor_prog']
    
    if major_hits == 0 or minor_hits == 0:
        return 0, 0
    
    # We want major_payout/minor_payout = minor_hits/major_hits
    # Let minor_payout = x
    # Then major_payout = (minor_hits/major_hits) * x
    # remaining = major_hits * ((minor_hits/major_hits) * x) + minor_hits * x
    # remaining = (minor_hits * x) + (minor_hits * x)
    # remaining = 2 * minor_hits * x
    
    ratio = minor_hits / major_hits
    minor_payout = remaining / ((ratio * major_hits) + minor_hits)
    major_payout = minor_payout * ratio
    
    return major_payout, minor_payout

def main():
    num_hands = 10_000_000  # 10 million hands
    chunk_size = 100_000  # Increased for more efficient processing
    
    print(f"Running simulation for {num_hands:,} hands...")
    
    # Initialize aggregate results
    total_results = defaultdict(int)
    chunk_results = []
    all_wait_times = {
        'major_prog': [],
        'minor_prog': []
    }
    
    # Track last hits across chunks
    last_major_hit = 0
    last_minor_hit = 0
    
    try:
        # Process in chunks
        num_chunks = num_hands // chunk_size
        for chunk in range(num_chunks):
            try:
                print(f"\nProcessing chunk {chunk + 1}/{num_chunks}")
                print(f"Total hands processed so far: {chunk * chunk_size:,}")
                
                start_hand = chunk * chunk_size
                results, wait_times, last_major_hit, last_minor_hit = simulate_hands(
                    chunk_size, start_hand, last_major_hit, last_minor_hit
                )
                
                # Store chunk results
                results['chunk'] = chunk + 1
                chunk_results.append(results.copy())
                
                # Aggregate results and wait times
                for key in results:
                    if key != 'chunk' and key != 'total_hands':
                        total_results[key] += results[key]
                
                all_wait_times['major_prog'].extend(wait_times['major_prog'])
                all_wait_times['minor_prog'].extend(wait_times['minor_prog'])
                
                # Print intermediate results every 10 chunks
                if (chunk + 1) % 10 == 0:
                    print("\nIntermediate results after", (chunk + 1), "chunks:")
                    print(f"Major Progressive: {total_results['major_prog']:,} hits")
                    print(f"Minor Progressive: {total_results['minor_prog']:,} hits")
                    
            except Exception as e:
                print(f"\nError processing chunk {chunk + 1}: {str(e)}")
                raise
        
        total_results['total_hands'] = num_hands
        
        # Calculate wait time statistics
        major_wait_stats = {
            'min': min(all_wait_times['major_prog']) if all_wait_times['major_prog'] else 0,
            'max': max(all_wait_times['major_prog']) if all_wait_times['major_prog'] else 0,
            'mean': np.mean(all_wait_times['major_prog']) if all_wait_times['major_prog'] else 0,
            'std': np.std(all_wait_times['major_prog']) if all_wait_times['major_prog'] else 0,
            'percentiles': np.percentile(all_wait_times['major_prog'], [25, 50, 75, 90, 95, 99]) if all_wait_times['major_prog'] else [0]*6
        }
        
        minor_wait_stats = {
            'min': min(all_wait_times['minor_prog']) if all_wait_times['minor_prog'] else 0,
            'max': max(all_wait_times['minor_prog']) if all_wait_times['minor_prog'] else 0,
            'mean': np.mean(all_wait_times['minor_prog']) if all_wait_times['minor_prog'] else 0,
            'std': np.std(all_wait_times['minor_prog']) if all_wait_times['minor_prog'] else 0,
            'percentiles': np.percentile(all_wait_times['minor_prog'], [25, 50, 75, 90, 95, 99]) if all_wait_times['minor_prog'] else [0]*6
        }
        
        # Calculate fair payouts
        major_payout, minor_payout = calculate_fair_payouts(total_results)
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(os.path.dirname(__file__), f"blackjack_results_{timestamp}.csv")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write summary
            writer.writerow(['Summary Statistics'])
            writer.writerow(['Total Hands', num_hands])
            writer.writerow(['Total Bet', num_hands * 5])
            writer.writerow([''])
            
            # Write payout analysis
            writer.writerow(['Payout Information'])
            writer.writerow(['Fixed Payouts'])
            suited_aj_payout = total_results['suited_aj'] * 350
            colored_aj_payout = total_results['colored_aj'] * 250
            mixed_aj_payout = total_results['mixed_aj'] * 100
            other_bj_payout = total_results['other_bj'] * 25
            total_fixed = suited_aj_payout + colored_aj_payout + mixed_aj_payout + other_bj_payout
            
            writer.writerow(['Suited A/J (350 CHF)', f"{suited_aj_payout:,.0f}"])
            writer.writerow(['Colored A/J (250 CHF)', f"{colored_aj_payout:,.0f}"])
            writer.writerow(['Mixed A/J (100 CHF)', f"{mixed_aj_payout:,.0f}"])
            writer.writerow(['Other BJ (25 CHF)', f"{other_bj_payout:,.0f}"])
            writer.writerow(['Total Fixed Payouts', f"{total_fixed:,.0f}"])
            writer.writerow([''])
            
            writer.writerow(['Progressive Information'])
            remaining = num_hands * 5 - total_fixed
            writer.writerow(['Remaining to Cover', f"{remaining:,.0f}"])
            writer.writerow(['Major/Minor Hit Ratio', f"{total_results['minor_prog']/total_results['major_prog']:.4f}"])
            writer.writerow(['Major Progressive Payout', f"CHF {major_payout:,.2f}"])
            writer.writerow(['Minor Progressive Payout', f"CHF {minor_payout:,.2f}"])
            writer.writerow([''])
            
            # Write frequencies
            writer.writerow(['Win Type', 'Hits', 'Frequency', '1 in X hands'])
            writer.writerow(['Major Progressive', total_results['major_prog'], 
                            f"{total_results['major_prog']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['major_prog']:,.0f}"])
            writer.writerow(['Minor Progressive', total_results['minor_prog'],
                            f"{total_results['minor_prog']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['minor_prog']:,.0f}"])
            writer.writerow(['Suited A/J', total_results['suited_aj'],
                            f"{total_results['suited_aj']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['suited_aj']:,.0f}"])
            writer.writerow(['Colored A/J', total_results['colored_aj'],
                            f"{total_results['colored_aj']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['colored_aj']:,.0f}"])
            writer.writerow(['Mixed A/J', total_results['mixed_aj'],
                            f"{total_results['mixed_aj']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['mixed_aj']:,.0f}"])
            writer.writerow(['Other BJ', total_results['other_bj'],
                            f"{total_results['other_bj']/num_hands*100:.6f}%",
                            f"1 in {num_hands/total_results['other_bj']:,.0f}"])
            writer.writerow([''])
            
            # Write wait time statistics
            writer.writerow(['Wait Time Statistics'])
            writer.writerow(['Progressive', 'Min Wait', 'Max Wait', 'Mean Wait', 'Std Dev', '25th', '50th', '75th', '90th', '95th', '99th'])
            writer.writerow(['Major Progressive', 
                           f"{major_wait_stats['min']:,}",
                           f"{major_wait_stats['max']:,}",
                           f"{major_wait_stats['mean']:,.1f}",
                           f"{major_wait_stats['std']:,.1f}",
                           f"{major_wait_stats['percentiles'][0]:,.0f}",
                           f"{major_wait_stats['percentiles'][1]:,.0f}",
                           f"{major_wait_stats['percentiles'][2]:,.0f}",
                           f"{major_wait_stats['percentiles'][3]:,.0f}",
                           f"{major_wait_stats['percentiles'][4]:,.0f}",
                           f"{major_wait_stats['percentiles'][5]:,.0f}"])
            writer.writerow(['Minor Progressive',
                           f"{minor_wait_stats['min']:,}",
                           f"{minor_wait_stats['max']:,}",
                           f"{minor_wait_stats['mean']:,.1f}",
                           f"{minor_wait_stats['std']:,.1f}",
                           f"{minor_wait_stats['percentiles'][0]:,.0f}",
                           f"{minor_wait_stats['percentiles'][1]:,.0f}",
                           f"{minor_wait_stats['percentiles'][2]:,.0f}",
                           f"{minor_wait_stats['percentiles'][3]:,.0f}",
                           f"{minor_wait_stats['percentiles'][4]:,.0f}",
                           f"{minor_wait_stats['percentiles'][5]:,.0f}"])
            writer.writerow([''])
            
            # Write wait times log
            writer.writerow(['Wait Times Log'])
            writer.writerow(['Major Progressive'] + [str(x) for x in all_wait_times['major_prog']])
            writer.writerow(['Minor Progressive'] + [str(x) for x in all_wait_times['minor_prog']])
            writer.writerow([''])
            
            # Write chunk data
            writer.writerow(['Chunk Results'])
            writer.writerow(['Chunk', 'Major Hits', 'Minor Hits', 'Suited A/J', 'Colored A/J', 'Mixed A/J', 'Other BJ'])
            for chunk in chunk_results:
                writer.writerow([
                    chunk['chunk'],
                    chunk['major_prog'],
                    chunk['minor_prog'],
                    chunk['suited_aj'],
                    chunk['colored_aj'],
                    chunk['mixed_aj'],
                    chunk['other_bj']
                ])
        
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"\nError in main(): {str(e)}")
        raise

if __name__ == "__main__":
    main() 