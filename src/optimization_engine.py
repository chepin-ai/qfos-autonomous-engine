"""
Optimization Engine Module
Multi-objective optimization, Pareto frontier
computation, and constrained optimization.
"""

import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field


@dataclass
class Objective:
    """An optimization objective."""
    name: str
    minimize: bool = True  # True = minimize, False = maximize
    weight: float = 1.0


@dataclass
class Solution:
    """A candidate solution."""
    values: Dict[str, float]
    objectives: Dict[str, float] = field(default_factory=dict)
    score: float = 0.0


class ParetoFrontier:
    """
    Compute and maintain Pareto frontier.
    
    Finds non-dominated solutions in multi-objective space.
    """
    
    def __init__(self, objectives: List[Objective]):
        """
        Args:
            objectives: List of objectives
        """
        self.objectives = objectives
        self.frontier: List[Solution] = []
    
    def dominates(self, a: Solution, b: Solution) -> bool:
        """
        Check if solution a dominates solution b.
        
        Args:
            a: Potential dominator
            b: Potential dominated
        
        Returns:
            True if a dominates b
        """
        better_in_at_least_one = False
        
        for obj in self.objectives:
            val_a = a.objectives.get(obj.name, 0.0)
            val_b = b.objectives.get(obj.name, 0.0)
            
            if obj.minimize:
                if val_a > val_b:
                    return False
                if val_a < val_b:
                    better_in_at_least_one = True
            else:
                if val_a < val_b:
                    return False
                if val_a > val_b:
                    better_in_at_least_one = True
        
        return better_in_at_least_one
    
    def add(self, solution: Solution) -> bool:
        """
        Add solution to frontier if non-dominated.
        
        Args:
            solution: Solution to add
        
        Returns:
            True if added
        """
        # Check if solution is dominated by any in frontier
        for f in self.frontier:
            if self.dominates(f, solution):
                return False
        
        # Remove solutions dominated by new one
        self.frontier = [f for f in self.frontier
                        if not self.dominates(solution, f)]
        
        self.frontier.append(solution)
        return True
    
    def get_frontier(self) -> List[Solution]:
        """Get current Pareto frontier."""
        return self.frontier[:]
    
    def size(self) -> int:
        """Get frontier size."""
        return len(self.frontier)


class GeneticOptimizer:
    """
    Genetic algorithm for multi-objective optimization.
    """
    
    def __init__(self, population_size: int = 50,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 seed: Optional[int] = None):
        """
        Args:
            population_size: Population size
            mutation_rate: Mutation probability
            crossover_rate: Crossover probability
            seed: Random seed
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.rng = random.Random(seed)
        self.population: List[Solution] = []
        self.generation = 0
    
    def initialize(self, variable_ranges: Dict[str, Tuple[float, float]]):
        """
        Initialize population.
        
        Args:
            variable_ranges: Dict of var_name -> (min, max)
        """
        self.population = []
        for _ in range(self.population_size):
            values = {}
            for var, (vmin, vmax) in variable_ranges.items():
                values[var] = self.rng.uniform(vmin, vmax)
            self.population.append(Solution(values=values))
    
    def evaluate(self, objective_fns: Dict[str, Callable[[Dict[str, float]], float]]):
        """
        Evaluate population objectives.
        
        Args:
            objective_fns: Dict of objective_name -> function
        """
        for sol in self.population:
            sol.objectives = {}
            for name, fn in objective_fns.items():
                sol.objectives[name] = fn(sol.values)
    
    def select_parent(self) -> Solution:
        """Select parent using tournament selection."""
        tournament = self.rng.sample(self.population, min(3, len(self.population)))
        return min(tournament, key=lambda s: s.score)
    
    def crossover(self, a: Solution, b: Solution) -> Tuple[Solution, Solution]:
        """
        Perform crossover.
        
        Args:
            a: Parent A
            b: Parent B
        
        Returns:
            Two children
        """
        if self.rng.random() > self.crossover_rate:
            return a, b
        
        child1_values = {}
        child2_values = {}
        
        for key in a.values:
            if self.rng.random() < 0.5:
                child1_values[key] = a.values[key]
                child2_values[key] = b.values.get(key, a.values[key])
            else:
                child1_values[key] = b.values.get(key, a.values[key])
                child2_values[key] = a.values[key]
        
        return Solution(values=child1_values), Solution(values=child2_values)
    
    def mutate(self, solution: Solution,
              variable_ranges: Dict[str, Tuple[float, float]]):
        """
        Mutate a solution.
        
        Args:
            solution: Solution to mutate
            variable_ranges: Variable bounds
        """
        for key in solution.values:
            if self.rng.random() < self.mutation_rate:
                vmin, vmax = variable_ranges[key]
                solution.values[key] = self.rng.uniform(vmin, vmax)
    
    def evolve(self, variable_ranges: Dict[str, Tuple[float, float]],
              objective_fns: Dict[str, Callable[[Dict[str, float]], float]],
              generations: int = 100) -> List[Solution]:
        """
        Run genetic optimization.
        
        Args:
            variable_ranges: Variable bounds
            objective_fns: Objective functions
            generations: Number of generations
        
        Returns:
            Final population
        """
        if not self.population:
            self.initialize(variable_ranges)
        
        for _ in range(generations):
            self.evaluate(objective_fns)
            
            # Update scores (simple weighted sum)
            for sol in self.population:
                sol.score = sum(sol.objectives.values())
            
            # Create new generation
            new_population = []
            while len(new_population) < self.population_size:
                parent1 = self.select_parent()
                parent2 = self.select_parent()
                
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1, variable_ranges)
                self.mutate(child2, variable_ranges)
                
                new_population.extend([child1, child2])
            
            self.population = new_population[:self.population_size]
            self.generation += 1
        
        self.evaluate(objective_fns)
        return self.population


class ConstrainedOptimizer:
    """
    Constrained optimization using penalty method.
    """
    
    def __init__(self, penalty_weight: float = 1000.0):
        """
        Args:
            penalty_weight: Penalty for constraint violation
        """
        self.penalty_weight = penalty_weight
        self.constraints: List[Callable[[Dict[str, float]], float]] = []
    
    def add_constraint(self, constraint: Callable[[Dict[str, float]], float]):
        """
        Add constraint g(x) <= 0.
        
        Args:
            constraint: Function returning constraint value
        """
        self.constraints.append(constraint)
    
    def penalized_objective(self, objective_fn: Callable[[Dict[str, float]], float],
                           values: Dict[str, float]) -> float:
        """
        Compute penalized objective.
        
        Args:
            objective_fn: Original objective
            values: Variable values
        
        Returns:
            Penalized objective value
        """
        obj = objective_fn(values)
        penalty = 0.0
        
        for constraint in self.constraints:
            violation = constraint(values)
            if violation > 0:
                penalty += self.penalty_weight * violation ** 2
        
        return obj + penalty
    
    def is_feasible(self, values: Dict[str, float],
                   tolerance: float = 1e-6) -> bool:
        """
        Check if solution is feasible.
        
        Args:
            values: Variable values
            tolerance: Feasibility tolerance
        
        Returns:
            True if feasible
        """
        for constraint in self.constraints:
            if constraint(values) > tolerance:
                return False
        return True


class OptimizationEngine:
    """
    Unified optimization engine.
    """
    
    def __init__(self):
        self.genetic = GeneticOptimizer()
        self.pareto: Optional[ParetoFrontier] = None
        self.constrained = ConstrainedOptimizer()
    
    def optimize_multiobjective(self,
                               variable_ranges: Dict[str, Tuple[float, float]],
                               objectives: List[Objective],
                               objective_fns: Dict[str, Callable[[Dict[str, float]], float]],
                               generations: int = 100) -> List[Solution]:
        """
        Multi-objective optimization.
        
        Args:
            variable_ranges: Variable bounds
            objectives: Objective definitions
            objective_fns: Objective functions
            generations: Generations
        
        Returns:
            Pareto frontier solutions
        """
        self.pareto = ParetoFrontier(objectives)
        
        # Run genetic algorithm
        population = self.genetic.evolve(variable_ranges, objective_fns, generations)
        
        # Build Pareto frontier
        for sol in population:
            self.pareto.add(sol)
        
        return self.pareto.get_frontier()
    
    def optimize_constrained(self,
                            variable_ranges: Dict[str, Tuple[float, float]],
                            objective_fn: Callable[[Dict[str, float]], float],
                            constraints: List[Callable[[Dict[str, float]], float]],
                            generations: int = 100) -> Optional[Solution]:
        """
        Constrained optimization.
        
        Args:
            variable_ranges: Variable bounds
            objective_fn: Objective function
            constraints: Constraint functions
            generations: Generations
        
        Returns:
            Best feasible solution
        """
        self.constrained.constraints = constraints
        
        # Wrap objective with penalty
        def penalized(values):
            return self.constrained.penalized_objective(objective_fn, values)
        
        self.genetic.initialize(variable_ranges)
        population = self.genetic.evolve(
            variable_ranges,
            {"obj": penalized},
            generations
        )
        
        # Find best feasible solution
        feasible = [sol for sol in population
                   if self.constrained.is_feasible(sol.values)]
        
        if not feasible:
            return None
        
        return min(feasible, key=lambda s: objective_fn(s.values))
    
    def engine_summary(self) -> Dict:
        """Get engine summary."""
        return {
            "pareto_size": self.pareto.size() if self.pareto else 0,
            "generations": self.genetic.generation,
            "population_size": self.genetic.population_size,
            "constraints": len(self.constrained.constraints)
        }
