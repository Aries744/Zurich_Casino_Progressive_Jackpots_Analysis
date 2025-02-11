# Casino Progressives Analysis

A Python-based analysis toolkit for simulating and analyzing the fair value of the progressive jackpots in Zurich Casino table games. This project simulates and analyzes the [Swiss Casinos Royal Jackpot](https://www.swisscasinos.ch/en/royal-jackpot) side bets for Ultimate Texas Hold'em and Blackjack to determine at which jackpot values the 5 CHF side bet becomes profitable. Both games are simulated with 100 million hands to ensure statistical significance.

## Royal Jackpot Details

### Ultimate Texas Hold'em Progressive
- Side bet: 5 CHF
- Networked across all Swiss Casinos locations (Pfäffikon, St. Gallen, Schaffhausen, Zurich)
- Must be placed before cards are dealt
- Base game bet required

**Payout Table:**
| Hand played | Payout | 
|-------------|--------|
| Royal flush | 100% of jackpot |
| Community royal | 5,000 CHF |
| Straight flush | 1,500 CHF |
| Four-of-a-kind | 500 CHF |
| Full house | 50 CHF |

### Blackjack Progressive
- Side bet: 5 CHF
- Networked across all Swiss Casinos locations
- Must be placed before cards are dealt
- Base game bet required
- First two cards of player and dealer determine outcome

**Payout Table:**
| Player's hand | Dealer's hand | Payout |
|--------------|---------------|---------|
| Suited A/J | Suited A/J | Major jackpot |
| Suited A/J | Off-suited A/J | Minor jackpot |
| Suited A/J | - | 350 CHF |
| Same color A/J | - | 250 CHF |
| Any A/J | - | 100 CHF |
| Blackjack | - | 25 CHF |

## Project Structure

```
zurich_casino_progressives_analysis/
├── blackjack/
│   ├── blackjack_simulation.py
│   ├── plot_results.py
│   └── blackjack_results_*.csv
├── ultimate_texas_holdem/
│   ├── ultimate_holdem_simulation.py
│   ├── plot_results.py
│   └── ultimate_holdem_results_*.csv
└── README.md
```

## Features

- **Ultimate Texas Hold'em Analysis**
  - Simulates poker hand combinations across 100M hands
  - Detects royal flushes, straight flushes, four of a kind, and full houses
  - Calculates probabilities and fair payouts to determine profitable jackpot thresholds
  - Generates detailed CSV reports with simulation results
  - Example results and visualizations included

- **Blackjack Progressive Analysis**
  - Simulates blackjack hands with progressive side bets across 100M hands
  - Tracks major and minor progressive hit frequencies as well as fixed payouts
  - Calculates expected value based on current jackpot amounts
  - Generates statistical analysis and visualizations
  - Example results and visualizations included

## Requirements

- Python 3.8+
- Required packages:
  - pandas
  - matplotlib
  - seaborn
  - numpy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/zurich_casino_progressives_analysis.git
cd zurich_casino_progressives_analysis
```

2. Install required packages:
```bash
pip install pandas matplotlib seaborn numpy
```

## Usage

### Ultimate Texas Hold'em Simulation

Run the Ultimate Texas Hold'em simulation:
```bash
cd ultimate_texas_holdem
python ultimate_holdem_simulation.py
```

The simulation will generate a CSV file with results in the format `ultimate_holdem_results_YYYYMMDD_HHMMSS.csv`.

### Blackjack Progressive Analysis

Run the Blackjack simulation:
```bash
cd blackjack
python blackjack_simulation.py
```

To visualize the results:
```bash
python plot_results.py
```

## Data Analysis

The project includes visualization scripts that generate plots and statistical analyses of the simulation results. These visualizations help in understanding:
- Hit frequencies for different hand combinations
- Progressive jackpot growth patterns
- Fair payout calculations
- Statistical distribution of winning hands

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE) 