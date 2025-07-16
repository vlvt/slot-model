# main.py
import pandas as pd
import random

# === Configuration ===
REELS_CSV = "reels.csv"
PAYTABLE_CSV = "paytable.csv"
N_SIMULATIONS = 100000
  # Number of spins to simulate
SEED = 4555665

random.seed(SEED)

# === Load and clean reels ===
reels_df = pd.read_csv(REELS_CSV)
reel_lists = {}
for i in range(1, 6):
    col = f"REEL{i}"
    reel = (
        reels_df[col]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
    # Remove empty strings if any
    reel_lists[col] = [s for s in reel if s]

# === Load paytable ===
paytable = pd.read_csv(PAYTABLE_CSV)
# Expected columns: SYMBOL, COUNT 1, COUNT 2, COUNT 3, COUNT 4, COUNT 5

# === Helper functions ===
def get_symbols(reel, pos):
    """Return [TOP, MIDDLE, BOTTOM] symbols for a given reel and stop position."""
    n = len(reel)
    return [
        reel[pos % n],
        reel[(pos + 1) % n],
        reel[(pos + 2) % n],
    ]

def calculate_line_win(middle_row):
    """Compute total line prize from all possible aligned sequences (2 to 5 in a row)."""
    total_win = 0
    for start in range(0, 5):  # возможные старты: 0,1,2,3,4
        for length in range(2, 6):  # длины: 2–5
            if start + length > 5:
                continue
            seq = middle_row[start:start + length]
            seq_sym = None
            count = 0
            for sym in seq:
                if sym == "BONUS":
                    break
                if sym == "WILD":
                    if seq_sym:
                        count += 1
                    continue
                if seq_sym is None:
                    seq_sym = sym
                    count = 1
                elif sym == seq_sym:
                    count += 1
                else:
                    break
            if not seq_sym or count != length:
                continue
            col = f"COUNT {count}"
            try:
                win = int(paytable.loc[paytable["SYMBOL"] == seq_sym, col].values[0])
                total_win += win
            except:
                continue
    return total_win

def is_bonus_trigger(all_symbols):
    """Return True if exactly 5 BONUS symbols appear anywhere in view."""
    return all_symbols.count("BONUS") == 5

# === Monte Carlo simulation ===
total_coins = 0
total_bonus_triggers = 0
total_free_spin_coins = 0

for _ in range(N_SIMULATIONS):
    # Regular spin
    view = []
    mid_row = []
    for i in range(1, 6):
        reel = reel_lists[f"REEL{i}"]
        pos = random.randint(0, len(reel) - 1)
        symbols = get_symbols(reel, pos)
        view.extend(symbols)
        mid_row.append(symbols[1])
    # Line win
    total_coins += calculate_line_win(mid_row)
    # Bonus check
    if is_bonus_trigger(view):
        total_bonus_triggers += 1
        # Simulate 3 free spins
        for _ in range(3):
            free_mid = []
            for j in range(1, 6):
                reel = reel_lists[f"REEL{j}"]
                pos = random.randint(0, len(reel) - 1)
                free_mid.append(get_symbols(reel, pos)[1])
            total_free_spin_coins += calculate_line_win(free_mid)

# === Results ===
E_line = total_coins / N_SIMULATIONS
P_bonus = total_bonus_triggers / N_SIMULATIONS
E_bonus_sim = total_free_spin_coins / N_SIMULATIONS
Gross_RTP = E_line + E_bonus_sim
Net_RTP = Gross_RTP - 1

# === Подсчёт вклада каждого символа ===
symbol_ev_sum = {}

for _ in range(N_SIMULATIONS):
    mid_row = []
    for i in range(1, 6):
        reel = reel_lists[f"REEL{i}"]
        pos = random.randint(0, len(reel) - 1)
        mid_row.append(get_symbols(reel, pos)[1])
        
    for start in range(0, 5):
        for length in range(2, 6):
            if start + length > 5:
                continue
            seq = mid_row[start:start + length]
            seq_sym = None
            count = 0
            for sym in seq:
                if sym == "BONUS":
                    break
                if sym == "WILD":
                    if seq_sym:
                        count += 1
                    continue
                if seq_sym is None:
                    seq_sym = sym
                    count = 1
                elif sym == seq_sym:
                    count += 1
                else:
                    break
            if not seq_sym or count != length:
                continue
            col = f"COUNT {count}"
            try:
                win = int(paytable.loc[paytable["SYMBOL"] == seq_sym, col].values[0])
                symbol_ev_sum[seq_sym] = symbol_ev_sum.get(seq_sym, 0) + win
            except:
                continue

symbol_ev_final = {sym: ev / N_SIMULATIONS for sym, ev in symbol_ev_sum.items()}
total_symbol_ev = sum(symbol_ev_final.values())

print("\n=== EV by SYMBOL ===")
for sym, ev in sorted(symbol_ev_final.items(), key=lambda x: -x[1]):
    perc = 100 * ev / (E_line + E_bonus_sim)
    print(f"{sym}: {ev:.6f} coins/spin ({perc:.2f}%)")

print("=== LUCKY7 SIMULATION WITH FREE SPINS ===")
print(f"Spins simulated:            {N_SIMULATIONS}")
print(f"E_line (avg coins/spin):    {E_line:.6f}")
print(f"P_bonus (chance bonus):     {P_bonus:.6%}")
print(f"E_bonus (avg from free):    {E_bonus_sim:.6f}")
print(f"Gross RTP:                  {Gross_RTP:.6f}")
print(f"Net RTP:                    {Net_RTP:.6f}")
