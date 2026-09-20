"""
Quantum Approximate Optimization Algorithm (QAOA) Module
MaxCut and combinatorial optimization with parameterized
circuit layers, expectation value computation, and classical optimization.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


class MaxCut:
    """
    MaxCut problem formulation.
    """
    
    def __init__(self, num_nodes: int = 4):
        """
        Args:
            num_nodes: Number of graph nodes
        """
        self.n = num_nodes
        self.edges: List[Tuple[int, int]] = []
        self.weights: Dict[Tuple[int, int], float] = {}
    
    def add_edge(self, u: int, v: int, weight: float = 1.0):
        """
        Add edge.
        
        Args:
            u: Node u
            v: Node v
            weight: Edge weight
        """
        if u > v:
            u, v = v, u
        self.edges.append((u, v))
        self.weights[(u, v)] = weight
    
    def cut_value(self, assignment: List[int]) -> float:
        """
        Compute cut value for assignment.
        
        Args:
            assignment: Node assignments (0 or 1)
        
        Returns:
            Cut value
        """
        value = 0.0
        for u, v in self.edges:
            if assignment[u] != assignment[v]:
                value += self.weights.get((u, v), 1.0)
        return value
    
    def cost_hamiltonian_term(self, bitstring: int) -> float:
        """
        Evaluate cost Hamiltonian.
        
        Args:
            bitstring: Bitstring encoding
        
        Returns:
            Cost
        """
        assignment = [(bitstring >> i) & 1 for i in range(self.n)]
        return -self.cut_value(assignment)  # Negative for minimization
    
    def max_possible_cut(self) -> float:
        """
        Compute maximum possible cut (sum of all weights).
        
        Returns:
            Maximum cut
        """
        return sum(self.weights.values())


class QAOACircuit:
    """
    QAOA parameterized circuit.
    """
    
    def __init__(self, maxcut: MaxCut, p: int = 2):
        """
        Args:
            maxcut: MaxCut problem
            p: Circuit depth
        """
        self.maxcut = maxcut
        self.p = p
        self.gammas = [random.uniform(0, math.pi) for _ in range(p)]
        self.betas = [random.uniform(0, math.pi) for _ in range(p)]
    
    def mixer_hamiltonian(self, beta: float,
                         state: List[complex]) -> List[complex]:
        """
        Apply mixer Hamiltonian e^(-i*beta*H_mixer).
        
        Args:
            beta: Mixer parameter
            state: State
        
        Returns:
            New state
        """
        new_state = []
        for i, amp in enumerate(state):
            # Mixer: X rotations on all qubits
            # Simplified: phase rotation based on bit parity
            bits = bin(i).count('1')
            phase = -beta * bits
            new_state.append(amp * complex(math.cos(phase), math.sin(phase)))
        return new_state
    
    def problem_hamiltonian(self, gamma: float,
                           state: List[complex]) -> List[complex]:
        """
        Apply problem Hamiltonian e^(-i*gamma*H_C).
        
        Args:
            gamma: Problem parameter
            state: State
        
        Returns:
            New state
        """
        new_state = []
        for i, amp in enumerate(state):
            cost = self.maxcut.cost_hamiltonian_term(i)
            phase = -gamma * cost
            new_state.append(amp * complex(math.cos(phase), math.sin(phase)))
        return new_state
    
    def apply_circuit(self, state: List[complex]) -> List[complex]:
        """
        Apply full QAOA circuit.
        
        Args:
            state: Initial state
        
        Returns:
            Final state
        """
        for gamma, beta in zip(self.gammas, self.betas):
            state = self.problem_hamiltonian(gamma, state)
            state = self.mixer_hamiltonian(beta, state)
        return state
    
    def expectation_value(self) -> float:
        """
        Compute expectation value of cost Hamiltonian.
        
        Returns:
            Expectation
        """
        dim = 2 ** self.maxcut.n
        # Initialize uniform superposition
        state = [complex(1.0 / math.sqrt(dim), 0.0)] * dim
        
        state = self.apply_circuit(state)
        
        # Compute expectation
        exp = 0.0
        for i in range(dim):
            prob = abs(state[i]) ** 2
            cost = self.maxcut.cost_hamiltonian_term(i)
            exp += prob * cost
        
        return exp
    
    def sample(self, shots: int = 100) -> Dict[int, int]:
        """
        Sample from QAOA state.
        
        Args:
            shots: Number of shots
        
        Returns:
            Counts
        """
        dim = 2 ** self.maxcut.n
        state = [complex(1.0 / math.sqrt(dim), 0.0)] * dim
        state = self.apply_circuit(state)
        
        probs = [abs(state[i]) ** 2 for i in range(dim)]
        
        counts = {}
        for _ in range(shots):
            r = random.random()
            cumsum = 0.0
            for i, p in enumerate(probs):
                cumsum += p
                if r <= cumsum:
                    counts[i] = counts.get(i, 0) + 1
                    break
        
        return counts


class ClassicalOptimizer:
    """
    Classical optimization for QAOA parameters.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Args:
            learning_rate: Learning rate
        """
        self.lr = learning_rate
    
    def optimize(self, circuit: QAOACircuit,
                epochs: int = 50) -> QAOACircuit:
        """
        Optimize QAOA parameters.
        
        Args:
            circuit: QAOA circuit
            epochs: Epochs
        
        Returns:
            Optimized circuit
        """
        for _ in range(epochs):
            current = circuit.expectation_value()
            
            # Gradient-free: random perturbation
            for i in range(circuit.p):
                # Perturb gamma
                delta = random.uniform(-0.1, 0.1)
                circuit.gammas[i] += delta
                new_exp = circuit.expectation_value()
                if new_exp >= current:
                    circuit.gammas[i] -= delta  # Revert
                else:
                    current = new_exp
                
                # Perturb beta
                delta = random.uniform(-0.1, 0.1)
                circuit.betas[i] += delta
                new_exp = circuit.expectation_value()
                if new_exp >= current:
                    circuit.betas[i] -= delta
                else:
                    current = new_exp
        
        return circuit


class QuantumApproximateOptimization:
    """
    Unified QAOA controller.
    """
    
    def __init__(self):
        self.maxcut: Optional[MaxCut] = None
        self.circuit: Optional[QAOACircuit] = None
        self.optimizer = ClassicalOptimizer()
        self.results: List[Dict] = []
    
    def build_problem(self, num_nodes: int, edges: List[Tuple[int, int]]):
        """
        Build MaxCut problem.
        
        Args:
            num_nodes: Nodes
            edges: Edges
        """
        self.maxcut = MaxCut(num_nodes)
        for u, v in edges:
            self.maxcut.add_edge(u, v)
    
    def solve(self, p: int = 2, epochs: int = 50) -> Dict:
        """
        Solve with QAOA.
        
        Args:
            p: Circuit depth
            epochs: Optimization epochs
        
        Returns:
            Result
        """
        if self.maxcut is None:
            return {"error": "no_problem"}
        
        self.circuit = QAOACircuit(self.maxcut, p)
        self.circuit = self.optimizer.optimize(self.circuit, epochs)
        
        # Sample solution
        counts = self.circuit.sample(1000)
        best = min(counts.keys(), key=lambda x: self.maxcut.cost_hamiltonian_term(x))
        best_cost = self.maxcut.cost_hamiltonian_term(best)
        
        result = {
            "best_solution": best,
            "best_cost": best_cost,
            "approximation_ratio": -best_cost / max(self.maxcut.max_possible_cut(), 1.0),
            "final_expectation": self.circuit.expectation_value()
        }
        self.results.append(result)
        return result
    
    def qaoa_summary(self) -> Dict:
        """Get summary."""
        return {
            "runs": len(self.results),
            "nodes": self.maxcut.n if self.maxcut else 0,
            "edges": len(self.maxcut.edges) if self.maxcut else 0
        }
