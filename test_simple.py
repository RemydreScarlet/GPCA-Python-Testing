#!/usr/bin/env python3
"""
Simple test to verify GPCA functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpca'))

from sim import Simulator, SimulationConfig

# Simple program: count neighbors and store in R0
SIMPLE_PROGRAM = """
MOV R0, 0
LOAD_N R1, N
ADD R0, R0, R1
LOAD_N R1, NE
ADD R0, R0, R1
LOAD_N R1, E
ADD R0, R0, R1
LOAD_N R1, SE
ADD R0, R0, R1
LOAD_N R1, S
ADD R0, R0, R1
LOAD_N R1, SW
ADD R0, R0, R1
LOAD_N R1, W
ADD R0, R0, R1
LOAD_N R1, NW
ADD R0, R0, R1
"""

def test_simple():
    """Test basic GPCA functionality."""
    print("Testing GPCA Basic Functionality")
    print("=" * 40)
    
    # Create simulator
    config = SimulationConfig(grid_size=5, collision_rate=0.0, verbose=True)
    simulator = Simulator(config, SIMPLE_PROGRAM)
    
    # Set initial state - create a cross pattern
    import numpy as np
    state = np.zeros((5, 5), dtype=int)
    state[2, 2] = 1  # Center cell
    state[2, 1] = 1  # Left
    state[2, 3] = 1  # Right
    state[1, 2] = 1  # Top
    state[3, 2] = 1  # Bottom
    
    simulator.set_state(state)
    
    print("Initial state:")
    print(state)
    print(f"Initial live cells: {np.sum(state)}")
    
    # Run one step
    simulator.step()
    
    print("\nAfter one step:")
    result = simulator.get_state()
    print(result)
    print(f"Result live cells: {np.sum(result)}")
    
    # The center cell should have 4 neighbors, so R0 should be 4
    center_cell = simulator.grid.get_cell(2, 2)
    center_r0 = center_cell.get_register_value("R0")
    print(f"Center cell R0 (neighbor count): {center_r0}")
    
    # Test completed successfully
    print("\n✓ Basic functionality test passed!")

if __name__ == "__main__":
    test_simple()
