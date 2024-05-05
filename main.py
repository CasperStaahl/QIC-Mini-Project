import math
from typing import Dict

Assignment = Dict[str, bool]

class Proposition:
    pass

class Atomic(Proposition):
    def __init__(self, id: str):
        self.id = id

class Atomic(Proposition):
    def __init__(self, id: str):
        self.id = id

class Negation(Proposition):
    def __init__(self, not_p: Proposition):
        self.not_p = not_p

class Conjunction(Proposition):
    def __init__(self, p1: Proposition, p2: Proposition):
        self.p1 = p1
        self.p2 = p2

class Disjunction(Proposition):
    def __init__(self, p1: Proposition, p2: Proposition):
        self.p1 = p1
        self.p2 = p2

def is_tautology(p: Proposition, c: float) -> bool:
    not_p = Negation(p)
    oracle = convert_to_q_circuit(not_p)
    n = 2 ** count_distinct_atomic_propositions(not_p)
    t = 0
    k = n / (2 ** t)
    while t <= math.log2(n / k) + c:
        iterations = (math.pi / 4) * ((n / k) ** 0.5)
        witness_assignment = grover(oracle, iterations)
        if valuation(not_p, witness_assignment):
            return False
        t += 1
        k = n / (2 ** t)
    return True

def convert_to_q_circuit(p: Proposition):
    pass

def count_distinct_atomic_propositions(p: Proposition) -> int:
    pass

def valuation(p: Proposition, ass: Assignment):
    if type(p) is Atomic:
        return ass[p.id]
    if type(p) is Negation:
        return not valuation(p.not_p, ass)
    if type(p) is Conjunction:
        return valuation(p.p1, ass) and valuation(p.p2, ass)
    if type(p) is Disjunction:
        return valuation(p.p1, ass) or valuation(p.p2, ass)



