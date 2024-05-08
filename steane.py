import numpy as np  
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute  
import matplotlib.pyplot as plt  
 
def initialize_logical_qubit():  
    logical_state = QuantumCircuit(1)  
    logical_state.h(0)  
    return logical_state  
  
def steane_encode(logical_state):  
    encoding_circuit = QuantumCircuit(7, 7)  
    encoding_circuit.append(logical_state.to_gate(), [0])  
  
    # Encode the logical qubit using Steane code  
    encoding_circuit.cx(0, 3)  
    encoding_circuit.cx(0, 5)  
    encoding_circuit.h([0, 1, 2, 3, 4, 5, 6])  
    encoding_circuit.cx(0, 1)  
    encoding_circuit.cx(0, 2)  
    encoding_circuit.cx(3, 4)  
    encoding_circuit.cx(3, 5)  
    encoding_circuit.cx(6, 4)  
    encoding_circuit.cx(6, 5)  
    encoding_circuit.h([0, 1, 2, 3, 4, 5, 6])  
  
    return encoding_circuit  
  
def introduce_errors(encoded_state, p):  
    error_circuit = encoded_state.copy()  
    errors = []  
    for i in range(7):  
        p_flip = np.random.random(1)[0]  
        if p_flip < p:  
            errors.append(i)  
            error_circuit.x(i)  
  
    return errors, error_circuit  
  
def measure_stabilizers(noisy_state):  
    stabilizer_circuit = noisy_state.copy()  
    ancilla = QuantumRegister(6, 'ancilla')  
    stabilizer_circuit.add_register(ancilla)  
    cr = ClassicalRegister(6, 'stabilizer_c')  # Change the register name here  
    stabilizer_circuit.add_register(cr)  
  
    # Measure the stabilizers in the Z-basis  
    for i in range(3):  
        stabilizer_circuit.cx(i, ancilla[i])  
        stabilizer_circuit.cx(i + 4, ancilla[i])  
        stabilizer_circuit.cx((i + 1) % 3 + 4, ancilla[i])  
  
    for i in range(3):  
        stabilizer_circuit.cx(i, ancilla[i + 3])  
        stabilizer_circuit.cx(i + 4, ancilla[i + 3])  
        stabilizer_circuit.cx((i + 1) % 3 + 4, ancilla[i + 3])  
  
    stabilizer_circuit.barrier()  
    stabilizer_circuit.measure(ancilla, cr)  
  
    return stabilizer_circuit  
  
  
def correct_errors(noisy_state, stabilizer_circuit):  
    result = execute(stabilizer_circuit, Aer.get_backend("qasm_simulator"), shots=1).result()  
    counts = result.get_counts()  
    error_key = list(counts.keys())[0][::-1]  # Reverse the key to match the qubit order  
  
    corrected_circuit = noisy_state.copy()  
  
    z_syndrome_to_error = {  
        '000': None,  
        '001': 2,  
        '010': 1,  
        '011': 5,  
        '100': 0,  
        '101': 4,  
        '110': 3,  
        '111': 6  
    }  
  
    x_syndrome_to_error = {  
        '000': None,  
        '001': 5,  
        '010': 3,  
        '011': 6,  
        '100': 4,  
        '101': 0,  
        '110': 1,  
        '111': 2  
    }  
  
    # Correction for X errors  
    x_error_key = error_key[3:6]  
    if x_error_key in x_syndrome_to_error:  
        error_pos = x_syndrome_to_error[x_error_key]  
        if error_pos is not None:  
            corrected_circuit.x(error_pos)  
  
    # Correction for Z errors  
    z_error_key = error_key[0:3]  
    if z_error_key in z_syndrome_to_error:  
        error_pos = z_syndrome_to_error[z_error_key]  
        if error_pos is not None:  
            corrected_circuit.z(error_pos)  
  
    return corrected_circuit  
  
  
  
def steane_decode(corrected_state):  
    decoding_circuit = corrected_state.copy()  
    decoding_circuit.reset(range(1, 7))  
    decoding_circuit.measure(0, 0)  
  
    return decoding_circuit  
  
  
def main():  
    N = 100  
    probs = np.linspace(0, 1, 10, endpoint=False)  
    plot_data = np.zeros(probs.shape)  
  
    for i_p, p in enumerate(probs):  
        success_count = 0  
        for n in range(N):  
            logical_state = initialize_logical_qubit()  
            steane_encoded_state = steane_encode(logical_state)  
            errors, noisy_state = introduce_errors(steane_encoded_state, p)  
            stabilizer_circuit_before_correction = measure_stabilizers(noisy_state)  
            corrected_state = correct_errors(noisy_state, stabilizer_circuit_before_correction)  
            stabilizer_circuit_after_correction = measure_stabilizers(corrected_state)  
  
            result_before_correction = execute(stabilizer_circuit_before_correction, Aer.get_backend("qasm_simulator"), shots=1).result()  
            counts_before_correction = result_before_correction.get_counts()  
            error_key_before_correction = list(counts_before_correction.keys())[0]  
  
            result_after_correction = execute(stabilizer_circuit_after_correction, Aer.get_backend("qasm_simulator"), shots=1).result()  
            counts_after_correction = result_after_correction.get_counts()  
            error_key_after_correction = list(counts_after_correction.keys())[0]  
  
            if error_key_before_correction == error_key_after_correction:  
                success_count += 1  
  
        plot_data[i_p] = success_count  
        print(f"Error probability: {p}, success rate: {success_count * 100 / N}%")  
  
    plt.plot(probs, plot_data * 100 / N, label="With Error Correction")  
    plt.plot(probs, np.linspace(100, 0, probs.shape[0]), linestyle='dashed', label="Without Error Correction")  
    plt.ylabel("% times where correct errors detected")  
    plt.xlabel("p")  
    plt.grid()  
    plt.legend()  
    plt.title("Effectiveness of Steane code error correction")  
    plt.savefig("steane_plot.png")  
  
main()