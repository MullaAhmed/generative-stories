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
        
        # Dynamic chapter tracking
        self.current_chapter_content = {
            'interactions': [],
            'events': [],
            'character_developments': [],
            'plot_points': [],
            'emotional_beats': [],
            'start_step': 0
        }
        
        # Chapter generation criteria
        self.chapter_criteria = {
            'min_interactions': 8,  # Minimum interactions before considering chapter end
            'max_interactions': 25,  # Force chapter end if too long
            'plot_significance_threshold': 0.7,  # How significant events need to be
            'character_development_threshold': 0.6,  # Character growth threshold
            'emotional_climax_threshold': 0.8,  # Emotional intensity threshold
            'relationship_change_threshold': 0.5,  # Relationship development threshold
        }
        
        # Plot tracking
        self.plot_threads = {}
        self.unresolved_conflicts = []
        self.character_relationship_changes = {}
        
    def observe_interaction(self, interaction_data: Dict):
        """Record and analyze an interaction between agents"""
        
        # Add to interaction history
        self.interaction_history.append(interaction_data)
        self.current_chapter_content['interactions'].append(interaction_data)
        self.story_metadata['total_interactions'] += 1
        
        # Analyze interaction significance
        significance = self._analyze_interaction_significance(interaction_data)
        
        # Update character arcs
        for participant in interaction_data.get('participants', []):
            if participant not in self.character_arcs:
                self.character_arcs[participant] = {
                    'interactions': 0,
                    'relationships_formed': 0,
                    'character_growth': [],
                    'key_moments': [],
                    'emotional_journey': [],
                    'current_arc_stage': 'introduction'
                }
            
            self.character_arcs[participant]['interactions'] += 1
            
            # Track significant interactions
            if significance['is_significant']:
                self.character_arcs[participant]['key_moments'].append({
                    'time': interaction_data.get('time'),
                    'description': interaction_data.get('content', ''),
                    'significance': significance['significance_score'],
                    'other_participants': [p for p in interaction_data.get('participants', []) if p != participant],
                    'emotional_impact': significance.get('emotional_impact', 0.5)
                })
                
                # Add to current chapter's plot points
                if significance['significance_score'] > self.chapter_criteria['plot_significance_threshold']:
                    self.current_chapter_content['plot_points'].append({
                        'type': 'interaction',
                        'participants': interaction_data.get('participants', []),
                        'significance': significance['significance_score'],
                        'description': interaction_data.get('content', ''),
                        'step': interaction_data.get('time', 0)
                    })
        
        # Track relationship changes
        self._track_relationship_changes(interaction_data, significance)
        
        # Track emotional beats
        if significance.get('emotional_impact', 0) > 0.6:
            self.current_chapter_content['emotional_beats'].append({
                'participants': interaction_data.get('participants', []),
                'emotional_intensity': significance.get('emotional_impact', 0),
                'type': significance.get('emotional_type', 'neutral'),
                'step': interaction_data.get('time', 0)
            })
    
    def observe_event(self, event_data: Dict):
        """Record and analyze a narrator-generated event"""
        
        # Add to event history
        self.event_history.append(event_data)
        self.current_chapter_content['events'].append(event_data)
        
        # Analyze event significance
        significance = self._analyze_event_significance(event_data)
        
        # Check if this is a major event
        if significance['is_major']:
            self.story_metadata['major_events'].append({
                'time': event_data.get('execution_time'),
                'description': event_data.get('description', ''),
                'type': event_data.get('type', 'unknown'),
                'significance': significance['significance_score']
            })
            
            # Add to current chapter's plot points
            self.current_chapter_content['plot_points'].append({
                'type': 'event',
                'description': event_data.get('description', ''),
                'significance': significance['significance_score'],
                'affected_agents': event_data.get('affected_agents', []),
                'step': event_data.get('execution_time', 0)
            })
    
    def _analyze_interaction_significance(self, interaction_data: Dict) -> Dict:
        """Analyze how significant an interaction is for the story"""
        significance_score = 0.0
        factors = []
        
        content = interaction_data.get('content', '').lower()
        participants = interaction_data.get('participants', [])
        
        # Check for emotional keywords
        emotional_keywords = {
            'high': ['love', 'hate', 'betrayal', 'secret', 'confession', 'revelation', 'death', 'birth'],
            'medium': ['angry', 'sad', 'happy', 'afraid', 'worried', 'excited', 'surprised'],
            'low': ['like', 'dislike', 'think', 'believe', 'wonder']
        }
        
        emotional_impact = 0.0
        emotional_type = 'neutral'
        
        for level, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    if level == 'high':
                        significance_score += 0.3
                        emotional_impact = max(emotional_impact, 0.8)
                        emotional_type = 'intense'
                    elif level == 'medium':
                        significance_score += 0.2
                        emotional_impact = max(emotional_impact, 0.6)
                        emotional_type = 'moderate'
                    else:
                        significance_score += 0.1
                        emotional_impact = max(emotional_impact, 0.4)
                        emotional_type = 'mild'
                    factors.append(f"emotional_keyword_{keyword}")
        
        # Check for relationship development
        relationship_keywords = ['friend', 'enemy', 'trust', 'distrust', 'alliance', 'partnership']
        for keyword in relationship_keywords:
            if keyword in content:
                significance_score += 0.2
                factors.append(f"relationship_development_{keyword}")
        
        # Check for plot advancement keywords
        plot_keywords = ['plan', 'mission', 'goal', 'quest', 'discovery', 'clue', 'mystery', 'truth']
        for keyword in plot_keywords:
            if keyword in content:
                significance_score += 0.15
                factors.append(f"plot_advancement_{keyword}")
        
        # Length factor (longer interactions might be more significant)
        if len(content) > 100:
            significance_score += 0.1
            factors.append("lengthy_interaction")
        
        # Multiple participants factor
        if len(participants) > 2:
            significance_score += 0.1
            factors.append("group_interaction")
        
        # Sentiment analysis factor
        sentiment = interaction_data.get('sentiment', {})
        if sentiment.get('emotional_intensity', 0) > 0.7:
            significance_score += 0.2
            factors.append("high_emotional_intensity")
        
        return {
            'significance_score': min(significance_score, 1.0),
            'is_significant': significance_score > 0.4,
            'factors': factors,
            'emotional_impact': emotional_impact,
            'emotional_type': emotional_type
        }
    
    def _analyze_event_significance(self, event_data: Dict) -> Dict:
        """Analyze how significant an event is for the story"""
        significance_score = 0.0
        factors = []
        
        event_type = event_data.get('type', 'unknown')
        description = event_data.get('description', '').lower()
        affected_agents = event_data.get('affected_agents', [])
        
        # Event type significance
        type_significance = {
            'character_introduction': 0.8,
            'conflict_escalation': 0.9,
            'conflict_resolution': 0.8,
            'information_reveal': 0.7,
            'relationship_catalyst': 0.6,
            'environmental_pressure': 0.4,
            'quantum_phenomena': 0.7,
            'political_revelations': 0.8,
            'romantic_moments': 0.6,
            'combat_encounters': 0.9,
            'prophecy_fulfillment': 0.9,
            'galactic_intrigue': 0.7,
            'technological_manifestations': 0.6,
            'alien_encounters': 0.8
        }
        
        significance_score += type_significance.get(event_type, 0.3)
        factors.append(f"event_type_{event_type}")
        
        # Number of affected agents
        if len(affected_agents) > 2:
            significance_score += 0.2
            factors.append("affects_multiple_agents")
        elif len(affected_agents) == 0:
            significance_score -= 0.1
            factors.append("affects_no_specific_agents")
        
        # Description keywords
        significant_keywords = ['crisis', 'revelation', 'discovery', 'attack', 'alliance', 'betrayal', 'death', 'birth', 'transformation']
        for keyword in significant_keywords:
            if keyword in description:
                significance_score += 0.15
                factors.append(f"significant_keyword_{keyword}")
        
        return {
            'significance_score': min(significance_score, 1.0),
            'is_major': significance_score > 0.6,
            'factors': factors
        }
    
    def _track_relationship_changes(self, interaction_data: Dict, significance: Dict):
        """Track changes in character relationships"""
        participants = interaction_data.get('participants', [])
        
        if len(participants) >= 2:
            for i, char1 in enumerate(participants):
                for char2 in participants[i+1:]:
                    relationship_key = tuple(sorted([char1, char2]))
                    
                    if relationship_key not in self.character_relationship_changes:
                        self.character_relationship_changes[relationship_key] = {
                            'initial_interaction': interaction_data.get('time', 0),
                            'interaction_count': 0,
                            'significant_moments': [],
                            'relationship_trajectory': 'neutral'
                        }
                    
                    rel_data = self.character_relationship_changes[relationship_key]
                    rel_data['interaction_count'] += 1
                    
                    if significance['is_significant']:
                        rel_data['significant_moments'].append({
                            'step': interaction_data.get('time', 0),
                            'significance': significance['significance_score'],
                            'emotional_impact': significance.get('emotional_impact', 0)
                        })
    
    def should_end_current_chapter(self, current_step: int) -> Dict:
        """Determine if the current chapter should end based on plot development"""
        chapter_content = self.current_chapter_content
        interactions_count = len(chapter_content['interactions'])
        
        # Don't end chapter too early
        if interactions_count < self.chapter_criteria['min_interactions']:
            return {'should_end': False, 'reason': 'too_few_interactions'}
        
        # Force end if chapter is getting too long
        if interactions_count >= self.chapter_criteria['max_interactions']:
            return {'should_end': True, 'reason': 'max_length_reached', 'urgency': 'high'}
        
        # Check for natural chapter ending points
        ending_score = 0.0
        reasons = []
        
        # 1. Major plot point reached
        recent_plot_points = [p for p in chapter_content['plot_points'] 
                            if current_step - p.get('step', 0) <= 3]
        if recent_plot_points:
            max_significance = max(p['significance'] for p in recent_plot_points)
            if max_significance > self.chapter_criteria['plot_significance_threshold']:
                ending_score += 0.4
                reasons.append('major_plot_point')
        
        # 2. Emotional climax reached
        recent_emotional_beats = [e for e in chapter_content['emotional_beats'] 
                                if current_step - e.get('step', 0) <= 2]
        if recent_emotional_beats:
            max_emotional_intensity = max(e['emotional_intensity'] for e in recent_emotional_beats)
            if max_emotional_intensity > self.chapter_criteria['emotional_climax_threshold']:
                ending_score += 0.3
                reasons.append('emotional_climax')
        
        # 3. Character development milestone
        character_developments = self._assess_character_development_in_chapter()
        if character_developments['significant_developments'] > 0:
            ending_score += 0.2
            reasons.append('character_development')
        
        # 4. Relationship changes
        relationship_changes = self._assess_relationship_changes_in_chapter()
        if relationship_changes['significant_changes'] > 0:
            ending_score += 0.2
            reasons.append('relationship_changes')
        
        # 5. Resolution of conflict or tension
        if self._detect_resolution_moment():
            ending_score += 0.3
            reasons.append('conflict_resolution')
        
        # 6. Natural pause in action
        if self._detect_natural_pause(current_step):
            ending_score += 0.1
            reasons.append('natural_pause')
        
        # Determine if chapter should end
        should_end = ending_score >= 0.6
        urgency = 'high' if ending_score >= 0.8 else 'medium' if ending_score >= 0.6 else 'low'
        
        return {
            'should_end': should_end,
            'ending_score': ending_score,
            'reasons': reasons,
            'urgency': urgency,
            'interactions_count': interactions_count
        }
    
    def _assess_character_development_in_chapter(self) -> Dict:
        """Assess character development within the current chapter"""
        developments = 0
        
        for char_name, arc in self.character_arcs.items():
            # Check for recent key moments
            recent_moments = [m for m in arc['key_moments'] 
                            if m.get('significance', 0) > self.chapter_criteria['character_development_threshold']]
            if recent_moments:
                developments += 1
        
        return {
            'significant_developments': developments,
            'total_characters_developed': len([c for c in self.character_arcs.keys() 
                                             if len(self.character_arcs[c]['key_moments']) > 0])
        }
    
    def _assess_relationship_changes_in_chapter(self) -> Dict:
        """Assess relationship changes within the current chapter"""
        significant_changes = 0
        
        for rel_key, rel_data in self.character_relationship_changes.items():
            recent_moments = [m for m in rel_data['significant_moments'] 
                            if m.get('significance', 0) > self.chapter_criteria['relationship_change_threshold']]
            if recent_moments:
                significant_changes += 1
        
        return {
            'significant_changes': significant_changes,
            'total_relationships_tracked': len(self.character_relationship_changes)
        }
    
    def _detect_resolution_moment(self) -> bool:
        """Detect if a conflict or tension has been resolved"""
        # Look for resolution keywords in recent interactions
        recent_interactions = self.current_chapter_content['interactions'][-3:]
        resolution_keywords = ['resolved', 'agreed', 'peace', 'understanding', 'forgiveness', 'solution', 'settled']
        
        for interaction in recent_interactions:
            content = interaction.get('content', '').lower()
            for keyword in resolution_keywords:
                if keyword in content:
                    return True
        
        return False
    
    def _detect_natural_pause(self, current_step: int) -> bool:
        """Detect if there's a natural pause in the action"""
        # Check if recent interactions have been low-intensity
        recent_interactions = self.current_chapter_content['interactions'][-3:]
        
        if len(recent_interactions) < 2:
            return False
        
        # Check emotional intensity of recent interactions
        total_intensity = 0
        for interaction in recent_interactions:
            sentiment = interaction.get('sentiment', {})
            total_intensity += sentiment.get('emotional_intensity', 0.5)
        
        avg_intensity = total_intensity / len(recent_interactions)
        return avg_intensity < 0.4  # Low average intensity suggests a natural pause
    
    def synthesize_chapter(self, current_step: int, force_end: bool = False) -> str:
        """Create a readable chapter from current chapter content"""
        
        chapter_content = self.current_chapter_content
        
        if not chapter_content['interactions'] and not chapter_content['events']:
            return f"Chapter {self.story_metadata['current_chapter']}: A quiet moment passes in the story."
        
        # Use text generator to create chapter summary
        generator = get_generator()
        
        # Prepare chapter data for the generator
        chapter_data = {
            'interactions': chapter_content['interactions'],
            'events': chapter_content['events'],
            'plot_points': chapter_content['plot_points'],
            'emotional_beats': chapter_content['emotional_beats'],
            'character_developments': self._get_chapter_character_developments(),
            'relationship_changes': self._get_chapter_relationship_changes(),
            'chapter_number': self.story_metadata['current_chapter'],
            'step_range': f"{chapter_content['start_step']}-{current_step}"
        }
        
        # Generate chapter text
        chapter_text = generator.synthesize_dynamic_chapter(chapter_data)
        
        # Create chapter entry
        chapter = {
            'number': self.story_metadata['current_chapter'],
            'start_step': chapter_content['start_step'],
            'end_step': current_step,
            'summary': chapter_text,
            'interactions': len(chapter_content['interactions']),
            'events': len(chapter_content['events']),
            'plot_points': len(chapter_content['plot_points']),
            'emotional_beats': len(chapter_content['emotional_beats']),
            'significance_score': self._calculate_chapter_significance()
        }
        
        self.chapters.append(chapter)
        self.chapter_summaries.append(chapter_text)
        
        # Reset current chapter content
        self._start_new_chapter(current_step)
        
        return f"Chapter {chapter['number']}: {chapter_text}"
    
    def _get_chapter_character_developments(self) -> List[Dict]:
        """Get character developments that occurred in this chapter"""
        developments = []
        
        for char_name, arc in self.character_arcs.items():
            chapter_moments = [m for m in arc['key_moments'] 
                             if m.get('time', 0) >= self.current_chapter_content['start_step']]
            if chapter_moments:
                developments.append({
                    'character': char_name,
                    'moments': chapter_moments,
                    'development_count': len(chapter_moments)
                })
        
        return developments
    
    def _get_chapter_relationship_changes(self) -> List[Dict]:
        """Get relationship changes that occurred in this chapter"""
        changes = []
        
        for rel_key, rel_data in self.character_relationship_changes.items():
            chapter_moments = [m for m in rel_data['significant_moments'] 
                             if m.get('step', 0) >= self.current_chapter_content['start_step']]
            if chapter_moments:
                changes.append({
                    'characters': list(rel_key),
                    'moments': chapter_moments,
                    'change_count': len(chapter_moments)
                })
        
        return changes
    
    def _calculate_chapter_significance(self) -> float:
        """Calculate the overall significance score for the current chapter"""
        content = self.current_chapter_content
        
        # Plot points significance
        plot_significance = sum(p.get('significance', 0) for p in content['plot_points'])
        
        # Emotional beats significance
        emotional_significance = sum(e.get('emotional_intensity', 0) for e in content['emotional_beats'])
        
        # Character development significance
        char_dev_significance = len(self._get_chapter_character_developments()) * 0.2
        
        # Relationship changes significance
        rel_change_significance = len(self._get_chapter_relationship_changes()) * 0.15
        
        total_significance = (plot_significance + emotional_significance + 
                            char_dev_significance + rel_change_significance)
        
        # Normalize by chapter length
        interaction_count = len(content['interactions'])
        if interaction_count > 0:
            return min(total_significance / interaction_count, 1.0)
        
        return 0.0
    
    def _start_new_chapter(self, current_step: int):
        """Start a new chapter"""
        self.story_metadata['current_chapter'] += 1
        self.current_chapter_content = {
            'interactions': [],
            'events': [],
            'character_developments': [],
            'plot_points': [],
            'emotional_beats': [],
            'start_step': current_step
        }
    
    def track_character_development(self, agent, interaction_data: Dict):
        """Monitor and record character growth and changes"""
        
        agent_name = agent.name
        
        if agent_name not in self.character_arcs:
            self.character_arcs[agent_name] = {
                'interactions': 0,
                'relationships_formed': 0,
                'character_growth': [],
                'key_moments': [],
                'emotional_journey': [],
                'current_arc_stage': 'introduction'
            }
        
        arc = self.character_arcs[agent_name]
        
        # Track relationship formation
        current_relationships = len(agent.relationships)
        if current_relationships > arc.get('last_relationship_count', 0):
            arc['relationships_formed'] += 1
            arc['character_growth'].append(f"Formed new relationship at step {interaction_data.get('time')}")
            
            # Add to current chapter developments
            self.current_chapter_content['character_developments'].append({
                'character': agent_name,
                'type': 'relationship_formation',
                'step': interaction_data.get('time'),
                'description': 'Formed new relationship'
            })
        
        arc['last_relationship_count'] = current_relationships
        
        # Track mood changes
        if hasattr(agent, 'current_mood'):
            last_mood = arc.get('last_mood')
            if last_mood and last_mood != agent.current_mood:
                arc['character_growth'].append(f"Mood changed from {last_mood} to {agent.current_mood}")
                arc['emotional_journey'].append({
                    'step': interaction_data.get('time'),
                    'from_mood': last_mood,
                    'to_mood': agent.current_mood
                })
            arc['last_mood'] = agent.current_mood
    
    def generate_story_summary(self) -> str:
        """Generate a human-readable summary of the entire story"""
        
        if not self.chapters:
            return "No story has been generated yet."
        
        # Combine all chapter summaries
        full_story = f"Story Summary:\n\n"
        
        for chapter in self.chapters:
            full_story += f"Chapter {chapter['number']}: {chapter['summary']}\n\n"
        
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
                'events': self.event_history,
                'plot_threads': self.plot_threads,
                'relationship_changes': self.character_relationship_changes
            }, indent=2)
        else:
            return self.generate_story_summary()
    
    def detect_ending_readiness(self, agents: List, story_metrics: Dict) -> bool:
        """Determine if the story is ready for a natural conclusion"""
        
        # Enhanced ending detection criteria
        ending_score = 0
        
        # Check if we have enough content
        if len(self.chapters) >= 3:
            ending_score += 1
        
        # Check if characters have developed relationships
        total_relationships = sum(len(agent.relationships) for agent in agents)
        if total_relationships >= len(agents):  # At least one relationship per character
            ending_score += 1
        
        # Check if there have been enough interactions
        if self.story_metadata['total_interactions'] >= 20:
            ending_score += 1
        
        # Check for character arc completion
        completed_arcs = 0
        for arc in self.character_arcs.values():
            if len(arc['character_growth']) >= 2:  # Character has grown
                completed_arcs += 1
        
        if completed_arcs >= len(agents) * 0.7:  # 70% of characters have developed
            ending_score += 1
        
        # Check for major plot resolution
        recent_major_events = [e for e in self.story_metadata['major_events'][-3:] 
                             if 'resolution' in e.get('description', '').lower()]
        if recent_major_events:
            ending_score += 1
        
        # Story is ready to end if it meets most criteria
        return ending_score >= 4
    
    def get_story_status(self) -> Dict:
        """Get current story status and statistics"""
        return {
            'current_chapter': self.story_metadata['current_chapter'],
            'total_interactions': self.story_metadata['total_interactions'],
            'total_events': len(self.event_history),
            'characters_tracked': len(self.character_arcs),
            'major_events': len(self.story_metadata['major_events']),
            'story_length': len(self.chapter_summaries),
            'current_chapter_interactions': len(self.current_chapter_content['interactions']),
            'current_chapter_plot_points': len(self.current_chapter_content['plot_points']),
            'relationship_changes_tracked': len(self.character_relationship_changes)
        }
    
    def to_dict(self) -> Dict:
        """Serialize the overseer to a dictionary"""
        return {
            'story_log': self.story_log.copy(),
            'character_arcs': self.character_arcs.copy(),
            'narrative_threads': self.narrative_threads.copy(),
            'chapters': self.chapters.copy(),
            'story_metadata': self.story_metadata.copy(),
            'interaction_history': self.interaction_history.copy(),
            'event_history': self.event_history.copy(),
            'chapter_summaries': self.chapter_summaries.copy(),
            'current_chapter_content': self.current_chapter_content.copy(),
            'chapter_criteria': self.chapter_criteria.copy(),
            'plot_threads': self.plot_threads.copy(),
            'unresolved_conflicts': self.unresolved_conflicts.copy(),
            'character_relationship_changes': self.character_relationship_changes.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OverseerAgent':
        """Reconstruct an overseer from a dictionary"""
        overseer = cls()
        
        overseer.story_log = data['story_log']
        overseer.character_arcs = data['character_arcs']
        overseer.narrative_threads = data['narrative_threads']
        overseer.chapters = data['chapters']
        overseer.story_metadata = data['story_metadata']
        overseer.interaction_history = data['interaction_history']
        overseer.event_history = data['event_history']
        overseer.chapter_summaries = data['chapter_summaries']
        overseer.current_chapter_content = data.get('current_chapter_content', {
            'interactions': [], 'events': [], 'character_developments': [],
            'plot_points': [], 'emotional_beats': [], 'start_step': 0
        })
        overseer.chapter_criteria = data.get('chapter_criteria', overseer.chapter_criteria)
        overseer.plot_threads = data.get('plot_threads', {})
        overseer.unresolved_conflicts = data.get('unresolved_conflicts', [])
        overseer.character_relationship_changes = data.get('character_relationship_changes', {})
        
        return overseer