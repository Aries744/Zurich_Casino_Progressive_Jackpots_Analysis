# Casino Progressives Analysis

A Python-based analysis toolkit for simulating and analyzing the fair value of the progressive jackpots in Zurich Casino table games. This project currently includes simulations for Ultimate Texas Hold'em and Blackjack progressive side bets, helping to understand the frequency of various winning combinations and calculate fair payouts. Both games are simulated with 100 million hands to ensure statistical significance.

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
  - Calculates probabilities and fair payouts
  - Generates detailed CSV reports with simulation results

- **Blackjack Progressive Analysis**
  - Simulates blackjack hands with progressive side bets across 100M hands
  - Tracks major and minor progressive hit frequencies as well as fixed payouts
  - Generates statistical analysis and visualizations

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