"""
Instruction Set Architecture (ISA) for GPCA.

This module defines the instruction set and parsing utilities for the GPCA simulator.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


class Opcode(Enum):
    """Instruction opcodes for GPCA."""
    MOV = "MOV"
    ADD = "ADD"
    SUB = "SUB"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    JMP = "JMP"
    JZ = "JZ"
    LOAD_N = "LOAD_N"
    SEND = "SEND"


class Direction(Enum):
    """Direction constants for LOAD_N instruction."""
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


@dataclass
class Instruction:
    """Single instruction in the GPCA ISA."""
    opcode: Opcode
    operands: List[Union[str, int]]
    
    def __str__(self) -> str:
        return f"{self.opcode.value} {', '.join(map(str, self.operands))}"


class Assembler:
    """Assembler for GPCA assembly language."""
    
    def __init__(self) -> None:
        self.labels: Dict[str, int] = {}
    
    def parse(self, program: str) -> List[Instruction]:
        """Parse assembly program into instruction list."""
        lines = program.strip().split('\n')
        instructions: List[Instruction] = []
        
        # First pass: collect labels
        pc = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.endswith(':'):
                label = line[:-1]
                self.labels[label] = pc
            else:
                pc += 1
        
        # Second pass: parse instructions
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.endswith(':'):
                continue
            
            instruction = self._parse_line(line)
            instructions.append(instruction)
        
        return instructions
    
    def _parse_line(self, line: str) -> Instruction:
        """Parse a single line of assembly."""
        parts = line.split()
        if not parts:
            raise ValueError(f"Empty instruction line: {line}")
        
        opcode_str = parts[0].upper()
        try:
            opcode = Opcode(opcode_str)
        except ValueError:
            raise ValueError(f"Unknown opcode: {opcode_str}")
        
        operands = []
        for part in parts[1:]:
            # Remove commas
            part = part.replace(',', '')
            
            # Check if it's a register (R0-R7 or SENDER)
            if part.startswith('R') and part[1:].isdigit():
                operands.append(part)
            elif part == 'SENDER':
                operands.append(part)
            # Check if it's a direction
            elif part in [d.value for d in Direction]:
                operands.append(Direction(part))
            # Check if it's a label (for JMP/JZ)
            elif opcode in [Opcode.JMP, Opcode.JZ] and part.isalpha():
                operands.append(part)
            # Otherwise, treat as integer literal
            else:
                try:
                    operands.append(int(part))
                except ValueError:
                    operands.append(part)  # Keep as string (label)
        
        return Instruction(opcode, operands)


class VM:
    """Virtual Machine for executing GPCA instructions."""
    
    def __init__(self) -> None:
        self.registers: Dict[str, int] = {f"R{i}": 0 for i in range(8)}
        self.pc: int = 0
        self.program: List[Instruction] = []
        self.labels: Dict[str, int] = {}
        self.running: bool = True
        self.sender_value: Optional[int] = None
        self.neighbor_values: Dict[Direction, int] = {d: 0 for d in Direction}
    
    def load_program(self, program: List[Instruction], labels: Dict[str, int]) -> None:
        """Load program into VM."""
        self.program = program
        self.labels = labels
        self.pc = 0
        self.running = True
    
    def step(self) -> None:
        """Execute one instruction."""
        if not self.running or self.pc >= len(self.program):
            self.running = False
            return
        
        instruction = self.program[self.pc]
        self._execute_instruction(instruction)
        
        # Auto-increment PC unless it was modified by jump
        if instruction.opcode not in [Opcode.JMP, Opcode.JZ]:
            self.pc += 1
    
    def _execute_instruction(self, instruction: Instruction) -> None:
        """Execute a single instruction."""
        opcode = instruction.opcode
        operands = instruction.operands
        
        if opcode == Opcode.MOV:
            dst, src = operands
            self.registers[dst] = self._get_value(src)
        
        elif opcode == Opcode.ADD:
            dst, src1, src2 = operands
            self.registers[dst] = self._get_value(src1) + self._get_value(src2)
        
        elif opcode == Opcode.SUB:
            dst, src1, src2 = operands
            self.registers[dst] = self._get_value(src1) - self._get_value(src2)
        
        elif opcode == Opcode.AND:
            dst, src1, src2 = operands
            self.registers[dst] = self._get_value(src1) & self._get_value(src2)
        
        elif opcode == Opcode.OR:
            dst, src1, src2 = operands
            self.registers[dst] = self._get_value(src1) | self._get_value(src2)
        
        elif opcode == Opcode.XOR:
            dst, src1, src2 = operands
            self.registers[dst] = self._get_value(src1) ^ self._get_value(src2)
        
        elif opcode == Opcode.JMP:
            label = operands[0]
            self.pc = self.labels[label]
        
        elif opcode == Opcode.JZ:
            dst, label = operands
            if self._get_value(dst) == 0:
                if label in self.labels:
                    self.pc = self.labels[label]
                else:
                    # Check if it's actually a register (malformed instruction)
                    if label.startswith('R') and label[1:].isdigit():
                        self.pc += 1
                    else:
                        raise ValueError(f"Label not found: {label}")
            else:
                self.pc += 1
        
        elif opcode == Opcode.LOAD_N:
            dst, direction = operands
            self.registers[dst] = self.neighbor_values[direction]
        
        elif opcode == Opcode.SEND:
            src, address = operands
            self.sender_value = self._get_value(src)
            # Address is handled by the network layer
    
    def _get_value(self, operand: Union[str, int]) -> int:
        """Get value from operand (register or immediate)."""
        if isinstance(operand, (int, float)) or hasattr(operand, '__index__'):
            return int(operand)
        elif isinstance(operand, str) and operand in self.registers:
            return int(self.registers[operand])
        elif isinstance(operand, str) and operand.startswith('R') and operand[1:].isdigit():
            return int(self.registers.get(operand, 0))
        else:
            return 0
    
    def reset(self) -> None:
        """Reset VM state."""
        self.registers = {f"R{i}": 0 for i in range(8)}
        self.pc = 0
        self.running = True
        self.sender_value = None
        self.neighbor_values = {d: 0 for d in Direction}
