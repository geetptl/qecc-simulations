import numpy as np  
from qiskit import QuantumCircuit, Aer, execute  
from qiskit.quantum_info import Statevector  
  
# Define Pauli matrices  
I = np.array([[1, 0], [0, 1]])  
X = np.array([[0, 1], [1, 0]])  
Z = np.array([[1, 0], [0, -1]])  
H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])  
  
# Define CNOT matrix  
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])  
  
def apply_gate(state_vector, gate_matrix, target_qubit, total_qubits):  
    gate_expanded = np.eye(1 << total_qubits)  
    for i in range(total_qubits):  
        if i == target_qubit:  
            gate_expanded = np.kron(gate_matrix, gate_expanded)  
        else:  
            gate_expanded = np.kron(I, gate_expanded)  
    return gate_expanded.dot(state_vector)  

def initialize_logical_qubit():  
    logical_state = QuantumCircuit(1)  
    logical_state.h(0)  
    return logical_state  

def steane_encode(logical_state):  
    # Initialize a 7-qubit quantum circuit  
    qc = QuantumCircuit(7)  
    qc.append(logical_state.to_gate(), [0])  
  
    # Execute the circuit to get the statevector  
    backend = Aer.get_backend('statevector_simulator')  
    state_vector = execute(qc, backend).result().get_statevector()  
  
    # Apply the Steane encoding operations using matrices  
    state_vector = apply_gate(state_vector, X, 0, 7)  
    state_vector = apply_gate(state_vector, X, 3, 7)  
    state_vector = apply_gate(state_vector, X, 5, 7)  
      
    for i in range(7):  
        state_vector = apply_gate(state_vector, H, i, 7)  
  
    state_vector = apply_gate(state_vector, X, 0, 7)  
    state_vector = apply_gate(state_vector, X, 1, 7)  
    state_vector = apply_gate(state_vector, X, 2, 7)  
    state_vector = apply_gate(state_vector, X, 3, 7)  
    state_vector = apply_gate(state_vector, X, 4, 7);  
    state_vector = apply_gate(state_vector, X, 5, 7);  
  
    for i in range(7):  
        state_vector = apply_gate(state_vector, H, i, 7)  
  
    return state_vector  
  
def main():  
    logical_state = initialize_logical_qubit()  
    steane_encoded_state_vector = steane_encode(logical_state)  
    print("Steane encoded state vector:")  
    print(steane_encoded_state_vector)  
  
# Call the main function  
main()  
