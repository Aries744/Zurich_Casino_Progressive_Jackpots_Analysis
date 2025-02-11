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
    'royal': '#8B0000',  # Dark red for royal flush
    'box_color': '#A5A5A5'  # Gray
}

# Read the CSV file - skip to the chunk results section
def process_latest_csv():
    import glob
    import os
    # Get the most recent results file
    list_of_files = glob.glob('ultimate_holdem_results_*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file, pd.read_csv(latest_file, skiprows=11)

latest_file, chunk_data = process_latest_csv()

# Calculate statistics
hands_per_chunk = 1_000_000
royal_freq = hands_per_chunk / chunk_data['Royal Flush Hits']
exp_royal_wait = royal_freq.mean()
royal_ci = np.percentile(royal_freq, [2.5, 97.5])

# Calculate session-based statistics
hands_per_session = 20 * 3  # 20 hands/hour * 3 hours
sessions_for_royal = exp_royal_wait / hands_per_session

# Calculate confidence intervals in terms of sessions
royal_sessions_ci = [ci / hands_per_session for ci in royal_ci]

# Create figure
fig = plt.figure(figsize=(16, 8))
gs = plt.GridSpec(2, 2, figure=fig)
fig.suptitle('Ultimate Texas Hold\'em Royal Flush Analysis\n10 Million Hands Simulation', 
             fontsize=14, y=0.95, fontweight='bold')

# Royal Flush Distribution
ax1 = fig.add_subplot(gs[0, 0])
sns.boxplot(data=chunk_data[['Royal Flush Hits']], ax=ax1,
            color=colors['royal'])
ax1.set_title('Royal Flush Hits\nper 1M Hands', pad=10)
ax1.set_ylabel('Number of Hits')
ax1.grid(True, alpha=0.3)

# Royal Flush Time Series
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(chunk_data['Chunk'], chunk_data['Royal Flush Hits'], '-o', 
         color=colors['royal'], linewidth=2, markersize=6)
ax2.set_title('Royal Flush Hits by Chunk', pad=10)
ax2.set_xlabel('Chunk Number (1M hands each)')
ax2.set_ylabel('Number of Hits')
ax2.grid(True, alpha=0.3)

# Statistics text box
stats_text = (
    "Playing Pattern:\n"
    "• 20 hands per hour\n"
    "• 3 hour sessions\n"
    "• 60 hands per session\n\n"
    "Royal Flush Statistics\n"
    f"Expected wait: 1 in {exp_royal_wait:,.0f} hands\n"
    f"Number of sessions: {sessions_for_royal:,.1f}\n"
    f"95% CI: [{royal_sessions_ci[0]:,.1f} to {royal_sessions_ci[1]:,.1f}] sessions\n\n"
    "Time to Hit (1 session/week):\n"
    f"Expected: {sessions_for_royal/52:.1f} years\n"
    f"95% CI: [{royal_sessions_ci[0]/52:.1f} to {royal_sessions_ci[1]/52:.1f}] years\n\n"
    "Time to Hit (2 sessions/week):\n"
    f"Expected: {sessions_for_royal/104:.1f} years\n"
    f"95% CI: [{royal_sessions_ci[0]/104:.1f} to {royal_sessions_ci[1]/104:.1f}] years\n\n"
    "Time to Hit (1 session/day):\n"
    f"Expected: {sessions_for_royal/365:.1f} years\n"
    f"95% CI: [{royal_sessions_ci[0]/365:.1f} to {royal_sessions_ci[1]/365:.1f}] years"
)

# Add text box for statistics
props = dict(boxstyle='round', facecolor='white', alpha=0.9)
fig.text(0.55, 0.45, stats_text, fontsize=10, 
         bbox=props, family='monospace', va='center')

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('ultimate_holdem_distributions.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

# Print statistics to console
print("\nDetailed Session Statistics:")
print("\nPlaying Pattern:")
print("• 20 hands per hour")
print("• 3 hour sessions")
print("• 60 hands per session")

print(f"\nRoyal Flush:")
print(f"Expected wait: 1 in {exp_royal_wait:,.0f} hands")
print(f"95% CI: 1 in {royal_ci[0]:,.0f} to 1 in {royal_ci[1]:,.0f} hands")
print(f"\nExpected sessions until hit: {sessions_for_royal:,.1f}")
print(f"95% CI: [{royal_sessions_ci[0]:,.1f} to {royal_sessions_ci[1]:,.1f}] sessions")

print("\nTime to Hit:")
print(f"At 1 session/week: {sessions_for_royal/52:.1f} years")
print(f"At 2 sessions/week: {sessions_for_royal/104:.1f} years")
print(f"At 1 session/day: {sessions_for_royal/365:.1f} years") 