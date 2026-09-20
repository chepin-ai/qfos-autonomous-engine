"""
Quantum Game Theory Module
Quantum strategies, payoff matrices, Nash equilibrium,
quantum prisoner dilemma, and cooperative game analysis.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumStrategy:
    """Quantum strategy."""
    name: str
    amplitudes: List[complex]


class PayoffMatrix:
    """
    Game payoff matrix.
    """
    
    def __init__(self, rows: int = 2, cols: int = 2):
        """
        Args:
            rows: Row player strategies
            cols: Column player strategies
        """
        self.rows = rows
        self.cols = cols
        self.matrix: List[List[Tuple[float, float]]] = [
            [(0.0, 0.0) for _ in range(cols)] for _ in range(rows)
        ]
    
    def set_payoff(self, row: int, col: int,
                  payoff_row: float, payoff_col: float):
        """
        Set payoff.
        
        Args:
            row: Row
            col: Column
            payoff_row: Row player payoff
            payoff_col: Column player payoff
        """
        self.matrix[row][col] = (payoff_row, payoff_col)
    
    def get_payoff(self, row: int, col: int) -> Tuple[float, float]:
        """
        Get payoff.
        
        Args:
            row: Row
            col: Column
        
        Returns:
            Payoff tuple
        """
        return self.matrix[row][col]
    
    def expected_payoff(self, row_strategy: List[float],
                       col_strategy: List[float]) -> Tuple[float, float]:
        """
        Compute expected payoff.
        
        Args:
            row_strategy: Row strategy
            col_strategy: Column strategy
        
        Returns:
            Expected payoffs
        """
        exp_row = 0.0
        exp_col = 0.0
        
        for i in range(self.rows):
            for j in range(self.cols):
                p = row_strategy[i] * col_strategy[j]
                pr, pc = self.matrix[i][j]
                exp_row += p * pr
                exp_col += p * pc
        
        return exp_row, exp_col


class NashEquilibriumFinder:
    """
    Find Nash equilibrium.
    """
    
    def __init__(self):
        pass
    
    def find_pure_strategy_nash(self, payoff: PayoffMatrix) -> List[Tuple[int, int]]:
        """
        Find pure strategy Nash equilibria.
        
        Args:
            payoff: Payoff matrix
        
        Returns:
            Equilibrium strategy pairs
        """
        equilibria = []
        
        for i in range(payoff.rows):
            for j in range(payoff.cols):
                # Check if (i, j) is Nash
                pr, pc = payoff.get_payoff(i, j)
                
                # Row player deviation
                row_best = True
                for k in range(payoff.rows):
                    if k != i:
                        prk, _ = payoff.get_payoff(k, j)
                        if prk > pr:
                            row_best = False
                            break
                
                # Column player deviation
                col_best = True
                for k in range(payoff.cols):
                    if k != j:
                        _, pck = payoff.get_payoff(i, k)
                        if pck > pc:
                            col_best = False
                            break
                
                if row_best and col_best:
                    equilibria.append((i, j))
        
        return equilibria


class QuantumPrisonerDilemma:
    """
    Quantum prisoner dilemma game.
    """
    
    def __init__(self):
        self.payoff = PayoffMatrix(2, 2)
        # C = Cooperate, D = Defect
        # (C, C) = (3, 3), (C, D) = (0, 5), (D, C) = (5, 0), (D, D) = (1, 1)
        self.payoff.set_payoff(0, 0, 3.0, 3.0)
        self.payoff.set_payoff(0, 1, 0.0, 5.0)
        self.payoff.set_payoff(1, 0, 5.0, 0.0)
        self.payoff.set_payoff(1, 1, 1.0, 1.0)
    
    def quantum_payoff(self, row_amp: List[complex],
                      col_amp: List[complex]) -> Tuple[float, float]:
        """
        Compute quantum payoff.
        
        Args:
            row_amp: Row amplitudes
            col_amp: Column amplitudes
        
        Returns:
            Payoffs
        """
        # Simplified quantum payoff
        probs_row = [abs(a)**2 for a in row_amp]
        probs_col = [abs(a)**2 for a in col_amp]
        
        # Normalize
        s_r = sum(probs_row)
        s_c = sum(probs_col)
        
        if s_r > 0:
            probs_row = [p / s_r for p in probs_row]
        if s_c > 0:
            probs_col = [p / s_c for p in probs_col]
        
        return self.payoff.expected_payoff(probs_row, probs_col)


class CooperativeGameAnalyzer:
    """
    Analyze cooperative games.
    """
    
    def __init__(self):
        pass
    
    def shapley_value(self, player: int,
                     coalition_values: Dict[Tuple[int, ...], float],
                     num_players: int) -> float:
        """
        Compute Shapley value.
        
        Args:
            player: Player index
            coalition_values: Coalition values
            num_players: Number of players
        
        Returns:
            Shapley value
        """
        import itertools
        
        value = 0.0
        other_players = [i for i in range(num_players) if i != player]
        
        for r in range(num_players):
            # Coalitions of size r not containing player
            for coalition in itertools.combinations(other_players, r):
                coalition_with = tuple(sorted(coalition + (player,)))
                
                v_with = coalition_values.get(coalition_with, 0.0)
                v_without = coalition_values.get(coalition, 0.0)
                
                weight = math.factorial(r) * math.factorial(num_players - r - 1)
                weight /= math.factorial(num_players)
                
                value += weight * (v_with - v_without)
        
        return value


class QuantumGameTheory:
    """
    Unified quantum game theory controller.
    """
    
    def __init__(self):
        self.payoff = PayoffMatrix()
        self.nash = NashEquilibriumFinder()
        self.pd = QuantumPrisonerDilemma()
        self.cooperative = CooperativeGameAnalyzer()
        self.strategies: List[QuantumStrategy] = []
    
    def add_strategy(self, name: str, amplitudes: List[complex]):
        """
        Add strategy.
        
        Args:
            name: Name
            amplitudes: Amplitudes
        """
        self.strategies.append(QuantumStrategy(name, amplitudes))
    
    def analyze_game(self, payoff: PayoffMatrix) -> Dict:
        """
        Analyze game.
        
        Args:
            payoff: Payoff matrix
        
        Returns:
            Analysis
        """
        equilibria = self.nash.find_pure_strategy_nash(payoff)
        
        return {
            "pure_nash": len(equilibria),
            "equilibria": equilibria
        }
    
    def qgt_summary(self) -> Dict:
        """Get summary."""
        return {
            "strategies": len(self.strategies),
            "payoff_size": f"{self.payoff.rows}x{self.payoff.cols}"
        }
