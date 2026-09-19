"""
Chaos Engineering Module
Chaos experiments, resilience validation, and
systematic disruption testing.
"""

import time
import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class ExperimentStatus(Enum):
    """Status of a chaos experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class ExperimentResult:
    """Result of a chaos experiment."""
    experiment_id: str
    status: ExperimentStatus
    duration_ms: float = 0.0
    steady_state_met: bool = False
    failures_observed: int = 0
    recoveries_observed: int = 0
    logs: List[str] = field(default_factory=list)


class SteadyStateMonitor:
    """
    Monitor system steady state conditions.
    """
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], bool]] = {}
        self.metrics: Dict[str, List[Tuple[float, float]]] = {}
    
    def add_check(self, name: str, check_fn: Callable[[], bool]):
        """Add a steady state check."""
        self.checks[name] = check_fn
    
    def add_metric(self, name: str, threshold: Tuple[float, float]):
        """
        Add metric with acceptable range.
        
        Args:
            name: Metric name
            threshold: (min, max) acceptable range
        """
        self.metrics[name] = [threshold]
    
    def record_metric(self, name: str, value: float, timestamp: float = 0.0):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append((timestamp, value))
    
    def verify(self) -> Dict:
        """
        Verify all steady state conditions.
        
        Returns:
            Verification result
        """
        results = {}
        all_pass = True
        
        # Check conditions
        for name, check_fn in self.checks.items():
            try:
                passed = check_fn()
            except Exception:
                passed = False
            results[name] = passed
            if not passed:
                all_pass = False
        
        # Check metrics
        for name, readings in self.metrics.items():
            if not readings:
                continue
            threshold = readings[0] if isinstance(readings[0], tuple) else (0, float('inf'))
            if isinstance(readings[0], tuple) and len(readings) > 1:
                recent = [v for _, v in readings[-5:]]
                avg = sum(recent) / len(recent)
                passed = threshold[0] <= avg <= threshold[1]
                results[f"metric:{name}"] = passed
                if not passed:
                    all_pass = False
        
        return {
            "all_pass": all_pass,
            "checks": results
        }


class ChaosExperiment:
    """
    A single chaos experiment.
    """
    
    def __init__(self, experiment_id: str,
                 description: str = "",
                 duration_s: float = 60.0):
        """
        Args:
            experiment_id: Unique ID
            description: Experiment description
            duration_s: Experiment duration
        """
        self.experiment_id = experiment_id
        self.description = description
        self.duration_s = duration_s
        self.status = ExperimentStatus.PENDING
        self.monitor = SteadyStateMonitor()
        self.result: Optional[ExperimentResult] = None
        self.disruption_actions: List[Callable[[], None]] = []
        self.rollback_actions: List[Callable[[], None]] = []
    
    def add_disruption(self, action: Callable[[], None]):
        """Add a disruption action."""
        self.disruption_actions.append(action)
    
    def add_rollback(self, action: Callable[[], None]):
        """Add rollback action."""
        self.rollback_actions.append(action)
    
    def run(self) -> ExperimentResult:
        """
        Execute the experiment.
        
        Returns:
            Experiment result
        """
        self.status = ExperimentStatus.RUNNING
        start_time = time.time()
        
        result = ExperimentResult(
            experiment_id=self.experiment_id,
            status=ExperimentStatus.RUNNING
        )
        
        # Verify steady state before
        pre_check = self.monitor.verify()
        result.steady_state_met = pre_check["all_pass"]
        result.logs.append(f"Pre-check: {'PASS' if pre_check['all_pass'] else 'FAIL'}")
        
        if not pre_check["all_pass"]:
            self.status = ExperimentStatus.ABORTED
            result.status = ExperimentStatus.ABORTED
            result.logs.append("Aborted: steady state not met")
            self.result = result
            return result
        
        # Apply disruptions
        try:
            for action in self.disruption_actions:
                action()
                result.logs.append("Disruption applied")
                
                # Check during disruption
                during_check = self.monitor.verify()
                if not during_check["all_pass"]:
                    result.failures_observed += 1
                    result.logs.append("Failure observed during disruption")
                else:
                    result.recoveries_observed += 1
            
            # Rollback
            for action in self.rollback_actions:
                action()
                result.logs.append("Rollback applied")
            
            # Verify steady state after
            post_check = self.monitor.verify()
            if post_check["all_pass"]:
                result.recoveries_observed += 1
                result.logs.append("System recovered")
            else:
                result.failures_observed += 1
                result.logs.append("System did not recover")
            
            result.duration_ms = (time.time() - start_time) * 1000
            result.status = ExperimentStatus.COMPLETED
            self.status = ExperimentStatus.COMPLETED
            
        except Exception as e:
            result.status = ExperimentStatus.FAILED
            self.status = ExperimentStatus.FAILED
            result.logs.append(f"Exception: {str(e)}")
        
        self.result = result
        return result


class ChaosEngine:
    """
    Chaos engineering engine.
    
    Manages and executes chaos experiments.
    """
    
    def __init__(self):
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.experiment_history: List[ExperimentResult] = []
        self.rng = random.Random()
    
    def create_experiment(self, experiment_id: str,
                         description: str = "",
                         duration_s: float = 60.0) -> ChaosExperiment:
        """
        Create a new experiment.
        
        Args:
            experiment_id: Unique ID
            description: Description
            duration_s: Duration
        
        Returns:
            ChaosExperiment
        """
        exp = ChaosExperiment(experiment_id, description, duration_s)
        self.experiments[experiment_id] = exp
        return exp
    
    def run_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """
        Run an experiment.
        
        Args:
            experiment_id: Experiment ID
        
        Returns:
            Result or None
        """
        if experiment_id not in self.experiments:
            return None
        
        result = self.experiments[experiment_id].run()
        self.experiment_history.append(result)
        return result
    
    def run_all(self) -> List[ExperimentResult]:
        """Run all pending experiments."""
        results = []
        for exp_id, exp in self.experiments.items():
            if exp.status == ExperimentStatus.PENDING:
                result = exp.run()
                results.append(result)
                self.experiment_history.append(result)
        return results
    
    def get_resilience_score(self) -> float:
        """
        Calculate overall resilience score.
        
        Returns:
            Score 0.0-1.0
        """
        if not self.experiment_history:
            return 0.0
        
        completed = [r for r in self.experiment_history
                    if r.status == ExperimentStatus.COMPLETED]
        
        if not completed:
            return 0.0
        
        total = len(completed)
        recovered = sum(1 for r in completed if r.recoveries_observed > 0)
        
        return recovered / total
    
    def get_experiment_stats(self) -> Dict:
        """Get experiment statistics."""
        total = len(self.experiment_history)
        completed = sum(1 for r in self.experiment_history
                       if r.status == ExperimentStatus.COMPLETED)
        failed = sum(1 for r in self.experiment_history
                    if r.status == ExperimentStatus.FAILED)
        aborted = sum(1 for r in self.experiment_history
                     if r.status == ExperimentStatus.ABORTED)
        
        total_failures = sum(r.failures_observed for r in self.experiment_history)
        total_recoveries = sum(r.recoveries_observed for r in self.experiment_history)
        
        return {
            "total_experiments": total,
            "completed": completed,
            "failed": failed,
            "aborted": aborted,
            "resilience_score": round(self.get_resilience_score(), 2),
            "total_failures_observed": total_failures,
            "total_recoveries_observed": total_recoveries
        }
    
    def engine_summary(self) -> Dict:
        """Get engine summary."""
        return {
            "experiments_defined": len(self.experiments),
            "experiments_run": len(self.experiment_history),
            "resilience_score": round(self.get_resilience_score(), 2),
            "stats": self.get_experiment_stats()
        }
