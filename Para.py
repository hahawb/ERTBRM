import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Set font to Times New Roman
plt.rcParams['font.family'] = 'Times New Roman'

# Define parameters for Credit Levels A
params_A = {
    "H": {"λ": 0.99, "τ": 0.000001, "α": 0.7, "γ": 0.3, "δ": 0.2, "ε": 0.},
    "M": {"λ": 0.95, "τ": -0.000001, "α": 0.6, "γ": 0.2, "δ": 0.1, "ε": 0.15},
    "L": {"λ": 0.88, "τ": -0.00001, "α": 0.35, "γ": 0.15, "δ": 0.1, "ε": 0.1}
}

# Define parameters for Credit Levels B
params_B = {
    "H": {"λ": 1, "τ": 0.000001, "α": 0.7, "γ": 0.3, "δ": 0.2, "ε": 0.2},
    "M": {"λ": 0.96, "τ": -0.000001, "α": 0.6, "γ": 0.2, "δ": 0.1, "ε": 0.15},
    "L": {"λ": 0.89, "τ": -0.00001, "α": 0.35, "γ": 0.15, "δ": 0.1, "ε": 0.1}
}

# Define parameters for Credit Levels C
params_C = {
    "H": {"λ": 0.98, "τ": 0.000001, "α": 0.7, "γ": 0.3, "δ": 0.2, "ε": 0.2},
    "M": {"λ": 0.94, "τ": -0.000001, "α": 0.6, "γ": 0.2, "δ": 0.1, "ε": 0.15},
    "L": {"λ": 0.87, "τ": -0.00001, "α": 0.35, "γ": 0.15, "δ": 0.1, "ε": 0.1}
}

# Define ranges for Credit Levels
ranges = {"H": [8, 11], "M": [4, 8], "L": [0, 4]}

# Number of transactions
transaction_count = 200

# Initial credit levels and values
init_levels = ["L"]
init_RPs = [1]

plt.figure(figsize=(12, 8))

# Simulate for parameters A
for level_0, RP_0 in zip(init_levels, init_RPs):
    RP_values = [RP_0]
    level_values = [level_0]

    for transaction in range(1, transaction_count + 1):
        previous_level = level_values[-1]
        previous_RP = RP_values[-1]
        params_for_level = params_A[previous_level]

        λ = params_for_level["λ"]
        τ = params_for_level["τ"]
        α = params_for_level["α"]
        γ = params_for_level["γ"]
        δ = params_for_level["δ"]
        ε = params_for_level["ε"]

        DQ = np.random.randint(4, 8)
        OT = np.random.randint(4, 8)
        DS = np.random.randint(4, 8)
        DI = np.random.randint(4, 8)

        RP = λ * previous_RP * np.exp(τ * transaction) + (1 - λ) * (
                α * DQ + γ * OT + δ * DS + ε * DI)

        if RP > 10:
            RP = 10

        current_level = None
        for level, range_values in ranges.items():
            if range_values[0] <= RP < range_values[1]:
                current_level = level
                break

        RP_values.append(RP)
        level_values.append(current_level)

    window_size = 15
    mean_series = pd.Series(RP_values).rolling(window=window_size).mean()

    plt.plot(range(transaction_count + 1), RP_values, label=f"$λ_A$_${level_0}$_$RepV$",marker='^',markevery=0.2,
        markersize=12,linewidth=3)

# Simulate for parameters B
for level_0, RP_0 in zip(init_levels, init_RPs):
    RP_values = [RP_0]
    level_values = [level_0]

    for transaction in range(1, transaction_count + 1):
        previous_level = level_values[-1]
        previous_RP = RP_values[-1]
        params_for_level = params_B[previous_level]

        λ = params_for_level["λ"]
        τ = params_for_level["τ"]
        α = params_for_level["α"]
        γ = params_for_level["γ"]
        δ = params_for_level["δ"]
        ε = params_for_level["ε"]

        DQ = np.random.randint(4, 8)
        OT = np.random.randint(4, 8)
        DS = np.random.randint(4, 8)
        DI = np.random.randint(4, 8)

        RP = λ * previous_RP * np.exp(τ * transaction) + (1 - λ) * (
                α * DQ + γ * OT + δ * DS + ε * DI)

        if RP > 10:
            RP = 10

        current_level = None
        for level, range_values in ranges.items():
            if range_values[0] <= RP < range_values[1]:
                current_level = level
                break

        RP_values.append(RP)
        level_values.append(current_level)

    window_size = 15
    mean_series = pd.Series(RP_values).rolling(window=window_size).mean()

    plt.plot(range(transaction_count + 1), RP_values, label=f"$λ_B$_${level_0}$_$RepV$",marker='*',markevery=0.2,
        markersize=12,linewidth=3)

# Simulate for parameters C
for level_0, RP_0 in zip(init_levels, init_RPs):
    RP_values = [RP_0]
    level_values = [level_0]

    for transaction in range(1, transaction_count + 1):
        previous_level = level_values[-1]
        previous_RP = RP_values[-1]
        params_for_level = params_C[previous_level]

        λ = params_for_level["λ"]
        τ = params_for_level["τ"]
        α = params_for_level["α"]
        γ = params_for_level["γ"]
        δ = params_for_level["δ"]
        ε = params_for_level["ε"]

        DQ = np.random.randint(4, 8)
        OT = np.random.randint(4, 8)
        DS = np.random.randint(4, 8)
        DI = np.random.randint(4, 8)

        RP = λ * previous_RP * np.exp(τ * transaction) + (1 - λ) * (
                α * DQ + γ * OT + δ * DS + ε * DI)

        if RP > 10:
            RP = 10

        current_level = None
        for level, range_values in ranges.items():
            if range_values[0] <= RP < range_values[1]:
                current_level = level
                break

        RP_values.append(RP)
        level_values.append(current_level)

    window_size = 15
    mean_series = pd.Series(RP_values).rolling(window=window_size).mean()

    plt.plot(range(transaction_count + 1), RP_values , label=f"$λ_C$_${level_0}$_$RepV$", linewidth=3,marker='o',markevery=0.2,
        markersize=12)

plt.xticks(fontsize=23)
plt.yticks(fontsize=23)
plt.xlabel("Share Count", fontsize=25)
plt.ylabel("Reputation Value", fontsize=25)
plt.xlim(left=0)
plt.ylim(bottom=0,top=10)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.legend(loc='lower right', fontsize=23)
plt.grid()
plt.show()
