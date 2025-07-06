# Memory Management - Integration with mem0 for agent memories

from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None

class MemoryManager:
    """
    Handles memory management for story agents using mem0
    """
    
    def __init__(self, config: Optional[Dict] = None):
        # Load mem0 config from file if no config provided
        if config is None:
            try:
                import os
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mem0_config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        import json
                        self.config = json.load(f)
                        print(f"✅ Loaded mem0 config from: {config_path}")
                else:
                    # Fallback to simple config
                    self.config = {
                        "vector_store": {
                            "provider": "chroma",
                            "config": {
                                "collection_name": "generative_stories_memories",
                                "path": "data/memories"
                            }
                        }
                    }
                    print("⚠️ Using fallback mem0 config (config file not found)")
            except Exception as e:
                print(f"Warning: Could not load mem0 config, using defaults: {e}")
                self.config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "generative_stories_memories",
                            "path": "data/memories"
                        }
                    }
                }
        else:
            self.config = config
        
        if not MEM0_AVAILABLE:
            raise ImportError(
                "mem0ai library is required for memory management. "
                "Please install it with: pip install mem0ai"
            )
        
        # Validate OpenAI API key for mem0
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for mem0 Memory class. "
                "Please set OPENAI_API_KEY in your .env file. "
                "mem0ai requires OpenAI API key for embeddings and LLM operations."
            )
        
        try:
            # Initialize mem0 with configuration
            self.memory = Memory(config=self.config)
            print("✅ Memory system initialized with mem0ai")
            print(f"   Vector store: {self.config.get('vector_store', {}).get('provider', 'unknown')}")
            print(f"   LLM provider: {self.config.get('llm', {}).get('provider', 'openai (default)')}")
            print(f"   Embedder: {self.config.get('embedder', {}).get('provider', 'openai (default)')}")
        except Exception as e:
            # Try with minimal config as fallback
            try:
                print(f"Warning: Primary mem0 config failed ({e}), trying minimal config...")
                minimal_config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "generative_stories_memories"
                        }
                    }
                }
                self.memory = Memory(config=minimal_config)
                print("✅ Memory system initialized with minimal mem0ai config")
                self.config = minimal_config
            except Exception as e2:
                print(f"❌ Failed to initialize mem0ai with both primary and minimal configs.")
                print(f"   Primary error: {e}")
                print(f"   Minimal error: {e2}")
                print(f"   Please check:")
                print(f"   1. OPENAI_API_KEY is set in your .env file")
                print(f"   2. mem0ai is installed: pip install mem0ai")
                print(f"   3. Your OpenAI API key has sufficient credits")
                raise RuntimeError(f"mem0ai initialization failed. See details above.")
        
        self.memory_counter = 0
    
    def add_memory(self, agent_id: str, memory_content: str, 
                   memory_type: str = "interaction", metadata: Optional[Dict] = None) -> str:
        """Add a memory for a specific agent"""
        
        self.memory_counter += 1
        memory_data = {
            'type': memory_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        try:
            # Use mem0 to store the memory - wrap content in messages format
            messages = [{"role": "user", "content": memory_content}]
            result = self.memory.add(
                messages=messages,
                user_id=agent_id,
                metadata=memory_data
            )
            memory_id = result.get('id', f"{agent_id}_{self.memory_counter}")
            return memory_id
        except Exception as e:
            raise RuntimeError(f"Error adding memory to mem0: {e}")
    
    def get_memories(self, agent_id: str, memory_type: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """Retrieve memories for a specific agent"""
        
        try:
            # Use mem0 to retrieve memories
            memories = self.memory.get_all(user_id=agent_id)
            
            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m.get('metadata', {}).get('type') == memory_type]
            
            # Apply limit by slicing
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
            raise RuntimeError(f"Could not get memory summary for {agent_id}: {e}")
    
    def to_dict(self) -> Dict:
        """Serialize the memory manager to a dictionary"""
        return {
            'config': self.config,
            'memory_counter': self.memory_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryManager':
        """Reconstruct a memory manager from a dictionary"""
        memory_manager = cls(data['config'])
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