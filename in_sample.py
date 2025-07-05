import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import yfinance as yf

from trading_development_stages import optimize_donchian
from permutation import get_permutation

df = yf.download("BTC-USD", interval="1h", start="2024-07-01", end="2025-07-01")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0).str.lower()
else:
    df.columns = df.columns.str.lower()

df.dropna(inplace=True)
df.index = df.index.tz_localize(None)

df = df[(df.index >= "2024-07-01") & (df.index < "2025-07-01")]

train_df = df.copy()


assert not train_df.empty, "Training DataFrame is empty. Adjust your date range."

best_lookback, best_real_pf = optimize_donchian(train_df)
print("In-sample PF:", best_real_pf, "Best Lookback:", best_lookback)

n_permutations = 1000
perm_better_count = 1
permuted_pfs = []

print("Running In-Sample MCPT...")
for perm_i in tqdm(range(1, n_permutations)):
    train_perm = get_permutation(train_df)
    _, best_perm_pf = optimize_donchian(train_perm)

    if best_perm_pf >= best_real_pf:
        perm_better_count += 1

    permuted_pfs.append(best_perm_pf)

insample_mcpt_pval = perm_better_count / n_permutations
print(f"In-sample MCPT P-Value: {insample_mcpt_pval:.4f}")

# Plot histogram
plt.style.use('dark_background')
pd.Series(permuted_pfs).hist(color='blue', label='Permuted PFs')
plt.axvline(best_real_pf, color='red', label='Real PF', linewidth=2)
plt.xlabel("Profit Factor")
plt.title(f"In-sample MCPT\nP-Value: {insample_mcpt_pval:.4f}")
plt.grid(False)
plt.legend()
plt.show()
