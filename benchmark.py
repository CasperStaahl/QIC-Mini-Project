from main import *
from qiskit.primitives import StatevectorSampler
import pandas as pd

if __name__ == "__main__":
    num_tests = 10000
    num_connectivities = 5
    max_num_atoms = 5
    num_false_negatives = 0
    num_false_positives = 0
    sampler = StatevectorSampler()
    df = pd.DataFrame(columns=["proposition", "satisfiable_brute", "satisfiable", "correct", "satisfiable_2nd", "correct_2nd"])

    for test in range(num_tests):
        p = random_proposition(num_connectivities, max_num_atoms)
        sat_b = satisfiable_brute(p)
        sat_q = satisfiable(p, sampler, False)
        print(f"test/num_tests: {test + 1}/{num_tests}")
        correct = sat_b == sat_q
        if correct:
            df.loc[len(df)] = [str(p), sat_b, sat_q, correct, None, None]
        else:
            sat_q2 = satisfiable(p, sampler, False)
            df.loc[len(df)] = [str(p), sat_b, sat_q, correct, sat_q2, sat_b == sat_q2]
        df.to_csv(f"results/sim_{num_tests}_{num_connectivities}_{max_num_atoms}.csv", index=False)

    df_not_correct = df[df["correct"] == False]
    print(df_not_correct)
    df_not_correct.to_csv(f"results/sim_{num_tests}_{num_connectivities}_{max_num_atoms}_not_correct.csv", index=False)

    df_both_not_correct = df[(df["correct"] == False) & (df["correct_2nd"] == False)]
    print(df_both_not_correct)
    df_not_correct.to_csv(f"results/sim_{num_tests}_{num_connectivities}_{max_num_atoms}_both_not_correct.csv", index=False)

