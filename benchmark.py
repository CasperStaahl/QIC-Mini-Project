from main import *
from qiskit.primitives import StatevectorSampler

if __name__ == "__main__":
    num_tests = 100
    num_connectivities = 10
    max_num_atmos = 10
    num_false_negatives = 0
    num_false_positives = 0
    sampler = StatevectorSampler()

    for test in range(num_tests):
        p = random_proposition(num_connectivities, max_num_atmos)
        sat_b = satisfiable_brute(p)
        sat_q = satisfiable(p, sampler)
        if sat_q == False and sat_b == True:
            num_false_negatives += 1
        if sat_q == True and sat_b == False:
            num_false_positives += 1
        print(f"test/num_tests: {test + 1}/{num_tests}")
        print(f"num_false_negatives: {num_false_negatives}")
        print(f"num_false_positives: {num_false_positives}")
