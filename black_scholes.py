import numpy as np
import scipy.stats as sp

def _d1_d2(S, K, T, r, vol):
    d1 = (np.log(S / K) + (r + (vol ** 2) / 2) * T) / (vol * np.sqrt(T))
    d2 = d1 - (vol * np.sqrt(T))
    return d1, d2

def bs_euro_call(S, K, T, r, vol):
    d1, d2 = _d1_d2(S, K, T, r, vol)
    C = S * sp.norm.cdf(d1) - np.exp(-r * T) * K * sp.norm.cdf(d2)
    return C

def bs_euro_put(S, K, T, r, vol):
    d1, d2 = _d1_d2(S, K, T, r, vol)
    P = -S * sp.norm.cdf(-d1) + np.exp(-r * T) * K * sp.norm.cdf(-d2)
    return P

def delta(S, K, T, r, vol):
    d1 = _d1_d2(S, K, T, r, vol)[0]
    delta_call = sp.norm.cdf(d1)
    delta_put = delta_call - 1
    return delta_call, delta_put

def gamma(S, K, T, r, vol):
    d1 = _d1_d2(S, K, T, r, vol)[0]
    gamma = sp.norm.pdf(d1)/(S * vol * np.sqrt(T))
    return gamma

def vega(S, K, T, r, vol):
    d1 = _d1_d2(S, K, T, r, vol)[0]
    vega = S * sp.norm.pdf(d1) * np.sqrt(T)
    return vega

def theta(S, K, T, r, vol):
    d1, d2 = _d1_d2(S, K, T, r, vol)
    theta_call = -(S * sp.norm.pdf(d1) * vol)/(2 * np.sqrt(T)) - r * K * np.exp(-r * T) * sp.norm.cdf(d2)
    theta_put = -(S * sp.norm.pdf(d1) * vol)/(2 * np.sqrt(T)) + r * K * np.exp(-r * T) * sp.norm.cdf(-d2)
    return theta_call, theta_put

def rho(S, K, T, r, vol):
    d2 = _d1_d2(S, K, T, r, vol)[1]
    rho_call = K * T * np.exp(-r * T) * sp.norm.cdf(d2)
    rho_put = -K * T * np.exp(-r * T) * sp.norm.cdf(-d2)
    return rho_call, rho_put

