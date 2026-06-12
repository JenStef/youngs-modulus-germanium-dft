#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter

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
data = pd.read_csv("poissons_compression_data.csv")

# Force numeric conversion in case CSV has text or blanks
data["par"] = pd.to_numeric(data["par"], errors="coerce")
data["perp"] = pd.to_numeric(data["perp"], errors="coerce")

# Drop rows with missing or invalid values
data = data.dropna(subset=["par", "perp"])

strain = data["par"].to_numpy()
stress = data["perp"].to_numpy()

# Plot title and axis labels
plot_title = "Lateral-Linear Strain Curve with Linear Fit - Compression"
x_label = "Linear Strain"
y_label = "Lateral Strain"

# Output image file name
output_figure = "poissons_ratio_compression_fit.png"

# Fit range (set to None to use all data)
fit_start = None
fit_end = None

# Decimal formatting for printed values
print_decimals = 6

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
# 3. Linear Fit
# Model: perp_strain = -K * par_strain + b
# -----------------------------
coeffs = np.polyfit(strain_fit, stress_fit, 1)
m = coeffs[0]          # slope = Poisson's ratio
b = coeffs[1]          # intercept

stress_fit_line = m * strain_fit + b

# -----------------------------
# 4. Compute R^2
# -----------------------------
stress_pred = m * strain_fit + b
ss_res = np.sum((stress_fit - stress_pred) ** 2)
ss_tot = np.sum((stress_fit - np.mean(stress_fit)) ** 2)

if ss_tot == 0:
    r_squared = 1.0
else:
    r_squared = 1 - (ss_res / ss_tot)

# -----------------------------
# 5. Print Results
# -----------------------------
print("=" * 60)
print("LINEAR FIT RESULTS FOR POISSON'S RATIO - COMPRESSION")
print("=" * 60)
print("Fit equation:")
print("    lateral_strain = -K * linear_strain + b")
print()
print(f"Slope (Poisson's ratio, -K) = {m:.{print_decimals}f}")
print(f"Intercept (b)              = {b:.{print_decimals}f}")
print(f"R^2                        = {r_squared:.{print_decimals}f}")
#print()
#print("Fit range used:")
#print(f"    Start index = {fit_start}")
#print(f"    End index   = {fit_end}")
print("=" * 60)

# -----------------------------
# 6. Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 4))

# Raw data
ax.plot(strain, stress, 'o', markersize=6, label="Data")

# Fit line over selected region
ax.plot(strain_fit, stress_fit_line, '-', linewidth=2,
        label=f"Linear fit: -K = {m:.3f}")

# Labels and title
ax.set_title(plot_title, fontsize=12)
ax.set_xlabel(x_label, fontsize=10)
ax.set_ylabel(y_label, fontsize=10)

# Publication-style axis formatting
ax.tick_params(axis='both', which='major', labelsize=11)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

# Optional scientific notation instead:
# formatter = ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))
# ax.xaxis.set_major_formatter(formatter)
# ax.yaxis.set_major_formatter(formatter)

ax.legend(fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(output_figure, dpi=300)
plt.show()

print(f"\nPlot saved as: {output_figure}")


# In[ ]:




