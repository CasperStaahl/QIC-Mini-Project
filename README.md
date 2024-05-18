# QIC-Mini-Project

## Introduction

The task is to use Grover's algorithm to implement a SAT solver.

## State of the art

## Method

The algorithm below serves as a high-level overview, and hopefully convinces you that the solution will work.

    def satisfiable(p: Proposition, sampler) -> bool:
        oracle = phase_oracle(p)
        N = 2 ** count_atomic_propositions(p)
        m = 1
        while m <= sqrt(N):
            k = random{1, 2, ..., round(m)}
            grover_k_times = grover(oracle, k)
            assignment = grover_k_times.run()
            if valuation(assignment):
                return True
            m = (5 / 4) * m
    return False

The idea is to convert `p` to an quantum circuit corresponding to the oracle in Grover's algorithm, and run Grover's algorithm  on this oracle until the probability of us missing a solution is sufficiently small.
For this purpose we use amplitude amplification:
we iteratively pick k, the number of Grover operator applications from the integer range [1 round(m)], with m = 1 initially.
If Grover's algorithm returns an assignment with the evaluates to true for the proposition `p` we stop otherwise we continue increasing m exponentially (in our case `m = (5 / 4) * m`) after each iteration.
We stop when `m <= sqrt(N)`.

## Implementation in Qiskit

An implementation with accompanying documentation can be found in `main.py`, see the `satisfiable` function for the top level algorithm.

## Simulations

For the simulation is just wanted to test how reliable the SAT solver was, my argument for why this is really the only meaningful metric for the simulations are as follows:
In general normal SAT benchmarks are far to large for the simulator to handle (32 qbits is the max), the smallest benchmarks I could find having 20 variables and 91 clauses, and further the simulation is far to slow on even smaller 'benchmarks'.

Therefore I wrote a small script to generate random propositions, with parameters for the maximum number of atoms and number of connectivities.
The only thing that can ever go wrong is that a false negative is reported, false positives are check by evaluating the assignment.
I carried out ad hoc fuzz testing to see if could get the solver to report false negatives (results were compared against a very simple brute force SAT solver), the results are provided below.

Running 10000 test with random proposition with maximum 3 atoms and 3 connectivities I was able to get 2 false negatives.

Running 1000 test with random proposition with maximum 5 atoms and 5 connectivities I was able to get 0 false negatives.

Running 100 test with random proposition with maximum 10 atoms and 10 connectivities I was not able to even finish a single run...


## Hardware execution

## Discussion of simulation and hardware results

## Conclusions
