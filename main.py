# main.py
import pandas as pd
import random

# === Configuration ===
REELS_CSV = "reels.csv"
PAYTABLE_CSV = "paytable.csv"
N_SIMULATIONS = 100000
SEED = 42

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
    """Compute line prize on the middle row, with wild substitution."""
    seq_sym = None
    count = 0
    for sym in middle_row:
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
    if not seq_sym or count < 1:
        return 0
    col = f"COUNT {count}"
    try:
        return int(paytable.loc[paytable["SYMBOL"] == seq_sym, col].values[0])
    except:
        return 0

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


print("=== LUCKY7 SIMULATION WITH FREE SPINS ===")
print(f"Spins simulated:            {N_SIMULATIONS}")
print(f"E_line (avg coins/spin):    {E_line:.6f}")
print(f"P_bonus (chance bonus):     {P_bonus:.6%}")
print(f"E_bonus (avg from free):    {E_bonus_sim:.6f}")
print(f"Gross RTP:                  {Gross_RTP:.6f}")
print(f"Net RTP:                    {Net_RTP:.6f}")
