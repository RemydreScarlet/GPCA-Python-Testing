#!/usr/bin/env python3
"""
Animated Conway's Game of Life demo for GPCA.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpca'))

from demo.life import GameOfLife

def main():
    """Run animated Game of Life demo."""
    print("GPCA - Animated Conway's Game of Life Demo")
    print("=" * 50)
    
    # Create Game of Life simulation
    life = GameOfLife(grid_size=40)
    
    # Set interesting patterns
    print("Setting up patterns...")
    
    # Add Gosper glider gun (creates gliders)
    try:
        life.set_gosper_glider_gun()
        print("✓ Gosper glider gun set")
    except ValueError as e:
        print(f"Could not set glider gun: {e}")
        # Fallback to multiple gliders
        life.set_glider(5, 5)
        life.set_glider(15, 10)
        life.set_glider(25, 15)
        print("✓ Multiple gliders set")
    
    # Add some static patterns
    life.set_block(30, 30)
    life.set_blinker(20, 20)
    
    print(f"Initial live cells: {life.count_live_cells()}")
    print("\nStarting animation...")
    print("Close the window to exit.")
    
    # Run animated simulation
    life.animate(steps=200, interval=150)
    
    print(f"\nFinal live cells: {life.count_live_cells()}")

if __name__ == "__main__":
    main()
