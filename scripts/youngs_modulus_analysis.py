#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
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
data = pd.read_csv("combined_youngs_data.csv")

# Clean up column names
data.columns = data.columns.str.strip().str.lower()

# Force numeric conversion in case CSV has text or blanks
data["strain"] = pd.to_numeric(data["strain"], errors="coerce")
data["stress"] = pd.to_numeric(data["stress"], errors="coerce")

# Drop rows with missing or invalid values
data = data.dropna(subset=["strain", "stress"])

# Sort by strain for cleaner plotting
data = data.sort_values("strain")

strain = data["strain"].to_numpy()
stress = data["stress"].to_numpy()

# Plot title and axis labels
plot_title = "Stress-Strain Curve with Linear Fits"
x_label = "Strain (%)"
y_label = "Stress (GPa)"

# Output image file name
output_figure = "youngs_modulus_analysis.png"

# Fit range (set to None to use all data)
fit_start = None
fit_end = None

# Decimal formatting for printed values
print_decimals = 6

# -----------------------------
# 2. Literature value (optional)
# -----------------------------
# E_lit = 84.1085 # GPa, based on materials project and quantumatk values
E_lit = 102.285 # GPa, based on lit values

# -----------------------------
# 3. Select Fit Region
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
# 4. Split into combined / tension / compression
# -----------------------------
mask_all = strain_fit != 0
mask_tens = strain_fit >= 0
mask_comp = strain_fit <= 0

strain_all = strain_fit[mask_all]
stress_all = stress_fit[mask_all]

strain_tens = strain_fit[mask_tens]
stress_tens = stress_fit[mask_tens]

strain_comp = strain_fit[mask_comp]
stress_comp = stress_fit[mask_comp]

# -----------------------------
# 5. Linear fits
# Model: stress = E * strain + b
# -----------------------------
fit_all = linregress(strain_all, stress_all)
E_all = fit_all.slope
b_all = fit_all.intercept
stderr_all = fit_all.stderr

fit_tens = linregress(strain_tens, stress_tens)
E_tens = fit_tens.slope
b_tens = fit_tens.intercept
stderr_tens = fit_tens.stderr

fit_comp = linregress(strain_comp, stress_comp)
E_comp = fit_comp.slope
b_comp = fit_comp.intercept
stderr_comp = fit_comp.stderr

# -----------------------------
# 6. Additional statistics
# -----------------------------
pred_all = E_all * strain_all + b_all
rmse_all = np.sqrt(np.mean((stress_all - pred_all) ** 2))

percent_diff_E = abs(E_tens - E_comp) / ((E_tens + E_comp) / 2) * 100

percent_error_E = None
if E_lit is not None:
    percent_error_E = abs(E_all - E_lit) / E_lit * 100

# -----------------------------
# 7. Print results
# -----------------------------
print("=" * 60)
print("YOUNG'S MODULUS ANALYSIS")
print("=" * 60)

print("COMBINED FIT")
print(f"  E (all data)           = {E_all:.{print_decimals}f} GPa") # Best Young's modulus
print(f"  Std error              = {stderr_all:.{print_decimals}f} GPa") # Uncertainty
print(f"  Intercept              = {b_all:.{print_decimals}f} GPa") # Systematic bias
print(f"  R^2                    = {fit_all.rvalue**2:.{print_decimals}f}") # How linear is the data
print(f"  RMSE                   = {rmse_all:.{print_decimals}f} GPa") # Fit quality
print()

print("TENSION FIT")
print(f"  E (tension)            = {E_tens:.{print_decimals}f} GPa") # Young's modulus - tension
print(f"  Std error              = {stderr_tens:.{print_decimals}f} GPa") # Uncertainty
print(f"  Intercept              = {b_tens:.{print_decimals}f} GPa") # Systematic bias
print(f"  R^2                    = {fit_tens.rvalue**2:.{print_decimals}f}") # How linear is the data
print()

print("COMPRESSION FIT")
print(f"  E (compression)        = {E_comp:.{print_decimals}f} GPa") # Young's modulus - compression
print(f"  Std error              = {stderr_comp:.{print_decimals}f} GPa") # Uncertainty
print(f"  Intercept              = {b_comp:.{print_decimals}f} GPa") # Systemic bias
print(f"  R^2                    = {fit_comp.rvalue**2:.{print_decimals}f}") # How linear is the data
#print()

#print("COMPARISON")
#print(f"  % difference (t vs c)  = {percent_diff_E:.{print_decimals}f}")

#if percent_error_E is not None:
#    print(f"  % error vs literature  = {percent_error_E:.{print_decimals}f}")

print("=" * 60)

# -----------------------------
# 8. Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(6, 4))

# Raw data
ax.plot(strain, stress, 'o', markersize=6, label="Data")

# Combined fit line
x_all = np.linspace(np.min(strain_all), np.max(strain_all), 200)
ax.plot(x_all, E_all * x_all + b_all, '-',
        label=f"Combined fit: E = {E_all:.3f} GPa")

# Tension fit line
x_tens = np.linspace(np.min(strain_tens), np.max(strain_tens), 100)
ax.plot(x_tens, E_tens * x_tens + b_tens, '--',
        label=f"Tension fit: E = {E_tens:.3f} GPa")

# Compression fit line
x_comp = np.linspace(np.min(strain_comp), np.max(strain_comp), 100)
ax.plot(x_comp, E_comp * x_comp + b_comp, '-.',
        label=f"Compression fit: E = {E_comp:.3f} GPa")

# Labels and title
ax.set_title(plot_title, fontsize=12)
ax.set_xlabel(x_label, fontsize=10)
ax.set_ylabel(y_label, fontsize=10)

# Axis formatting
ax.tick_params(axis='both', which='major', labelsize=11)
ax.xaxis.set_major_locator(MultipleLocator(0.01))
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

# Reference lines at zero
ax.axhline(0, linewidth=0.8, linestyle=':', alpha=0.7)
ax.axvline(0, linewidth=0.8, linestyle=':', alpha=0.7)

ax.legend(fontsize=9)
ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(output_figure, dpi=300)
plt.show()

print(f"\nPlot saved as: {output_figure}")


# In[ ]:




