import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os

# Set style for better looking plots
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Custom color palette
colors = {
    'royal': '#2E86AB',      # Blue
    'community': '#F6511D',  # Orange
    'straight': '#7FB800',   # Green
    'four': '#FFB400',       # Yellow
    'full': '#A239CA'        # Purple
}

def get_color_key(hand_type: str) -> str:
    """Get the color key for a hand type."""
    if 'Royal Flush' in hand_type:
        return 'royal'
    elif 'Community Royal' in hand_type:
        return 'community'
    elif 'Straight Flush' in hand_type:
        return 'straight'
    elif 'Four Of A Kind' in hand_type:
        return 'four'
    else:  # Full House
        return 'full'

def process_latest_csv():
    """Get the most recent results file."""
    import glob
    import os
    list_of_files = glob.glob('ultimate_holdem_results_*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    
    # Read different sections of the CSV
    chunk_data = None
    wait_time_stats = None
    wait_times = {
        'royal_flush': [],
        'community_royal': [],
        'straight_flush': [],
        'four_of_a_kind': [],
        'full_house': []
    }
    
    with open(latest_file, 'r') as f:
        lines = f.readlines()
        
        # Find the chunk results section
        for i, line in enumerate(lines):
            if 'Chunk Results' in line:
                chunk_data = pd.read_csv(latest_file, skiprows=i+1)
                break
        
        # Find the wait time statistics section
        for i, line in enumerate(lines):
            if 'Wait Time Statistics' in line:
                wait_time_stats = pd.read_csv(latest_file, skiprows=i+1, nrows=6, thousands=',')
                break
                
        # Find and parse wait times
        for i, line in enumerate(lines):
            if 'Wait Times Log' in line:
                for j, hand_type in enumerate(['Royal Flush', 'Community Royal', 'Straight Flush', 'Four of a Kind', 'Full House']):
                    line = lines[i+1+j].strip()
                    times = [int(x.strip()) for x in line.split(',')[1:] if x.strip()]
                    wait_times[hand_type.lower().replace(' ', '_')] = times
                break
    
    return latest_file, chunk_data, wait_time_stats, wait_times

def main():
    # Read the CSV file
    latest_file, chunk_data, wait_time_stats, wait_times = process_latest_csv()
    
    # Create figure
    fig = plt.figure(figsize=(16, 12))
    gs = plt.GridSpec(2, 2, figure=fig)
    fig.suptitle('Ultimate Texas Hold\'em Progressive Analysis', 
                 fontsize=14, y=0.95, fontweight='bold')
    
    # Progressive Hits Time Series
    ax1 = fig.add_subplot(gs[0, 0])
    hand_types = ['Royal Flush', 'Community Royal', 'Straight Flush', 'Four Of A Kind', 'Full House']
    for hand_type in hand_types:
        col_name = hand_type
        color_key = get_color_key(hand_type)
        ax1.plot(chunk_data['Chunk'], chunk_data[col_name], '-o', 
                color=colors[color_key], label=hand_type, 
                linewidth=2, markersize=6)
    ax1.set_title('Hand Type Hits by Chunk', pad=10)
    ax1.set_xlabel('Chunk Number (100K hands each)')
    ax1.set_ylabel('Number of Hits')
    ax1.legend(frameon=True, facecolor='white', framealpha=1)
    ax1.grid(True, alpha=0.3)
    
    # Wait Time Distributions - Royal Flush and Community Royal
    ax2 = fig.add_subplot(gs[0, 1])
    for hand_type in ['royal_flush', 'community_royal']:
        if len(wait_times[hand_type]) > 1:
            sns.histplot(data=wait_times[hand_type], 
                        color=colors[get_color_key(hand_type)], alpha=0.6,
                        label=f"{hand_type.replace('_', ' ').title()} (n={len(wait_times[hand_type])})",
                        stat='density', bins=min(20, len(wait_times[hand_type])), ax=ax2)
    ax2.set_title('Royal Flush Wait Time Distributions', pad=10)
    ax2.set_xlabel('Wait Time (hands)')
    ax2.set_ylabel('Density')
    if all(len(wait_times[t]) <= 1 for t in ['royal_flush', 'community_royal']):
        ax2.text(0.5, 0.5, 'Insufficient wait time data\nfor distribution plot',
                 ha='center', va='center', transform=ax2.transAxes)
    else:
        ax2.legend(frameon=True, facecolor='white', framealpha=1)
    ax2.grid(True, alpha=0.3)
    
    # Wait Time Distributions - Other Hands
    ax3 = fig.add_subplot(gs[1, 0])
    for hand_type in ['straight_flush', 'four_of_a_kind', 'full_house']:
        if len(wait_times[hand_type]) > 1:
            sns.histplot(data=wait_times[hand_type],
                        color=colors[get_color_key(hand_type)], alpha=0.6,
                        label=f"{hand_type.replace('_', ' ').title()} (n={len(wait_times[hand_type])})",
                        stat='density', bins=min(20, len(wait_times[hand_type])), ax=ax3)
    ax3.set_title('Other Hand Types Wait Time Distributions', pad=10)
    ax3.set_xlabel('Wait Time (hands)')
    ax3.set_ylabel('Density')
    if all(len(wait_times[t]) <= 1 for t in ['straight_flush', 'four_of_a_kind', 'full_house']):
        ax3.text(0.5, 0.5, 'Insufficient wait time data\nfor distribution plot',
                 ha='center', va='center', transform=ax3.transAxes)
    else:
        ax3.legend(frameon=True, facecolor='white', framealpha=1)
    ax3.grid(True, alpha=0.3)
    
    # Statistics text box
    stats_text = "Wait Time Statistics (hands)\n\n"
    for hand_type in hand_types:
        key = hand_type.lower().replace(' ', '_')
        stats_text += (
            f"{hand_type} (n={len(wait_times[key])})\n"
            f"Min Wait: {wait_time_stats.iloc[hand_types.index(hand_type)]['Min Wait']}\n"
            f"Max Wait: {wait_time_stats.iloc[hand_types.index(hand_type)]['Max Wait']}\n"
            f"Mean Wait: {wait_time_stats.iloc[hand_types.index(hand_type)]['Mean Wait']}\n"
            f"Std Dev: {wait_time_stats.iloc[hand_types.index(hand_type)]['Std Dev']}\n\n"
            "Percentiles:\n"
            f"50th (Median): {wait_time_stats.iloc[hand_types.index(hand_type)]['50th']}\n"
            f"90th: {wait_time_stats.iloc[hand_types.index(hand_type)]['90th']}\n"
            f"95th: {wait_time_stats.iloc[hand_types.index(hand_type)]['95th']}\n"
            f"99th: {wait_time_stats.iloc[hand_types.index(hand_type)]['99th']}\n\n"
        )
    
    # Add text box for statistics
    props = dict(boxstyle='round', facecolor='white', alpha=0.9)
    fig.text(0.98, 0.50, stats_text, fontsize=10,
             bbox=props, family='monospace', va='center', ha='right')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 0.95, 0.95])
    plt.savefig('ultimate_holdem_analysis.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Plot saved as ultimate_holdem_analysis.png")

if __name__ == '__main__':
    main() 