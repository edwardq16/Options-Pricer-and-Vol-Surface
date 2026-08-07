import numpy as np
#long/short digital options

class Leg:
    def __init__(self, option_type, strike, position):
        self.option_type = option_type
        self.strike = strike
        self.position = position

    def leg_payoff(self, S):
        if self.option_type == "call":
            payoff = np.maximum(S - self.strike, 0)
        elif self.option_type == "put":
            payoff = np.maximum(self.strike - S, 0)
        elif self.option_type == "stock":
            payoff = S

        return payoff * self.position

class Strategy:
    def __init__(self, name, legs):
        self.name = name
        self.legs = legs

    def strat_payoff(self, S):
        total = 0
        for leg in self.legs:
            total += leg.leg_payoff(S)

        return total

#### 2-legged strategies ####

def straddle(K, direction):
    straddle = Strategy("Straddle",[
        Leg("call", K, direction),
        Leg("put", K, direction)
    ])
    return straddle

def strangle(K_L, K_H, direction):
    strangle = Strategy("Strangle",[
        Leg("put", K_L, direction),
        Leg("call", K_H, direction)
    ])
    return strangle

def bull_spread(K_L, K_H, type, direction):
    bull_spread = Strategy("Bull spread",[
        Leg(type, K_L, direction),
        Leg(type, K_H, -direction)
    ])
    return bull_spread

def bear_spread(K_L, K_H, type, direction):
    bear_spread = Strategy("Bear spread",[
        Leg(type, K_H, direction),
        Leg(type, K_L, -direction)
    ])
    return bear_spread

def covered_call(K):
    covered_call = Strategy("Covered call",[
        Leg("stock", None, 1),
        Leg("call", K, -1)
    ])
    return covered_call

def protective_put(K):
    protective_put = Strategy("Protective put",[
        Leg("stock", None, 1),
        Leg("put", K, 1)
    ])
    return protective_put

#### 3-legged strategies ####

def collar(K_L, K_H, direction):
    collar = Strategy("Collar",[
        Leg("stock", None, direction),
        Leg("put", K_L, direction),
        Leg("call", K_H, -direction)
    ])
    return collar

#### 4-legged strategies ####

def box_spread(K_L, K_H, direction):
    box_spread = Strategy("Box spread",[
        Leg("call", K_L, direction),
        Leg("call", K_H, -direction),
        Leg("put", K_H, direction),
        Leg("put", K_L, -direction)
    ])
    return box_spread

def butterfly(K_L, K, K_H, type, direction):
    butterfly = Strategy("Butterfly",[
        Leg(type, K_L, direction),
        Leg(type, K, -2 * direction),
        Leg(type, K_H, direction),
    ])
    return butterfly

def iron_butterfly(K_L, K, K_H, direction):
    iron_butterfly = Strategy("Iron butterfly", [
        Leg("put",  K_L, direction),
        Leg("put",  K, -direction),
        Leg("call", K, -direction),
        Leg("call", K_H, direction),
    ])
    return iron_butterfly

def condor(K1, K2, K3, K4, type, direction):
    condor = Strategy("Condor",[
        Leg(type, K1, direction),
        Leg(type, K2, -direction),
        Leg(type, K3, -direction),
        Leg(type, K4, direction),
    ])
    return condor

def iron_condor(K1, K2, K3, K4, direction):
    iron_condor = Strategy("Iron condor", [
        Leg("put",  K1, direction),
        Leg("put",  K2, -direction),
        Leg("call", K3, -direction),
        Leg("call", K4, direction),
    ])
    return iron_condor
