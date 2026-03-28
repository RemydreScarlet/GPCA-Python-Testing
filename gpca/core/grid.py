"""
Grid implementation for GPCA.

This module defines the Grid class, which manages the 2D array of cells
and coordinates their execution.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import numpy as np

from .cell import Cell, CellState
from .isa import Instruction, Direction, Assembler


class Grid:
    """2D grid of cells for GPCA simulation.
    
    Manages the spatial arrangement of cells and provides methods for
    coordinated execution and neighbor access.
    """
    
    def __init__(self, size: int, program: str) -> None:
        """Initialize the grid.
        
        Args:
            size: Grid size (N x N).
            program: Assembly program to run on all cells.
        """
        self.size = size
        self.cells: List[List[Cell]] = []
        self.ticks: int = 0
        
        # Parse program
        assembler = Assembler()
        self.instructions = assembler.parse(program)
        self.labels = assembler.labels
        
        # Initialize cells
        self._initialize_cells()
    
    def _initialize_cells(self) -> None:
        """Initialize all cells in the grid."""
        for y in range(self.size):
            row: List[Cell] = []
            for x in range(self.size):
                cell = Cell(x, y, self.instructions, self.labels)
                row.append(cell)
            self.cells.append(row)
    
    def get_neighbor_states(self, x: int, y: int) -> Dict[Direction, CellState]:
        """Get states of all 8 neighbors for a cell.
        
        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.
            
        Returns:
            Dictionary mapping directions to neighbor states.
            Missing neighbors (at edges) return state with value 0.
        """
        neighbors = {}
        
        # Define neighbor offsets for Moore neighborhood
        offsets = {
            Direction.N: (0, -1),
            Direction.NE: (1, -1),
            Direction.E: (1, 0),
            Direction.SE: (1, 1),
            Direction.S: (0, 1),
            Direction.SW: (-1, 1),
            Direction.W: (-1, 0),
            Direction.NW: (-1, -1),
        }
        
        for direction, (dx, dy) in offsets.items():
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors[direction] = CellState(value=self.cells[ny][nx].state.value)
            else:
                # Out of bounds - return zero state
                neighbors[direction] = CellState(value=0)
        
        return neighbors
    
    def step(self, network_messages: Optional[Dict[Tuple[int, int], int]] = None) -> None:
        """Execute one tick of the simulation.
        
        All cells execute one step simultaneously, then updates are applied.
        
        Args:
            network_messages: Dictionary of messages to deliver to cells.
        """
        if network_messages is None:
            network_messages = {}
        
        # Step 1: Execute all cells
        for y in range(self.size):
            for x in range(self.size):
                cell = self.cells[y][x]
                neighbor_states = self.get_neighbor_states(x, y)
                received_value = network_messages.get((x, y))
                cell.step(neighbor_states, received_value)
        
        # Step 2: Apply all updates
        for y in range(self.size):
            for x in range(self.size):
                self.cells[y][x].apply_update()
        
        self.ticks += 1
    
    def get_state_array(self) -> np.ndarray:
        """Get current state of all cells as numpy array.
        
        Returns:
            N x N array of cell states.
        """
        state_array = np.zeros((self.size, self.size), dtype=int)
        for y in range(self.size):
            for x in range(self.size):
                state_array[y, x] = self.cells[y][x].state.value
        return state_array
    
    def set_state_array(self, state_array: np.ndarray) -> None:
        """Set state of all cells from numpy array.
        
        Args:
            state_array: N x N array of cell states.
        """
        if state_array.shape != (self.size, self.size):
            raise ValueError(f"State array shape {state_array.shape} doesn't match grid size {self.size}x{self.size}")
        
        for y in range(self.size):
            for x in range(self.size):
                self.cells[y][x].state.value = int(state_array[y, x])
    
    def get_cell(self, x: int, y: int) -> Cell:
        """Get cell at position.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            Cell at the specified position.
        """
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise IndexError(f"Cell position ({x}, {y}) out of bounds")
        
        return self.cells[y][x]
    
    def collect_send_values(self) -> Dict[Tuple[int, int], int]:
        """Collect values to send from all cells.
        
        Returns:
            Dictionary mapping cell positions to values they want to send.
        """
        send_values = {}
        for y in range(self.size):
            for x in range(self.size):
                value = self.cells[y][x].get_send_value()
                if value is not None:
                    send_values[(x, y)] = value
        return send_values
    
    def reset(self) -> None:
        """Reset all cells to initial state."""
        for y in range(self.size):
            for x in range(self.size):
                self.cells[y][x].reset()
        self.ticks = 0
    
    def get_size(self) -> int:
        """Get grid size."""
        return self.size
    
    def get_ticks(self) -> int:
        """Get number of ticks executed."""
        return self.ticks
