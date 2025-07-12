import pandas as pd
import random
import math

# === Configuration 
REELS_CSV = "reels.csv"
N_TEST_SPINS = 1_000_000 # number of spins 
SEED = 123

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
    reel = [s for s in reel if s] # Remove any empty strings
    reel_lists[i] = reel

# === Calculate individual reel probabilities ===
# p_i: Probability of a "BONUS" symbol appearing on any single position on Reel i
# P_bonus_in_view_i: Probability of at least one "BONUS" symbol in the 3-symbol view of Reel i
p = {}
P_bonus_in_view = {} # Renamed 'b' to be more descriptive

for i in range(1, 6):
    symbols = reel_lists[i]
    total_symbols = len(symbols)
    bonus_count = symbols.count("BONUS")

    p_i = bonus_count / total_symbols

    # --- ACCURATE CALCULATION FOR P_bonus_in_view_i ---
    count_windows_with_no_bonus = 0
    for j in range(total_symbols):
        # Creating the 3-symbol window starting at position j
        three_symbol_view = [
            symbols[j % total_symbols],
            symbols[(j + 1) % total_symbols],
            symbols[(j + 2) % total_symbols]
        ]
        if "BONUS" not in three_symbol_view:
            count_windows_with_no_bonus += 1

    P_bonus_in_view_i = 1 - (count_windows_with_no_bonus / total_symbols)
    #     --- END OF ACCURATE CALCULATION FOR P_bonus_in_view_i ---

    p[i] = p_i
    P_bonus_in_view[i] = P_bonus_in_view_i

print("=== Individual Reel Probabilities ===")
for i in range(1, 6):
    print(f"Reel {i}: length={len(reel_lists[i])}, bonus_count={reel_lists[i].count('BONUS')}, "
          f"p_i (single symbol) = {p[i]:.6f}, "
          f"P_bonus_in_view_i (at least one in 3-view) = {P_bonus_in_view[i]:.6f}")
print("-" * 40)

# ==============================================================================
# SCENARIO 2: "Reels with Bonus" - At least one BONUS symbol appears in the 3-symbol view
# on a specific number of reels (e.g., 5 reels)

BONUS_REEL_THRESHOLD = 5 # Number of reels that must show at least one BONUS symbol

P_bonus_theory = 1
for i in range(1, 6):
    P_bonus_theory *= P_bonus_in_view[i]

print(f"\n=== Scenario 2: Bonus if {BONUS_REEL_THRESHOLD} Reels show at least one BONUS symbol ===")
print(f"P_bonus_theory = {P_bonus_theory:.8f}\n")

count_reels_with_bonus_met_condition = 0
for _ in range(N_TEST_SPINS):
    reels_showing_bonus = 0
    for i in range(1, 6):
        reel = reel_lists[i]
        pos = random.randint(0, len(reel) - 1)
        # Get the 3-symbol view for the current reel
        three_symbol_view = [
            reel[pos % len(reel)],
            reel[(pos + 1) % len(reel)],
            reel[(pos + 2) % len(reel)]
        ]
        if "BONUS" in three_symbol_view:
            reels_showing_bonus += 1

    if reels_showing_bonus >= BONUS_REEL_THRESHOLD:
        count_reels_with_bonus_met_condition += 1

P_bonus_emp = count_reels_with_bonus_met_condition / N_TEST_SPINS
diff_P = P_bonus_emp - P_bonus_theory
print(f"P_bonus_emp = {P_bonus_emp:.8f}, diff = {diff_P:+.8f}")
print("-" * 40)