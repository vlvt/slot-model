# Slot Model

- **Python** scripts for Monte-Carlo simulation and empirical verification  

## Repository Contents

```text

├── reels.csv           # Reel strips: REEL1…REEL5 columns
├── paytable.csv        # Coins paytable: SYMBOL, COUNT 1…COUNT 5
├── main.py             # Full simulation (line wins + free spins)
├── test.py             # Empirical bonus‐probability verification
└── README.md           # This file
```
## Quickstart

1. **Clone** the repository:  
   ```bash
   git clone https://github.com/<your-username>/slot-model.git
   cd slot-model

	2.	Inspect the input CSVs (reels.csv, paytable.csv).
	3.	Run the full simulation (main.py):

python main.py

This prints:
	•	E_line: average coins per spin from line wins
	•	P_bonus: probability of triggering the bonus
	•	E_bonus: average coins earned from free spins
	•	Gross RTP and Net RTP

	4.	Verify bonus probability (test.py):

python test.py

This prints per-reel and overall theoretical vs. empirical bonus probabilities, their differences.

Google Sheets Model

All theoretical calculations are implemented in a spreadsheet with these tabs:

	1.	Inputs – raw reel definitions & coins paytable
	2.	Probabilities – per-symbol and per-reel probability tables
	3.	PayTable – dynamic VLOOKUP source for payouts
	4.	Line EV – expected line-win contributions by symbol
	5.	Bonus – bonus-trigger probability and EV contribution
	6.	Summary – final RTP metrics & theory vs. simulation comparison

License

This project is licensed under the MIT License.

