"""
Cell implementation for GPCA.

This module defines the Cell class, which represents a single processing unit
in the cellular automaton grid.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .isa import VM, Instruction, Direction


@dataclass
class CellState:
    """State of a cell that can be shared with neighbors."""
    value: int = 0


class Cell:
    """A single cell in the GPCA grid.
    
    Each cell contains a VM that executes the same program as all other cells,
    but with its own register state and access to neighbor states.
    """
    
    def __init__(self, x: int, y: int, program: List[Instruction], labels: Dict[str, int]) -> None:
        """Initialize a cell.
        
        Args:
            x: X coordinate in the grid.
            y: Y coordinate in the grid.
            program: List of instructions to execute.
            labels: Label mapping for jumps.
        """
        self.x = x
        self.y = y
        self.vm = VM()
        self.vm.load_program(program, labels)
        self.state = CellState()
        self.pending_state: Optional[CellState] = None
        self.received_value: Optional[int] = None
    
    def step(self, neighbor_states: Dict[Direction, CellState], received_value: Optional[int] = None) -> None:
        # 近傍・受信値をVMにセット
        for direction, state in neighbor_states.items():
            self.vm.neighbor_values[direction] = state.value
    
        if received_value is not None:
            self.vm.registers["R8"] = received_value
        else:
            self.vm.registers["R8"] = 0

        # PCをリセットしてプログラムを最初から完走
        self.vm.pc = 0
        self.vm.running = True
        self.vm.sender_value = None
    
        # プログラムを最後まで実行
        while self.vm.running and self.vm.pc < len(self.vm.program):
            self.vm.step()

        # R0の値を次の状態として保存
        self.pending_state = CellState(value=self.vm.registers.get("R0", 0))
        self.sender_value = self.vm.sender_value    
        
    def apply_update(self) -> None:
        """Apply pending state update."""
        if self.pending_state is not None:
            self.state = self.pending_state
            self.pending_state = None
    
    def get_send_value(self) -> Optional[int]:
        """Get value to send via network layer."""
        return getattr(self, 'sender_value', None)
    
    def reset(self) -> None:
        """Reset cell state."""
        self.vm.reset()
        self.state = CellState()
        self.pending_state = None
        self.received_value = None
    
    def get_position(self) -> Tuple[int, int]:
        """Get cell position in grid."""
        return (self.x, self.y)
    
    def get_register_value(self, register: str) -> int:
        """Get current register value."""
        return self.vm.registers.get(register, 0)
    
    def set_register_value(self, register: str, value: int) -> None:
        """Set register value (for debugging/testing)."""
        self.vm.registers[register] = value
