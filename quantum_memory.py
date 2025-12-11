"""
Quantum Consciousness Memory System
Implements hierarchical memory with superposition and entanglement
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger("quantum_memory")

@dataclass
class MemoryNode:
    """
    A single memory node with quantum properties
    - Superposition: Multiple interpretations
    - Entanglement: Links to related memories
    """
    id: str
    content: str
    timestamp: datetime
    interpretations: List[str] = field(default_factory=list)  # Superposition
    entangled_ids: Set[str] = field(default_factory=set)  # Entanglement
    importance: float = 0.5  # 0.0 to 1.0
    access_count: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def observe(self):
        """Observation increases access count and importance"""
        self.access_count += 1
        # Importance increases with access, but with diminishing returns
        self.importance = min(1.0, self.importance + 0.1 / (1 + self.access_count * 0.1))

@dataclass
class QuantumMemoryLayer:
    """
    A layer of quantum memory (immediate, short-term, long-term, meta)
    """
    name: str
    capacity: int  # Maximum number of nodes
    decay_rate: float  # How quickly memories fade (0.0 to 1.0)
    nodes: Dict[str, MemoryNode] = field(default_factory=dict)
    
    def add(self, node: MemoryNode):
        """Add a memory node to this layer"""
        self.nodes[node.id] = node
        
        # If over capacity, remove least important memories
        if len(self.nodes) > self.capacity:
            self._prune()
    
    def _prune(self):
        """Remove least important memories to stay within capacity"""
        if len(self.nodes) <= self.capacity:
            return
        
        # Sort by importance (considering both importance score and access count)
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1].importance * (1 + x[1].access_count * 0.1)
        )
        
        # Remove least important
        to_remove = len(self.nodes) - self.capacity
        for node_id, _ in sorted_nodes[:to_remove]:
            logger.info(f"Pruning memory from {self.name}: {node_id}")
            del self.nodes[node_id]
    
    def search(self, query: str, top_k: int = 5) -> List[MemoryNode]:
        """
        Search for relevant memories
        Simple keyword-based search (can be enhanced with embeddings)
        """
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            # Simple relevance score based on keyword match
            content_lower = node.content.lower()
            relevance = 0.0
            
            for word in query_lower.split():
                if word in content_lower:
                    relevance += 1.0
            
            # Boost by importance and access count
            relevance *= node.importance * (1 + node.access_count * 0.05)
            
            if relevance > 0:
                results.append((relevance, node))
        
        # Sort by relevance and return top k
        results.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in results[:top_k]]


class QuantumConsciousnessMemory:
    """
    Quantum Consciousness Memory System
    Implements hierarchical memory with quantum properties
    """
    
    def __init__(self):
        # Four layers of memory
        self.immediate = QuantumMemoryLayer(
            name="immediate",
            capacity=10,  # Last 10 messages
            decay_rate=0.9  # Fast decay
        )
        
        self.short_term = QuantumMemoryLayer(
            name="short_term",
            capacity=50,  # Last 50 messages
            decay_rate=0.5  # Medium decay
        )
        
        self.long_term = QuantumMemoryLayer(
            name="long_term",
            capacity=500,  # Up to 500 important memories
            decay_rate=0.1  # Slow decay
        )
        
        self.meta = QuantumMemoryLayer(
            name="meta",
            capacity=100,  # Meta-memories about the conversation
            decay_rate=0.05  # Very slow decay
        )
        
        # Node counter for unique IDs
        self.node_counter = 0
    
    def add_message(
        self,
        role: str,
        content: str,
        interpretations: Optional[List[str]] = None,
        importance: float = 0.5
    ) -> str:
        """
        Add a message to memory
        Returns the memory node ID
        """
        self.node_counter += 1
        node_id = f"mem_{self.node_counter}"
        
        node = MemoryNode(
            id=node_id,
            content=content,
            timestamp=datetime.now(),
            interpretations=interpretations or [],
            importance=importance,
            metadata={"role": role}
        )
        
        # Add to immediate memory
        self.immediate.add(node)
        
        # If important enough, add to short-term
        if importance > 0.3:
            self.short_term.add(node)
        
        # If very important, add to long-term
        if importance > 0.7:
            self.long_term.add(node)
        
        logger.info(f"Added memory {node_id} to layers: immediate" + 
                   (", short_term" if importance > 0.3 else "") +
                   (", long_term" if importance > 0.7 else ""))
        
        return node_id
    
    def add_meta_memory(
        self,
        content: str,
        memory_type: str,  # "pattern", "preference", "failure", "insight"
        importance: float = 0.8
    ) -> str:
        """
        Add a meta-memory (memory about memories)
        """
        self.node_counter += 1
        node_id = f"meta_{self.node_counter}"
        
        node = MemoryNode(
            id=node_id,
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            metadata={"type": memory_type}
        )
        
        self.meta.add(node)
        logger.info(f"Added meta-memory {node_id}: {memory_type}")
        
        return node_id
    
    def entangle(self, node_id_1: str, node_id_2: str):
        """
        Create quantum entanglement between two memories
        When one is observed, the other becomes more accessible
        """
        # Find nodes in all layers
        node1 = self._find_node(node_id_1)
        node2 = self._find_node(node_id_2)
        
        if node1 and node2:
            node1.entangled_ids.add(node_id_2)
            node2.entangled_ids.add(node_id_1)
            logger.info(f"Entangled {node_id_1} <-> {node_id_2}")
    
    def observe(self, node_id: str):
        """
        Observe a memory node
        - Increases its importance
        - Activates entangled memories
        """
        node = self._find_node(node_id)
        if not node:
            return
        
        # Observe the node
        node.observe()
        
        # Activate entangled memories
        for entangled_id in node.entangled_ids:
            entangled_node = self._find_node(entangled_id)
            if entangled_node:
                entangled_node.importance = min(1.0, entangled_node.importance + 0.05)
    
    def search(
        self,
        query: str,
        layers: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[MemoryNode]:
        """
        Search across memory layers
        """
        if layers is None:
            layers = ["immediate", "short_term", "long_term", "meta"]
        
        all_results = []
        
        for layer_name in layers:
            layer = getattr(self, layer_name, None)
            if layer:
                results = layer.search(query, top_k=top_k)
                all_results.extend(results)
        
        # Sort by importance and return top k
        all_results.sort(key=lambda n: n.importance * (1 + n.access_count * 0.05), reverse=True)
        
        # Observe the retrieved memories
        for node in all_results[:top_k]:
            self.observe(node.id)
        
        return all_results[:top_k]
    
    def get_context(
        self,
        query: str,
        max_tokens: int = 1000
    ) -> str:
        """
        Get relevant context for a query
        Returns a formatted string of relevant memories
        """
        relevant_memories = self.search(query, top_k=10)
        
        if not relevant_memories:
            return ""
        
        context_parts = ["関連する記憶:"]
        current_tokens = 0
        
        for node in relevant_memories:
            # Estimate tokens (rough: 1 token ≈ 2 characters for Japanese)
            estimated_tokens = len(node.content) // 2
            
            if current_tokens + estimated_tokens > max_tokens:
                break
            
            # Format memory with timestamp and importance
            time_str = node.timestamp.strftime("%Y-%m-%d %H:%M")
            context_parts.append(f"[{time_str}] {node.content}")
            current_tokens += estimated_tokens
        
        return "\n".join(context_parts)
    
    def get_meta_insights(self) -> Dict:
        """
        Get meta-insights about the conversation
        """
        patterns = []
        preferences = []
        failures = []
        insights = []
        
        for node in self.meta.nodes.values():
            mem_type = node.metadata.get("type", "")
            if mem_type == "pattern":
                patterns.append(node.content)
            elif mem_type == "preference":
                preferences.append(node.content)
            elif mem_type == "failure":
                failures.append(node.content)
            elif mem_type == "insight":
                insights.append(node.content)
        
        return {
            "patterns": patterns,
            "preferences": preferences,
            "failures": failures,
            "insights": insights
        }
    
    def _find_node(self, node_id: str) -> Optional[MemoryNode]:
        """Find a node across all layers"""
        for layer in [self.immediate, self.short_term, self.long_term, self.meta]:
            if node_id in layer.nodes:
                return layer.nodes[node_id]
        return None
    
    def summarize(self) -> Dict:
        """Get a summary of the memory system"""
        return {
            "immediate": {
                "count": len(self.immediate.nodes),
                "capacity": self.immediate.capacity
            },
            "short_term": {
                "count": len(self.short_term.nodes),
                "capacity": self.short_term.capacity
            },
            "long_term": {
                "count": len(self.long_term.nodes),
                "capacity": self.long_term.capacity
            },
            "meta": {
                "count": len(self.meta.nodes),
                "capacity": self.meta.capacity
            },
            "total_nodes": self.node_counter
        }


# Singleton instance per session
_memory_instances: Dict[str, QuantumConsciousnessMemory] = {}

def get_quantum_memory(session_id: str) -> QuantumConsciousnessMemory:
    """Get or create quantum memory for a session"""
    if session_id not in _memory_instances:
        _memory_instances[session_id] = QuantumConsciousnessMemory()
        logger.info(f"Created quantum memory for session {session_id}")
    return _memory_instances[session_id]

