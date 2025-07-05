# Narrator Agent - Contextual event generation and story momentum management

import random
from typing import Dict, List, Any
from ..utils.text_generation import get_generator

class NarratorAgent:
    """
    Contextual event generation and story momentum management.
    """
    
    def __init__(self):
        self.story_health_metrics = {
            'interaction_density': 0.0,
            'emotional_variety': 0.0,
            'relationship_velocity': 0.0,
            'conflict_temperature': 0.0,
            'stagnation_score': 0.0
        }
        
        self.intervention_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
        
        self.last_intervention_time = None
        self.event_history = []
        self.steps_since_last_event = 0
        
    def analyze_story_state(self, agents: List, environment, time_step: int):
        """Analyze current story state and update health metrics"""
        
        # Calculate interaction density (interactions per agent per time step)
        total_interactions = sum(agent.interaction_count for agent in agents)
        max_possible = len(agents) * time_step if time_step > 0 else 1
        self.story_health_metrics['interaction_density'] = min(1.0, total_interactions / max_possible)
        
        # Calculate emotional variety
        moods = set(agent.current_mood for agent in agents)
        self.story_health_metrics['emotional_variety'] = len(moods) / 5.0  # Assume 5 possible moods
        
        # Calculate relationship velocity (how fast relationships are changing)
        relationship_changes = 0
        total_relationships = 0
        for agent in agents:
            total_relationships += len(agent.relationships)
            # Count relationships that have changed recently (simplified)
            relationship_changes += len([r for r in agent.relationships.values() if abs(r) > 0.1])
        
        if total_relationships > 0:
            self.story_health_metrics['relationship_velocity'] = relationship_changes / total_relationships
        
        # Calculate conflict temperature (average relationship negativity)
        negative_relationships = 0
        total_rel_count = 0
        for agent in agents:
            for rel_score in agent.relationships.values():
                total_rel_count += 1
                if rel_score < -0.2:
                    negative_relationships += 1
        
        if total_rel_count > 0:
            self.story_health_metrics['conflict_temperature'] = negative_relationships / total_rel_count
        
        # Calculate stagnation score
        self.steps_since_last_event += 1
        recent_interactions = sum(1 for agent in agents if agent.last_interaction_time and 
                                time_step - agent.last_interaction_time < 3)
        
        if recent_interactions == 0 and self.steps_since_last_event > 5:
            self.story_health_metrics['stagnation_score'] = min(1.0, self.steps_since_last_event / 10.0)
        else:
            self.story_health_metrics['stagnation_score'] = 0.0
    
    def detect_stagnation(self, agents: List, environment) -> bool:
        """Detect if the story is stagnating and needs intervention"""
        
        # Check multiple stagnation indicators
        stagnation_indicators = 0
        
        # Low interaction density
        if self.story_health_metrics['interaction_density'] < 0.2:
            stagnation_indicators += 1
        
        # High stagnation score
        if self.story_health_metrics['stagnation_score'] > 0.5:
            stagnation_indicators += 1
        
        # All agents in same location with no recent interactions
        locations = set(agent.location for agent in agents)
        if len(locations) == 1 and self.steps_since_last_event > 3:
            stagnation_indicators += 1
        
        # Low emotional variety
        if self.story_health_metrics['emotional_variety'] < 0.3:
            stagnation_indicators += 1
        
        return stagnation_indicators >= 2
    
    def evaluate_intervention_need(self) -> str:
        """Determine if and what type of intervention is needed"""
        
        # Check if enough time has passed since last intervention
        if self.steps_since_last_event < 3:
            return "none"
        
        # Calculate overall story health
        health_score = (
            self.story_health_metrics['interaction_density'] * 0.3 +
            self.story_health_metrics['emotional_variety'] * 0.2 +
            self.story_health_metrics['relationship_velocity'] * 0.2 +
            (1.0 - self.story_health_metrics['stagnation_score']) * 0.3
        )
        
        if health_score < self.intervention_thresholds['low']:
            return "high"
        elif health_score < self.intervention_thresholds['medium']:
            return "medium"
        elif health_score < self.intervention_thresholds['high']:
            return "low"
        else:
            return "none"
    
    def generate_event_candidates(self, agents: List, environment) -> List[Dict]:
        """Generate potential events that could improve story flow"""
        
        candidates = []
        
        # Relationship catalyst events
        candidates.extend(self._generate_relationship_catalysts(agents, environment))
        
        # Environmental events
        candidates.extend(self._generate_environmental_events(agents, environment))
        
        # Information reveal events
        candidates.extend(self._generate_information_reveals(agents, environment))
        
        return candidates
    
    def _generate_relationship_catalysts(self, agents: List, environment) -> List[Dict]:
        """Generate events that encourage character interaction"""
        events = []
        
        # Find agents who haven't interacted much
        isolated_agents = [agent for agent in agents if agent.interaction_count < 2]
        
        if len(isolated_agents) >= 2:
            events.append({
                'type': 'relationship_catalyst',
                'subtype': 'forced_cooperation',
                'description': 'A situation arises that requires cooperation',
                'affected_agents': isolated_agents[:2],
                'location': isolated_agents[0].location,
                'priority': 0.8
            })
        
        # Create events that bring agents together
        locations = list(environment.locations.keys())
        if len(locations) > 1:
            events.append({
                'type': 'relationship_catalyst',
                'subtype': 'gathering',
                'description': 'An event draws people to a central location',
                'affected_agents': agents,
                'location': random.choice(locations),
                'priority': 0.6
            })
        
        return events
    
    def _generate_environmental_events(self, agents: List, environment) -> List[Dict]:
        """Generate environmental events that affect the story"""
        events = []
        
        # Weather events
        weather_events = [
            'A sudden rainstorm begins',
            'The sun breaks through the clouds',
            'A gentle breeze picks up',
            'The temperature drops noticeably'
        ]
        
        events.append({
            'type': 'environmental_pressure',
            'subtype': 'weather_change',
            'description': random.choice(weather_events),
            'affected_agents': agents,
            'location': 'all',
            'priority': 0.4
        })
        
        # Time-based events
        events.append({
            'type': 'environmental_pressure',
            'subtype': 'time_pressure',
            'description': 'The day is getting late',
            'affected_agents': agents,
            'location': 'all',
            'priority': 0.3
        })
        
        return events
    
    def _generate_information_reveals(self, agents: List, environment) -> List[Dict]:
        """Generate events that reveal character information"""
        events = []
        
        # Pick a random agent to have something revealed about them
        if agents:
            target_agent = random.choice(agents)
            events.append({
                'type': 'information_reveal',
                'subtype': 'backstory_opportunity',
                'description': f'A situation that might reveal something about {target_agent.name}',
                'affected_agents': [target_agent],
                'location': target_agent.location,
                'priority': 0.5
            })
        
        return events
    
    def select_optimal_event(self, event_candidates: List[Dict], story_context: Dict) -> Dict:
        """Select the best event from candidates based on story needs"""
        
        if not event_candidates:
            return None
        
        # Sort by priority and add some randomness
        scored_events = []
        for event in event_candidates:
            score = event.get('priority', 0.5) + random.uniform(-0.1, 0.1)
            scored_events.append((score, event))
        
        scored_events.sort(key=lambda x: x[0], reverse=True)
        return scored_events[0][1]
    
    def execute_event(self, event: Dict, environment) -> Dict:
        """Execute the selected event in the environment"""
        
        if not event:
            return None
        
        # Use text generator to create a more detailed event description
        generator = get_generator()
        
        story_context = {
            'agents': [{'name': agent.name} for agent in event.get('affected_agents', [])],
            'current_time': environment.current_time,
            'location': event.get('location', 'unknown')
        }
        
        detailed_event = generator.generate_narrator_event(story_context, event['type'])
        
        # Merge the generated details with the original event
        executed_event = {
            **event,
            'detailed_description': detailed_event.get('description', event['description']),
            'consequences': detailed_event.get('consequences', []),
            'execution_time': environment.current_time
        }
        
        # Add to event history
        self.event_history.append(executed_event)
        self.steps_since_last_event = 0
        self.last_intervention_time = environment.current_time
        
        return executed_event
    
    def get_story_health_summary(self) -> Dict:
        """Get a summary of current story health metrics"""
        return {
            'metrics': self.story_health_metrics.copy(),
            'last_intervention': self.last_intervention_time,
            'steps_since_event': self.steps_since_last_event,
            'total_events': len(self.event_history)
        }