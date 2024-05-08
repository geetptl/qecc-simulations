import numpy as np  
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute  
from matplotlib import pyplot as plt  
  
  
# Initialize logical qubit  
def initialize_logical_qubit():  
    logical_state = QuantumCircuit(1)  
    return logical_state  
  
  
# Encoding  
def encode(logical_state):  
    encoding_circuit = QuantumCircuit(6, 6)  
    encoding_circuit.append(logical_state.to_gate(), [0])  
      
    encoding_circuit.h([0, 1, 2, 3, 4, 5])  
    encoding_circuit.cx(0, 1)  
    encoding_circuit.cx(2, 3)  
    encoding_circuit.cx(4, 5)  
    encoding_circuit.h([0, 1, 2, 3, 4, 5])  
  
    return encoding_circuit  
  
  
# Introduce errors (for testing purposes)  
def introduce_errors(encoded_state, p):  
    error_circuit = encoded_state.copy()  
    errors = []  
    for i in range(6):  
        p_flip = np.random.random(1)[0]  
        if p_flip < p:  
            errors.append(i)  
            error_circuit.x(i)  
  
    return errors, error_circuit  
  
  
# Measure errors  
def measure_errors(encoded_state):  
    error_measurement_circuit = encoded_state.copy()  
    error_measurement_circuit.measure([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])  
    return error_measurement_circuit  
  
  
def main():  
    N = 100  
    probs = np.linspace(0, 1, 10, endpoint=False)  
    plot_data = np.zeros(probs.shape)  
  
    for i_p, p in enumerate(probs):  
        total_qubits_affected = 0  
        for n in range(N):  
            logical_state = initialize_logical_qubit()  
            encoded_state = encode(logical_state)  
            errors, noisy_state = introduce_errors(encoded_state, p)  
            error_measurement_circuit = measure_errors(noisy_state)  
  
            # Execute the circuit and get the results  
            backend = Aer.get_backend('qasm_simulator')  
            result = execute(error_measurement_circuit, backend, shots=1).result()  
            counts = result.get_counts()  
  
            # Count the number of qubits affected by errors  
            total_qubits_affected += sum([bin(int(k, 2)).count('1') for k in counts.keys()])  
  
        plot_data[i_p] = total_qubits_affected / N  
  
    plt.plot(probs, plot_data, label="Number of qubits affected by errors")  
    plt.ylabel("Average number of qubits affected by errors")  
    plt.xlabel("p")  
    plt.grid()  
    plt.legend()  
    plt.title("Effect of error probability on the number of qubits affected by errors")  
    plt.savefig("6qubit_plot.png")  
  
  
# Call the main function  
main()  

