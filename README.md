# Casino Progressives Analysis

A Python-based analysis toolkit for simulating and analyzing the fair value of the progressive jackpots in Zurich Casino table games. This project simulates and analyzes the [Swiss Casinos Royal Jackpot](https://www.swisscasinos.ch/en/royal-jackpot) side bets for Ultimate Texas Hold'em and Blackjack to determine at which jackpot values the 5 CHF side bet becomes profitable. Both games are simulated with 10 million hands to ensure statistical significance.

## Royal Jackpot Details

### Ultimate Texas Hold'em Progressive
- Side bet: 5 CHF
- Networked across all Swiss Casinos locations (Pfäffikon, St. Gallen, Schaffhausen, Zurich)
- Must be placed before cards are dealt
- Base game bet required

**Payout Table:**
| Hand played | Payout | Frequency (1 in X hands) |
|-------------|--------|------------------------|
| Royal flush | Progressive | 1,111,111 |
| Community royal | 5,000 CHF | 1,111,111 |
| Straight flush | 50 CHF | 3,220 |
| Four-of-a-kind | 40 CHF | 592 |
| Full house | 30 CHF | 39 |

### Blackjack Progressive
- Side bet: 5 CHF
- Networked across all Swiss Casinos locations
- Must be placed before cards are dealt
- Base game bet required
- First two cards of player and dealer determine outcome

**Payout Table:**
| Player's hand | Dealer's hand | Payout | Frequency (1 in X hands) |
|--------------|---------------|---------|------------------------|
| Suited A/J | Suited A/J | Major Progressive | 117,647 |
| Suited A/J | Off-suited A/J | Minor Progressive | 39,683 |
| Suited A/J | - | 350 CHF | 352 |
| Same color A/J | - | 250 CHF | 353 |
| Any A/J | - | 100 CHF | 178 |
| Blackjack | - | 25 CHF | 29 |

## Simulation Features

### Core Features
- Simulates 10 million hands for each game type
- Processes hands in chunks of 100,000 for memory efficiency
- Tracks exact hand number for each progressive hit
- Calculates wait times between hits
- Records longest drought periods
- Generates comprehensive statistical analysis

### Analysis Outputs
- Hit frequencies and distributions
- Wait time statistics (min, max, average, standard deviation)
- Percentile analysis (25th, 50th, 75th, 90th, 95th, 99th)
- Drought period analysis
- Running hit rates by chunk
- Detailed CSV reports with timestamped results

### Visualization
- Time series plots of hits per chunk
- Wait time distribution histograms
- Statistical summary boxes
- Separate visualizations for rare and common hands
- High-resolution PNG output with publication-quality formatting

## Project Structure

```
zurich_casino_progressives_analysis/
├── blackjack/
│   ├── blackjack_simulation.py   # Blackjack simulation logic
│   ├── plot_results.py          # Blackjack visualization
│   └── blackjack_results_*.csv  # Timestamped results
├── ultimate_texas_holdem/
│   ├── ultimate_holdem_simulation.py   # UTH simulation logic
│   ├── plot_results.py                # UTH visualization
│   └── ultimate_holdem_results_*.csv  # Timestamped results
└── README.md
```

## Requirements

- Python 3.8+
- Required packages:
  - numpy
  - pandas
  - matplotlib
  - seaborn

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Aries744/Zurich_Casino_Progressive_Jackpots_Analysis.git
cd zurich_casino_progressives_analysis
```

2. Install required packages:
```bash
pip install numpy pandas matplotlib seaborn
```

## Usage

### Running Simulations

Run the Ultimate Texas Hold'em simulation:
```bash
cd ultimate_texas_holdem
python ultimate_holdem_simulation.py
```

Run the Blackjack simulation:
```bash
cd blackjack
python blackjack_simulation.py
```

### Generating Visualizations

For Ultimate Texas Hold'em:
```bash
cd ultimate_texas_holdem
python plot_results.py
```

For Blackjack:
```bash
cd blackjack
python plot_results.py
```

### Output Files

Each simulation generates:
1. A timestamped CSV file with detailed results (`*_results_YYYYMMDD_HHMMSS.csv`)
2. A high-resolution plot (`*_analysis.png`)

The CSV files contain:
- Summary statistics
- Hit frequencies
- Wait time statistics
- Complete wait time logs
- Chunk-by-chunk results

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE) 