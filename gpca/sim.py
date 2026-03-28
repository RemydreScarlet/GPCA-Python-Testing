"""
Main simulator for GPCA.

This module provides the main Simulator class that coordinates the grid,
network layer, and execution of the cellular automaton.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass

from core.grid import Grid
from routing.network import Network, AddressedNetwork


@dataclass
class SimulationConfig:
    """Configuration for GPCA simulation."""
    grid_size: int = 50
    collision_rate: float = 0.1
    addressed_network: bool = False
    verbose: bool = False


class Simulator:
    """Main simulator class for GPCA.
    
    Coordinates the grid, network layer, and provides utilities for
    running and visualizing simulations.
    """
    
    def __init__(self, config: SimulationConfig, program: str) -> None:
        """Initialize the simulator.
        
        Args:
            config: Simulation configuration.
            program: Assembly program to run on all cells.
        """
        self.config = config
        self.grid = Grid(config.grid_size, program)
        
        # Initialize network
        if config.addressed_network:
            self.network = AddressedNetwork(config.grid_size, config.collision_rate)
        else:
            self.network = Network(config.grid_size, config.collision_rate)
        
        self.step_count: int = 0
        self.history: List[np.ndarray] = []
        self.running: bool = False
    
    def step(self) -> None:
        """Execute one step of the simulation."""
        # Collect values to send from cells
        send_values = self.grid.collect_send_values()
        
        # Route messages through network
        deliveries = self.network.route_messages(send_values)
        
        # Execute grid step with network messages
        self.grid.step(deliveries)
        
        self.step_count += 1
        
        # Store state in history
        if self.config.verbose:
            self.history.append(self.grid.get_state_array().copy())
    
    def run(self, steps: int, callback: Optional[Callable[[int, np.ndarray], None]] = None) -> None:
        """Run simulation for specified number of steps.
        
        Args:
            steps: Number of steps to run.
            callback: Optional callback function called after each step.
        """
        self.running = True
        
        for i in range(steps):
            if not self.running:
                break
            
            self.step()
            
            if callback is not None:
                callback(i, self.grid.get_state_array())
        
        self.running = False
    
    def run_until_stable(self, max_steps: int = 1000, patience: int = 10) -> int:
        """Run simulation until state stabilizes.
        
        Args:
            max_steps: Maximum number of steps to run.
            patience: Number of steps to wait for stability check.
            
        Returns:
            Number of steps run until stability.
        """
        if len(self.history) < patience:
            # Need to build up history first
            self.run(patience)
        
        for i in range(patience, max_steps):
            self.step()
            
            # Check if state is stable (same as patience steps ago)
            current_state = self.grid.get_state_array()
            old_state = self.history[-patience]
            
            if np.array_equal(current_state, old_state):
                return i - patience + 1
        
        return max_steps
    
    def reset(self) -> None:
        """Reset simulator to initial state."""
        self.grid.reset()
        self.network.reset()
        self.step_count = 0
        self.history = []
        self.running = False
    
    def get_state(self) -> np.ndarray:
        """Get current grid state."""
        return self.grid.get_state_array()
    
    def set_state(self, state: np.ndarray) -> None:
        """Set grid state."""
        self.grid.set_state_array(state)
    
    def get_step_count(self) -> int:
        """Get current step count."""
        return self.step_count
    
    def get_grid_size(self) -> int:
        """Get grid size."""
        return self.config.grid_size
    
    def set_address(self, source: Tuple[int, int], destination: Tuple[int, int]) -> None:
        """Set message routing address (for addressed network).
        
        Args:
            source: Source cell coordinates.
            destination: Destination cell coordinates.
        """
        if isinstance(self.network, AddressedNetwork):
            self.network.set_address(source, destination)
        else:
            raise RuntimeError("Addressed network not enabled")
    
    def get_network_stats(self) -> Dict[str, int]:
        """Get network statistics.
        
        Returns:
            Dictionary with network statistics.
        """
        return {
            "messages_sent": self.network.get_message_count(),
            "timestamp": self.network.timestamp
        }
    
    def visualize(self, title: str = "GPCA Simulation", cmap: str = "viridis") -> None:
        """Visualize current grid state.
        
        Args:
            title: Plot title.
            cmap: Matplotlib colormap.
        """
        state = self.get_state()
        
        plt.figure(figsize=(8, 8))
        plt.imshow(state, cmap=cmap, interpolation='nearest')
        plt.title(f"{title} - Step {self.step_count}")
        plt.colorbar(label="Cell State")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def animate(self, steps: int, interval: int = 100, save_path: Optional[str] = None) -> animation.FuncAnimation:
        """Create animation of simulation.
        
        Args:
            steps: Number of steps to animate.
            interval: Delay between frames in milliseconds.
            save_path: Optional path to save animation.
            
        Returns:
            Matplotlib animation object.
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Initial frame
        state = self.get_state()
        im = ax.imshow(state, cmap='viridis', interpolation='nearest')
        ax.set_title(f"GPCA Simulation - Step 0")
        plt.colorbar(im, ax=ax, label="Cell State")
        
        def update_frame(frame):
            self.step()
            state = self.get_state()
            im.set_array(state)
            ax.set_title(f"GPCA Simulation - Step {self.step_count}")
            return [im]
        
        anim = animation.FuncAnimation(
            fig, update_frame, frames=steps, interval=interval, blit=True
        )
        
        if save_path:
            anim.save(save_path, writer='pillow')
        
        plt.show()
        return anim
    
    def print_state(self) -> None:
        """Print current state to console."""
        state = self.get_state()
        print(f"Step {self.step_count}:")
        print(state)
    
    def print_summary(self) -> None:
        """Print simulation summary."""
        print(f"GPCA Simulation Summary:")
        print(f"  Grid size: {self.config.grid_size}x{self.config.grid_size}")
        print(f"  Steps executed: {self.step_count}")
        print(f"  Network type: {'Addressed' if self.config.addressed_network else 'Random'}")
        print(f"  Collision rate: {self.config.collision_rate}")
        
        stats = self.get_network_stats()
        print(f"  Messages sent: {stats['messages_sent']}")
        
        if self.history:
            print(f"  History size: {len(self.history)} states")
