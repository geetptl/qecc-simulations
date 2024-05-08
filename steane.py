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
    encoding_circuit.h([4, 5, 6])
    encoding_circuit.cx(0, 1)
    encoding_circuit.cx(0, 2)
    encoding_circuit.barrier()

    encoding_circuit.cx(6, 0)
    encoding_circuit.cx(6, 1)
    encoding_circuit.cx(6, 3)
    encoding_circuit.barrier()

    encoding_circuit.cx(5, 0)
    encoding_circuit.cx(5, 2)
    encoding_circuit.cx(5, 3)
    encoding_circuit.barrier()

    encoding_circuit.cx(4, 1)
    encoding_circuit.cx(4, 2)
    encoding_circuit.cx(4, 3)
    encoding_circuit.barrier()
    
    return encoding_circuit


def introduce_errors(encoded_state, p):
    error_circuit = encoded_state.copy()

    errors_X = [5]
    for ex in errors_X:
        error_circuit.x(ex)

    errors_Z = [4]
    for ez in errors_Z:
        error_circuit.z(ez)

    error_circuit.barrier()

    # error_circuit.x(0)
    # for i in range(7):
    #     p_flip = np.random.random(1)[0]
    #     if p_flip < p:
    #         errors.append(i)
    #         error_circuit.x(i)

    return errors_X, errors_Z, error_circuit


def measure_stabilizers(noisy_state):
    stabilizer_circuit = noisy_state.copy()
    bit = QuantumRegister(3, "bit")
    stabilizer_circuit.add_register(bit)
    c_bit = ClassicalRegister(3, "c_bit")
    stabilizer_circuit.add_register(c_bit)

    phase = QuantumRegister(3, "phase")
    stabilizer_circuit.add_register(phase)
    c_phase = ClassicalRegister(3, "c_phase")
    stabilizer_circuit.add_register(c_phase)

    stabilizer_circuit.cx(0, bit[2])
    stabilizer_circuit.cx(2, bit[2])
    stabilizer_circuit.cx(4, bit[2])
    stabilizer_circuit.cx(6, bit[2])
    stabilizer_circuit.barrier()

    stabilizer_circuit.cx(1, bit[1])
    stabilizer_circuit.cx(2, bit[1])
    stabilizer_circuit.cx(5, bit[1])
    stabilizer_circuit.cx(6, bit[1])
    stabilizer_circuit.barrier()

    stabilizer_circuit.cx(3, bit[0])
    stabilizer_circuit.cx(4, bit[0])
    stabilizer_circuit.cx(5, bit[0])
    stabilizer_circuit.cx(6, bit[0])
    stabilizer_circuit.barrier()

    stabilizer_circuit.h(phase)
    stabilizer_circuit.cx(phase[2], 0)
    stabilizer_circuit.cx(phase[2], 2)
    stabilizer_circuit.cx(phase[2], 4)
    stabilizer_circuit.cx(phase[2], 6)
    stabilizer_circuit.barrier()

    stabilizer_circuit.cx(phase[1], 1)
    stabilizer_circuit.cx(phase[1], 2)
    stabilizer_circuit.cx(phase[1], 5)
    stabilizer_circuit.cx(phase[1], 6)
    stabilizer_circuit.barrier()

    stabilizer_circuit.cx(phase[0], 3)
    stabilizer_circuit.cx(phase[0], 4)
    stabilizer_circuit.cx(phase[0], 5)
    stabilizer_circuit.cx(phase[0], 6)
    stabilizer_circuit.barrier()

    # stabilizer_circuit.barrier()
    stabilizer_circuit.h(phase)
    stabilizer_circuit.barrier()

    stabilizer_circuit.measure(bit, c_bit)
    stabilizer_circuit.measure(phase, c_phase)
    stabilizer_circuit.barrier()
    return stabilizer_circuit


def correct_errors(noisy_state, stabilizer_circuit):
    result = execute(
        stabilizer_circuit, Aer.get_backend("qasm_simulator"), shots=1
    ).result()
    counts = result.get_counts()
    phase_ = list(counts.keys())[0].split()[0][::-1]
    bit_ = list(counts.keys())[0].split()[1][::-1]
    corrected_circuit = noisy_state.copy()

    z_syndrome_to_error = {
        "000": None,
        "001": 0,
        "010": 1,
        "011": 2,
        "100": 3,
        "101": 4,
        "110": 5,
        "111": 6,
    }

    x_syndrome_to_error = {
        "000": None,
        "001": 0,
        "010": 1,
        "011": 2,
        "100": 3,
        "101": 4,
        "110": 5,
        "111": 6,
    }

    # Correction for X errors
    x_error_key = bit_
    error_X = []
    if x_error_key in x_syndrome_to_error:
        error_pos = x_syndrome_to_error[x_error_key]
        if error_pos is not None:
            error_X.append(error_pos)
            corrected_circuit.x(error_pos)

    # Correction for Z errors
    z_error_key = phase_
    error_Z = []
    if z_error_key in z_syndrome_to_error:
        error_pos = z_syndrome_to_error[z_error_key]
        if error_pos is not None:
            error_Z.append(error_pos)
            corrected_circuit.z(error_pos)

    return error_X, error_Z, corrected_circuit


def steane_decode(corrected_state):
    decoding_circuit = corrected_state.copy()
    decoding_circuit.reset(range(1, 7))
    decoding_circuit.measure(0, 0)

    return decoding_circuit


def main():
    N = 10
    probs = np.linspace(0, 1, 10, endpoint=False)
    plot_data = np.zeros(probs.shape)

    for i_p, p in enumerate(probs):
        success_count = 0
        for n in range(N):
            logical_state = initialize_logical_qubit()

            steane_encoded_state = steane_encode(logical_state)
            print(steane_encoded_state)

            error_X, error_Z, noisy_state = introduce_errors(steane_encoded_state, p)
            stabilizer_circuit_before_correction = measure_stabilizers(noisy_state)
            print(stabilizer_circuit_before_correction)

            detected_error_X, detected_error_Z, corrected_state = correct_errors(
                noisy_state, stabilizer_circuit_before_correction
            )
            print(corrected_state)

            if error_X == detected_error_X and error_Z == detected_error_Z:
                success_count += 1

        plot_data[i_p] = success_count
        print(f"Error probability: {p}, success rate: {success_count * 100 / N}%")

    plt.plot(probs, plot_data * 100 / N, label="With Error Correction")
    plt.plot(
        probs,
        np.linspace(100, 0, probs.shape[0]),
        linestyle="dashed",
        label="Without Error Correction",
    )
    plt.ylabel("% times where correct errors detected")
    plt.xlabel("p")
    plt.grid()
    plt.legend()
    plt.title("Effectiveness of Steane code error correction")
    plt.savefig("plots/steane.svg")


main()
