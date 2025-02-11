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
    def __init__(self):
        self.reset()
    
    def reset(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♣', '♥', '♦']
        self.cards = []
        for rank in ranks:
            for suit in suits:
                self.cards.append(Card(rank, suit))
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        return self.cards.pop()

def is_royal_flush(cards: List[Card]) -> bool:
    if len(cards) < 5:
        return False
        
    # Check if we have all the same suit
    suits = {card.suit for card in cards}
    if len(suits) != 1:
        return False
    
    # Get the ranks we need for a royal flush
    royal_ranks = {'10', 'J', 'Q', 'K', 'A'}
    card_ranks = {card.rank for card in cards}
    
    # Check if we have all royal flush ranks
    return royal_ranks.issubset(card_ranks)

def is_community_royal(community_cards: List[Card]) -> bool:
    """Check if the community cards make a royal flush."""
    if len(community_cards) != 5:
        return False
        
    # Check if we have all the same suit
    suits = {card.suit for card in community_cards}
    if len(suits) != 1:
        return False
    
    # Get the ranks we need for a royal flush
    royal_ranks = {'10', 'J', 'Q', 'K', 'A'}
    card_ranks = {card.rank for card in community_cards}
    
    # Check if we have all royal flush ranks
    return royal_ranks == card_ranks

def is_straight_flush(cards: List[Card]) -> bool:
    """Check if the cards make a straight flush."""
    if len(cards) < 5:
        return False
        
    # Get all cards of each suit
    suit_cards = defaultdict(list)
    for card in cards:
        suit_cards[card.suit].append(card)
    
    # Check each suit for a straight flush
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
                  'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    for suit_group in suit_cards.values():
        if len(suit_group) >= 5:
            # Sort by rank value
            values = sorted([rank_values[card.rank] for card in suit_group])
            
            # Check for straight (including Ace-low straight)
            for i in range(len(values) - 4):
                if values[i+4] - values[i] == 4:  # Found 5 consecutive cards
                    return True
            
            # Check specifically for Ace-low straight (A,2,3,4,5)
            if 14 in values:  # If we have an Ace
                values = [1 if x == 14 else x for x in values]  # Convert Ace to 1
                values.sort()
                for i in range(len(values) - 4):
                    if values[i+4] - values[i] == 4:  # Found 5 consecutive cards
                        return True
    
    return False

def is_four_of_a_kind(cards: List[Card]) -> bool:
    """Check if the cards contain four of a kind."""
    if len(cards) < 4:
        return False
    
    # Count occurrences of each rank
    rank_counts = defaultdict(int)
    for card in cards:
        rank_counts[card.rank] += 1
    
    # Check if any rank appears 4 times
    return any(count >= 4 for count in rank_counts.values())

def is_full_house(cards: List[Card]) -> bool:
    """Check if the cards contain a full house."""
    if len(cards) < 5:
        return False
    
    # Count occurrences of each rank
    rank_counts = defaultdict(int)
    for card in cards:
        rank_counts[card.rank] += 1
    
    # Need at least one three of a kind and one pair
    counts = sorted(rank_counts.values(), reverse=True)
    return len(counts) >= 2 and counts[0] >= 3 and counts[1] >= 2

def simulate_hands(num_hands: int, start_hand: int = 0, last_hits: Dict[str, int] = None) -> tuple[dict, dict, Dict[str, int]]:
    if last_hits is None:
        last_hits = {
            'royal_flush': 0,
            'community_royal': 0,
            'straight_flush': 0,
            'four_of_a_kind': 0,
            'full_house': 0
        }
    
    results = defaultdict(int)
    wait_times = {
        'royal_flush': [],
        'community_royal': [],
        'straight_flush': [],
        'four_of_a_kind': [],
        'full_house': []
    }
    
    deck = Deck()
    
    for i in range(start_hand, start_hand + num_hands):
        if (i - start_hand) % 1_000_000 == 0:  # Print progress less frequently
            print(f"Progress: {(i - start_hand)/num_hands*100:.1f}% complete...")
            
        # Reset and shuffle deck
        deck.reset()
        
        # Deal hole cards (2 cards)
        hole_cards = [deck.deal() for _ in range(2)]
        
        # Deal community cards (5 cards)
        community_cards = [deck.deal() for _ in range(5)]
        
        # Check for all possible hands using all 7 cards
        all_cards = hole_cards + community_cards
        
        # Check for hands in order of priority
        if is_royal_flush(all_cards):
            results['royal_flush'] += 1
            if last_hits['royal_flush'] > 0:
                wait_times['royal_flush'].append(i - last_hits['royal_flush'])
            last_hits['royal_flush'] = i
        elif is_community_royal(community_cards):
            results['community_royal'] += 1
            if last_hits['community_royal'] > 0:
                wait_times['community_royal'].append(i - last_hits['community_royal'])
            last_hits['community_royal'] = i
        elif is_straight_flush(all_cards):
            results['straight_flush'] += 1
            if last_hits['straight_flush'] > 0:
                wait_times['straight_flush'].append(i - last_hits['straight_flush'])
            last_hits['straight_flush'] = i
        elif is_four_of_a_kind(all_cards):
            results['four_of_a_kind'] += 1
            if last_hits['four_of_a_kind'] > 0:
                wait_times['four_of_a_kind'].append(i - last_hits['four_of_a_kind'])
            last_hits['four_of_a_kind'] = i
        elif is_full_house(all_cards):
            results['full_house'] += 1
            if last_hits['full_house'] > 0:
                wait_times['full_house'].append(i - last_hits['full_house'])
            last_hits['full_house'] = i
    
    results['total_hands'] = num_hands
    return results, wait_times, last_hits

def calculate_fair_payouts(results: dict) -> tuple:
    """Calculate fair progressive payouts for 5 CHF bet."""
    total_hands = results['total_hands']
    bet_amount = 5  # CHF
    
    # Calculate total amount bet
    total_bet = total_hands * bet_amount
    
    # Calculate fixed payouts
    fixed_payouts = (
        results['community_royal'] * 5000 +  # Community Royal is fixed at 5000 CHF
        results['straight_flush'] * 50 +
        results['four_of_a_kind'] * 40 +
        results['full_house'] * 30
    )
    
    # Remaining amount that needs to be covered by progressives
    remaining = total_bet - fixed_payouts
    
    royal_hits = results['royal_flush']
    
    if royal_hits == 0:
        return 0
    
    # Only royal flush is progressive now
    royal_payout = remaining / royal_hits
    
    return royal_payout, 5000  # Return fixed community payout

def main():
    NUM_HANDS = 10_000_000  # 10 million hands
    CHUNK_SIZE = 100_000   # Process in chunks of 100K for memory efficiency
    
    print(f"Running simulation for {NUM_HANDS:,} hands...")
    
    # Initialize aggregate results
    total_results = defaultdict(int)
    chunk_results = []
    all_wait_times = {
        'royal_flush': [],
        'community_royal': [],
        'straight_flush': [],
        'four_of_a_kind': [],
        'full_house': []
    }
    
    # Track last hits across chunks
    last_hits = {
        'royal_flush': 0,
        'community_royal': 0,
        'straight_flush': 0,
        'four_of_a_kind': 0,
        'full_house': 0
    }
    
    try:
        # Process in chunks
        num_chunks = NUM_HANDS // CHUNK_SIZE
        for chunk in range(num_chunks):
            try:
                print(f"\nProcessing chunk {chunk + 1}/{num_chunks}")
                print(f"Total hands processed so far: {chunk * CHUNK_SIZE:,}")
                
                start_hand = chunk * CHUNK_SIZE
                results, wait_times, last_hits = simulate_hands(CHUNK_SIZE, start_hand, last_hits)
                
                # Store chunk results
                results['chunk'] = chunk + 1
                chunk_results.append(results.copy())
                
                # Aggregate results and wait times
                for key in results:
                    if key != 'chunk' and key != 'total_hands':
                        total_results[key] += results[key]
                
                for hand_type in wait_times:
                    all_wait_times[hand_type].extend(wait_times[hand_type])
                
                # Print intermediate results every 10 chunks
                if (chunk + 1) % 10 == 0:
                    print("\nIntermediate results after", (chunk + 1), "chunks:")
                    for hand_type in ['royal_flush', 'community_royal', 'straight_flush', 'four_of_a_kind', 'full_house']:
                        print(f"{hand_type.replace('_', ' ').title()}: {total_results[hand_type]:,} hits")
                    
            except Exception as e:
                print(f"\nError processing chunk {chunk + 1}: {str(e)}")
                raise
        
        total_results['total_hands'] = NUM_HANDS
        
        # Calculate wait time statistics for each hand type
        wait_stats = {}
        for hand_type in all_wait_times:
            if all_wait_times[hand_type]:
                wait_stats[hand_type] = {
                    'min': min(all_wait_times[hand_type]),
                    'max': max(all_wait_times[hand_type]),
                    'mean': np.mean(all_wait_times[hand_type]),
                    'std': np.std(all_wait_times[hand_type]),
                    'percentiles': np.percentile(all_wait_times[hand_type], [25, 50, 75, 90, 95, 99])
                }
            else:
                wait_stats[hand_type] = {
                    'min': 0, 'max': 0, 'mean': 0, 'std': 0,
                    'percentiles': [0] * 6
                }
        
        # Calculate fair payouts
        royal_payout, community_payout = calculate_fair_payouts(total_results)
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(os.path.dirname(__file__), f"ultimate_holdem_results_{timestamp}.csv")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write summary
            writer.writerow(['Summary Statistics'])
            writer.writerow(['Total Hands', NUM_HANDS])
            writer.writerow(['Total Bet', NUM_HANDS * 5])
            writer.writerow([''])
            
            # Write payout analysis
            writer.writerow(['Payout Information'])
            writer.writerow(['Fixed Payouts'])
            community_royal_payout = total_results['community_royal'] * 5000
            straight_flush_payout = total_results['straight_flush'] * 50
            four_kind_payout = total_results['four_of_a_kind'] * 40
            full_house_payout = total_results['full_house'] * 30
            total_fixed = community_royal_payout + straight_flush_payout + four_kind_payout + full_house_payout
            
            writer.writerow(['Community Royal (5000 CHF)', f"{community_royal_payout:,.0f}"])
            writer.writerow(['Straight Flush (50 CHF)', f"{straight_flush_payout:,.0f}"])
            writer.writerow(['Four of a Kind (40 CHF)', f"{four_kind_payout:,.0f}"])
            writer.writerow(['Full House (30 CHF)', f"{full_house_payout:,.0f}"])
            writer.writerow(['Total Fixed Payouts', f"{total_fixed:,.0f}"])
            writer.writerow([''])
            
            writer.writerow(['Progressive Information'])
            remaining = NUM_HANDS * 5 - total_fixed
            writer.writerow(['Remaining to Cover', f"{remaining:,.0f}"])
            writer.writerow(['Royal Progressive Payout', f"CHF {royal_payout:,.2f}"])
            writer.writerow([''])
            
            # Write frequencies
            writer.writerow(['Win Type', 'Hits', 'Frequency', '1 in X hands'])
            for hand_type in ['royal_flush', 'community_royal', 'straight_flush', 'four_of_a_kind', 'full_house']:
                hits = total_results[hand_type]
                writer.writerow([
                    hand_type.replace('_', ' ').title(),
                    hits,
                    f"{hits/NUM_HANDS*100:.6f}%",
                    f"1 in {NUM_HANDS/hits:,.0f}" if hits > 0 else "N/A"
                ])
            writer.writerow([''])
            
            # Write wait time statistics
            writer.writerow(['Wait Time Statistics'])
            writer.writerow(['Hand Type', 'Min Wait', 'Max Wait', 'Mean Wait', 'Std Dev', '25th', '50th', '75th', '90th', '95th', '99th'])
            for hand_type in wait_stats:
                stats = wait_stats[hand_type]
                writer.writerow([
                    hand_type.replace('_', ' ').title(),
                    f"{stats['min']:,}",
                    f"{stats['max']:,}",
                    f"{stats['mean']:,.1f}",
                    f"{stats['std']:,.1f}",
                    f"{stats['percentiles'][0]:,.0f}",
                    f"{stats['percentiles'][1]:,.0f}",
                    f"{stats['percentiles'][2]:,.0f}",
                    f"{stats['percentiles'][3]:,.0f}",
                    f"{stats['percentiles'][4]:,.0f}",
                    f"{stats['percentiles'][5]:,.0f}"
                ])
            writer.writerow([''])
            
            # Write wait times log
            writer.writerow(['Wait Times Log'])
            for hand_type in all_wait_times:
                writer.writerow([hand_type.replace('_', ' ').title()] + [str(x) for x in all_wait_times[hand_type]])
            writer.writerow([''])
            
            # Write chunk data
            writer.writerow(['Chunk Results'])
            writer.writerow(['Chunk'] + [hand_type.replace('_', ' ').title() for hand_type in ['royal_flush', 'community_royal', 'straight_flush', 'four_of_a_kind', 'full_house']])
            for chunk in chunk_results:
                writer.writerow([
                    chunk['chunk']] + [chunk[hand_type] for hand_type in ['royal_flush', 'community_royal', 'straight_flush', 'four_of_a_kind', 'full_house']
                ])
        
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"\nError in main(): {str(e)}")
        raise

if __name__ == '__main__':
    main() 