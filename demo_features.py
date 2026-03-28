#!/usr/bin/env python3
"""
GPCA Feature Demonstration
Shows various capabilities of the GPCA simulator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpca'))

from sim import Simulator, SimulationConfig
import numpy as np

def demo_basic_operations():
    """Demonstrate basic arithmetic operations."""
    print("=" * 60)
    print("DEMO 1: Basic Arithmetic Operations")
    print("=" * 60)
    
    program = """
# Initialize R0 with value 5
MOV R0, 5
# Add 3 to get 8
ADD R0, R0, 3
# Subtract 2 to get 6
SUB R0, R0, 2
# Multiply by 4 using repeated addition (no MUL instruction)
MOV R1, 0
ADD R1, R1, R0
ADD R1, R1, R0
ADD R1, R1, R0
ADD R1, R1, R0
MOV R0, R1
"""
    
    config = SimulationConfig(grid_size=3, collision_rate=0.0)
    simulator = Simulator(config, program)
    
    print("Running arithmetic operations...")
    simulator.run(steps=5)
    
    # Check result
    cell = simulator.grid.get_cell(1, 1)
    result = cell.get_register_value("R0")
    print(f"Expected result: 24 (5 + 3 - 2) * 4 = 24")
    print(f"Actual result: {result}")
    print(f"✓ {'PASS' if result == 24 else 'FAIL'}")

def demo_neighbor_access():
    """Demonstrate neighbor state access."""
    print("\n" + "=" * 60)
    print("DEMO 2: Neighbor State Access")
    print("=" * 60)
    
    program = """
# Count all living neighbors
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
    
    config = SimulationConfig(grid_size=5, collision_rate=0.0)
    simulator = Simulator(config, program)
    
    # Create a pattern where center cell has 8 neighbors
    state = np.zeros((5, 5), dtype=int)
    for i in range(5):
        for j in range(5):
            if i != 2 or j != 2:  # All cells except center
                state[i, j] = 1
    
    simulator.set_state(state)
    print("Initial state (center cell surrounded by 8 neighbors):")
    print(state)
    
    simulator.step()
    
    center_cell = simulator.grid.get_cell(2, 2)
    neighbor_count = center_cell.get_register_value("R0")
    print(f"Center cell neighbor count: {neighbor_count}")
    print(f"✓ {'PASS' if neighbor_count == 8 else 'FAIL'}")

def demo_conditional_logic():
    """Demonstrate conditional jumps."""
    print("\n" + "=" * 60)
    print("DEMO 3: Conditional Logic")
    print("=" * 60)
    
    program = """
# Set R0 to 5
MOV R0, 5
# Check if R0 equals 5
MOV R1, 5
SUB R2, R0, R1
JZ equal_branch, R2

# Not equal branch
MOV R0, 0
JMP end

equal_branch:
# Equal branch
MOV R0, 1

end:
# End of program
"""
    
    config = SimulationConfig(grid_size=3, collision_rate=0.0)
    simulator = Simulator(config, program)
    
    print("Testing conditional jump with R0 = 5...")
    simulator.run(steps=5)
    
    cell = simulator.grid.get_cell(1, 1)
    result = cell.get_register_value("R0")
    print(f"Expected result: 1 (equal branch taken)")
    print(f"Actual result: {result}")
    print(f"✓ {'PASS' if result == 1 else 'FAIL'}")

def demo_bitwise_operations():
    """Demonstrate bitwise operations."""
    print("\n" + "=" * 60)
    print("DEMO 4: Bitwise Operations")
    print("=" * 60)
    
    program = """
# Test bitwise AND: 5 & 3 = 1 (101 & 011 = 001)
MOV R0, 5
MOV R1, 3
AND R0, R0, R1

# Test bitwise OR: 5 | 3 = 7 (101 | 011 = 111)
MOV R2, 5
MOV R3, 3
OR R2, R2, R3

# Test bitwise XOR: 5 ^ 3 = 6 (101 ^ 011 = 110)
MOV R4, 5
MOV R5, 3
XOR R4, R4, R5
"""
    
    config = SimulationConfig(grid_size=3, collision_rate=0.0)
    simulator = Simulator(config, program)
    
    print("Testing bitwise operations...")
    simulator.run(steps=5)
    
    cell = simulator.grid.get_cell(1, 1)
    
    and_result = cell.get_register_value("R0")
    or_result = cell.get_register_value("R2")
    xor_result = cell.get_register_value("R4")
    
    print(f"5 AND 3 = {and_result} (expected: 1)")
    print(f"5 OR 3 = {or_result} (expected: 7)")
    print(f"5 XOR 3 = {xor_result} (expected: 6)")
    
    success = (and_result == 1 and or_result == 7 and xor_result == 6)
    print(f"✓ {'PASS' if success else 'FAIL'}")

def demo_network_communication():
    """Demonstrate basic network communication."""
    print("\n" + "=" * 60)
    print("DEMO 5: Network Communication")
    print("=" * 60)
    
    program = """
# Send current state to network
SEND R0, 0
# Store received value in R1
MOV R1, R8
"""
    
    config = SimulationConfig(grid_size=3, collision_rate=0.0)
    simulator = Simulator(config, program)
    
    # Set initial state
    state = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
    simulator.set_state(state)
    
    print("Initial state:")
    print(state)
    
    simulator.step()
    
    print("After network step:")
    result = simulator.get_state()
    print(result)
    
    # Check network stats
    stats = simulator.get_network_stats()
    print(f"Messages sent: {stats['messages_sent']}")
    print("✓ Network communication demo completed")

def main():
    """Run all demonstrations."""
    print("GPCA (General Purpose Cellular Automaton) Feature Demonstration")
    print("This showcases the simulator's capabilities:")
    print("- Arithmetic operations")
    print("- Neighbor state access")
    print("- Conditional logic")
    print("- Bitwise operations")
    print("- Network communication")
    
    demo_basic_operations()
    demo_neighbor_access()
    demo_conditional_logic()
    demo_bitwise_operations()
    demo_network_communication()
    
    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETED")
    print("=" * 60)
    print("The GPCA simulator is fully functional!")
    print("Try running: python gpca/demo/life.py for Conway's Game of Life")

if __name__ == "__main__":
    main()
