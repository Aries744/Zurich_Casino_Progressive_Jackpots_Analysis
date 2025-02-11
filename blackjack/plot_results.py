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
    'major': '#2E86AB',  # Blue
    'minor': '#F6511D',  # Orange
    'box_color': '#A5A5A5'  # Gray
}

def process_latest_csv():
    """Get the most recent results file."""
    import glob
    import os
    list_of_files = glob.glob('blackjack_results_*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    
    # Read different sections of the CSV
    chunk_data = None
    wait_time_stats = None
    wait_times = {'major': [], 'minor': []}
    
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
                wait_time_stats = pd.read_csv(latest_file, skiprows=i+1, nrows=3, thousands=',')
                break
                
        # Find and parse wait times
        for i, line in enumerate(lines):
            if 'Wait Times Log' in line:
                major_line = lines[i+1].strip()  # Get full line for Major Progressive
                minor_line = lines[i+2].strip()  # Get full line for Minor Progressive
                
                # Split on comma and convert all non-empty values after the label to integers
                major_times = [int(x.strip()) for x in major_line.split(',')[1:] if x.strip()]
                minor_times = [int(x.strip()) for x in minor_line.split(',')[1:] if x.strip()]
                
                wait_times['major'] = major_times
                wait_times['minor'] = minor_times
                break
    
    return latest_file, chunk_data, wait_time_stats, wait_times

def main():
    # Read the CSV file
    latest_file, chunk_data, wait_time_stats, wait_times = process_latest_csv()
    
    # Create figure
    fig = plt.figure(figsize=(16, 8))
    gs = plt.GridSpec(1, 2, figure=fig)
    fig.suptitle('Blackjack Progressive Jackpot Analysis', 
                 fontsize=14, y=0.95, fontweight='bold')
    
    # Progressive Hits Time Series
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(chunk_data['Chunk'], chunk_data['Major Hits'], '-o', 
             color=colors['major'], label='Major', linewidth=2, markersize=6)
    ax1.plot(chunk_data['Chunk'], chunk_data['Minor Hits'], '-o', 
             color=colors['minor'], label='Minor', linewidth=2, markersize=6)
    ax1.set_title('Progressive Hits by Chunk', pad=10)
    ax1.set_xlabel('Chunk Number (100K hands each)')
    ax1.set_ylabel('Number of Hits')
    ax1.legend(frameon=True, facecolor='white', framealpha=1)
    ax1.grid(True, alpha=0.3)
    
    # Wait Time Distributions
    ax2 = fig.add_subplot(gs[0, 1])
    if len(wait_times['major']) > 1:  # Only plot if we have more than one wait time
        sns.histplot(data=wait_times['major'], color=colors['major'], alpha=0.6, 
                    label=f'Major (n={len(wait_times["major"])})', stat='density', bins=min(20, len(wait_times['major'])), ax=ax2)
    if len(wait_times['minor']) > 1:  # Only plot if we have more than one wait time
        sns.histplot(data=wait_times['minor'], color=colors['minor'], alpha=0.6, 
                    label=f'Minor (n={len(wait_times["minor"])})', stat='density', bins=min(20, len(wait_times['minor'])), ax=ax2)
    ax2.set_title('Wait Time Distributions', pad=10)
    ax2.set_xlabel('Wait Time (hands)')
    ax2.set_ylabel('Density')
    if len(wait_times['major']) <= 1 and len(wait_times['minor']) <= 1:
        ax2.text(0.5, 0.5, 'Insufficient wait time data\nfor distribution plot', 
                 ha='center', va='center', transform=ax2.transAxes)
    else:
        ax2.legend(frameon=True, facecolor='white', framealpha=1)
    ax2.grid(True, alpha=0.3)
    
    # Statistics text box
    stats_text = (
        "Wait Time Statistics (hands)\n\n"
        f"Major Progressive (n={len(wait_times['major'])})\n"
        f"Min Wait: {wait_time_stats.iloc[0]['Min Wait']}\n"
        f"Max Wait: {wait_time_stats.iloc[0]['Max Wait']}\n"
        f"Mean Wait: {wait_time_stats.iloc[0]['Mean Wait']}\n"
        f"Std Dev: {wait_time_stats.iloc[0]['Std Dev']}\n\n"
        "Percentiles:\n"
        f"50th (Median): {wait_time_stats.iloc[0]['50th']}\n"
        f"90th: {wait_time_stats.iloc[0]['90th']}\n"
        f"95th: {wait_time_stats.iloc[0]['95th']}\n"
        f"99th: {wait_time_stats.iloc[0]['99th']}\n\n"
        f"Minor Progressive (n={len(wait_times['minor'])})\n"
        f"Min Wait: {wait_time_stats.iloc[1]['Min Wait']}\n"
        f"Max Wait: {wait_time_stats.iloc[1]['Max Wait']}\n"
        f"Mean Wait: {wait_time_stats.iloc[1]['Mean Wait']}\n"
        f"Std Dev: {wait_time_stats.iloc[1]['Std Dev']}\n\n"
        "Percentiles:\n"
        f"50th (Median): {wait_time_stats.iloc[1]['50th']}\n"
        f"90th: {wait_time_stats.iloc[1]['90th']}\n"
        f"95th: {wait_time_stats.iloc[1]['95th']}\n"
        f"99th: {wait_time_stats.iloc[1]['99th']}"
    )
    
    # Add text box for statistics
    props = dict(boxstyle='round', facecolor='white', alpha=0.9)
    fig.text(0.98, 0.50, stats_text, fontsize=10, 
             bbox=props, family='monospace', va='center', ha='right')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 0.95, 0.95])
    plt.savefig('blackjack_analysis.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Plot saved as blackjack_analysis.png")

if __name__ == '__main__':
    main() 