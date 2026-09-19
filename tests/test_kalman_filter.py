"""
Unit tests for Extended Kalman Filter module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kalman_filter import (
    ExtendedKalmanFilter, EKFState, MatrixOps, OrbitEKF
)


class TestMatrixOps(unittest.TestCase):
    """Test matrix operations."""
    
    def test_identity(self):
        """Should create identity matrix."""
        I = MatrixOps.identity(3)
        self.assertEqual(I[0][0], 1.0)
        self.assertEqual(I[0][1], 0.0)
        self.assertEqual(I[2][2], 1.0)
        print("  [PASS] Identity matrix")
    
    def test_mat_mult(self):
        """Should multiply matrices."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = MatrixOps.mat_mult(A, B)
        self.assertEqual(C[0][0], 19)
        self.assertEqual(C[1][1], 50)
        print("  [PASS] Matrix multiplication")
    
    def test_mat_transpose(self):
        """Should transpose matrix."""
        A = [[1, 2, 3], [4, 5, 6]]
        AT = MatrixOps.mat_transpose(A)
        self.assertEqual(AT[0][1], 4)
        self.assertEqual(AT[2][1], 6)
        print("  [PASS] Matrix transpose")
    
    def test_invert_2x2(self):
        """Should invert 2x2 matrix."""
        A = [[4, 7], [2, 6]]
        inv = MatrixOps.invert_2x2(A)
        self.assertIsNotNone(inv)
        # Check A * A^-1 = I
        I = MatrixOps.mat_mult(A, inv)
        self.assertAlmostEqual(I[0][0], 1.0, delta=0.01)
        self.assertAlmostEqual(I[1][1], 1.0, delta=0.01)
        print("  [PASS] 2x2 inversion")
    
    def test_invert_3x3(self):
        """Should invert 3x3 matrix."""
        A = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
        inv = MatrixOps.invert_3x3(A)
        self.assertIsNotNone(inv)
        I = MatrixOps.mat_mult(A, inv)
        self.assertAlmostEqual(I[0][0], 1.0, delta=0.01)
        self.assertAlmostEqual(I[2][2], 1.0, delta=0.01)
        print("  [PASS] 3x3 inversion")


class TestExtendedKalmanFilter(unittest.TestCase):
    """Test EKF."""
    
    def setUp(self):
        self.ekf = ExtendedKalmanFilter(state_dim=2, measurement_dim=1)
    
    def test_predict_constant_velocity(self):
        """Should predict state forward."""
        state = EKFState(x=[0.0, 1.0], P=[[1.0, 0.0], [0.0, 1.0]])
        
        def f(x):
            return [x[0] + x[1], x[1]]  # Constant velocity
        
        pred = self.ekf.predict(state, f, dt=1.0)
        self.assertAlmostEqual(pred.x[0], 1.0, delta=0.01)
        self.assertAlmostEqual(pred.x[1], 1.0, delta=0.01)
        print(f"  [PASS] Predict: x={pred.x}")
    
    def test_update_position(self):
        """Should update state with measurement."""
        state = EKFState(x=[0.0, 1.0], P=[[10.0, 0.0], [0.0, 1.0]])
        
        def f(x):
            return [x[0] + x[1], x[1]]
        
        pred = self.ekf.predict(state, f, dt=1.0)
        
        def h(x):
            return [x[0]]  # Observe position
        
        updated = self.ekf.update(pred, [2.0], h, R=[[0.1]])
        # Should move toward measurement
        self.assertGreater(updated.x[0], pred.x[0])
        print(f"  [PASS] Update: x={updated.x}")
    
    def test_full_cycle(self):
        """Should complete predict-update cycle."""
        state = EKFState(x=[0.0, 1.0], P=[[1.0, 0.0], [0.0, 1.0]])
        
        for t in range(5):
            def f(x):
                return [x[0] + x[1], x[1]]
            
            state = self.ekf.predict(state, f, dt=1.0)
            
            def h(x):
                return [x[0]]
            
            measurement = [float(t + 1) + 0.1]  # Noisy measurement
            state = self.ekf.update(state, measurement, h, R=[[0.5]])
        
        self.assertIsNotNone(state)
        self.assertEqual(len(state.x), 2)
        print(f"  [PASS] Full cycle: x={state.x}")


class TestOrbitEKF(unittest.TestCase):
    """Test orbital EKF."""
    
    def setUp(self):
        self.ekf = OrbitEKF()
    
    def test_state_transition(self):
        """Should propagate orbital state."""
        x = [7000.0, 0.0, 0.0, 0.0, 7.5, 0.0]  # LEO-ish
        x_new = self.ekf.state_transition(x, 1.0)
        self.assertEqual(len(x_new), 6)
        self.assertNotEqual(x_new[0], x[0])  # Position changed
        print(f"  [PASS] Propagation: pos=({x_new[0]:.1f}, {x_new[1]:.1f}, {x_new[2]:.1f})")
    
    def test_position_observation(self):
        """Should extract position from state."""
        x = [7000.0, 1000.0, 500.0, 1.0, 2.0, 3.0]
        pos = self.ekf.position_observation(x)
        self.assertEqual(pos, [7000.0, 1000.0, 500.0])
        print("  [PASS] Position observation")
    
    def test_initialize(self):
        """Should initialize filter state."""
        state = self.ekf.initialize(
            position_km=[7000.0, 0.0, 0.0],
            velocity_km_s=[0.0, 7.5, 0.0],
            pos_sigma_km=1.0
        )
        self.assertEqual(len(state.x), 6)
        self.assertEqual(len(state.P), 6)
        self.assertEqual(len(state.P[0]), 6)
        print("  [PASS] Initialization")
    
    def test_filter_step_position(self):
        """Should run full filter step with position measurement."""
        state = self.ekf.initialize(
            position_km=[7000.0, 0.0, 0.0],
            velocity_km_s=[0.0, 7.5, 0.0]
        )
        
        # Simulate measurement slightly offset
        measurement = [7000.2, 0.1, 0.0]
        state_new = self.ekf.filter_step(
            state, dt_s=1.0, measurement=measurement,
            measurement_type="position"
        )
        
        self.assertIsNotNone(state_new)
        self.assertEqual(len(state_new.x), 6)
        print(f"  [PASS] Filter step: pos=({state_new.x[0]:.2f}, {state_new.x[1]:.2f}, {state_new.x[2]:.2f})")
    
    def test_filter_convergence(self):
        """Should converge to true state."""
        # True state
        true_pos = [7000.0, 1000.0, 500.0]
        true_vel = [1.0, 7.0, 0.5]
        
        # Initialize with error
        state = self.ekf.initialize(
            position_km=[7100.0, 1100.0, 600.0],  # 100km error
            velocity_km_s=[1.5, 7.5, 1.0],
            pos_sigma_km=100.0
        )
        
        # Run multiple filter steps with perfect measurements
        for _ in range(10):
            state = self.ekf.filter_step(
                state, dt_s=1.0,
                measurement=true_pos[:],
                measurement_type="position",
                R=[[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
            )
        
        # Position should be closer to true
        pos_error = math.sqrt(sum((state.x[i] - true_pos[i])**2 for i in range(3)))
        self.assertLess(pos_error, 50.0)  # Less than 50km error
        print(f"  [PASS] Convergence: error={pos_error:.2f} km")


if __name__ == '__main__':
    unittest.main(verbosity=2)
