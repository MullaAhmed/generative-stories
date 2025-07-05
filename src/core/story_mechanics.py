# Story Mechanics - Logic for autonomous interactions, relationship development, and core story rules

class RelationshipManager:
    """Manages relationships between story agents"""
    
    RELATIONSHIP_STAGES = {
        'stranger': 0,
        'acquaintance': 1,
        'developing': 2,
        'established': 3,
        'complex': 4
    }
    
    def __init__(self):
        self.relationships = {}  # (agent1, agent2) -> relationship_data
    
    def get_relationship(self, agent1, agent2):
        """Get relationship data between two agents"""
        key = tuple(sorted([agent1.name, agent2.name]))
        return self.relationships.get(key, self.create_new_relationship(agent1, agent2))
    
    def create_new_relationship(self, agent1, agent2):
        """Create a new relationship between two agents"""
        relationship = {
            'stage': 'stranger',
            'trust_level': 0,
            'affection_level': 0,
            'interaction_count': 0,
            'shared_experiences': [],
            'conflicts': [],
            'secrets_shared': 0,
            'last_interaction': None
        }
        key = tuple(sorted([agent1.name, agent2.name]))
        self.relationships[key] = relationship
        return relationship
    
    def update_relationship(self, agent1, agent2, interaction_data):
        """Update relationship based on interaction"""
        relationship = self.get_relationship(agent1, agent2)
        
        # Update interaction count
        relationship['interaction_count'] += 1
        relationship['last_interaction'] = interaction_data.get('time')
        
        # Analyze interaction for relationship effects
        interaction_quality = self.analyze_interaction_quality(interaction_data)
        
        # Update trust and affection based on interaction
        relationship['trust_level'] += interaction_quality.get('trust_change', 0)
        relationship['affection_level'] += interaction_quality.get('affection_change', 0)
        
        # Check for stage progression
        self.check_relationship_progression(relationship)
        
        return relationship
    
    def analyze_interaction_quality(self, interaction_data):
        """Analyze an interaction to determine its effect on relationships"""
        # This would use LLM to analyze the interaction content
        # For now, return a simple random effect
        import random
        return {
            'trust_change': random.uniform(-0.1, 0.2),
            'affection_change': random.uniform(-0.1, 0.2),
            'emotional_impact': random.choice(['positive', 'neutral', 'negative'])
        }
    
    def check_relationship_progression(self, relationship):
        """Check if relationship should progress to next stage"""
        current_stage = relationship['stage']
        
        # Simple progression logic based on interaction count and levels
        if (relationship['interaction_count'] >= 5 and 
            relationship['trust_level'] > 0.5 and 
            current_stage == 'stranger'):
            relationship['stage'] = 'acquaintance'
        
        elif (relationship['interaction_count'] >= 10 and 
              relationship['trust_level'] > 1.0 and 
              current_stage == 'acquaintance'):
            relationship['stage'] = 'developing'
        
        # Add more progression logic as needed


class InteractionTriggerSystem:
    """Determines when and why agents should interact"""
    
    def __init__(self):
        self.trigger_types = [
            'proximity_based',
            'goal_driven',
            'emotional_seeking',
            'interest_alignment',
            'unfinished_business'
        ]
    
    def should_agents_interact(self, agent1, agent2, environment, relationship_manager):
        """Determine if two agents should interact"""
        triggers = []
        
        # Check proximity-based triggers
        if self.check_proximity_trigger(agent1, agent2, environment):
            triggers.append('proximity_based')
        
        # Check goal-driven triggers
        if self.check_goal_driven_trigger(agent1, agent2):
            triggers.append('goal_driven')
        
        # Check emotional seeking triggers
        if self.check_emotional_trigger(agent1, agent2):
            triggers.append('emotional_seeking')
        
        # Check interest alignment triggers
        if self.check_interest_alignment_trigger(agent1, agent2):
            triggers.append('interest_alignment')
        
        # Check unfinished business triggers
        relationship = relationship_manager.get_relationship(agent1, agent2)
        if self.check_unfinished_business_trigger(agent1, agent2, relationship):
            triggers.append('unfinished_business')
        
        return len(triggers) > 0, triggers
    
    def check_proximity_trigger(self, agent1, agent2, environment):
        """Check if agents are in proximity and likely to interact"""
        return agent1.location == agent2.location
    
    def check_goal_driven_trigger(self, agent1, agent2):
        """Check if agent1 needs agent2 to achieve goals"""
        # This would analyze if agent2 can help agent1 with their goals
        return False  # Placeholder
    
    def check_emotional_trigger(self, agent1, agent2):
        """Check if agent1 is emotionally drawn to interact with agent2"""
        # This would analyze emotional compatibility and current emotional needs
        return False  # Placeholder
    
    def check_interest_alignment_trigger(self, agent1, agent2):
        """Check if agents have aligned interests for natural conversation"""
        # This would compare personality traits and current activities
        return False  # Placeholder
    
    def check_unfinished_business_trigger(self, agent1, agent2, relationship):
        """Check if there's unresolved conversation or conflict"""
        # Check for unresolved conflicts or incomplete conversations
        return len(relationship.get('conflicts', [])) > 0


class StoryHealthMonitor:
    """Monitors various aspects of story health and progression"""
    
    def __init__(self):
        self.metrics = {
            'interaction_density': 0.0,
            'emotional_variety': 0.0,
            'relationship_velocity': 0.0,
            'conflict_temperature': 0.0,
            'mystery_discovery_rate': 0.0
        }
        
        self.history = []
    
    def calculate_interaction_density(self, agents, time_window=10):
        """Calculate how frequently agents are interacting"""
        # Count interactions in recent time window
        recent_interactions = 0
        total_possible_interactions = len(agents) * (len(agents) - 1) / 2
        
        # This would analyze actual interaction history
        # For now, return a placeholder
        return min(recent_interactions / (total_possible_interactions * time_window), 1.0)
    
    def calculate_emotional_variety(self, agents):
        """Calculate the variety of emotions being expressed"""
        emotions_present = set()
        for agent in agents:
            emotions_present.add(agent.current_mood)
        
        # Normalize by total possible emotions
        max_emotions = 7  # happy, sad, angry, fearful, surprised, disgusted, neutral
        return len(emotions_present) / max_emotions
    
    def calculate_relationship_velocity(self, relationship_manager, agents):
        """Calculate how quickly relationships are developing"""
        total_relationship_changes = 0
        total_relationships = 0
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                relationship = relationship_manager.get_relationship(agent1, agent2)
                total_relationships += 1
                # This would track relationship changes over time
        
        return total_relationship_changes / max(total_relationships, 1)
    
    def calculate_conflict_temperature(self, agents, relationship_manager):
        """Calculate the level of tension and unresolved conflicts"""
        total_conflicts = 0
        total_relationships = 0
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                relationship = relationship_manager.get_relationship(agent1, agent2)
                total_relationships += 1
                total_conflicts += len(relationship.get('conflicts', []))
        
        return total_conflicts / max(total_relationships, 1)
    
    def update_metrics(self, agents, environment, relationship_manager):
        """Update all story health metrics"""
        self.metrics['interaction_density'] = self.calculate_interaction_density(agents)
        self.metrics['emotional_variety'] = self.calculate_emotional_variety(agents)
        self.metrics['relationship_velocity'] = self.calculate_relationship_velocity(relationship_manager, agents)
        self.metrics['conflict_temperature'] = self.calculate_conflict_temperature(agents, relationship_manager)
        
        # Store historical data
        self.history.append({
            'time': environment.current_time,
            'metrics': self.metrics.copy()
        })
        
        return self.metrics
    
    def detect_stagnation(self, threshold=0.3):
        """Detect if the story is stagnating"""
        if len(self.history) < 3:
            return False
        
        # Check if metrics have been consistently low
        recent_metrics = self.history[-3:]
        avg_interaction_density = sum(m['metrics']['interaction_density'] for m in recent_metrics) / 3
        avg_relationship_velocity = sum(m['metrics']['relationship_velocity'] for m in recent_metrics) / 3
        
        return avg_interaction_density < threshold and avg_relationship_velocity < threshold


class EventGenerator:
    """Generates events to improve story flow and create opportunities"""
    
    def __init__(self):
        self.event_categories = [
            'relationship_catalyst',
            'information_reveal',
            'environmental_pressure',
            'conflict_escalation',
            'conflict_resolution'
        ]
    
    def generate_relationship_catalyst(self, agents, environment):
        """Generate events that force cooperation or reveal character depth"""
        events = []
        
        # Forced cooperation scenario
        events.append({
            'type': 'relationship_catalyst',
            'subtype': 'forced_cooperation',
            'description': 'A situation arises that requires multiple characters to work together',
            'affected_agents': agents[:2] if len(agents) >= 2 else agents,
            'location': environment.locations[list(environment.locations.keys())[0]].name if environment.locations else None
        })
        
        return events
    
    def generate_information_reveal(self, agents, relationship_manager):
        """Generate events that naturally lead to secret sharing or backstory reveals"""
        events = []
        
        for agent in agents:
            events.append({
                'type': 'information_reveal',
                'subtype': 'backstory_opportunity',
                'description': f'A situation that naturally leads to {agent.name} sharing their background',
                'affected_agents': [agent],
                'trigger': 'conversation_topic'
            })
        
        return events
    
    def generate_environmental_pressure(self, agents, environment):
        """Generate external pressures that affect character decisions"""
        events = []
        
        # Weather event
        events.append({
            'type': 'environmental_pressure',
            'subtype': 'weather_change',
            'description': 'Sudden weather change affects character plans',
            'affected_agents': agents,
            'effect': 'forces_indoor_gathering'
        })
        
        return events
    
    def select_best_event(self, event_candidates, story_context):
        """Select the most appropriate event from candidates"""
        if not event_candidates:
            return None
        
        # Simple selection logic - in practice, this would be more sophisticated
        import random
        return random.choice(event_candidates)