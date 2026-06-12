#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator
from scipy.stats import linregress

# --------------------------------
# Global plot style (publication style)
# --------------------------------
plt.rcParams.update({
    "font.size": 8,
    "axes.labelsize": 10,
    "axes.titlesize": 12,
    "legend.fontsize": 8,
    "figure.figsize": (6.5, 4),
    "lines.linewidth": 2,
})

# -----------------------------
# 1. Read data
# -----------------------------
data = pd.read_csv("combined_poissons_data.csv")

# Force numeric conversion in case CSV has text or blanks
data["par"] = pd.to_numeric(data["par"], errors="coerce")
data["perp"] = pd.to_numeric(data["perp"], errors="coerce")

# Drop rows with missing or invalid values
data = data.dropna(subset=["par", "perp"])

# Sort by parallel strain so lines plot cleanly
data = data.sort_values("par")

strain = data["par"].to_numpy()
stress = data["perp"].to_numpy()

# Plot title and axis labels
plot_title = "Lateral-Linear Strain Curve with Linear Fits"
x_label = "Linear Strain"
y_label = "Lateral Strain"

# Output image file name
output_figure = "poissons_ratio_analysis.png"

# Fit range (set to None to use all data)
fit_start = None
fit_end = None

# Decimal formatting for printed values
print_decimals = 6

# -----------------------------
# OPTIONAL: Literature values (EDIT THESE)
# -----------------------------
#E_lit = 103       # GPa
nu_lit = 0.19      # Poisson's ratio using average of sources

# -----------------------------
# 2. Select Fit Region
# -----------------------------
if fit_start is None:
    fit_start = 0
if fit_end is None:
    fit_end = len(strain)

strain_fit = strain[fit_start:fit_end]
stress_fit = stress[fit_start:fit_end]

# Safety checks
if len(strain_fit) < 2:
    raise ValueError("Need at least 2 data points for a linear fit.")

if np.all(strain_fit == strain_fit[0]):
    raise ValueError("All strain values in the fit region are identical, so a linear fit cannot be computed.")

# -----------------------------
# 3. Linear Fits (combined, tension, compression)
# -----------------------------

# Masks
mask_all = strain_fit != 0
mask_tens = strain_fit >= 0
mask_comp = strain_fit <= 0

# Separate tension and compression datasets
strain_tens = strain_fit[mask_tens]
stress_tens = stress_fit[mask_tens]
strain_comp = strain_fit[mask_comp]
stress_comp = stress_fit[mask_comp]

# ---- Combined fit ----
fit_all = linregress(strain_fit[mask_all], stress_fit[mask_all])
m_all = fit_all.slope
b_all = fit_all.intercept
stderr_all = fit_all.stderr

# ---- Tension fit ----
fit_tens = linregress(strain_fit[mask_tens], stress_fit[mask_tens])
m_tens = fit_tens.slope
b_tens = fit_tens.intercept
stderr_tens = fit_tens.stderr

# ---- Compression fit ----
fit_comp = linregress(strain_fit[mask_comp], stress_fit[mask_comp])
m_comp = fit_comp.slope
b_comp = fit_comp.intercept
stderr_comp = fit_comp.stderr

# Convert slope → Poisson’s ratio
nu_all = -m_all
nu_tens = -m_tens
nu_comp = -m_comp

# -----------------------------
# 4. Additional Statistics
# -----------------------------

# Predictions
pred_all = m_all * strain_fit + b_all

# RMSE
rmse = np.sqrt(np.mean((stress_fit - pred_all)**2))

# Percent difference (tension vs compression)
percent_diff_nu = abs(nu_tens - nu_comp) / ((nu_tens + nu_comp)/2) * 100

# Percent error vs literature (if provided)
percent_error_nu = None
if nu_lit is not None:
    percent_error_nu = abs(nu_all - nu_lit) / nu_lit * 100

# -----------------------------
# 5. Compute R^2 values
# -----------------------------
# Combined
stress_pred_all = m_all * strain_fit + b_all
ss_res_all = np.sum((stress_fit - stress_pred_all) ** 2)
ss_tot_all = np.sum((stress_fit - np.mean(stress_fit)) ** 2)
r_squared_all = 1.0 if ss_tot_all == 0 else 1 - (ss_res_all / ss_tot_all)

# Compression
if m_comp is not None:
    stress_pred_comp = m_comp * strain_comp + b_comp
    ss_res_comp = np.sum((stress_comp - stress_pred_comp) ** 2)
    ss_tot_comp = np.sum((stress_comp - np.mean(stress_comp)) ** 2)
    r2_comp = 1.0 if ss_tot_comp == 0 else 1 - (ss_res_comp / ss_tot_comp)

# Tension
if m_tens is not None:
    stress_pred_tens = m_tens * strain_tens + b_tens
    ss_res_tens = np.sum((stress_tens - stress_pred_tens) ** 2)
    ss_tot_tens = np.sum((stress_tens - np.mean(stress_tens)) ** 2)
    r2_tens = 1.0 if ss_tot_tens == 0 else 1 - (ss_res_tens / ss_tot_tens)

# -----------------------------
# 5. Print Results
# -----------------------------
print("=" * 60)
print("POISSON'S RATIO ANALYSIS")
print("=" * 60)

print("COMBINED FIT")
print(f"  ν (all data)           = {nu_all:.{print_decimals}f}") # Best Poisson's ratio
print(f"  Std error              = {stderr_all:.{print_decimals}f}") # Uncertainty
print(f"  Intercept              = {b_all:.{print_decimals}f}") # Systematic bias
print(f"  R^2                    = {fit_all.rvalue**2:.{print_decimals}f}") # How linear is the data
print(f"  RMSE                   = {rmse:.{print_decimals}f}") # Fit quality
print()

print("TENSION FIT")
print(f"  ν (tension)            = {nu_tens:.{print_decimals}f}") # Poisson's ratio - tension
print(f"  Std error              = {stderr_tens:.{print_decimals}f}") # Uncertainty
print()

print("COMPRESSION FIT")
print(f"  ν (compression)        = {nu_comp:.{print_decimals}f}") # Poisson's ratio - compression
print(f"  Std error              = {stderr_comp:.{print_decimals}f}") # Uncertainty
#print()

#print("COMPARISON")
#print(f"  % difference (t vs c)  = {percent_diff_nu:.{print_decimals}f}") # Symmetry check

#if percent_error_nu is not None:
#    print(f"  % error vs literature  = {percent_error_nu:.{print_decimals}f}") # Accuracy

print("=" * 60)

# -----------------------------
# 7. Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 4))

# Raw data
ax.plot(strain, stress, 'o', markersize=6, label="Data")

# Combined fit
x_all = np.linspace(min(strain_fit), max(strain_fit), 200)
ax.plot(x_all, m_all * x_all + b_all,
        label=f"Combined: ν={nu_all:.3f}")

# Tension fit
x_tens = np.linspace(min(strain_tens), max(strain_tens), 100)
ax.plot(x_tens, m_tens * x_tens + b_tens,
        linestyle='--',
        label=f"Tension: ν={nu_tens:.3f}")

# Compression fit
x_comp = np.linspace(min(strain_comp), max(strain_comp), 100)
ax.plot(x_comp, m_comp * x_comp + b_comp,
        linestyle='-.',
        label=f"Compression: ν={nu_comp:.3f}")

# Labels and title
ax.set_title(plot_title, fontsize=12)
ax.set_xlabel(x_label, fontsize=10)
ax.set_ylabel(y_label, fontsize=10)

# Publication-style axis formatting
ax.tick_params(axis='both', which='major', labelsize=11)

# Set tick spacing
ax.xaxis.set_major_locator(MultipleLocator(0.01))   # X ticks every 0.01
ax.yaxis.set_major_locator(MultipleLocator(0.005))      # Y ticks every 0.005

# Number formatting
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

# Optional scientific notation instead:
# formatter = ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))
# ax.xaxis.set_major_formatter(formatter)
# ax.yaxis.set_major_formatter(formatter)

# Optional reference lines at zero
ax.axhline(0, linewidth=0.8, linestyle=':', alpha=0.7)
ax.axvline(0, linewidth=0.8, linestyle=':', alpha=0.7)

ax.legend(fontsize=9)
ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(output_figure, dpi=300)
plt.show()

print(f"\nPlot saved as: {output_figure}")


# In[ ]:




