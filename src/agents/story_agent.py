# Story Agent - Individual characters that drive the narrative through autonomous interactions

import random
from typing import List, Dict, Optional
from ..utils.text_generation import generate_dialogue, generate_action
from ..utils.memory_management import AgentMemoryInterface

class StoryAgent:
    """
    Individual characters that drive the narrative through autonomous interactions.
    """
    
    def __init__(self, name: str, description: str, personality_traits: List[str], 
                 background: str, starting_location: str, goals: List[str] = None,
                 fears: List[str] = None):
        self.name = name
        self.description = description
        self.personality_traits = personality_traits or []
        self.background = background
        self.location = starting_location
        
        # Motivations and goals
        self.goals = goals or []
        self.fears = fears or []
        
        # Emotional state
        self.current_mood = "neutral"
        self.stress_level = 0.0
        self.energy_level = 1.0
        
        # Interaction state
        self.last_interaction_time = None
        self.interaction_count = 0
        
        # Memory interface (will be set by memory manager)
        self.memory = None
        
        # Simple relationship tracking
        self.relationships = {}  # other_agent_name -> relationship_score (-1 to 1)
    
    def __repr__(self):
        return f"StoryAgent({self.name}, {self.location})"
    
    def set_memory_interface(self, memory_interface: AgentMemoryInterface):
        """Set the memory interface for this agent"""
        self.memory = memory_interface
    
    def should_initiate_interaction(self, other_agents: List['StoryAgent'], current_time: int) -> bool:
        """Determine if this agent wants to initiate an interaction"""
        
        # Don't interact too frequently
        if self.last_interaction_time and current_time - self.last_interaction_time < 2:
            return False
        
        # Higher energy = more likely to interact
        if self.energy_level < 0.3:
            return False
        
        # Check if there are other agents in the same location
        same_location_agents = [agent for agent in other_agents if agent.location == self.location]
        if not same_location_agents:
            return False
        
        # Personality-based probability
        base_probability = 0.3
        if "outgoing" in self.personality_traits or "social" in self.personality_traits:
            base_probability += 0.2
        if "shy" in self.personality_traits or "introverted" in self.personality_traits:
            base_probability -= 0.1
        
        return random.random() < base_probability
    
    def choose_interaction_target(self, available_agents: List['StoryAgent']) -> Optional['StoryAgent']:
        """Choose which agent to interact with"""
        if not available_agents:
            return None
        
        # Simple selection based on relationship scores
        best_target = None
        best_score = -2  # Start below minimum relationship score
        
        for agent in available_agents:
            if agent.name == self.name:
                continue
            
            # Get relationship score (default to 0 for new relationships)
            relationship_score = self.relationships.get(agent.name, 0)
            
            # Add some randomness
            score = relationship_score + random.uniform(-0.3, 0.3)
            
            # Prefer agents we haven't talked to recently
            if agent.last_interaction_time is None:
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_target = agent
        
        return best_target
    
    def initiate_interaction(self, target_agent: 'StoryAgent', environment, current_time: int) -> Dict:
        """Initiate an interaction with another agent"""
        
        # Get other characters in the location
        other_characters = [agent.name for agent in environment.get_agents_at_location(self.location) 
                          if agent.name != self.name]
        
        # Get recent memories for context
        recent_memories = []
        if self.memory:
            memories = self.memory.get_recent_memories(limit=3)
            recent_memories = [mem.get('content', '') for mem in memories]
        
        # Generate dialogue
        situation = f"You are at {self.location} and want to talk to {target_agent.name}"
        dialogue = generate_dialogue(
            self.name, 
            self.description, 
            situation, 
            other_characters,
            recent_memories
        )
        
        # Create interaction data
        interaction_data = {
            'initiator': self.name,
            'target': target_agent.name,
            'location': self.location,
            'time': current_time,
            'type': 'conversation',
            'content': dialogue,
            'participants': [self.name, target_agent.name]
        }
        
        # Update interaction tracking
        self.last_interaction_time = current_time
        self.interaction_count += 1
        
        return interaction_data
    
    def respond_to_interaction(self, interaction_data: Dict, environment, current_time: int) -> str:
        """Respond to an interaction from another agent"""
        
        initiator_name = interaction_data['initiator']
        original_content = interaction_data['content']
        
        # Get other characters in the location
        other_characters = [agent.name for agent in environment.get_agents_at_location(self.location) 
                          if agent.name != self.name]
        
        # Get recent memories for context
        recent_memories = []
        if self.memory:
            memories = self.memory.recall_about_agent(initiator_name, limit=2)
            recent_memories = [mem.get('content', '') for mem in memories]
        
        # Generate response
        situation = f"{initiator_name} just said: '{original_content}'. You are responding."
        response = generate_dialogue(
            self.name,
            self.description,
            situation,
            other_characters,
            recent_memories
        )
        
        # Update interaction tracking
        self.last_interaction_time = current_time
        self.interaction_count += 1
        
        return response
    
    def decide_action(self, environment, current_time: int) -> str:
        """Decide what action to take when not interacting"""
        
        # Get other characters in location
        other_characters = [agent.name for agent in environment.get_agents_at_location(self.location) 
                          if agent.name != self.name]
        
        # Generate action
        action = generate_action(
            self.name,
            self.description,
            self.location,
            self.goals,
            self.current_mood,
            other_characters
        )
        
        return action
    
    def update_relationship(self, other_agent_name: str, interaction_quality: float):
        """Update relationship with another agent based on interaction quality"""
        current_score = self.relationships.get(other_agent_name, 0.0)
        
        # Simple relationship update
        change = interaction_quality * 0.1  # Small incremental changes
        new_score = max(-1.0, min(1.0, current_score + change))
        
        self.relationships[other_agent_name] = new_score
    
    def update_emotional_state(self, interaction_data: Dict = None):
        """Update emotional state based on recent events"""
        
        # Simple mood updates
        if interaction_data:
            # Positive interactions improve mood slightly
            if self.current_mood == "sad":
                self.current_mood = "neutral"
            elif self.current_mood == "neutral" and random.random() < 0.3:
                self.current_mood = "happy"
        
        # Energy decreases over time
        self.energy_level = max(0.1, self.energy_level - 0.05)
        
        # Occasionally restore energy
        if random.random() < 0.1:
            self.energy_level = min(1.0, self.energy_level + 0.3)
    
    def move_to_location(self, new_location: str, environment):
        """Move to a new location"""
        old_location = self.location
        
        # Remove from old location
        if old_location in environment.locations:
            environment.locations[old_location].remove_agent(self)
        
        # Add to new location
        self.location = new_location
        if new_location in environment.locations:
            environment.locations[new_location].add_agent(self)
        
        return True
    
    def get_status_summary(self) -> Dict:
        """Get a summary of the agent's current status"""
        return {
            'name': self.name,
            'location': self.location,
            'mood': self.current_mood,
            'energy': self.energy_level,
            'interaction_count': self.interaction_count,
            'relationships': self.relationships.copy(),
            'goals': self.goals.copy()
        }