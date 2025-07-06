# Memory Management - Integration with mem0 for agent memories

from typing import Dict, List, Optional, Any
from datetime import datetime
from src.config.settings import settings

try:
    from mem0 import MemoryClient
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    MemoryClient = None

class MemoryManager:
    """
    Handles memory management for story agents using mem0
    """
    
    def __init__(self, config: Optional[Dict] = None):
        # Store config for reference (though MemoryClient doesn't use it directly)
        self.config = config or {}
        
        if not MEM0_AVAILABLE:
            raise ImportError(
                "mem0ai library is required for memory management. "
                "Please install it with: pip install mem0ai"
            )
        
        # Check for MEM0_API_KEY
        if not settings.MEM0_API_KEY:
            raise RuntimeError(
                "MEM0_API_KEY is required for mem0 MemoryClient. "
                "Please set MEM0_API_KEY in your .env file. "
                "Get your API key from https://app.mem0.ai/"
            )
        
        try:
            # Initialize MemoryClient with API key
            self.memory = MemoryClient(api_key=settings.MEM0_API_KEY)
            print("✅ Memory system initialized with mem0 MemoryClient")
            print(f"   Using managed mem0 service")
        except Exception as e:
            print(f"❌ Failed to initialize mem0 MemoryClient: {e}")
            print(f"   Please check:")
            print(f"   1. MEM0_API_KEY is set correctly in your .env file")
            print(f"   2. mem0ai is installed: pip install mem0ai")
            print(f"   3. Your mem0 API key is valid")
            print(f"   4. You have internet connectivity")
            raise RuntimeError(f"mem0 MemoryClient initialization failed: {e}")
        
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
                memory_content,
                user_id=agent_id,
                metadata=memory_data
            )
            # Handle different response formats from mem0
            if isinstance(result, dict):
                memory_id = result.get('id', f"{agent_id}_{self.memory_counter}")
            else:
                memory_id = f"{agent_id}_{self.memory_counter}"
            return memory_id
        except Exception as e:
            raise RuntimeError(f"Error adding memory to mem0: {e}")
    
    def get_memories(self, agent_id: str, memory_type: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """Retrieve memories for a specific agent"""
        
        try:
            # Use mem0 to retrieve memories
            memories = self.memory.get_all(user_id=agent_id, limit=limit)
            
            # Filter by type if specified
            if memory_type:
                filtered_memories = []
                for m in memories:
                    if isinstance(m, dict):
                        metadata = m.get('metadata', {})
                        if isinstance(metadata, dict) and metadata.get('type') == memory_type:
                            filtered_memories.append(m)
                memories = filtered_memories
            
            return memories
        except Exception as e:
            raise RuntimeError(f"Error retrieving memories from mem0: {e}")
    
    def search_memories(self, agent_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Search memories for a specific agent using semantic search"""
        
        try:
            # Use mem0's search functionality
            results = self.memory.search(query, user_id=agent_id, limit=limit)
            return results
        except Exception as e:
            raise RuntimeError(f"Error searching memories: {e}")
    
    def get_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of an agent's memory statistics"""
        try:
            memories = self.get_memories(agent_id, limit=100)  # Get recent memories
            
            memory_types = {}
            for memory in memories:
                if isinstance(memory, dict):
                    metadata = memory.get('metadata', {})
                    if isinstance(metadata, dict):
                        mem_type = metadata.get('type', 'unknown')
                        memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            return {
                'total_memories': len(memories),
                'memory_types': memory_types,
                'sample_size': min(len(memories), 100)
            }
        except Exception as e:
            raise RuntimeError(f"Could not get memory summary for {agent_id}: {e}")
    
    def to_dict(self) -> Dict:
        """Serialize the memory manager to a dictionary"""
        return {
            'config': self.config,
            'memory_counter': self.memory_counter,
            'api_key_configured': bool(settings.MEM0_API_KEY)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryManager':
        """Reconstruct a memory manager from a dictionary"""
        memory_manager = cls(data['config'])
        memory_manager.memory_counter = data.get('memory_counter', 0)
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
        
        try:
            return self.memory_manager.add_memory(
                self.agent_id, 
                memory_content, 
                'interaction', 
                metadata
            )
        except Exception as e:
            raise RuntimeError(f"Failed to remember interaction for {self.agent_id}: {e}")
    
    def remember_observation(self, observation: str, location: str) -> str:
        """Remember an observation about the environment"""
        memory_content = f"Observed at {location}: {observation}"
        metadata = {'location': location}
        
        try:
            return self.memory_manager.add_memory(
                self.agent_id,
                memory_content,
                'observation',
                metadata
            )
        except Exception as e:
            raise RuntimeError(f"Failed to remember observation for {self.agent_id}: {e}")
    
    def remember_thought(self, thought: str) -> str:
        """Remember an internal thought or reflection"""
        try:
            return self.memory_manager.add_memory(
                self.agent_id,
                thought,
                'thought'
            )
        except Exception as e:
            raise RuntimeError(f"Failed to remember thought for {self.agent_id}: {e}")
    
    def recall_about_agent(self, other_agent_name: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific agent"""
        query = f"interaction with {other_agent_name}"
        try:
            return self.memory_manager.search_memories(self.agent_id, query, limit)
        except Exception as e:
            raise RuntimeError(f"Failed to recall memories about {other_agent_name} for {self.agent_id}: {e}")
    
    def recall_about_location(self, location: str, limit: int = 5) -> List[Dict]:
        """Recall memories about a specific location"""
        query = f"at {location}"
        try:
            return self.memory_manager.search_memories(self.agent_id, query, limit)
        except Exception as e:
            raise RuntimeError(f"Failed to recall memories about {location} for {self.agent_id}: {e}")
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get the most recent memories"""
        try:
            return self.memory_manager.get_memories(self.agent_id, limit=limit)
        except Exception as e:
            raise RuntimeError(f"Failed to get recent memories for {self.agent_id}: {e}")
    
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
            raise RuntimeError(f"Failed to get emotional memories for {self.agent_id}: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of this agent's memories"""
        try:
            return self.memory_manager.get_memory_summary(self.agent_id)
        except Exception as e:
            raise RuntimeError(f"Failed to get memory summary for {self.agent_id}: {e}")