"""
GPCA - General Purpose Cellular Automaton

A Python simulator for 2D grid-based cellular automaton with GPU-like architecture.
"""

from .sim import Simulator, SimulationConfig
from .core.isa import Opcode, Direction, Instruction, Assembler, VM
from .core.cell import Cell, CellState
from .core.grid import Grid
from .routing.network import Network, AddressedNetwork

__version__ = "1.0.0"
__author__ = "GPCA Team"
__description__ = "General Purpose Cellular Automaton Simulator"

__all__ = [
    "Simulator",
    "SimulationConfig", 
    "Opcode",
    "Direction",
    "Instruction",
    "Assembler",
    "VM",
    "Cell",
    "CellState",
    "Grid",
    "Network",
    "AddressedNetwork",
]
