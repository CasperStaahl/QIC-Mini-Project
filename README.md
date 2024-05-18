# QIC-Mini-Project

## Introduction

The task is to use Grover's algorithm to implement a tautology/contradiction checker for zeroth-order propositions.
Further I want to use this to implement a reachability analysis for a simple while programming language if I have the time.

## State of the art

## Method

The algorithm below serves as a high-level overview, and hopefully convince you that the solution will work.

    isTautology(p: Proposition, c: Float)
        p' = not(p)
        oracle = convertToQCircuit(p')
        N = 2^countDistinctAtomicPropositions(p')
        t = 0
        k = N / 2^t
        while(t <= log2(N / k) + c)
            iterations = (pi / 4) * (N / k)^0.5
            witness = grover(oracle, iterations)
            if (p'(witness) == true)
                return false
            t++
            k = N / 2^t
        return true

The intuition is as follows: We convert the proposition `p` to it's it's negation `p'`.
`p'` will be a contradiction iff `p` is a tautology, and therefore if `p` is a tautology we won't be able to find an assignment such that `p'` is true.
The idea is then to convert `p'` to an quantum circuit corresponding to the oracle in Grover's algorithm, and run Grover's algorithm  on this oracle until the probability of us missing a solution is sufficiently small.
In particular we run Grover's algorithm with a number of iterations equal to `(pi / 4) * (N / k)^(1/2)` where `N` is the number of distinct truth assignments in `p'` and `k` is our "guess" of how many assignments exists where `p'` is true.
We continue to run Grover's algorithm for smaller and smaller guesses for `k` (`k = N / 2^t` in particular), if we find a witness assignment where `p'` evaluates to true `p` is not a tautology and we return false.
In the case where no counter witness is found we continue until the probability that we have missed such a witness is sufficiently small (`t = log2(N / k) + c` in particular) and return true.

## Implementation in Qiskit

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
