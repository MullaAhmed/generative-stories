# Memory Management - Integration with mem0 for agent memories

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False

class MemoryManager:
    """
    Handles memory management for story agents using mem0
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        if not MEM0_AVAILABLE:
            raise ImportError("mem0 library is required for memory management. Please install it with: pip install mem0")
        
        try:
            # Initialize mem0 with configuration
            self.memory = Memory(config=self.config)
            print("✅ Using mem0 for memory management")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize mem0: {e}")
        
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
        
        try:
            # Use mem0 to store the memory
            result = self.memory.add(
                messages=[{"role": "user", "content": memory_content}],
                user_id=agent_id,
                metadata=memory_data
            )
            memory_id = result.get('id', f"{agent_id}_{self.memory_counter}")
        except Exception as e:
            raise RuntimeError(f"Error adding memory to mem0: {e}")
        
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
        
        return memory_id
    
    def get_memories(self, agent_id: str, memory_type: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """Retrieve memories for a specific agent"""
        
        try:
            # Use mem0 to retrieve memories
            memories = self.memory.get_all(user_id=agent_id)
            
            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m.get('metadata', {}).get('type') == memory_type]
            
            return memories[:limit]
        except Exception as e:
            raise RuntimeError(f"Error retrieving memories from mem0: {e}")
    
    def search_memories(self, agent_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Search memories for a specific agent using semantic search"""
        
        try:
            # Use mem0's search functionality
            results = self.memory.search(
                query=query,
                user_id=agent_id,
                limit=limit
            )
            return results
        except Exception as e:
            raise RuntimeError(f"Error searching memories: {e}")
    
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
                'oldest_memory': memories[-1].get('metadata', {}).get('timestamp') if memories else None,
                'newest_memory': memories[0].get('metadata', {}).get('timestamp') if memories else None
            }
        except Exception as e:
            print(f"Warning: Could not get memory summary for {agent_id}: {e}")
            return {
                'total_memories': 0,
                'memory_types': {},
                'oldest_memory': None,
                'newest_memory': None
            }
    
    def to_dict(self) -> Dict:
        """Serialize the memory manager to a dictionary"""
        return {
            'config': self.config,
            'agent_memories': self.agent_memories.copy(),
            'memory_counter': self.memory_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryManager':
        """Reconstruct a memory manager from a dictionary"""
        memory_manager = cls(data['config'])
        
        # Restore state
        memory_manager.agent_memories = data['agent_memories']
        memory_manager.memory_counter = data['memory_counter']
        
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
            'emotional_impact': emotional_impact
        }
        
        return self.memory_manager.add_memory(
            self.agent_id, 
            memory_content, 
            'interaction', 
            metadata
        )
    
    def remember_observation(self, observation: str, location: str) -> str:
        """Remember an observation about the environment"""
        memory_content = f"Observed at {location}: {observation}"
        metadata = {'location': location}
        
        return self.memory_manager.add_memory(
            self.agent_id,
            memory_content,
            'observation',
            metadata
        )
    
    def remember_thought(self, thought: str) -> str:
        """Remember an internal thought or reflection"""
        return self.memory_manager.add_memory(
            self.agent_id,
            thought,
            'thought'
        )
    
    def recall_about_agent(self, other_agent_name: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific agent"""
        query = f"interaction with {other_agent_name}"
        return self.memory_manager.search_memories(self.agent_id, query, limit)
    
    def recall_about_location(self, location: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific location"""
        query = f"at {location}"
        return self.memory_manager.search_memories(self.agent_id, query, limit)
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get the most recent memories"""
        return self.memory_manager.get_memories(self.agent_id, limit=limit)
    
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
        return self.memory_manager.get_memory_summary(self.agent_id)