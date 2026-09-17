import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency

def run_chi_square(feature_name, script_count, script_total, ice_count, ice_total):
    """
    Calculate the significance of feature differences between the script and the corpus.
    """
    table = [
        [script_count, script_total - script_count],
        [ice_count, ice_total - ice_count]
    ]
    # Perform a chi-square test (using Yates continuity correction).
    chi2, p, dof, expected = chi2_contingency(table, correction=True)
    
    print(f"--- {feature_name} Significance test ---")
    print(f"Chi-sqaure (χ²): {chi2:.4f}, P-value: {p:.4f}")
    print(f"Conclusion: {'Significantly different ✅' if p < 0.05 else 'not significantly different ❌'}")
    return chi2, p

if __name__ == "__main__":
    # --- Step 1: set Token number ---
    script_tokens = 72530  # provided by AntConc
    ice_tokens = 1000000   # ICE-Ireland reference corpus (1M)
    print(f"Set the total number of tokens in the script: {script_tokens}")

    # --- Step 2: Define feature frequencies and normalization calculation ---
    # Raw Counts
    features = ["Never_Negator", "Conditional_Was", "2nd_Person_Pronouns", "Them+Plural", "There's+Plural"]
    script_counts = [13, 8, 20, 6, 12]  # feature frequency in script
    ice_counts = [113, 125, 183, 30, 33]   # feature frequency in ICE

    # Frequency Normalization (per 1,000,000 tokens)
    # formula: (raw counts / total tokens) * 1,000,000
    script_freq = [(c / script_tokens) * 1000000 for c in script_counts]
    ice_freq = [(c / ice_tokens) * 1000000 for c in ice_counts]

    # --- Step 3: 运行统计检验 ---
    print("\n" + "="*30)
    for i, name in enumerate(features):
        run_chi_square(name, script_counts[i], script_tokens, ice_counts[i], ice_tokens)
    print("="*30 + "\n")

    # --- Step 4: 绘图并保存 ---
    x = np.arange(len(features))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))

    rects1 = ax.bar(x - width/2, script_freq, width, label='Derry Girls (Script)', color='#2c3e50')
    rects2 = ax.bar(x + width/2, ice_freq, width, label='ICE-Ireland (Reference)', color='#bdc3c7')

    ax.set_ylabel('Frequency (per 1,000,000 tokens)')
    ax.set_title('Dialectal Feature Distribution: Script vs. Reference')
    ax.set_xticks(x)
    ax.set_xticklabels(features)
    ax.legend()

    # Annotate O/E Ratio (observed frequency / expected frequency)
    # visually display the density of this feature in the script relative to the benchmark corpus.
    for i in range(len(features)):
        oe_ratio = script_freq[i] / ice_freq[i] if ice_freq[i] > 0 else 0
        ax.text(i - width/2, script_freq[i] + 0.1, f'O/E: {oe_ratio:.2f}', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    
    # Save as PNG file
    output_filename = "dialect_analysis_final.png"
    plt.savefig(output_filename, dpi=300)
    print(f"analysis results saved as: {output_filename}")