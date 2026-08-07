# Options Pricer & Volatility Surface

An interactive Streamlit application for pricing European options, visualising the Greeks, and building real-time implied volatility smiles and surfaces from live market data.

## What it does

- **Black-Scholes pricing** for European calls and puts, implemented from the closed-form formula.
- **All five Greeks** (Delta, Gamma, Vega, Theta, Rho).
- **A custom implied volatility solver** (Newton-Raphson), including a Vega-floor guard and a sanity check against negative volatilities
- **Live market data** pulled via `yfinance` for AAPL, MSFT, GOOGL, and AMZN.
- **A volatility smile**, fitted per expiry using an **SVI (Stochastic Volatility Inspired) parametrisation**.
- **A 3D implied volatility surface** (strike × time-to-expiry × IV), built by repeating the smile-fitting pipeline across multiple expiries.
- **A fully interactive dashboard**: strike, expiry, and option type are chosen via sliders/radio buttons; volatility and the risk-free rate are derived from the fitted smile and a live 13-week Treasury yield (`^IRX`) respectively.
- **Multi-option strategies payoff graphs**: `payoff_diagram_main.py` contains a small matplotlib UI which allows you to visualise the long and short payoffs of several multi-option strategies, including straddles, collars and bearish and bullish spreads.

## Architecture

The project is split into modules by responsibility, with `app.py` handling only UI/plotting:

| File | Responsibility |
|---|---|
| `black_scholes.py` | Closed-form pricing (`bs_euro_call`, `bs_euro_put`) and the five Greeks |
| `implied_volatility.py` | Newton-Raphson IV solver for calls and puts |
| `market_data.py` | All `yfinance` interaction: fetching option chains, expiries, the risk-free rate, and running the IV solver |
| `vol_surface.py` | SVI smile fitting (`fit_smile`) and multi-expiry surface construction (`build_vol_surface`) |
| `app.py` | Streamlit UI |

## Future work

- **Dupire local volatility calibration** — using the fitted price surface (via `∂C/∂T` and `∂²C/∂K²`) to back out a unique local volatility function `σ_loc(S,t)` consistent with all quoted vanilla prices.
- **A Monte Carlo pricer for exotic (path-dependent) payoffs**, simulating under the calibrated local volatility surface.
- **A delta-hedging backtest**, using the fitted surface and real Greeks to simulate the P&L of a dynamically-hedged option position over historical data.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

(or, on Windows, double-click `run_app.bat`)

## Tech stack

Python, NumPy, SciPy (`scipy.stats`, `scipy.optimize.curve_fit`), pandas, Matplotlib, Streamlit, yfinance.
