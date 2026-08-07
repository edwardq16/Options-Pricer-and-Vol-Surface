import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider
import payoff_diagrams_setup as pds

S = np.linspace(50, 150, 500)

# registry: name -> (function, list of param kinds)
# param kinds: "K" (a strike), "type" (call/put), "direction" (long/short)
STRATEGIES = {
    "Straddle":     (pds.straddle,     ["K", "direction"]),
    "Strangle":     (pds.strangle,     ["K", "K", "direction"]),
    "Bull spread":  (pds.bull_spread,  ["K", "K", "type", "direction"]),
    "Bear spread":  (pds.bear_spread,  ["K", "K", "type", "direction"]),
    "Collar":       (pds.collar,       ["K", "K", "direction"]),
    "Box spread":   (pds.box_spread,   ["K", "K", "direction"]),
    "Butterfly":    (pds.butterfly,    ["K", "K", "K", "type", "direction"]),
    "Condor":       (pds.condor,       ["K", "K", "K", "K", "type", "direction"]),
    "Iron butterfly": (pds.iron_butterfly, ["K", "K", "K", "direction"]),
    "Iron condor":  (pds.iron_condor,  ["K", "K", "K", "K", "direction"]),
}

MAX_STRIKES = 4

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.35, bottom=0.1)

line, = ax.plot(S, np.zeros_like(S), 'k-', linewidth=2)
ax.axhline(0, color='gray', linewidth=0.8)
ax.set_xlabel("Stock price at expiry")
ax.set_ylabel("Payoff")

# --- strategy selector ---
strategy_names = list(STRATEGIES.keys())
radio_ax = plt.axes([0.02, 0.55, 0.28, 0.4])
radio = RadioButtons(radio_ax, strategy_names)

# --- strike sliders (create max needed, hide unused ones later) ---
strike_sliders = []
for i in range(MAX_STRIKES):
    slider_ax = plt.axes([0.35, 0.02 + i * 0.04, 0.55, 0.03])
    slider = Slider(slider_ax, f"K{i+1}", 50, 150, valinit=90 + i * 10, valstep=1)
    strike_sliders.append(slider)

# --- type toggle (call/put) ---
type_ax = plt.axes([0.02, 0.35, 0.15, 0.1])
type_radio = RadioButtons(type_ax, ["call", "put"])

# --- direction toggle (long/short) ---
direction_ax = plt.axes([0.02, 0.2, 0.15, 0.1])
direction_radio = RadioButtons(direction_ax, ["long", "short"])


def get_current_strategy():
    name = radio.value_selected
    func, param_kinds = STRATEGIES[name]

    direction = 1 if direction_radio.value_selected == "long" else -1
    option_type = type_radio.value_selected

    args = []
    strike_count = 0
    for kind in param_kinds:
        if kind == "K":
            args.append(strike_sliders[strike_count].val)
            strike_count += 1
        elif kind == "type":
            args.append(option_type)
        elif kind == "direction":
            args.append(direction)

    return func(*args)


def update_slider_visibility():
    name = radio.value_selected
    _, param_kinds = STRATEGIES[name]
    n_strikes_needed = param_kinds.count("K")

    for i, slider in enumerate(strike_sliders):
        slider.ax.set_visible(i < n_strikes_needed)


def redraw(_event=None):
    strat = get_current_strategy()
    line.set_ydata(strat.strat_payoff(S))
    ax.set_title(strat.name)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()


def on_strategy_change(_label):
    update_slider_visibility()
    redraw()


radio.on_clicked(on_strategy_change)
type_radio.on_clicked(redraw)
direction_radio.on_clicked(redraw)
for slider in strike_sliders:
    slider.on_changed(redraw)

update_slider_visibility()
redraw()
plt.show()