from main import *
import azure.quantum
from azure.quantum.qiskit import AzureQuantumProvider
from azure.quantum import Workspace
import json

if __name__ == "__main__":
    num_tests = 1
    num_connectivities = 3
    max_num_atmos = 3
    num_false_negatives = 0
    num_false_positives = 0

    with open('resource.json', 'r') as resource_file:
        resource = json.load(resource_file)
    workspace = Workspace(
            resource_id = resource['id'],
            location = resource['location']
            )
    provider = AzureQuantumProvider(workspace)
    backend = provider.get_backend("rigetti.sim.qvm")

    for test in range(num_tests):
        p = random_proposition(num_connectivities, max_num_atmos)
        sat_b = satisfiable_brute(p)
        sat_q = satisfiable(p, backend, True)
        if sat_q == False and sat_b == True:
            num_false_negatives += 1
        if sat_q == True and sat_b == False:
            num_false_positives += 1
        print(f"test/num_tests: {test + 1}/{num_tests}")
        print(f"num_false_negatives: {num_false_negatives}")
        print(f"num_false_positives: {num_false_positives}")
