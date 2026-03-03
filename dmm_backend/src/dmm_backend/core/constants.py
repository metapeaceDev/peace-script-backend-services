# core/constants.py

"""
This file centralizes all the game balance and simulation constants.
Adjusting these values will directly impact the character's reaction and progression.
"""

# --- Reaction Calculation Constants ---

# The weight of ambient stress on the initial stimulus intensity.
# Higher value means environment has more impact.
AMBIENT_STRESS_MULTIPLIER = 0.1

# The weight of the character's latent tendency (Anusaya) level in the conflict.
ANUSAYA_LEVEL_WEIGHT = 0.6

# The weight of the external stimulus intensity in the conflict.
STIMULUS_INTENSITY_WEIGHT = 0.4

# Divisor for calculating the chance of Sati (mindfulness) intervention.
# A lower number makes Sati intervention MORE likely.
SATI_CHANCE_DIVISOR = 15.0

# Divisor for calculating the chance of Paññā (wisdom) override after Sati has intervened.
# A lower number makes Paññā override MORE likely.
PANNA_CHANCE_DIVISOR = 20.0

# The percentage by which Paññā reduces the final Kilesa (defilement) force.
# 0.2 means an 80% reduction.
PANNA_KILESA_REDUCTION_FACTOR = 0.2

# The weight of Khanti (patience) in the Pāramī (perfection) force calculation.
PARAMI_KHANTI_WEIGHT = 1.0

# The weight of Upekkhā (equanimity) in the Pāramī force calculation.
PARAMI_UPEKKHA_WEIGHT = 0.5


# --- Consequence Constants ---

# The amount of experience points gained for a wholesome action.
WHOLESOME_REACTION_EXP_GAIN = 15

# The amount the unwholesome tendency level increases after an unwholesome action.
UNWHOLESOME_REACTION_LEVEL_INCREASE = 0.1
