# Options Pricer & Volatility Surface

An interactive Streamlit application for pricing European options, visualising the Greeks, and building implied volatility smiles and surfaces from live market data.

## What it does

- **Black-Scholes pricing** for European calls and puts, with a continuous dividend yield `q`.
- **All five Greeks** (Delta, Gamma, Vega, Theta, Rho), each adjusted for `q`.
- **A Newton-Raphson implied volatility solver**, with a vega-floor guard and a negative-volatility check.
- **Live market data** via `yfinance` for AAPL, MSFT, GOOGL and AMZN.
- **Quote filtering**: prices are taken as the bid-ask midpoint, with zero-bid, crossed and wide-spread quotes discarded, and a minimum volume and open interest requirement.
- **One implied volatility smile per expiry**, built from out-of-the-money options only (puts below spot, calls above), fitted with an **SVI (Stochastic Volatility Inspired)** parametrisation.
- **A 3D implied volatility surface** (strike × time-to-expiry × IV) across multiple expiries.
- **An interactive dashboard**: strike snapped to listed strikes, expiry and option type selectable; market mid and model price displayed side by side.
- **Validation checks** (`put_call_validator.py`) covering put-call parity on the pricer and on live market mids.
- **Multi-option strategy payoff diagrams**: `payoff_diagrams_main.py` is a standalone matplotlib UI for straddles, strangles, spreads, collars, butterflies and condors.

## Validation

- **Put-call parity on the pricer**: `C − P = S·e^(−qT) − K·e^(−rT)` holds to ~6e-16 relative error (machine precision) across 10,000 randomised parameter sets.
- **Put-call parity on market mids**: median deviation of around one basis point of spot on a near-dated AAPL chain, confirming the quote-filtering and discounting are consistent.
- **SVI fit quality**: 0.04–0.52 vol points RMSE across expiries from roughly ten days to 2.4 years, on 12–45 strikes per slice. Error grows with maturity.

## Architecture

The project is split into modules by responsibility, with `app.py` handling only UI and plotting:

| File                    | Responsibility |
|-------------------------|---|
| `black_scholes.py`      | Closed-form pricing and the five Greeks, with dividend yield |
| `implied_volatility.py` | Newton-Raphson IV solver, shared between calls and puts |
| `market_data.py`        | All `yfinance` interaction: option chains, expiries, risk-free rate, dividend yield, quote cleaning, and smile construction |
| `vol_surface.py`        | SVI smile fitting and multi-expiry surface construction |
| `put_call_validator.py`  | Put-call parity checks against the pricer and against market data |
| `app.py`                | Streamlit UI |

## Known limitations

- **European pricing applied to American options.** Single-name US equity options are American, so put-call parity is strictly an inequality rather than an equality. The effect is small for short-dated near-the-money contracts, which is where the surface is most reliable.
- **A continuous dividend yield.** Real dividends are discrete cash payments on specific ex-dividend dates, so a single annualised `q` is wrong for any given expiry except by coincidence.
- 
## Future work

- **Dupire local volatility calibration** — using the fitted price surface (via `∂C/∂T` and `∂²C/∂K²`) to back out a local volatility function `σ_loc(S,t)` consistent with all quoted vanillas.
- **A Monte Carlo pricer for exotic (path-dependent) payoffs**, simulating under the calibrated local volatility surface.
- **A delta-hedging backtest**, using the fitted surface and real Greeks to simulate the P&L of a dynamically-hedged position over historical data.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

(or, on Windows, `run_app.bat`)

US equity options trade 14:30–21:00 UK time. Outside those hours `yfinance` often returns zero bids across the whole chain, in which case the quote filters correctly discard everything and the app reports that there are not enough liquid strikes.

## Tech stack

Python, NumPy, SciPy (`scipy.stats`, `scipy.optimize.curve_fit`), pandas, Matplotlib, Streamlit, yfinance.