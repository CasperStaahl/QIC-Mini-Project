import math
import random
from itertools import product
from typing import Dict, Set, Tuple
from qiskit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import GroverOperator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit import transpile

# from qiskit_ibm_runtime import SamplerV2 as Sampler

Assignment = Dict[str, bool]


class Proposition:
    pass


class Atomic(Proposition):
    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return f"{self.id}"


class Negation(Proposition):
    def __init__(self, not_p: Proposition):
        self.not_p = not_p

    def __str__(self):
        return f"¬{self.not_p.__str__()}"


class Conjunction(Proposition):
    def __init__(self, p1: Proposition, p2: Proposition):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return f"({self.p1.__str__()}∧{self.p2.__str__()})"


class Disjunction(Proposition):
    def __init__(self, p1: Proposition, p2: Proposition):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return f"({self.p1.__str__()}∨{self.p2.__str__()})"


def satisfiable(p: Proposition, backend_or_sampler, is_backend: bool) -> bool:
    """
    Determines if proposition p is satisfiable, using Grover's algorithm with amplitude amplification.

    Args:
        p (Proposition): The proposition to check.
        sampler (Sampler): The sampler that should be used for the execution of the quantum circuit.

    Returns:
        bool: True if p is satisfiable, False if p is unsatisfiable with high probability.

    """
    # pm = generate_preset_pass_manager(backend=backend, optimization_level=1)

    # Convert proposition p to phase oracle and use oracle to create Grover operator.
    oracle, atom_lookup = phase_oracle(p)
    grover_op = grover(oracle, atom_lookup)

    # Count number of assignments.
    N = 2 ** count_atomic_propositions(p)

    m = 1
    while m <= math.sqrt(N):
        # randomly select number of applications of the Grover operator.
        k = random.randint(1, round(m))

        # Create Grover's algorithm circuit
        grover_k_times = QuantumCircuit(grover_op.num_qubits)
        grover_k_times.h(list(range(len(atom_lookup))) + [grover_op.num_qubits - 1])
        for _ in range(k):
            grover_k_times.compose(grover_op, inplace=True)
        grover_k_times.measure_all()
        # isa_grover_i_times = pm.run(grover_i_times)

        # Run circuit, get result.
        if is_backend :
            grover_k_times = transpile(grover_k_times, backend_or_sampler)
            result = (
                backend_or_sampler.run(grover_k_times, shots=1).result().get_counts()
            )
        else:
            result = backend_or_sampler.run([grover_k_times], shots=1).result()[0].data.meas.get_counts()
        result_bit_string = next(iter(result))[::-1]

        # Convert result to an assignment, and check if the valuation of the assignment is True.
        witness_assignment = {}
        for atom in atomic_propositions(p):
            witness_assignment[atom] = char_to_bool(
                result_bit_string[atom_lookup[atom]]
            )
        if valuation(p, witness_assignment):
            return True

        # Increase m exponentially.
        m = (5 / 4) * m

    # If no assignment is found return False.
    return False


def phase_oracle(p: Proposition) -> Tuple[QuantumCircuit, Dict[str, int]]:
    """
    Creates a quantum circuit that represents the proposition p.

    The circuit that is returned has a number of input bits at the top corresponding to the atomic propositions.
    The middle section of the circuit is reserved for workspace bits.
    The bottom most bit is the result bit, the result is encoded in the phase of the bit.

    Args:
        p (Proposition): Proposition that should be converted.

    Returns:
        QuantumCircuit: p as a QuantumCircuit.
        Dict[str, int]: a lookup table that corresponds atomic proposition to their location in the circuit.
    """
    # Create a lookup table that corresponds atomic proposition to their location in the circuit.
    atom_lookup = {item: index for index, item in enumerate(atomic_propositions(p))}

    # Create the 'left' side of of the circuit corresponding to a classical bit circuit.
    qc_base = QuantumCircuit(len(atom_lookup))
    qc_r = phase_oracle_recur(p, qc_base, atom_lookup)

    # Compose the classical bit circuit with a result phase flip bit and its own inverse
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


def phase_oracle_recur(
    p: Proposition, qc_base: QuantumCircuit, atom_lookup: Dict[str, int]
) -> QuantumCircuit:
    """
    Converts the proposition p to the corresponding classical circuit embedded in a quantum circuit.

    Args:
        p (Proposition): Proposition that should be converted..
        qc_base (QuantumCircuit): A circuit containing qubits corresponding to the ones present in atom_lookup.
        atom_lookup (Dict[str, int]): lookup table corresponding atomic propositions to qubits in qc_base.

    Returns:
        QuantumCircuit: p as a quantum embedded classical circuit.

    """

    # If the proposition is an atom 'fanout' on the corresponding bit.
    if type(p) is Atomic:
        qc_atom = QuantumCircuit(qc_base.num_qubits + 1)
        qc_atom.cx(atom_lookup[p.id], qc_base.num_qubits, f"atom {p.id}")
        qc_atom.compose(qc_base, list(range(1, qc_base.num_qubits + 1)))
        return qc_atom

    # If the proposition (not p) is a negation, construct the circuit for p and x/not gate the result bit.
    if type(p) is Negation:
        qc_pnot = phase_oracle_recur(p.not_p, qc_base, atom_lookup)
        qc_pnot.x(qc_pnot.num_qubits - 1)
        return qc_pnot

    # If the proposition is (p and p') or (p or p') convert p and p',
    # compose the two new circuits and/or gate the result bit of the two circuits to a new result bit.
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
        qc_junction.compose(qc_1, qc_1_range, inplace=True)

        qc_2_range = qc_base_range + list(range(qc_2_start, qc_2_end))
        qc_junction.compose(qc_2, qc_2_range, inplace=True)

        if type(p) is Disjunction:
            qc_junction.x(qc_1_end - 1)
            qc_junction.x(qc_2_end - 1)
        qc_junction.ccx(qc_1_end - 1, qc_2_end - 1, qc_junction.num_qubits - 1)
        if type(p) is Disjunction:
            qc_junction.x(qc_junction.num_qubits - 1)

        return qc_junction


def grover(oracle: QuantumCircuit , atom_lookup: Dict[str, int]) -> QuantumCircuit:
    """
    Creates the corresponding Grover operator given a phase oracle describing a proposition.

    Args:
        oracle (QuantumCircuit): Phase oracle describing a proposition, top most bits should correspond to the atomic propositions and align with atom_lookup, the bottom most bit should be the result bit.
        atom_lookup (Dict[str, int]): Lookup table corresponding atomic propositions to their location in oracle.

    Returns:
        QuantumCircuit: A grover operator with oracle as the oracle.

    """
    # All the workspace bits should be ignored in the Grover operator, hence the lines below
    qc_state_prep = QuantumCircuit(oracle.num_qubits)
    qc_state_prep.h(oracle.num_qubits - 1)
    for i in range(len(atom_lookup)):
        qc_state_prep.h(i)
    reflection_qubits = list(range(len(atom_lookup))) + [oracle.num_qubits - 1]

    # Create and return the Grover operator.
    grover_op = GroverOperator(
        oracle, qc_state_prep, reflection_qubits=reflection_qubits
    )
    return grover_op


def count_atomic_propositions(p: Proposition) -> int:
    """
    Counts the number of atomic proposition in p.
    """
    return len(atomic_propositions(p))


def atomic_propositions(p: Proposition) -> Set[str]:
    """
    Gives all atomic propositions in p.
    """
    if type(p) is Atomic:
        return {p.id}
    if type(p) is Negation:
        return atomic_propositions(p.not_p)
    if type(p) is Conjunction or type(p) is Disjunction:
        return atomic_propositions(p.p1) | atomic_propositions(p.p2)


def valuation(p: Proposition, ass: Assignment):
    """
    Evaluate proposition p using the assignment ass.
    """
    if type(p) is Atomic:
        return ass[p.id]
    if type(p) is Negation:
        return not valuation(p.not_p, ass)
    if type(p) is Conjunction:
        return valuation(p.p1, ass) and valuation(p.p2, ass)
    if type(p) is Disjunction:
        return valuation(p.p1, ass) or valuation(p.p2, ass)


def char_to_bool(char: str) -> bool:
    if char == "0":
        return False
    if char == "1":
        return True


def random_proposition(max_num_atoms: int, num_connectivities: int) -> Proposition:
    if num_connectivities == 0:
        atom = Atomic(f"{random.randint(0, max_num_atoms - 1)}")
        if random.choice([True, False]):
            atom = Negation(atom)
        return atom
    if 0 < num_connectivities:
        split = random.uniform(0, 1)
        _num_connectivities = num_connectivities - 1
        num_left = math.floor(_num_connectivities * split)
        num_right = math.ceil(_num_connectivities * (1 - split))
        left = random_proposition(max_num_atoms, num_left)
        right = random_proposition(max_num_atoms, num_right)
        if random.choice([True, False]):
            p = Conjunction(left, right)
        else:
            p = Disjunction(left, right)
        if random.choice([True, False]):
            p = Negation(p)
        return p


def satisfiable_brute(proposition):
    atoms = atomic_propositions(proposition)
    for assignment in all_assignments(atoms):
        if valuation(proposition, assignment):
            return True
    return False


def all_assignments(atoms):
    for values in product([False, True], repeat=len(atoms)):
        yield dict(zip(atoms, values))

def satisfiable_count(proposition):
    atoms = atomic_propositions(proposition)
    count = 0
    for assignment in all_assignments(atoms):
        if valuation(proposition, assignment):
            count += 1
    return count


if __name__ == "__main__":
    p0 = Atomic("0")
    p1 = Atomic("1")
    p2 = Atomic("2")

    not_p0 = Negation(p0)
    not_p1 = Negation(p1)
    not_p2 = Negation(p2)

    not_p0_and_p2 = Conjunction(not_p0, p2)
    not_not_p0_and_p2 = Negation(not_p0_and_p2)

    not_p2_or_not_p1 = Disjunction(not_p2, not_p1)
    not_not_p2_or_not_p1 = Negation(not_p2_or_not_p1)

    expression = Conjunction(not_not_p0_and_p2, not_not_p2_or_not_p1)

    # Printing the expression
    print(expression)
    print(satisfiable_count(expression))

