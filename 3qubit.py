import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from matplotlib import pyplot as plt


# Initialize logical qubit
def initialize_logical_qubit():
    logical_state = QuantumCircuit(1)
    return logical_state


# Encoding
def encode(logical_state):
    encoding_circuit = QuantumCircuit(5, 3)
    encoding_circuit.append(logical_state.to_gate(), [0])
    encoding_circuit.cx(0, 1)
    encoding_circuit.cx(0, 2)
    return encoding_circuit


# Introduce errors (for testing purposes)
def introduce_errors(encoded_state, p):
    error_circuit = encoded_state.copy()
    errors = []
    for i in range(3):
        p_flip = np.random.random(1)[0]
        if p_flip < p:
            errors.append(i)
            error_circuit.x(i)

    return errors, error_circuit


# Measure stabilizers
def measure_stabilizers(noisy_state):
    stabilizer_circuit = noisy_state.copy()
    stabilizer_circuit.cx(0, 3)
    stabilizer_circuit.cx(1, 3)
    stabilizer_circuit.cx(0, 4)
    stabilizer_circuit.cx(2, 4)
    stabilizer_circuit.measure([3, 4], [0, 1])
    return stabilizer_circuit


# Correct errors
def correct_errors(stabilizer_circuit):
    result = execute(stabilizer_circuit, Aer.get_backend("qasm_simulator"), shots=1).result()
    counts = result.get_counts()
    error_key = list(counts.keys())[0]

    corrected_circuit = stabilizer_circuit.copy()
    if error_key == "011":
        corrected_circuit.x(0)
        return [0], corrected_circuit
    elif error_key == "001":
        corrected_circuit.x(1)
        return [1], corrected_circuit
    elif error_key == "010":
        corrected_circuit.x(2)
        return [2], corrected_circuit
    elif error_key == "000":
        return [], corrected_circuit

    return [-1], corrected_circuit


# Main function
def main():
    N = 1000
    probs = np.linspace(0, 1, 100, endpoint=False)
    plot_data = np.zeros(probs.shape)

    for i_p, p in enumerate(probs):
        for n in range(N):
            logical_state = initialize_logical_qubit()
            encoded_state = encode(logical_state)
            errors, noisy_state = introduce_errors(encoded_state, p)
            stabilizer_circuit = measure_stabilizers(noisy_state)
            identified_errors, corrected_circuit = correct_errors(stabilizer_circuit)
            # print(corrected_circuit)
            # print(f"{identified_errors} == {errors} = {identified_errors == errors}")
            if identified_errors == errors:
                plot_data[i_p] += 1
        print(plot_data)
    
    plt.plot(probs, plot_data*100/N, label="With Error Correction")
    plt.plot(probs, np.linspace(100, 0, probs.shape[0]), linestyle='dashed', label="Without Error Correction")
    plt.ylabel("% times where correct errors detected")
    plt.xlabel("p")
    plt.grid()
    plt.legend()
    plt.title("Effectiveness of 3-qubit error correction code")
    plt.savefig("plots/3qubit.svg")


# Call the main function
main()
