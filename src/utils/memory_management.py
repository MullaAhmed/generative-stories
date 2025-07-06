# Memory Management - Simple fallback memory system without external dependencies

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

class SimpleMemoryStore:
    """
    Simple in-memory storage for agent memories without external dependencies
    """
    
    def __init__(self, storage_path: str = "data/memories"):
        self.storage_path = storage_path
        self.memories = {}  # agent_id -> list of memories
        self.memory_counter = 0
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Try to load existing memories
        self.load_memories()
    
    def add_memory(self, agent_id: str, content: str, metadata: Dict = None) -> str:
        """Add a memory for an agent"""
        self.memory_counter += 1
        memory_id = f"{agent_id}_{self.memory_counter}"
        
        memory = {
            'id': memory_id,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        if agent_id not in self.memories:
            self.memories[agent_id] = []
        
        self.memories[agent_id].append(memory)
        
        # Keep only last 100 memories per agent to prevent memory bloat
        if len(self.memories[agent_id]) > 100:
            self.memories[agent_id] = self.memories[agent_id][-100:]
        
        return memory_id
    
    def get_memories(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get recent memories for an agent"""
        if agent_id not in self.memories:
            return []
        
        # Return most recent memories first
        return self.memories[agent_id][-limit:][::-1]
    
    def search_memories(self, agent_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Simple text search in memories"""
        if agent_id not in self.memories:
            return []
        
        query_lower = query.lower()
        matching_memories = []
        
        for memory in self.memories[agent_id]:
            if query_lower in memory['content'].lower():
                matching_memories.append(memory)
        
        # Return most recent matches first
        return matching_memories[-limit:][::-1]
    
    def save_memories(self):
        """Save memories to disk"""
        try:
            memory_file = os.path.join(self.storage_path, "agent_memories.json")
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'memories': self.memories,
                    'memory_counter': self.memory_counter
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memories: {e}")
    
    def load_memories(self):
        """Load memories from disk"""
        try:
            memory_file = os.path.join(self.storage_path, "agent_memories.json")
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = data.get('memories', {})
                    self.memory_counter = data.get('memory_counter', 0)
        except Exception as e:
            print(f"Warning: Could not load memories: {e}")
            self.memories = {}
            self.memory_counter = 0

class MemoryManager:
    """
    Handles memory management for story agents using simple fallback system
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        print("🧠 Using simple fallback memory system (mem0 not available)")
        
        # Initialize simple memory store
        storage_path = self.config.get('storage_path', 'data/memories')
        self.memory_store = SimpleMemoryStore(storage_path)
        
        self.agent_memories = {}  # agent_id -> memory_data
        self.memory_counter = 0
    
    def add_memory(self, agent_id: str, memory_content: str, 
                   memory_type: str = "interaction", metadata: Optional[Dict] = None) -> str:
        """Add a memory for a specific agent"""
        
        self.memory_counter += 1
        memory_data = {
            'content': memory_content,
            'type': memory_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Use simple memory store
        memory_id = self.memory_store.add_memory(agent_id, memory_content, memory_data)
        
        # Update local tracking
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = []
        
        self.agent_memories[agent_id].append({
            'id': memory_id,
            'content': memory_content,
            'type': memory_type,
            'timestamp': memory_data['timestamp'],
            'metadata': metadata or {}
        })
        
        # Keep only recent memories in local tracking
        if len(self.agent_memories[agent_id]) > 50:
            self.agent_memories[agent_id] = self.agent_memories[agent_id][-50:]
        
        return memory_id
    
    def get_memories(self, agent_id: str, memory_type: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """Retrieve memories for a specific agent"""
        
        memories = self.memory_store.get_memories(agent_id, limit * 2)  # Get more to filter
        
        # Filter by type if specified
        if memory_type:
            memories = [m for m in memories if m.get('metadata', {}).get('type') == memory_type]
        
        return memories[:limit]
    
    def search_memories(self, agent_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Search memories for a specific agent using simple text search"""
        return self.memory_store.search_memories(agent_id, query, limit)
    
    def get_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of an agent's memory statistics"""
        try:
            memories = self.get_memories(agent_id, limit=1000)  # Get all memories
            
            memory_types = {}
            for memory in memories:
                mem_type = memory.get('metadata', {}).get('type', 'unknown')
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            return {
                'total_memories': len(memories),
                'memory_types': memory_types,
                'oldest_memory': memories[-1].get('timestamp') if memories else None,
                'newest_memory': memories[0].get('timestamp') if memories else None
            }
        except Exception as e:
            print(f"Warning: Could not get memory summary for {agent_id}: {e}")
            return {
                'total_memories': 0,
                'memory_types': {},
                'oldest_memory': None,
                'newest_memory': None
            }
    
    def save_all_memories(self):
        """Save all memories to disk"""
        self.memory_store.save_memories()
    
    def to_dict(self) -> Dict:
        """Serialize the memory manager to a dictionary"""
        return {
            'config': self.config,
            'agent_memories': self.agent_memories.copy(),
            'memory_counter': self.memory_counter,
            'memory_store_data': {
                'memories': self.memory_store.memories.copy(),
                'memory_counter': self.memory_store.memory_counter
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryManager':
        """Reconstruct a memory manager from a dictionary"""
        memory_manager = cls(data['config'])
        
        # Restore state
        memory_manager.agent_memories = data.get('agent_memories', {})
        memory_manager.memory_counter = data.get('memory_counter', 0)
        
        # Restore memory store data
        store_data = data.get('memory_store_data', {})
        if store_data:
            memory_manager.memory_store.memories = store_data.get('memories', {})
            memory_manager.memory_store.memory_counter = store_data.get('memory_counter', 0)
        
        return memory_manager


class AgentMemoryInterface:
    """High-level interface for agents to interact with their memories"""
    
    def __init__(self, agent_id: str, memory_manager: MemoryManager):
        self.agent_id = agent_id
        self.memory_manager = memory_manager
    
    def remember_interaction(self, other_agent_name: str, interaction_content: str, 
                           location: str, emotional_impact: float = 0.0) -> str:
        """Remember an interaction with another agent"""
        memory_content = f"Interaction with {other_agent_name} at {location}: {interaction_content}"
        metadata = {
            'other_agent': other_agent_name,
            'location': location,
            'emotional_impact': emotional_impact,
            'type': 'interaction'
        }
        
        try:
            return self.memory_manager.add_memory(
                self.agent_id, 
                memory_content, 
                'interaction', 
                metadata
            )
        except Exception as e:
            print(f"Warning: Could not store interaction memory for {self.agent_id}: {e}")
            return f"failed_{self.agent_id}_{datetime.now().timestamp()}"
    
    def remember_observation(self, observation: str, location: str) -> str:
        """Remember an observation about the environment"""
        memory_content = f"Observed at {location}: {observation}"
        metadata = {
            'location': location,
            'type': 'observation'
        }
        
        try:
            return self.memory_manager.add_memory(
                self.agent_id,
                memory_content,
                'observation',
                metadata
            )
        except Exception as e:
            print(f"Warning: Could not store observation memory for {self.agent_id}: {e}")
            return f"failed_{self.agent_id}_{datetime.now().timestamp()}"
    
    def remember_thought(self, thought: str) -> str:
        """Remember an internal thought or reflection"""
        try:
            return self.memory_manager.add_memory(
                self.agent_id,
                thought,
                'thought',
                {'type': 'thought'}
            )
        except Exception as e:
            print(f"Warning: Could not store thought memory for {self.agent_id}: {e}")
            return f"failed_{self.agent_id}_{datetime.now().timestamp()}"
    
    def recall_about_agent(self, other_agent_name: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific agent"""
        query = f"interaction with {other_agent_name}"
        try:
            return self.memory_manager.search_memories(self.agent_id, query, limit)
        except Exception as e:
            print(f"Warning: Could not recall memories about {other_agent_name} for {self.agent_id}: {e}")
            return []
    
    def recall_about_location(self, location: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific location"""
        query = f"at {location}"
        try:
            return self.memory_manager.search_memories(self.agent_id, query, limit)
        except Exception as e:
            print(f"Warning: Could not recall memories about {location} for {self.agent_id}: {e}")
            return []
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get the most recent memories"""
        try:
            return self.memory_manager.get_memories(self.agent_id, limit=limit)
        except Exception as e:
            print(f"Warning: Could not get recent memories for {self.agent_id}: {e}")
            return []
    
    def get_emotional_memories(self, limit: int = 5) -> List[Dict]:
        """Get memories with high emotional impact"""
        try:
            all_memories = self.memory_manager.get_memories(self.agent_id, limit=50)
            
            # Filter for memories with high emotional impact
            emotional_memories = []
            for memory in all_memories:
                emotional_impact = memory.get('metadata', {}).get('emotional_impact', 0)
                if abs(emotional_impact) > 0.5:  # High emotional impact threshold
                    emotional_memories.append(memory)
            
            return emotional_memories[:limit]
        except Exception as e:
            print(f"Warning: Could not get emotional memories for {self.agent_id}: {e}")
            return []
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of this agent's memories"""
        try:
            return self.memory_manager.get_memory_summary(self.agent_id)
        except Exception as e:
            print(f"Warning: Could not get memory summary for {self.agent_id}: {e}")
            return {
                'total_memories': 0,
                'memory_types': {},
                'oldest_memory': None,
                'newest_memory': None,
                'error': str(e)
            }