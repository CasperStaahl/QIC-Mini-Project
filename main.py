import math
from typing import Dict, Set
from qiskit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import GroverOperator

Assignment = Dict[str, bool]

class Proposition:
    pass

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
    oracle, atom_lookup = convert_to_q_circuit(not_p)
    grover = grover(oracle, atom_lookup)
    n = 2 ** count_atomic_propositions(not_p)
    t = 0
    k = n / (2 ** t)
    while t <= math.log2(n / k) + c:
        iterations = (math.pi / 4) * ((n / k) ** 0.5)
        # todo repeat grover onto itself iterations times and run it to get  a valuation.
        # witness_assignment = grover(oracle, iterations)
        if valuation(not_p, witness_assignment):
            return False
        t += 1
        k = n / (2 ** t)
    return True

def phase_oracle(p: Proposition):
    atom_lookup = {item: index for index, item in enumerate(atomic_propositions(p))}
    qc_base = QuantumCircuit(len(atom_lookup))
    qc_r = phase_oracle_recur(p, qc_base, atom_lookup)
    qc_r_r_daggert_pos = list(range(0, qc_r.num_qubits))
    qc_final = QuantumCircuit(qc_r.num_qubits + 1)
    qc_final.compose(qc_r, qc_r_r_daggert_pos, inplace=True)
    qc_final.x(qc_final.num_qubits - 1)
    qc_final.h(qc_final.num_qubits - 1)
    qc_final.cx(qc_final.num_qubits - 2, qc_final.num_qubits - 1)
    qc_final.h(qc_final.num_qubits - 1)
    qc_final.x(qc_final.num_qubits - 1)
    qc_r_daggert = qc_r.inverse()
    qc_final.compose(qc_r_daggert, qc_r_r_daggert_pos, inplace=True)
    return qc_final, atom_lookup

def phase_oracle_recur(p: Proposition, qc_base: QuantumCircuit, atom_lookup):
    if type(p) is Atomic:
        qc_atom = QuantumCircuit(qc_base.num_qubits + 1)
        qc_atom.cx(atom_lookup[p.id], qc_base.num_qubits, f"atom {p.id}")
        qc_atom.compose(qc_base, list(range(1, qc_base.num_qubits + 1)))
        return qc_atom

    if type(p) is Negation:
        qc_pnot = phase_oracle_recur(p.not_p, qc_base, atom_lookup)
        qc_pnot.x(qc_pnot.num_qubits - 1)
        return qc_pnot

    if type(p) is Conjunction or Disjunction:
        qc_1 = phase_oracle_recur(p.p1, qc_base, atom_lookup)
        qc_2 = phase_oracle_recur(p.p2, qc_base, atom_lookup)

        qc_base_start = 0
        qc_base_end = qc_base_start + qc_base.num_qubits
        qc_base_range = list(range(qc_base_start, qc_base_end))

        qc_1_start = qc_base_end
        qc_1_end = qc_1_start + qc_1.num_qubits - qc_base.num_qubits

        qc_2_start = qc_1_end
        qc_2_end = qc_2_start + qc_2.num_qubits - qc_base.num_qubits

        qc_junction = QuantumCircuit(qc_2_end + 1)

        qc_1_range = qc_base_range + list(range(qc_1_start, qc_1_end))
        qc_junction.compose(qc_1, qc_1_range , inplace=True)

        qc_2_range = qc_base_range + list(range(qc_2_start, qc_2_end))
        qc_junction.compose(qc_2, qc_2_range, inplace=True)

        if type(p) is Disjunction:
            qc_junction.x(qc_1_end - 1)
            qc_junction.x(qc_2_end - 1)
        qc_junction.ccx(qc_1_end - 1, qc_2_end - 1, qc_junction.num_qubits -1)
        if type(p) is Disjunction:
                qc_junction.x(qc_junction.num_qubits - 1)

        return qc_junction

def grover(oracle, atom_lookup):
    qc_state_prep = QuantumCircuit(oracle.num_qubits)
    qc_state_prep.h(oracle.num_qubits - 1)
    for i in range(len(atom_lookup)):
        qc_state_prep.h(i)
    grover_op = GroverOperator(oracle, qc_state_prep, insert_barriers=True)
    return grover_op

def count_atomic_propositions(p: Proposition) -> int:
    return len(atomic_propositions(p))

def atomic_propositions(p: Proposition) -> Set[str]:
    if type(p) is Atomic:
        return {p.id}
    if type(p) is Negation:
        return atomic_propositions(p.not_p)
    if type(p) is Conjunction or type(p) is Disjunction:
        return atomic_propositions(p.p1) | atomic_propositions(p.p2)

def valuation(p: Proposition, ass: Assignment):
    if type(p) is Atomic:
        return ass[p.id]
    if type(p) is Negation:
        return not valuation(p.not_p, ass)
    if type(p) is Conjunction:
        return valuation(p.p1, ass) and valuation(p.p2, ass)
    if type(p) is Disjunction:
        return valuation(p.p1, ass) or valuation(p.p2, ass)

if __name__ == "__main__":
    p = Conjunction(
            Disjunction(
                Atomic("A"),
                Atomic("B")
                ),
            Negation(
                Atomic("C")
                )
            )
    qc, lookup = phase_oracle(p)
    qc = grover(qc, lookup).decompose()
    print(qc)

