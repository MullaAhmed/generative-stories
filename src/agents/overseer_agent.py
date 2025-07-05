# Overseer Agent - Story documentation and narrative coherence

from typing import Dict, List, Any
from src.utils.text_generation import get_generator

class OverseerAgent:
    """
    Story documentation and narrative coherence.
    """
    
    def __init__(self):
        self.story_log = []
        self.character_arcs = {}
        self.narrative_threads = []
        self.chapters = []
        self.story_metadata = {
            'start_time': None,
            'current_chapter': 1,
            'total_interactions': 0,
            'major_events': []
        }
        
        # Track story progression
        self.interaction_history = []
        self.event_history = []
        self.chapter_summaries = []
        
    def observe_interaction(self, interaction_data: Dict):
        """Record and analyze an interaction between agents"""
        
        # Add to interaction history
        self.interaction_history.append(interaction_data)
        self.story_metadata['total_interactions'] += 1
        
        # Update character arcs
        for participant in interaction_data.get('participants', []):
            if participant not in self.character_arcs:
                self.character_arcs[participant] = {
                    'interactions': 0,
                    'relationships_formed': 0,
                    'character_growth': [],
                    'key_moments': []
                }
            
            self.character_arcs[participant]['interactions'] += 1
            
            # Check if this is a significant interaction
            if self._is_significant_interaction(interaction_data):
                self.character_arcs[participant]['key_moments'].append({
                    'time': interaction_data.get('time'),
                    'description': interaction_data.get('content', ''),
                    'other_participants': [p for p in interaction_data.get('participants', []) if p != participant]
                })
    
    def observe_event(self, event_data: Dict):
        """Record and analyze a narrator-generated event"""
        
        # Add to event history
        self.event_history.append(event_data)
        
        # Check if this is a major event
        if self._is_major_event(event_data):
            self.story_metadata['major_events'].append({
                'time': event_data.get('execution_time'),
                'description': event_data.get('description', ''),
                'type': event_data.get('type', 'unknown')
            })
    
    def _is_significant_interaction(self, interaction_data: Dict) -> bool:
        """Determine if an interaction is significant for character development"""
        
        # Simple heuristics for significance
        content = interaction_data.get('content', '').lower()
        
        # Look for emotional words or important topics
        significant_words = ['sorry', 'love', 'hate', 'afraid', 'dream', 'secret', 'family', 'past']
        
        for word in significant_words:
            if word in content:
                return True
        
        # Long interactions might be significant
        if len(content) > 50:
            return True
        
        return False
    
    def _is_major_event(self, event_data: Dict) -> bool:
        """Determine if an event is major for the story"""
        
        # Events that affect multiple characters are usually major
        affected_agents = event_data.get('affected_agents', [])
        if len(affected_agents) > 2:
            return True
        
        # Certain event types are inherently major
        major_types = ['conflict_escalation', 'information_reveal', 'relationship_catalyst']
        if event_data.get('type') in major_types:
            return True
        
        return False
    
    def synthesize_chapter(self, time_period: int, max_interactions: int = 10) -> str:
        """Create a readable chapter from recent interactions and events"""
        
        # Get recent interactions and events
        recent_interactions = self.interaction_history[-max_interactions:]
        recent_events = [event for event in self.event_history 
                        if event.get('execution_time', 0) >= time_period - 5]
        
        if not recent_interactions and not recent_events:
            return f"Chapter {self.story_metadata['current_chapter']}: A quiet moment passes in the story."
        
        # Use text generator to create chapter summary
        generator = get_generator()
        chapter_text = generator.summarize_story_chapter(recent_interactions, recent_events)
        
        # Create chapter entry
        chapter = {
            'number': self.story_metadata['current_chapter'],
            'time_period': time_period,
            'summary': chapter_text,
            'interactions': len(recent_interactions),
            'events': len(recent_events)
        }
        
        self.chapters.append(chapter)
        self.chapter_summaries.append(chapter_text)
        self.story_metadata['current_chapter'] += 1
        
        return f"Chapter {chapter['number']}: {chapter_text}"
    
    def track_character_development(self, agent, interaction_data: Dict):
        """Monitor and record character growth and changes"""
        
        agent_name = agent.name
        
        if agent_name not in self.character_arcs:
            self.character_arcs[agent_name] = {
                'interactions': 0,
                'relationships_formed': 0,
                'character_growth': [],
                'key_moments': []
            }
        
        arc = self.character_arcs[agent_name]
        
        # Track relationship formation
        current_relationships = len(agent.relationships)
        if current_relationships > arc.get('last_relationship_count', 0):
            arc['relationships_formed'] += 1
            arc['character_growth'].append(f"Formed new relationship at time {interaction_data.get('time')}")
        
        arc['last_relationship_count'] = current_relationships
        
        # Track mood changes
        if hasattr(agent, 'current_mood'):
            last_mood = arc.get('last_mood')
            if last_mood and last_mood != agent.current_mood:
                arc['character_growth'].append(f"Mood changed from {last_mood} to {agent.current_mood}")
            arc['last_mood'] = agent.current_mood
    
    def generate_story_summary(self) -> str:
        """Generate a human-readable summary of the entire story"""
        
        if not self.chapters:
            return "No story has been generated yet."
        
        # Combine all chapter summaries
        full_story = f"Story Summary:\n\n"
        
        for i, chapter_summary in enumerate(self.chapter_summaries, 1):
            full_story += f"Chapter {i}: {chapter_summary}\n\n"
        
        # Add character development summary
        full_story += "Character Development:\n"
        for character, arc in self.character_arcs.items():
            interactions = arc['interactions']
            relationships = arc['relationships_formed']
            growth_events = len(arc['character_growth'])
            
            full_story += f"- {character}: {interactions} interactions, {relationships} relationships formed, {growth_events} growth moments\n"
        
        # Add story statistics
        full_story += f"\nStory Statistics:\n"
        full_story += f"- Total Chapters: {len(self.chapters)}\n"
        full_story += f"- Total Interactions: {self.story_metadata['total_interactions']}\n"
        full_story += f"- Major Events: {len(self.story_metadata['major_events'])}\n"
        
        return full_story
    
    def export_story(self, format_type: str = 'text') -> str:
        """Export the complete story in specified format"""
        
        if format_type == 'text':
            return self.generate_story_summary()
        elif format_type == 'json':
            import json
            return json.dumps({
                'chapters': self.chapters,
                'character_arcs': self.character_arcs,
                'metadata': self.story_metadata,
                'interactions': self.interaction_history,
                'events': self.event_history
            }, indent=2)
        else:
            return self.generate_story_summary()
    
    def detect_ending_readiness(self, agents: List, story_metrics: Dict) -> bool:
        """Determine if the story is ready for a natural conclusion"""
        
        # Simple ending detection criteria
        ending_score = 0
        
        # Check if we have enough content
        if len(self.chapters) >= 3:
            ending_score += 1
        
        # Check if characters have developed relationships
        total_relationships = sum(len(agent.relationships) for agent in agents)
        if total_relationships >= len(agents):  # At least one relationship per character
            ending_score += 1
        
        # Check if there have been enough interactions
        if self.story_metadata['total_interactions'] >= 15:
            ending_score += 1
        
        # Check if story momentum is declining
        recent_interactions = len([i for i in self.interaction_history[-10:] if i])
        if recent_interactions < 3:  # Low recent activity
            ending_score += 1
        
        # Story is ready to end if it meets most criteria
        return ending_score >= 3
    
    def get_story_status(self) -> Dict:
        """Get current story status and statistics"""
        return {
            'current_chapter': self.story_metadata['current_chapter'],
            'total_interactions': self.story_metadata['total_interactions'],
            'total_events': len(self.event_history),
            'characters_tracked': len(self.character_arcs),
            'major_events': len(self.story_metadata['major_events']),
            'story_length': len(self.chapter_summaries)
        }