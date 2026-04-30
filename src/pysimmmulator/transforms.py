import pandas as pd
import numpy as np

def geometric_adstock(vector: pd.Series, lambda_: float) -> pd.Series:
  """Applies geometric decay adstock to a vector."""
  decayed_vector = [vector.values[0]]
  for i, val in enumerate(vector.values[1:]):
    decayed_vector.append(val + lambda_ * decayed_vector[i])
  return pd.Series(decayed_vector, index=vector.index)

def weibull_adstock(vector: pd.Series, shape: float, scale: float, adstock_type: str = 'pdf') -> pd.Series:
  """Applies Weibull adstock to a vector.

  Args:
    vector (pd.Series): media vector
    shape (float): shape parameter (k)
    scale (float): scale parameter (theta)
    adstock_type (str): 'pdf' or 'cdf'
  """
  n = len(vector)
  x = np.arange(n)
  if adstock_type == 'pdf':
    # Weibull PDF: (k/theta) * (x/theta)**(k-1) * exp(-(x/theta)**k)
    # We normalize it so it can be used as a weighting vector
    weights = (shape / scale) * (x / scale)**(shape - 1) * np.exp(-(x / scale)**shape)
  else:
    # Weibull CDF: 1 - exp(-(x/theta)**k)
    # For adstock, we typically use the survival function (1-CDF) or its increments
    weights = np.exp(-(x / scale)**shape)

  weights = weights / weights.sum() if weights.sum() > 0 else weights

  # Convolution for adstock
  # We use 'full' and then slice to maintain length
  adstocked = np.convolve(vector.values, weights)[:n]
  return pd.Series(adstocked, index=vector.index)

def scurve_saturation(vector: pd.Series, alpha: float, gamma: float) -> pd.Series:
  """Applies S-curve saturation (Logistic) to a vector."""
  # gamma is treated as a quantile to find the inflection point
  gamma_trans = np.quantile(np.linspace(min(vector), max(vector), num=100), gamma)
  denom = vector**alpha + gamma_trans**alpha
  return (vector**alpha / denom) * vector if np.any(denom != 0) else vector

def hill_saturation(vector: pd.Series, alpha: float, gamma: float) -> pd.Series:
  """Applies Hill saturation to a vector.

  Args:
    vector (pd.Series): adstocked media vector
    alpha (float): shape parameter (slope)
    gamma (float): scale parameter (half-saturation point)
  """
  # Hill function: x**alpha / (x**alpha + gamma**alpha)
  # Often gamma is specified as a value in the same scale as x
  # Here we'll treat gamma as a quantile similar to scurve for consistency in config if preferred,
  # but the classic Hill uses an absolute value.
  # Let's use absolute value for Hill to differentiate it.
  inflection = gamma * np.max(vector) if gamma <= 1.0 else gamma
  denom = vector**alpha + inflection**alpha
  return (vector**alpha / denom) * vector if np.any(denom != 0) else vector
