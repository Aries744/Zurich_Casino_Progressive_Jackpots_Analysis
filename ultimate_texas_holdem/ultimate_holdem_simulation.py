import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Tuple
import csv
from datetime import datetime

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

def simulate_hands(num_hands: int) -> dict:
    results = defaultdict(int)
    deck = Deck()
    
    for i in range(num_hands):
        if i % 1_000_000 == 0:  # Print progress less frequently
            print(f"Progress: {i/num_hands*100:.1f}% complete...")
            
        # Reset and shuffle deck
        deck.reset()
        
        # Deal hole cards (2 cards)
        hole_cards = [deck.deal() for _ in range(2)]
        
        # Deal community cards (5 cards)
        community_cards = [deck.deal() for _ in range(5)]
        
        # Check for all possible hands using all 7 cards
        all_cards = hole_cards + community_cards
        
        # Check for royal flush (highest priority)
        if is_royal_flush(all_cards):
            results['royal_flush'] += 1
        # Check for community royal (second priority)
        elif is_community_royal(community_cards):
            results['community_royal'] += 1
        # Check for straight flush (third priority)
        elif is_straight_flush(all_cards):
            results['straight_flush'] += 1
        # Check for four of a kind (fourth priority)
        elif is_four_of_a_kind(all_cards):
            results['four_of_a_kind'] += 1
        # Check for full house (fifth priority)
        elif is_full_house(all_cards):
            results['full_house'] += 1
        
    results['total_hands'] = num_hands
    return results

def calculate_fair_payouts(results: dict) -> float:
    """Calculate fair progressive payout for 5 CHF bet."""
    total_hands = results['total_hands']
    bet_amount = 5  # CHF
    
    # Calculate total amount bet
    total_bet = total_hands * bet_amount
    
    # Calculate fixed payouts
    fixed_payouts = (
        results['community_royal'] * 5000 +  # Community Royal pays 5,000
        results['straight_flush'] * 1500 +   # Straight Flush pays 1,500
        results['four_of_a_kind'] * 500 +    # Four of a Kind pays 500
        results['full_house'] * 50           # Full House pays 50
    )
    
    # Calculate frequency
    royal_hits = results['royal_flush']
    
    if royal_hits == 0:
        return 0
    
    # Remaining amount that needs to be covered by progressive
    remaining = total_bet - fixed_payouts
    
    # Fair progressive payout would be remaining / number_of_hits
    fair_payout = remaining / royal_hits
    
    return fair_payout

def main():
    NUM_HANDS = 100_000_000  # 100 million hands
    CHUNK_SIZE = 1_000_000   # Process in chunks of 1M for memory efficiency
    
    print(f"Running simulation for {NUM_HANDS:,} hands...")
    
    # Initialize aggregate results
    total_results = defaultdict(int)
    chunk_results = []
    
    try:
        # Process in chunks
        num_chunks = NUM_HANDS // CHUNK_SIZE
        for chunk in range(num_chunks):
            try:
                print(f"\nProcessing chunk {chunk + 1}/{num_chunks}")
                print(f"Total hands processed so far: {chunk * CHUNK_SIZE:,}")
                
                results = simulate_hands(CHUNK_SIZE)
                
                # Store chunk results
                results['chunk'] = chunk + 1
                chunk_results.append(results.copy())
                
                # Aggregate results
                for key in results:
                    if key != 'chunk' and key != 'total_hands':
                        total_results[key] += results[key]
                
                # Print intermediate results every 10 chunks
                if (chunk + 1) % 10 == 0:
                    print("\nIntermediate results after", (chunk + 1), "chunks:")
                    print(f"Royal Flush hits: {total_results['royal_flush']:,}")
                    print(f"Community Royal hits: {total_results['community_royal']:,}")
                    print(f"Straight Flush hits: {total_results['straight_flush']:,}")
                    print(f"Four of a Kind hits: {total_results['four_of_a_kind']:,}")
                    print(f"Full House hits: {total_results['full_house']:,}")
                    
            except Exception as e:
                print(f"\nError processing chunk {chunk + 1}: {str(e)}")
                raise
        
        total_results['total_hands'] = NUM_HANDS
        
        # Calculate total bet and payouts
        total_bet = NUM_HANDS * 5
        community_royal_paid = total_results['community_royal'] * 5000
        straight_flush_paid = total_results['straight_flush'] * 1500
        four_kind_paid = total_results['four_of_a_kind'] * 500
        full_house_paid = total_results['full_house'] * 50
        total_fixed = community_royal_paid + straight_flush_paid + four_kind_paid + full_house_paid
        
        fair_payout = calculate_fair_payouts(total_results)
        
        print("\nFinal Results:")
        print(f"Total Hands: {total_results['total_hands']:,}")
        print(f"\nHand Frequencies:")
        print(f"Royal Flush: {total_results['royal_flush']:,} hits (1 in {NUM_HANDS/total_results['royal_flush']:,.0f})")
        print(f"Community Royal: {total_results['community_royal']:,} hits (1 in {NUM_HANDS/total_results['community_royal']:,.0f})")
        print(f"Straight Flush: {total_results['straight_flush']:,} hits (1 in {NUM_HANDS/total_results['straight_flush']:,.0f})")
        print(f"Four of a Kind: {total_results['four_of_a_kind']:,} hits (1 in {NUM_HANDS/total_results['four_of_a_kind']:,.0f})")
        print(f"Full House: {total_results['full_house']:,} hits (1 in {NUM_HANDS/total_results['full_house']:,.0f})")
        
        print(f"\nPayout Analysis:")
        print(f"Total Amount Bet: {total_bet:,.2f} CHF")
        print(f"Fixed Payouts Paid: {total_fixed:,.2f} CHF")
        print(f"Remaining for Progressive: {total_bet - total_fixed:,.2f} CHF")
        print(f"\nFair Progressive Value: {fair_payout:,.2f} CHF")
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ultimate_texas_holdem/ultimate_holdem_results_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write summary
            writer.writerow(['Summary Statistics'])
            writer.writerow(['Total Hands', NUM_HANDS])
            writer.writerow(['Total Bet', f"{total_bet:,.2f}"])
            writer.writerow([''])
            
            # Write frequencies
            writer.writerow(['Hand Type', 'Hits', 'Frequency', '1 in X hands'])
            writer.writerow(['Royal Flush', total_results['royal_flush'], 
                           f"{total_results['royal_flush']/NUM_HANDS*100:.6f}%",
                           f"1 in {NUM_HANDS/total_results['royal_flush']:,.0f}"])
            writer.writerow(['Community Royal', total_results['community_royal'],
                           f"{total_results['community_royal']/NUM_HANDS*100:.6f}%",
                           f"1 in {NUM_HANDS/total_results['community_royal']:,.0f}"])
            writer.writerow(['Straight Flush', total_results['straight_flush'],
                           f"{total_results['straight_flush']/NUM_HANDS*100:.6f}%",
                           f"1 in {NUM_HANDS/total_results['straight_flush']:,.0f}"])
            writer.writerow(['Four of a Kind', total_results['four_of_a_kind'],
                           f"{total_results['four_of_a_kind']/NUM_HANDS*100:.6f}%",
                           f"1 in {NUM_HANDS/total_results['four_of_a_kind']:,.0f}"])
            writer.writerow(['Full House', total_results['full_house'],
                           f"{total_results['full_house']/NUM_HANDS*100:.6f}%",
                           f"1 in {NUM_HANDS/total_results['full_house']:,.0f}"])
            writer.writerow([''])
            
            # Write payout information
            writer.writerow(['Payout Information'])
            writer.writerow(['Fixed Payouts'])
            writer.writerow(['Community Royal (5,000 CHF)', f"{community_royal_paid:,.2f}"])
            writer.writerow(['Straight Flush (1,500 CHF)', f"{straight_flush_paid:,.2f}"])
            writer.writerow(['Four of a Kind (500 CHF)', f"{four_kind_paid:,.2f}"])
            writer.writerow(['Full House (50 CHF)', f"{full_house_paid:,.2f}"])
            writer.writerow(['Total Fixed Payouts', f"{total_fixed:,.2f}"])
            writer.writerow([''])
            
            # Write progressive information
            writer.writerow(['Progressive Information'])
            writer.writerow(['Remaining to Cover', f"{total_bet - total_fixed:,.2f}"])
            writer.writerow(['Fair Progressive Value', f"{fair_payout:,.2f}"])
            writer.writerow([''])
            
            # Write chunk data
            writer.writerow(['Chunk Results'])
            writer.writerow(['Chunk', 'Royal Flush', 'Community Royal', 'Straight Flush', 'Four of a Kind', 'Full House'])
            for chunk in chunk_results:
                writer.writerow([
                    chunk['chunk'],
                    chunk['royal_flush'],
                    chunk['community_royal'],
                    chunk['straight_flush'],
                    chunk['four_of_a_kind'],
                    chunk['full_house']
                ])
        
        print(f"\nResults saved to {filename}")
        
    except Exception as e:
        print(f"\nError in main(): {str(e)}")
        raise

if __name__ == "__main__":
    main() 