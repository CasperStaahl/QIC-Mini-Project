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

def test_satisfiable_complex_contradiction():
    A = Atomic("A")
    B = Atomic("B")
    C = Atomic("C")

    not_A = Negation(A)
    not_B = Negation(B)

    A_or_B = Disjunction(A, B)
    not_A_or_C = Disjunction(not_A, C)
    not_B_or_C = Disjunction(not_B, C)

    conjunction_part = Conjunction(Conjunction(A_or_B, not_A_or_C), not_B_or_C)

    negated_conjunction = Negation(conjunction_part)
    p = Disjunction(negated_conjunction, C)
    not_p = Negation(p)

    c = 0
    sampler = StatevectorSampler()
    assert satisfiable(not_p, c, sampler) == False

def test_satisfiable_complex_single_solution():
    # Creating atomic propositions
    A = Atomic("A")
    B = Atomic("B")
    C = Atomic("C")

    # Creating negations
    not_B = Negation(B)

    # Creating conjunctions
    A_and_not_B = Conjunction(A, not_B)
    C_and_B = Conjunction(C, B)

    # Creating disjunctions
    left_expression = Disjunction(A_and_not_B, C_and_B)

    # Rewriting the implication as negation and disjunction
    negated_left_expression = Negation(left_expression)
    p = Disjunction(negated_left_expression, A)
    not_p = Negation(p)

    c = 1
    sampler = StatevectorSampler()
    assert satisfiable(not_p, c, sampler) == True

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










