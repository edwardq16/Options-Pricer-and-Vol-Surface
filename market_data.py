import yfinance as yf
import numpy as np
from datetime import date
import streamlit as st
from implied_volatility import implied_vol_call, implied_vol_put

@st.cache_data
def get_option_chain(symbol, expiry):
    ticker = yf.Ticker(symbol)
    chain = ticker.option_chain(expiry)
    S = ticker.fast_info['lastPrice']
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    return chain.calls, chain.puts, S, T

@st.cache_data
def get_expiries(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.options

@st.cache_data
def get_rfr():
    irx = yf.Ticker("^IRX")
    r = irx.fast_info['lastPrice'] / 100
    return r

@st.cache_data
def solve_iv_smile(calls, puts, S, T, r, vol_0=0.2):
    filtered_calls = calls[(calls["volume"] > 0) | (calls["openInterest"] > 0)]
    filtered_puts = puts[(puts["volume"] > 0) | (puts["openInterest"] > 0)]
    call_data = {}
    put_data = {}

    for index, row in filtered_calls.iterrows():
        K = row["strike"]
        C_mkt = row["lastPrice"]
        call_data[K] = implied_vol_call(S, K, T, r, vol_0, C_mkt)

    for index, row in filtered_puts.iterrows():
        K = row["strike"]
        P_mkt = row["lastPrice"]
        put_data[K] = implied_vol_put(S, K, T, r, vol_0, P_mkt)

    clean_call_data = {K: iv for K, iv in call_data.items() if not np.isnan(iv) and 0.85 * S <= K <= 1.15 * S}
    clean_put_data = {K: iv for K, iv in put_data.items() if not np.isnan(iv) and 0.85 * S <= K <= 1.15 * S}
    return clean_call_data, clean_put_data