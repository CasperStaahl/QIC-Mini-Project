from main import *
import pytest
from qiskit.primitives import StatevectorSampler

def test_satisfiable_simple_tautologi():
    p = Disjunction(
            Atomic("A"),
            Negation(
                Atomic("A")
                )
            )
    c = 0
    sampler = StatevectorSampler()
    assert satisfiable(p, c, sampler) == True

def test_satisfiable_simple_contradiction():
    p = Conjunction(
            Atomic("A"),
            Negation(
                Atomic("A")
                )
            )
    c = 0
    sampler = StatevectorSampler()
    assert satisfiable(p, c, sampler) == False

@pytest.mark.parametrize("a,b,expected", [
    (True, True, True),
    (True, False, False),
    (False, True, False),
    (False, False, False),
])
def test_valuation_conjunction(a, b, expected):
    p = Conjunction(
            Atomic("A"),
            Atomic("B")
            )
    ass = {"A": a, "B": b}
    assert valuation(p, ass) == expected


@pytest.mark.parametrize("a,b,expected", [
    (True, True, True),
    (True, False, True),
    (False, True, True),
    (False, False, False),
])
def test_valuation_disjunction(a, b, expected):
    p = Disjunction(
            Atomic("A"),
            Atomic("B")
            )
    ass = {"A": a, "B": b}
    assert valuation(p, ass) == expected

@pytest.mark.parametrize("a,expected", [
    (True, False),
    (False, True),
])
def test_valuation_negation(a, expected):
    p = Negation(
            Atomic("A"),
            )
    ass = {"A": a}
    assert valuation(p, ass) == expected

def test_count_atomic_propositions():
    p = Conjunction(
            Disjunction(
                Atomic("A"),
                Atomic("B")
                ),
            Negation(
                Atomic("C")
                )
            )
    assert count_atomic_propositions(p) == 3










