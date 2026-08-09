import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import date
from black_scholes import bs_euro_call, bs_euro_put, delta, gamma, vega, theta, rho
from vol_surface import fit_smile, build_vol_surface
from market_data import get_option_chain, get_expiries, get_rfr, get_div_yield, solve_iv_smile

st.title("Options Pricer & Greeks Visualiser")

symbol = st.sidebar.radio("Underlyings", ["AAPL", "MSFT", "GOOGL", "AMZN"])
r = get_rfr()
q = get_div_yield(symbol)
expiries = get_expiries(symbol)
expiries = [e for e in expiries if (date.fromisoformat(e) - date.today()).days > 7]
expiry = st.sidebar.select_slider("Expiry date", options=expiries, value=expiries[min(4, len(expiries) - 1)])

option_type = st.sidebar.radio("Option type", ["Call", "Put"])
calls, puts, S, T = get_option_chain(symbol, expiry)
clean_iv_data, clean_mid_data = solve_iv_smile(calls, puts, S, T, r, q=q)
if len(clean_iv_data) < 8:
    st.error("Not enough liquid strikes to build a smile for this selection.")
    st.stop()

smile = fit_smile(np.array(list(clean_iv_data.keys())), np.array(list(clean_iv_data.values())), S, T, r, q)
strikes_available = sorted(clean_iv_data.keys())
K = st.sidebar.select_slider("K", options=strikes_available, value=min(strikes_available, key=lambda x: abs(x - S)))
if option_type == "Call":
    index = 0
else:
    index = 1

vol = smile(K)
otm_mid = clean_mid_data[K]
parity = S * np.exp(-q * T) - K * np.exp(-r * T)

if index == 0:
    model_price = bs_euro_call(S, K, T, r, vol, q)
    mkt_price = otm_mid if K > S else otm_mid + parity
else:
    model_price = bs_euro_put(S, K, T, r, vol, q)
    mkt_price = otm_mid if K < S else otm_mid - parity
diff = model_price - mkt_price
c1, c2 = st.columns(2)
c1.metric("Market price" , f"${mkt_price:.2f}")
c2.metric("Model price", f"${model_price:.2f}", delta=f"{diff:+.2f}", delta_color="off")

S_range = np.linspace(0.5 * S, 1.5 * S, 200)
if index == 0:
    price_vals = bs_euro_call(S_range, K, T, r, vol, q)
    payoff_vals = np.maximum(S_range - K, 0)
else:
    price_vals = bs_euro_put(S_range, K, T, r, vol, q)
    payoff_vals = np.maximum(K - S_range, 0)
delta_vals = delta(S_range, K, T, r, vol, q)[index]
gamma_vals = gamma(S_range, K, T, r, vol, q)
vega_vals = vega(S_range, K, T, r, vol, q)
theta_vals = theta(S_range, K, T, r, vol, q)[index]
rho_vals = rho(S_range, K, T, r, vol, q)[index]

fig = plt.figure(figsize=(14, 10), constrained_layout=True)
gs = GridSpec(3, 4, figure=fig)

def add_panel(gs_slice, data, title):
    ax = fig.add_subplot(gs_slice)
    ax.plot(S_range, data)
    ax.set_title(title)
    ax.axvline(K, linestyle='--', color='gray', alpha=0.6, label=f"K = {K:.2f}")
    ax.axvline(S, linestyle='-', color='tab:orange', alpha=0.6, label=f"Spot = {S:.2f}")
    return ax

ax_price = add_panel(gs[0:2, 1:3], price_vals, "Price")
ax_delta = add_panel(gs[0, 3], delta_vals, "Delta")
delta_spot = delta(S, K, T, r, vol, q)[index]
ax_gamma = add_panel(gs[1, 3], gamma_vals, "Gamma")
gamma_spot = gamma(S, K, T, r, vol, q)
ax_theta = add_panel(gs[2, 0], theta_vals, "Theta")
theta_spot = theta(S, K, T, r, vol, q)[index]
ax_vega = add_panel(gs[2, 1], vega_vals, "Vega")
vega_spot = vega(S, K, T, r, vol, q)
ax_rho = add_panel(gs[2, 2], rho_vals, "Rho")
rho_spot = rho(S, K, T, r, vol, q)[index]
ax_payoff = add_panel(gs[2, 3], payoff_vals, "Payoff")

ax_key = fig.add_subplot(gs[0:2, 0])
ax_key.axis('off')
ax_key.text(0.05, 0.96, f"Spot = {S:.2f}", fontsize=14, fontweight='bold', color='tab:orange', transform=ax_key.transAxes)
ax_key.text(0.05, 0.91, f"Strike = {K:.2f}", fontsize=14, fontweight='bold', color='gray', transform=ax_key.transAxes)

ax_key.text(0.05, 0.79, "Greeks at spot price:", fontsize=18, fontweight='bold', transform=ax_key.transAxes)

ax_key.text(0.05, 0.70, "Delta  (∂V/∂S)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.65, f"Delta = {delta_spot:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.56, "Gamma  (∂²V/∂S²)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.51, f"Gamma = {gamma_spot:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.42, "Theta  (-∂V/∂T)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.37, f"Theta = {theta_spot:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.28, "Vega  (∂V/∂σ)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.23, f"Vega = {vega_spot:.4f}", fontsize=13, transform=ax_key.transAxes)

ax_key.text(0.05, 0.14, "Rho  (∂V/∂r)", fontsize=15, fontweight='bold', transform=ax_key.transAxes)
ax_key.text(0.05, 0.09, f"Rho = {rho_spot:.4f}", fontsize=13, transform=ax_key.transAxes)

st.pyplot(fig)

st.subheader(f"Volatility Smile — {symbol} {expiry}")

smile_strikes = np.array(list(clean_iv_data.keys()))
smile_ivs = np.array(list(clean_iv_data.values()))

K_dense = np.linspace(smile_strikes.min(), smile_strikes.max(), 200)
iv_dense = smile(K_dense)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(K_dense, iv_dense)
ax2.scatter(smile_strikes, smile_ivs, color='red', zorder=5)
ax2.set_xlabel("Strike")
ax2.set_ylabel("Implied Vol")
ax2.set_title(f"{symbol} Vol Smile — {expiry}")

st.pyplot(fig2)

st.subheader(f"Volatility Surface — {symbol}")

surface_df = build_vol_surface(symbol, r, q=q)

fig3 = plt.figure(figsize=(10, 8))
ax3 = fig3.add_subplot(projection='3d')
ax3.plot_trisurf(surface_df['K'], surface_df['T'], surface_df['IV'], cmap='viridis')
ax3.set_xlabel("Strike")
ax3.set_ylabel("T")
ax3.set_zlabel("Implied Vol")

st.pyplot(fig3)