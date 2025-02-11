import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
    'other': '#7FB800',  # Green
    'box_color': '#A5A5A5'  # Gray
}

# Read the CSV file - skip to the chunk results section
def process_latest_csv():
    import glob
    import os
    # Get the most recent results file
    list_of_files = glob.glob('blackjack_results_*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file, pd.read_csv(latest_file, skiprows=27)

latest_file, chunk_data = process_latest_csv()

# Calculate statistics
hands_per_chunk = 10_000_000
major_freq = hands_per_chunk / chunk_data['Major Hits']
minor_freq = hands_per_chunk / chunk_data['Minor Hits']
exp_major_wait = major_freq.mean()
exp_minor_wait = minor_freq.mean()
major_ci = np.percentile(major_freq, [2.5, 97.5])
minor_ci = np.percentile(minor_freq, [2.5, 97.5])

# Calculate session-based statistics
hands_per_session = 20 * 3  # 20 hands/hour * 3 hours
sessions_for_major = exp_major_wait / hands_per_session
sessions_for_minor = exp_minor_wait / hands_per_session

# Calculate confidence intervals in terms of sessions
major_sessions_ci = [ci / hands_per_session for ci in major_ci]
minor_sessions_ci = [ci / hands_per_session for ci in minor_ci]

# Create figure
fig = plt.figure(figsize=(16, 10))
gs = plt.GridSpec(2, 4, figure=fig)
fig.suptitle('Blackjack Progressive Jackpot Analysis\n100 Million Hands Simulation', 
             fontsize=14, y=0.95, fontweight='bold')

# Progressive Hits Distribution (larger, spanning two columns)
ax1 = fig.add_subplot(gs[0, :2])
sns.boxplot(data=chunk_data[['Major Hits', 'Minor Hits']], ax=ax1,
            palette=[colors['major'], colors['minor']])
ax1.set_title('Progressive Jackpot Hits\nper 10M Hands', pad=10)
ax1.set_ylabel('Number of Hits')
ax1.grid(True, alpha=0.3)

# A/J Combinations (larger, spanning two columns)
ax2 = fig.add_subplot(gs[0, 2:])
sns.boxplot(data=chunk_data[['Suited A/J', 'Colored A/J', 'Mixed A/J']], ax=ax2,
            palette=['#FFB400', '#DC851F', '#C05640'])
ax2.set_title('Ace-Jack Combination Hits\nper 10M Hands', pad=10)
ax2.set_ylabel('Number of Hits')
ax2.grid(True, alpha=0.3)

# Progressive Hits Time Series
ax3 = fig.add_subplot(gs[1, :2])
ax3.plot(chunk_data['Chunk'], chunk_data['Major Hits'], '-o', 
         color=colors['major'], label='Major', linewidth=2, markersize=6)
ax3.plot(chunk_data['Chunk'], chunk_data['Minor Hits'], '-o', 
         color=colors['minor'], label='Minor', linewidth=2, markersize=6)
ax3.set_title('Progressive Hits by Chunk', pad=10)
ax3.set_xlabel('Chunk Number (10M hands each)')
ax3.set_ylabel('Number of Hits')
ax3.legend(frameon=True, facecolor='white', framealpha=1)
ax3.grid(True, alpha=0.3)

# Statistics text box
stats_text = (
    "Playing Pattern:\n"
    "• 20 hands per hour\n"
    "• 3 hour sessions\n"
    "• 60 hands per session\n\n"
    "Major Progressive Jackpot\n"
    f"Expected wait: 1 in {exp_major_wait:,.0f} hands\n"
    f"Number of sessions: {sessions_for_major:,.1f}\n"
    f"95% CI: [{major_sessions_ci[0]:,.1f} to {major_sessions_ci[1]:,.1f}] sessions\n"
    f"Years at 1 session/week: {sessions_for_major/52:.1f}\n\n"
    "Minor Progressive Jackpot\n"
    f"Expected wait: 1 in {exp_minor_wait:,.0f} hands\n"
    f"Number of sessions: {sessions_for_minor:,.1f}\n"
    f"95% CI: [{minor_sessions_ci[0]:,.1f} to {minor_sessions_ci[1]:,.1f}] sessions\n"
    f"Years at 1 session/week: {sessions_for_minor/52:.1f}\n\n"
    "Session Frequencies:\n"
    f"1 session/day: {sessions_for_major/365:.1f} years for Major\n"
    f"1 session/week: {sessions_for_major/52:.1f} years for Major\n"
    f"2 sessions/week: {sessions_for_major/104:.1f} years for Major"
)

# Add text box for statistics
props = dict(boxstyle='round', facecolor='white', alpha=0.9)
fig.text(0.55, 0.30, stats_text, fontsize=10, 
         bbox=props, family='monospace', va='center')

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('blackjack_distributions.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

# Print detailed statistics
print("\nDetailed Session Statistics:")
print("\nPlaying Pattern:")
print("• 20 hands per hour")
print("• 3 hour sessions")
print("• 60 hands per session")

print(f"\nMajor Progressive:")
print(f"Expected sessions until hit: {sessions_for_major:,.1f}")
print(f"95% CI: [{major_sessions_ci[0]:,.1f} to {major_sessions_ci[1]:,.1f}] sessions")
print(f"Years at 1 session/week: {sessions_for_major/52:.1f}")
print(f"Years at 2 sessions/week: {sessions_for_major/104:.1f}")
print(f"Years at 1 session/day: {sessions_for_major/365:.1f}")

print(f"\nMinor Progressive:")
print(f"Expected sessions until hit: {sessions_for_minor:,.1f}")
print(f"95% CI: [{minor_sessions_ci[0]:,.1f} to {minor_sessions_ci[1]:,.1f}] sessions")
print(f"Years at 1 session/week: {sessions_for_minor/52:.1f}")
print(f"Years at 2 sessions/week: {sessions_for_minor/104:.1f}")
print(f"Years at 1 session/day: {sessions_for_minor/365:.1f}") 