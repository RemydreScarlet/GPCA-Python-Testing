"""
Network layer for GPCA communication.

This module implements the communication layer that handles message routing
between cells in the grid.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import random


@dataclass
class Message:
    """Message sent between cells."""
    source: Tuple[int, int]
    destination: Tuple[int, int]
    value: int
    timestamp: int


class Network:
    """Network layer for inter-cell communication.
    
    Handles message routing with collision detection and dropping.
    Messages are delivered on a best-effort basis.
    """
    
    def __init__(self, grid_size: int, collision_rate: float = 0.1) -> None:
        """Initialize network.
        
        Args:
            grid_size: Size of the grid (N x N).
            collision_rate: Probability of collision when multiple messages target same cell.
        """
        self.grid_size = grid_size
        self.collision_rate = collision_rate
        self.timestamp: int = 0
        self.message_buffer: List[Message] = []
        self.delivery_log: List[Tuple[int, Message]] = []
    
    def route_messages(self, send_values: Dict[Tuple[int, int], int]) -> Dict[Tuple[int, int], int]:
        """Route messages from senders to receivers.
        
        Args:
            send_values: Dictionary mapping source positions to values to send.
            
        Returns:
            Dictionary mapping destination positions to received values.
        """
        # Create messages from send values
        messages = []
        for (x, y), value in send_values.items():
            # For now, assume messages are sent to random neighbors
            # In a more complex implementation, addresses would be specified
            destination = self._get_random_destination(x, y)
            message = Message(
                source=(x, y),
                destination=destination,
                value=value,
                timestamp=self.timestamp
            )
            messages.append(message)
        
        # Simulate network collisions
        delivered_messages = self._handle_collisions(messages)
        
        # Convert delivered messages to delivery dictionary
        deliveries = {}
        for message in delivered_messages:
            deliveries[message.destination] = message.value
            self.delivery_log.append((self.timestamp, message))
        
        self.timestamp += 1
        return deliveries
    
    def _get_random_destination(self, source_x: int, source_y: int) -> Tuple[int, int]:
        """Get a random destination for a message (neighbor of source).
        
        Args:
            source_x: Source X coordinate.
            source_y: Source Y coordinate.
            
        Returns:
            Random neighbor coordinates.
        """
        # Moore neighborhood offsets
        offsets = [
            (0, -1), (1, -1), (1, 0), (1, 1),
            (0, 1), (-1, 1), (-1, 0), (-1, -1)
        ]
        
        # Filter valid neighbors (within bounds)
        valid_neighbors = []
        for dx, dy in offsets:
            nx, ny = source_x + dx, source_y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                valid_neighbors.append((nx, ny))
        
        if valid_neighbors:
            return random.choice(valid_neighbors)
        else:
            # No valid neighbors (isolated cell), send to self
            return (source_x, source_y)
    
    def _handle_collisions(self, messages: List[Message]) -> List[Message]:
        """Handle network collisions by dropping messages.
        
        Args:
            messages: List of messages to route.
            
        Returns:
            List of messages that were successfully delivered.
        """
        # Group messages by destination
        destination_groups: Dict[Tuple[int, int], List[Message]] = {}
        for message in messages:
            if message.destination not in destination_groups:
                destination_groups[message.destination] = []
            destination_groups[message.destination].append(message)
        
        delivered_messages = []
        
        for destination, msg_list in destination_groups.items():
            if len(msg_list) == 1:
                # No collision, deliver the message
                delivered_messages.append(msg_list[0])
            else:
                # Multiple messages targeting same destination
                if random.random() < self.collision_rate:
                    # Collision occurred, drop all messages
                    pass
                else:
                    # No collision, deliver one randomly chosen message
                    delivered_messages.append(random.choice(msg_list))
        
        return delivered_messages
    
    def get_delivery_log(self) -> List[Tuple[int, Message]]:
        """Get log of all delivered messages.
        
        Returns:
            List of (timestamp, message) tuples.
        """
        return self.delivery_log.copy()
    
    def get_message_count(self) -> int:
        """Get total number of messages processed.
        
        Returns:
            Total message count.
        """
        return len(self.delivery_log)
    
    def reset(self) -> None:
        """Reset network state."""
        self.timestamp = 0
        self.message_buffer = []
        self.delivery_log = []
    
    def set_collision_rate(self, rate: float) -> None:
        """Set collision rate for the network.
        
        Args:
            rate: Collision probability (0.0 to 1.0).
        """
        if not 0.0 <= rate <= 1.0:
            raise ValueError("Collision rate must be between 0.0 and 1.0")
        self.collision_rate = rate


class AddressedNetwork(Network):
    """Extended network that supports addressed messages.
    
    Allows cells to specify exact destination addresses instead of
    random neighbor routing.
    """
    
    def __init__(self, grid_size: int, collision_rate: float = 0.1) -> None:
        """Initialize addressed network."""
        super().__init__(grid_size, collision_rate)
        self.addressed_messages: Dict[Tuple[int, int], Tuple[int, int]] = {}
    
    def set_address(self, source: Tuple[int, int], destination: Tuple[int, int]) -> None:
        """Set destination address for a source cell.
        
        Args:
            source: Source cell coordinates.
            destination: Destination cell coordinates.
        """
        self.addressed_messages[source] = destination
    
    def route_messages(self, send_values: Dict[Tuple[int, int], int]) -> Dict[Tuple[int, int], int]:
        """Route messages using specified addresses.
        
        Args:
            send_values: Dictionary mapping source positions to values to send.
            
        Returns:
            Dictionary mapping destination positions to received values.
        """
        # Create messages from send values using addresses
        messages = []
        for (x, y), value in send_values.items():
            source = (x, y)
            if source in self.addressed_messages:
                destination = self.addressed_messages[source]
            else:
                # Fallback to random destination
                destination = self._get_random_destination(x, y)
            
            message = Message(
                source=source,
                destination=destination,
                value=value,
                timestamp=self.timestamp
            )
            messages.append(message)
        
        # Handle collisions
        delivered_messages = self._handle_collisions(messages)
        
        # Convert to delivery dictionary
        deliveries = {}
        for message in delivered_messages:
            deliveries[message.destination] = message.value
            self.delivery_log.append((self.timestamp, message))
        
        self.timestamp += 1
        return deliveries
    
    def clear_addresses(self) -> None:
        """Clear all address mappings."""
        self.addressed_messages.clear()
