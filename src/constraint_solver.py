"""
Constraint Solver Module
CSP solver with backtracking, constraint propagation,
and SAT encoding for spacecraft planning.
"""

from typing import Dict, List, Set, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Variable:
    """A CSP variable."""
    name: str
    domain: List[Any]
    value: Optional[Any] = None


@dataclass
class Constraint:
    """A binary constraint between two variables."""
    var1: str
    var2: str
    check: Callable[[Any, Any], bool]


class CSPSolver:
    """
    Constraint Satisfaction Problem solver.
    
    Uses backtracking with arc consistency.
    """
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.constraints: List[Constraint] = []
        self.solution: Dict[str, Any] = {}
    
    def add_variable(self, name: str, domain: List[Any]):
        """Add a variable with domain."""
        self.variables[name] = Variable(name, domain[:])
    
    def add_constraint(self, var1: str, var2: str,
                      check: Callable[[Any, Any], bool]):
        """Add binary constraint."""
        self.constraints.append(Constraint(var1, var2, check))
    
    def get_neighbors(self, var_name: str) -> List[str]:
        """Get variable neighbors."""
        neighbors = []
        for c in self.constraints:
            if c.var1 == var_name:
                neighbors.append(c.var2)
            elif c.var2 == var_name:
                neighbors.append(c.var1)
        return neighbors
    
    def is_consistent(self, var_name: str, value: Any,
                     assignment: Dict[str, Any]) -> bool:
        """
        Check if value is consistent with assignment.
        
        Args:
            var_name: Variable name
            value: Value to check
            assignment: Partial assignment
        
        Returns:
            True if consistent
        """
        for c in self.constraints:
            if c.var1 == var_name and c.var2 in assignment:
                if not c.check(value, assignment[c.var2]):
                    return False
            elif c.var2 == var_name and c.var1 in assignment:
                if not c.check(assignment[c.var1], value):
                    return False
        return True
    
    def select_unassigned(self, assignment: Dict[str, Any]) -> Optional[str]:
        """Select unassigned variable (MRV heuristic)."""
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None
        
        # Minimum remaining values
        return min(unassigned,
                  key=lambda v: len(self.variables[v].domain))
    
    def order_values(self, var_name: str,
                    assignment: Dict[str, Any]) -> List[Any]:
        """Order values (least constraining value)."""
        return self.variables[var_name].domain[:]
    
    def backtrack(self, assignment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Backtracking search.
        
        Args:
            assignment: Partial assignment
        
        Returns:
            Complete assignment or None
        """
        if len(assignment) == len(self.variables):
            return assignment
        
        var = self.select_unassigned(assignment)
        if var is None:
            return None
        
        for value in self.order_values(var, assignment):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                
                del assignment[var]
        
        return None
    
    def solve(self) -> Optional[Dict[str, Any]]:
        """
        Solve CSP.
        
        Returns:
            Solution dict or None
        """
        self.solution = self.backtrack({})
        return self.solution
    
    def arc_consistency(self) -> bool:
        """
        Enforce arc consistency (AC-3).
        
        Returns:
            True if consistent, False if empty domain
        """
        queue = deque()
        
        for c in self.constraints:
            queue.append((c.var1, c.var2))
            queue.append((c.var2, c.var1))
        
        while queue:
            xi, xj = queue.popleft()
            if self._revise(xi, xj):
                if not self.variables[xi].domain:
                    return False
                for xk in self.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        
        return True
    
    def _revise(self, xi: str, xj: str) -> bool:
        """
        Revise domain of xi based on xj.
        
        Returns:
            True if domain was revised
        """
        revised = False
        new_domain = []
        
        for vi in self.variables[xi].domain:
            has_support = False
            for vj in self.variables[xj].domain:
                for c in self.constraints:
                    if (c.var1 == xi and c.var2 == xj):
                        if c.check(vi, vj):
                            has_support = True
                            break
                    elif (c.var1 == xj and c.var2 == xi):
                        if c.check(vj, vi):
                            has_support = True
                            break
                if has_support:
                    break
            
            if has_support:
                new_domain.append(vi)
            else:
                revised = True
        
        self.variables[xi].domain = new_domain
        return revised


class SATEncoder:
    """
    Simple SAT encoder/decoder for CSP.
    """
    
    def __init__(self):
        self.clauses: List[List[int]] = []
        self.var_map: Dict[Tuple[str, Any], int] = {}
        self.next_var = 1
    
    def encode_variable(self, var_name: str, value: Any) -> int:
        """Get SAT variable for CSP assignment."""
        key = (var_name, value)
        if key not in self.var_map:
            self.var_map[key] = self.next_var
            self.next_var += 1
        return self.var_map[key]
    
    def add_clause(self, literals: List[int]):
        """Add SAT clause."""
        self.clauses.append(literals[:])
    
    def encode_exactly_one(self, var_name: str, domain: List[Any]):
        """
        Encode "exactly one" constraint.
        
        At least one value must be assigned.
        At most one value can be assigned.
        """
        vars_list = [self.encode_variable(var_name, v) for v in domain]
        
        # At least one
        self.add_clause(vars_list)
        
        # At most one (pairwise)
        for i in range(len(vars_list)):
            for j in range(i + 1, len(vars_list)):
                self.add_clause([-vars_list[i], -vars_list[j]])
    
    def encode_binary_constraint(self, var1: str, val1: Any,
                                 var2: str, val2: Any,
                                 allowed: bool = True):
        """
        Encode binary constraint.
        
        Args:
            var1, val1: First variable assignment
            var2, val2: Second variable assignment
            allowed: True if allowed, False if forbidden
        """
        v1 = self.encode_variable(var1, val1)
        v2 = self.encode_variable(var2, val2)
        
        if allowed:
            # If v1 then v2: -v1 or v2
            self.add_clause([-v1, v2])
        else:
            # Not both: -v1 or -v2
            self.add_clause([-v1, -v2])
    
    def get_formula(self) -> Dict:
        """Get SAT formula."""
        return {
            "num_vars": self.next_var - 1,
            "num_clauses": len(self.clauses),
            "clauses": self.clauses,
            "var_map": self.var_map
        }
    
    def decode_solution(self, sat_assignment: Dict[int, bool]) -> Dict[str, Any]:
        """
        Decode SAT solution to CSP assignment.
        
        Args:
            sat_assignment: SAT variable assignments
        
        Returns:
            CSP assignment
        """
        assignment = {}
        for (var_name, value), var_id in self.var_map.items():
            if sat_assignment.get(var_id, False):
                assignment[var_name] = value
        return assignment


class ConstraintSolver:
    """
    Unified constraint solver.
    """
    
    def __init__(self):
        self.csp = CSPSolver()
        self.sat = SATEncoder()
    
    def solve_csp(self, variables: Dict[str, List[Any]],
                 constraints: List[Tuple[str, str, Callable[[Any, Any], bool]]]) -> Optional[Dict[str, Any]]:
        """
        Solve CSP.
        
        Args:
            variables: var_name -> domain
            constraints: List of (var1, var2, check_fn)
        
        Returns:
            Solution or None
        """
        for name, domain in variables.items():
            self.csp.add_variable(name, domain)
        
        for var1, var2, check in constraints:
            self.csp.add_constraint(var1, var2, check)
        
        # Run arc consistency first
        if not self.csp.arc_consistency():
            return None
        
        return self.csp.solve()
    
    def solver_summary(self) -> Dict:
        """Get solver summary."""
        return {
            "variables": len(self.csp.variables),
            "constraints": len(self.csp.constraints),
            "sat_vars": self.sat.next_var - 1,
            "sat_clauses": len(self.sat.clauses)
        }
