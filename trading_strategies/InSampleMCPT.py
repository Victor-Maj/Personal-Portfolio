import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from permutation_utils import get_permutation

class InSampleMCPT: 
    def __init__(self, df: pd.DataFrame, n_permutations = 1000):
        self.n_permutations = n_permutations
        self.train_df = df.copy()
        self.best_lookback = None
        self.best_real_pf = None
        self.permuted_pfs = []
        self.insample_mcpt_pval = None


    def run_InSampleMCPT(self, strategy_function):
        print("Optimizing on original data...")
        self.best_lookback, self.best_real_pf = strategy_function(self.train_df)
        print(f"In-sample PF: {self.best_real_pf:.4f}, Best Lookback: {self.best_lookback}")

        perm_better_count = 1

        print("Running In-Sample MCPT...")
        for perm_i in tqdm(range(self.n_permutations)):
            train_perm = get_permutation(self.train_df)
            _, best_perm_pf = strategy_function(train_perm)

            if best_perm_pf >= self.best_real_pf:
                perm_better_count += 1

            self.permuted_pfs.append(best_perm_pf)

        self.insample_mcpt_pval = perm_better_count / self.n_permutations
        print(f"In-sample MCPT P-Value: {self.insample_mcpt_pval:.4f}")

        return self.insample_mcpt_pval



    def plot_InSampleMCPT(self):
        if self.insample_mcpt_pval is None or self.best_real_pf is None:
            raise RuntimeError("Run `run_InSampleMCPT()` before plotting.")

        plt.style.use('dark_background')
        pd.Series(self.permuted_pfs).hist(color='blue', label='Permuted PFs')
        plt.axvline(self.best_real_pf, color='red', label='Real PF', linewidth=2)
        plt.xlabel("Profit Factor")
        plt.title(f"In-sample MCPT\nP-Value: {self.insample_mcpt_pval:.4f}")
        plt.grid(False)
        plt.legend()
        plt.show()
        

