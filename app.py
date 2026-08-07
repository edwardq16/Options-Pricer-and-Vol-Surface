import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import date
from black_scholes import bs_euro_call, bs_euro_put, delta, gamma, vega, theta, rho
from vol_surface import fit_smile, build_vol_surface
from market_data import get_option_chain, get_expiries, get_rfr, solve_iv_smile

st.title("Options Pricer & Greeks Visualiser")

symbol = st.sidebar.radio("Underlyings", ["AAPL", "MSFT", "GOOGL", "AMZN"])
r = get_rfr()
expiries = get_expiries(symbol)
expiries = [e for e in expiries if (date.fromisoformat(e) - date.today()).days > 0]
expiry = st.sidebar.select_slider("Expiry date", options=expiries)

option_type = st.sidebar.radio("Option type", ["Call", "Put"])
calls, puts, S, T = get_option_chain(symbol, expiry)
clean_call_data, clean_put_data = solve_iv_smile(calls, puts, S, T, r)

if option_type == "Call":
    if len(clean_call_data) < 2:
        st.error("Not enough liquid strikes to build a call smile for this selection.")
        st.stop()
    else:
        call_smile = fit_smile(np.array(list(clean_call_data.keys())), np.array(list(clean_call_data.values())), S, T)
    K = st.sidebar.slider("K", min(clean_call_data.keys()), max(clean_call_data.keys()), float(S))
    index = 0
else:
    if len(clean_put_data) < 2:
        st.error("Not enough liquid strikes to build a put smile for this selection.")
        st.stop()
    else:
        put_smile = fit_smile(np.array(list(clean_put_data.keys())), np.array(list(clean_put_data.values())), S, T)
    K = st.sidebar.slider("K", min(clean_put_data.keys()), max(clean_put_data.keys()), float(S))
    index = 1

vol = call_smile(K) if option_type == "Call" else put_smile(K)
S_range = np.linspace(0.5 * S, 1.5 * S, 200)
price_vals, delta_vals, gamma_vals, vega_vals, theta_vals, rho_vals, payoff_vals = [], [], [], [], [], [], []

for S in S_range:
    if index == 0:
        price_vals.append(bs_euro_call(S, K, T, r, vol))
        payoff_vals.append(np.maximum(S - K, 0))
    else:
        price_vals.append(bs_euro_put(S, K, T, r, vol))
        payoff_vals.append(np.maximum(K - S, 0))
    delta_vals.append(delta(S, K, T, r, vol)[index])
    gamma_vals.append(gamma(S, K, T, r, vol))
    vega_vals.append(vega(S, K, T, r, vol))
    theta_vals.append(theta(S, K, T, r, vol)[index])
    rho_vals.append(rho(S, K, T, r, vol)[index])

fig = plt.figure(figsize=(14, 10), constrained_layout=True)
gs = GridSpec(3, 4, figure=fig)

def add_panel(gs_slice, data, title):
    ax = fig.add_subplot(gs_slice)
    ax.plot(S_range, data)
    ax.set_title(title)
    ax.axvline(K, linestyle='--', color='gray', alpha=0.6)
    return ax

ax_price = add_panel(gs[0:2, 1:3], price_vals, "Price")
ax_delta = add_panel(gs[0, 3], delta_vals, "Delta")
delta_atm = delta(K, K, T, r, vol)[index]
ax_gamma = add_panel(gs[1, 3], gamma_vals, "Gamma")
gamma_atm = gamma(K, K, T, r, vol)
ax_theta = add_panel(gs[2, 0], theta_vals, "Theta")
theta_atm = theta(K, K, T, r, vol)[index]
ax_vega = add_panel(gs[2, 1], vega_vals, "Vega")
vega_atm = vega(K, K, T, r, vol)
ax_rho = add_panel(gs[2, 2], rho_vals, "Rho")
rho_atm = rho(K, K, T, r, vol)[index]
ax_payoff = add_panel(gs[2, 3], payoff_vals, "Payoff")

ax_key = fig.add_subplot(gs[0:2, 0])
ax_key.axis('off')
ax_key.text(0.05, 0.95, "Greeks at S = K", fontsize=18, fontweight='bold', transform=ax_key.transAxes)

ax_key.text(0.05, 0.80, "Delta  (∂V/∂S)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.75, f"ATM Delta = {delta_atm:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.65, "Gamma  (∂²V/∂S²)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.60, f"ATM Gamma = {gamma_atm:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.50, "Theta  (∂V/∂T)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.45, f"ATM Theta = {theta_atm:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.35, "Vega  (∂V/∂σ)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.30, f"ATM Vega = {vega_atm:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.20, "Rho  (∂V/∂r)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.15, f"ATM Rho = {rho_atm:.4f}", fontsize=13, transform=ax_key.transAxes)

st.pyplot(fig)

st.subheader(f"Volatility Smile — {symbol} {expiry} ({option_type})")

if option_type == "Call":
    smile_strikes = np.array(list(clean_call_data.keys()))
    smile_ivs = np.array(list(clean_call_data.values()))
else:
    smile_strikes = np.array(list(clean_put_data.keys()))
    smile_ivs = np.array(list(clean_put_data.values()))

smile = call_smile if option_type == "Call" else put_smile
K_dense = np.linspace(smile_strikes.min(), smile_strikes.max(), 200)
iv_dense = smile(K_dense)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(K_dense, iv_dense)
ax2.scatter(smile_strikes, smile_ivs, color='red', zorder=5)
ax2.set_xlabel("Strike")
ax2.set_ylabel("Implied Vol")
ax2.set_title(f"{symbol} Vol Smile — {expiry}")

st.pyplot(fig2)

st.subheader(f"Volatility Surface — {symbol} ({option_type})")

surface_df = build_vol_surface(symbol, r, option_type)

fig3 = plt.figure(figsize=(10, 8))
ax3 = fig3.add_subplot(projection='3d')
ax3.plot_trisurf(surface_df['K'], surface_df['T'], surface_df['IV'], cmap='viridis')
ax3.set_xlabel("Strike")
ax3.set_ylabel("T")
ax3.set_zlabel("Implied Vol")

st.pyplot(fig3)