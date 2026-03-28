# GPCA (General Purpose Cellular Automaton)

A Python simulator for 2D grid-based cellular automaton with GPU-like architecture. Each cell acts as a small CPU executing the same program in parallel (SIMT-style execution).

## Features

- **2D Grid Architecture**: N×N grid of cells with Moore neighborhood (8 neighbors)
- **Custom ISA**: Minimal instruction set including arithmetic, logic, jumps, and communication
- **Parallel Execution**: All cells execute simultaneously with batch updates
- **Network Layer**: Inter-cell communication with collision detection
- **Visualization**: Built-in plotting and animation capabilities
- **Conway's Game of Life**: Complete demo implementation

## Architecture

### Core Components

- **Cell**: Individual processing unit with registers R0-R7 and VM
- **Grid**: 2D array managing all cells and their interactions
- **ISA**: Instruction set architecture with assembler and VM
- **Network**: Communication layer handling message routing

### Instruction Set

| Instruction | Description |
|-------------|-------------|
| `MOV dst, src` | Copy value from source to destination |
| `ADD dst, src1, src2` | Add two values |
| `SUB dst, src1, src2` | Subtract two values |
| `AND dst, src1, src2` | Bitwise AND |
| `OR dst, src1, src2` | Bitwise OR |
| `XOR dst, src1, src2` | Bitwise XOR |
| `JMP label` | Unconditional jump |
| `JZ dst, label` | Jump if destination is zero |
| `LOAD_N dst, direction` | Load from neighbor (N/NE/E/SE/S/SW/W/NW) |
| `SEND src, address` | Send value via network |

### Registers

- **R0-R7**: General purpose registers
- **R8**: 9th cell register (network input, read-only)
- **SENDER**: Special register for network output

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GPCA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Simulation

```python
from gpca.sim import Simulator, SimulationConfig

# Define your program in GPCA assembly
program = """
MOV R0, 1
LOAD_N R1, N
ADD R0, R0, R1
"""

# Create simulator
config = SimulationConfig(grid_size=50, collision_rate=0.1)
simulator = Simulator(config, program)

# Run simulation
simulator.run(steps=100)

# Visualize
simulator.visualize()
```

### Conway's Game of Life Demo

```bash
cd gpca/demo
python life.py
```

This will run a Game of Life simulation with various patterns (gliders, blinkers, blocks) and show visualization.

### Custom Patterns

```python
from gpca.demo.life import GameOfLife

# Create Game of Life instance
life = GameOfLife(grid_size=50)

# Set specific patterns
life.set_glider(10, 10)
life.set_block(20, 20)
life.set_random(density=0.3)

# Run with animation
life.animate(steps=200, interval=100)
```

## Directory Structure

```
gpca/
├── core/
│   ├── cell.py       # Cell class implementation
│   ├── grid.py       # Grid management
│   └── isa.py        # Instruction set and VM
├── routing/
│   └── network.py    # Network communication layer
├── sim.py            # Main simulator
├── demo/
│   └── life.py       # Conway's Game of Life demo
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Examples

### Simple Counter

```python
program = """
# Increment R0 each step
MOV R1, 1
ADD R0, R0, R1
"""
```

### Neighbor Sum

```python
program = """
# Sum all 8 neighbors into R0
MOV R0, 0
LOAD_N R1, N
ADD R0, R0, R1
LOAD_N R1, NE
ADD R0, R0, R1
# ... continue for all directions
"""
```

## Network Communication

Cells can communicate using the `SEND` instruction and `SENDER` register:

```python
program = """
# Send current state to neighbor
SEND R0, neighbor_address
# Receive from network (available in R8)
MOV R1, R8
```

The network layer handles:
- Message routing between cells
- Collision detection and message dropping
- Configurable collision rates
- Addressed or random routing

## Visualization

The simulator provides several visualization options:

- **Static plots**: `simulator.visualize()`
- **Animation**: `simulator.animate(steps=100)`
- **Console output**: `simulator.print_state()`

## Performance

- Grid size: Configurable (tested up to 100×100)
- Execution: Pure Python (suitable for educational purposes)
- Memory: O(N²) for grid state storage
- Network: O(M) where M is number of messages per step

## Extending GPCA

### Adding New Instructions

1. Update `Opcode` enum in `core/isa.py`
2. Add parsing logic in `Assembler._parse_line()`
3. Implement execution in `VM._execute_instruction()`

### Custom Network Layers

Create new network classes by extending the base `Network` class:

```python
class CustomNetwork(Network):
    def route_messages(self, send_values):
        # Your custom routing logic
        pass
```

## Requirements

- Python 3.11+
- numpy >= 1.21.0
- matplotlib >= 3.5.0

## License

This project is provided for educational and research purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the simulator.

## Future Enhancements

- GPU acceleration with CUDA/OpenCL
- More complex network topologies
- Additional instruction set features
- Performance optimizations
- Web-based visualization interface
