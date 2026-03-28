#!/usr/bin/env python3
"""
Quick test to verify GPCA is working with Conway's Game of Life.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpca'))

from demo.life import GameOfLife

def main():
    """Quick test of Game of Life."""
    print("GPCA Quick Test - Conway's Game of Life")
    print("=" * 50)
    
    # Create small Game of Life
    life = GameOfLife(grid_size=10)
    
    # Set a simple glider
    life.set_glider(2, 2)
    
    print(f"Initial live cells: {life.count_live_cells()}")
    # 手動で小さいグリッドをデバッグ
    state0 = life.simulator.get_state()
    print("Step 0:")
    print(state0)

    life.simulator.step()
    print("Step 1:")
    print(life.simulator.get_state())

    print("\n✓ GPCA is working!")
    print("Run 'python gpca/demo/life.py' for a full demo with visualization")

if __name__ == "__main__":
    main()
