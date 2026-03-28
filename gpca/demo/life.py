"""
Conway's Game of Life demo for GPCA.

This module implements Conway's Game of Life using the GPCA instruction set.
Each cell follows the classic Life rules based on its 8 neighbors.
"""

from __future__ import annotations
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim import Simulator, SimulationConfig


# Conway's Game of Life rules implemented in GPCA assembly
LIFE_PROGRAM = """
# Conway's Game of Life Implementation
# Each cell uses R0 as its state (0=dead, 1=alive)
# Count living neighbors in R1

# Initialize neighbor count to 0
MOV R1, 0

# Count living neighbors from all 8 directions
LOAD_N R2, N
ADD R1, R1, R2
LOAD_N R2, NE
ADD R1, R1, R2
LOAD_N R2, E
ADD R1, R1, R2
LOAD_N R2, SE
ADD R1, R1, R2
LOAD_N R2, S
ADD R1, R1, R2
LOAD_N R2, SW
ADD R1, R1, R2
LOAD_N R2, W
ADD R1, R1, R2
LOAD_N R2, NW
ADD R1, R1, R2

# Apply Life rules:
# 1. Any live cell with 2 or 3 live neighbors survives
# 2. Any dead cell with exactly 3 live neighbors becomes alive
# 3. All other live cells die, and all other dead cells stay dead

# Check if current cell is alive
MOV R2, R0
JZ R2, checkbirth

# Cell is alive - check survival (2 or 3 neighbors)
MOV R3, 2
SUB R4, R1, R3
JZ R4, survive

MOV R3, 3
SUB R4, R1, R3
JZ R4, survive

# Die (set to 0)
MOV R0, 0
JMP end

survive:
# Stay alive (set to 1)
MOV R0, 1
JMP end

checkbirth:
MOV R3, 3
SUB R4, R1, R3
JZ R4, birth
JMP end
birth:
MOV R0, 1
end:
"""


class GameOfLife:
    """Conway's Game of Life simulation using GPCA."""
    
    def __init__(self, grid_size: int = 50) -> None:
        """Initialize Game of Life.
        
        Args:
            grid_size: Size of the grid (N x N).
        """
        config = SimulationConfig(
            grid_size=grid_size,
            collision_rate=0.0,  # No network needed for Life
            addressed_network=False,
            verbose=True
        )
        
        self.simulator = Simulator(config, LIFE_PROGRAM)
        self.grid_size = grid_size
    
    def set_glider(self, x: int, y: int) -> None:
        """Set a glider pattern at specified position.
        
        Args:
            x: X coordinate of glider top-left.
            y: Y coordinate of glider top-left.
        """
        # Glider pattern
        glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])
        
        state = self.simulator.get_state()
        
        # Place glider
        for dy in range(glider.shape[0]):
            for dx in range(glider.shape[1]):
                px, py = x + dx, y + dy
                if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                    state[py, px] = glider[dy, dx]
        
        self.simulator.set_state(state)
    
    def set_blinker(self, x: int, y: int) -> None:
        """Set a blinker pattern at specified position.
        
        Args:
            x: X coordinate of blinker center.
            y: Y coordinate of blinker center.
        """
        state = self.simulator.get_state()
        
        # Vertical blinker
        if 0 <= x < self.grid_size and 0 <= y-1 < self.grid_size:
            state[y-1, x] = 1
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            state[y, x] = 1
        if 0 <= x < self.grid_size and 0 <= y+1 < self.grid_size:
            state[y+1, x] = 1
        
        self.simulator.set_state(state)
    
    def set_block(self, x: int, y: int) -> None:
        """Set a block pattern at specified position.
        
        Args:
            x: X coordinate of block top-left.
            y: Y coordinate of block top-left.
        """
        state = self.simulator.get_state()
        
        # 2x2 block
        for dy in range(2):
            for dx in range(2):
                px, py = x + dx, y + dy
                if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                    state[py, px] = 1
        
        self.simulator.set_state(state)
    
    def set_random(self, density: float = 0.3) -> None:
        """Set random initial state.
        
        Args:
            density: Probability of a cell being alive.
        """
        state = np.random.random((self.grid_size, self.grid_size)) < density
        self.simulator.set_state(state.astype(int))
    
    def set_gosper_glider_gun(self) -> None:
        """Set Gosper glider gun pattern (requires grid size >= 40)."""
        if self.grid_size < 40:
            raise ValueError("Grid size must be at least 40 for Gosper glider gun")
        
        # Gosper glider gun pattern
        gun = np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ])
        
        state = self.simulator.get_state()
        
        # Place gun in center-left
        start_x = 2
        start_y = 10
        
        for dy in range(gun.shape[0]):
            for dx in range(gun.shape[1]):
                px, py = start_x + dx, start_y + dy
                if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                    state[py, px] = gun[dy, dx]
        
        self.simulator.set_state(state)
    
    def run(self, steps: int = 100, visualize: bool = True, animate: bool = False) -> None:
        """Run Game of Life simulation.
        
        Args:
            steps: Number of steps to run.
            visualize: Whether to show visualization.
            animate: Whether to show animation instead of static plots.
        """
        print(f"Running Conway's Game of Life for {steps} steps...")
        
        if animate:
            # Create animation
            self.animate(steps, interval=200)
            return
        
        if visualize:
            # Show initial state
            self.simulator.visualize("Conway's Game of Life - Initial State")
        
        # Run simulation
        self.simulator.run(steps)
        
        if visualize:
            # Show final state
            self.simulator.visualize("Conway's Game of Life - Final State")
        
        # Print summary
        self.simulator.print_summary()
    
    def animate(self, steps: int = 100, interval: int = 200) -> None:
        """Create animated visualization.
        
        Args:
            steps: Number of steps to animate.
            interval: Delay between frames in milliseconds.
        """
        print(f"Creating animation for {steps} steps...")
        self.simulator.animate(steps, interval)
    
    def count_live_cells(self) -> int:
        """Count number of live cells.
        
        Returns:
            Number of live cells.
        """
        state = self.simulator.get_state()
        return int(np.sum(state))


def main() -> None:
    """Main function to run Game of Life demo."""
    print("GPCA - Conway's Game of Life Demo")
    print("=" * 40)
    
    # Create Game of Life simulation
    life = GameOfLife(grid_size=50)
    
    # Set initial patterns
    print("Setting up initial patterns...")
    
    # Add some gliders
    life.set_glider(5, 5)
    life.set_glider(15, 10)
    life.set_glider(25, 15)
    
    # Add some static patterns
    life.set_block(35, 35)
    life.set_block(40, 40)
    life.set_blinker(30, 30)
    
    # Add some random cells
    life.set_random(density=0.1)
    
    # Show initial state
    print(f"Initial live cells: {life.count_live_cells()}")
    
    # Run simulation with animation
    life.run(steps=100, visualize=False, animate=True)
    
    # Show final state
    print(f"Final live cells: {life.count_live_cells()}")


if __name__ == "__main__":
    main()
