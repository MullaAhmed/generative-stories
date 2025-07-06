# Text Generation - Functions for interacting with multiple LLM providers

import os
import json
import re
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv

from src.utils.llm_client import LLMClient
from src.config.settings import settings

# Load environment variables
load_dotenv()

class TextGenerator:
    """
    Handles text generation using multiple LLM providers
    """
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.llm_client = LLMClient()
        
        # Check if the selected provider is available
        if not self._is_provider_available(self.provider):
            print(f"Warning: {self.provider} provider not available. Falling back to mock responses.")
            self.provider = "mock"
    
    def _is_provider_available(self, provider: str) -> bool:
        """Check if the specified provider is available"""
        if provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        elif provider == "groq":
            return bool(settings.GROQ_API_KEY)
        elif provider == "gemini":
            return bool(settings.GOOGLE_API_KEY)
        return False
    
    def generate_response(self, prompt: str, max_tokens: int = 150, temperature: float = 2) -> str:
        """
        Generate a response using the configured LLM provider
        """
        if self.provider == "mock":
            return self._mock_response(prompt)
        
        try:
            # Convert prompt to messages format
            messages = [{"role": "user", "content": prompt}]
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self.llm_client.generate_chat_completion(
                        messages=messages,
                        provider=self.provider,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                )
            finally:
                loop.close()
            
            if "error" in response:
                print(f"Error generating text: {response['error']}")
                return self._mock_response(prompt)
            
            return response.get("content", "").strip()
            
        except Exception as e:
            print(f"Error generating text: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing without API"""
        if "dialogue" in prompt.lower() or "conversation" in prompt.lower():
            return "Hello, how are you doing today?"
        elif "action" in prompt.lower() or "what do you do" in prompt.lower():
            return "I look around and decide to start a conversation."
        elif "sentiment" in prompt.lower() or "analyze" in prompt.lower():
            return '{"positive_sentiment": 0.6, "negative_sentiment": 0.2, "trust_building": 0.5, "conflict_level": 0.1, "emotional_intensity": 0.4}'
        elif "event" in prompt.lower():
            return '{"description": "A gentle rain begins to fall", "affected_characters": [], "location": "town_square", "consequences": ["Characters seek shelter", "Intimate conversations"]}'
        elif "character" in prompt.lower() and "generate" in prompt.lower():
            return '{"name": "Alex Morgan", "description": "A mysterious traveler with keen eyes", "personality_traits": ["curious", "observant", "friendly"], "background": "A wanderer seeking answers", "goals": ["discover the truth", "make new friends"], "fears": ["being alone", "losing memories"]}'
        else:
            return "I understand and will respond appropriately."
    
    def generate_character_dialogue(self, character_name: str, character_description: str, 
                                  situation: str, other_characters: List[str], 
                                  recent_memories: List[str] = None) -> str:
        """Generate dialogue for a specific character in a given situation"""
        
        memories_context = ""
        if recent_memories:
            memories_context = f"\nRecent memories: {'; '.join(recent_memories[:3])}"
        
        prompt = f"""You are {character_name}. {character_description}
        
Current situation: {situation}
Other characters present: {', '.join(other_characters)}{memories_context}

Generate a natural response that fits your character. Keep it conversational and under 30 words. Be authentic to your personality."""
        
        return self.generate_response(prompt, max_tokens=60, temperature=0.8)
    
    def generate_character_action(self, character_name: str, character_description: str,
                                location: str, goals: List[str], current_mood: str,
                                other_characters: List[str] = None) -> str:
        """Generate an action for a character based on their current state"""
        
        others_context = ""
        if other_characters:
            others_context = f" Other people here: {', '.join(other_characters)}."
        
        prompt = f"""You are {character_name}. {character_description}

Location: {location}{others_context}
Your goals: {', '.join(goals[:2])}
Current mood: {current_mood}

What do you do next? Describe your action in one simple sentence (under 20 words)."""
        
        return self.generate_response(prompt, max_tokens=40, temperature=2)
    
    def analyze_interaction_sentiment(self, interaction_text: str) -> Dict[str, float]:
        """Analyze the sentiment and emotional impact of an interaction"""
        
        prompt = f"""Analyze this interaction and rate it (0.0 to 1.0):

Interaction: "{interaction_text}"

Respond with ONLY a JSON object with these exact keys:
{{"positive_sentiment": 0.0, "negative_sentiment": 0.0, "trust_building": 0.0, "conflict_level": 0.0, "emotional_intensity": 0.0}}"""
        
        response = self.generate_response(prompt, max_tokens=100, temperature=0.3)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Return default values if parsing fails
        return {
            'positive_sentiment': 0.5,
            'negative_sentiment': 0.3,
            'trust_building': 0.4,
            'conflict_level': 0.2,
            'emotional_intensity': 0.5
        }
    
    def generate_narrator_event(self, story_context: Dict, event_type: str) -> Dict:
        """Generate a narrator event to improve story flow"""
        
        characters = [agent.get('name', 'Unknown') for agent in story_context.get('agents', [])]
        
        prompt = f"""Create a {event_type} event for this story:

Characters: {', '.join(characters)}
Current time: {story_context.get('current_time', 0)}
Story needs: More interaction and development

Generate a simple event that creates opportunities for character interaction.

Respond with ONLY a JSON object:
{{"description": "brief event description", "affected_characters": ["name1"], "location": "location_name", "consequences": ["effect1"]}}"""
        
        response = self.generate_response(prompt, max_tokens=150, temperature=0.8)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Return default event
        return {
            "description": "An unexpected visitor arrives",
            "affected_characters": characters[:2] if characters else [],
            "location": "town_square",
            "consequences": ["New conversation opportunities"]
        }
    
    def generate_new_character_profile(self, existing_characters: List[Dict], 
                                     story_theme: str, available_locations: List[str]) -> Dict:
        """Generate a new character profile that fits the story"""
        
        existing_names = [char.get('name', 'Unknown') for char in existing_characters]
        existing_traits = []
        for char in existing_characters:
            existing_traits.extend(char.get('personality_traits', []))
        
        prompt = f"""Create a new character for a {story_theme} story.

Existing characters: {', '.join(existing_names)}
Available locations: {', '.join(available_locations)}
Story theme: {story_theme}

The new character should:
- Have a unique personality different from existing characters
- Fit the story theme and world
- Have clear motivations that could create interesting interactions
- Have a compelling backstory

Respond with ONLY a JSON object:
{{
    "name": "Character Name",
    "description": "Physical and personality description",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "background": "Character's backstory",
    "starting_location": "location_name",
    "goals": ["goal1", "goal2"],
    "fears": ["fear1", "fear2"],
    "technological_abilities": ["ability1", "ability2"],
    "relationships": {{"existing_char": 0.0}}
}}"""
        
        response = self.generate_response(prompt, max_tokens=300, temperature=0.8)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                character_data = json.loads(json_match.group())
                
                # Ensure required fields exist
                required_fields = ['name', 'description', 'personality_traits', 'background', 'starting_location', 'goals', 'fears']
                for field in required_fields:
                    if field not in character_data:
                        character_data[field] = self._get_default_field_value(field)
                
                return character_data
        except Exception as e:
            print(f"Error parsing character data: {e}")
        
        # Return default character if parsing fails
        return self._get_default_character(available_locations)
    
    def _get_default_field_value(self, field: str):
        """Get default value for a character field"""
        defaults = {
            'name': 'New Character',
            'description': 'A mysterious newcomer',
            'personality_traits': ['curious', 'observant'],
            'background': 'A traveler with unknown origins',
            'starting_location': 'town_square',
            'goals': ['explore the area', 'meet new people'],
            'fears': ['being discovered', 'losing purpose']
        }
        return defaults.get(field, '')
    
    def _get_default_character(self, available_locations: List[str]) -> Dict:
        """Generate a default character when LLM fails"""
        import random
        
        names = ['Alex Morgan', 'Jordan Blake', 'Casey Rivers', 'Riley Stone', 'Avery Cross']
        traits = [
            ['curious', 'brave', 'analytical'],
            ['mysterious', 'charming', 'secretive'],
            ['friendly', 'optimistic', 'helpful'],
            ['cautious', 'wise', 'protective'],
            ['adventurous', 'impulsive', 'loyal']
        ]
        
        return {
            'name': random.choice(names),
            'description': 'A newcomer with an air of mystery and purpose',
            'personality_traits': random.choice(traits),
            'background': 'A traveler who has arrived seeking something important',
            'starting_location': available_locations[0] if available_locations else 'town_square',
            'goals': ['discover the truth', 'find their place'],
            'fears': ['being rejected', 'failing their mission'],
            'technological_abilities': [],
            'relationships': {}
        }
    
    def summarize_story_chapter(self, interactions: List[Dict], events: List[Dict]) -> str:
        """Summarize interactions and events into a readable chapter"""
        
        # Simplify the data for the prompt
        interaction_summaries = []
        for interaction in interactions[-5:]:  # Last 5 interactions
            participants = interaction.get('participants', [])
            content = interaction.get('content', 'had a conversation')
            interaction_summaries.append(f"{' and '.join(participants)} {content}")
        
        event_summaries = []
        for event in events[-3:]:  # Last 3 events
            desc = event.get('description', 'Something happened')
            event_summaries.append(desc)
        
        prompt = f"""Write a brief story summary of these events:

Interactions:
{chr(10).join(interaction_summaries)}

Events:
{chr(10).join(event_summaries)}

Write a flowing narrative paragraph (2-3 sentences) that captures what happened."""
        
        return self.generate_response(prompt, max_tokens=200, temperature=0.6)


    def synthesize_dynamic_chapter(self, chapter_data: Dict) -> str:
        """Synthesize a chapter based on plot development and character arcs"""
        
        interactions = chapter_data.get('interactions', [])
        events = chapter_data.get('events', [])
        plot_points = chapter_data.get('plot_points', [])
        emotional_beats = chapter_data.get('emotional_beats', [])
        character_developments = chapter_data.get('character_developments', [])
        relationship_changes = chapter_data.get('relationship_changes', [])
        chapter_number = chapter_data.get('chapter_number', 1)
        
        # Create a comprehensive prompt for chapter synthesis
        prompt = f"""Write a compelling chapter summary for Chapter {chapter_number} of a story.

This chapter contains:
- {len(interactions)} character interactions
- {len(events)} significant events
- {len(plot_points)} major plot developments
- {len(emotional_beats)} emotional moments
- {len(character_developments)} character growth moments
- {len(relationship_changes)} relationship changes

Key plot developments:
{self._format_plot_points(plot_points)}

Character developments:
{self._format_character_developments(character_developments)}

Emotional highlights:
{self._format_emotional_beats(emotional_beats)}

Relationship changes:
{self._format_relationship_changes(relationship_changes)}

Write a flowing narrative summary (3-5 sentences) that captures the essence of this chapter, focusing on the most significant developments and their impact on the story. Make it read like a chapter summary from a novel."""
        
        return self.generate_response(prompt, max_tokens=300, temperature=0.7)
    
    def _format_plot_points(self, plot_points: List[Dict]) -> str:
        """Format plot points for the chapter synthesis prompt"""
        if not plot_points:
            return "- No major plot developments"
        
        formatted = []
        for point in plot_points[:3]:  # Top 3 most significant
            participants = point.get('participants', [])
            description = point.get('description', 'Unknown event')
            significance = point.get('significance', 0)
            
            if participants:
                formatted.append(f"- {', '.join(participants)}: {description} (significance: {significance:.1f})")
            else:
                formatted.append(f"- {description} (significance: {significance:.1f})")
        
        return '\n'.join(formatted)
    
    def _format_character_developments(self, developments: List[Dict]) -> str:
        """Format character developments for the chapter synthesis prompt"""
        if not developments:
            return "- No significant character developments"
        
        formatted = []
        for dev in developments[:3]:  # Top 3 characters with most development
            character = dev.get('character', 'Unknown')
            moment_count = dev.get('development_count', 0)
            moments = dev.get('moments', [])
            
            if moments:
                latest_moment = moments[-1]
                description = latest_moment.get('description', 'Character development')
                formatted.append(f"- {character}: {description} ({moment_count} developments)")
            else:
                formatted.append(f"- {character}: Character growth ({moment_count} developments)")
        
        return '\n'.join(formatted)
    
    def _format_emotional_beats(self, emotional_beats: List[Dict]) -> str:
        """Format emotional beats for the chapter synthesis prompt"""
        if not emotional_beats:
            return "- No significant emotional moments"
        
        # Sort by emotional intensity
        sorted_beats = sorted(emotional_beats, key=lambda x: x.get('emotional_intensity', 0), reverse=True)
        
        formatted = []
        for beat in sorted_beats[:3]:  # Top 3 most intense moments
            participants = beat.get('participants', [])
            intensity = beat.get('emotional_intensity', 0)
            emotion_type = beat.get('type', 'emotional')
            
            if participants:
                formatted.append(f"- {', '.join(participants)}: {emotion_type} moment (intensity: {intensity:.1f})")
            else:
                formatted.append(f"- {emotion_type} moment (intensity: {intensity:.1f})")
        
        return '\n'.join(formatted)
    
    def _format_relationship_changes(self, relationship_changes: List[Dict]) -> str:
        """Format relationship changes for the chapter synthesis prompt"""
        if not relationship_changes:
            return "- No significant relationship changes"
        
        formatted = []
        for change in relationship_changes[:3]:  # Top 3 relationship changes
            characters = change.get('characters', [])
            change_count = change.get('change_count', 0)
            
            if len(characters) >= 2:
                formatted.append(f"- {characters[0]} and {characters[1]}: relationship development ({change_count} moments)")
            else:
                formatted.append(f"- Relationship development ({change_count} moments)")
        
        return '\n'.join(formatted)

# Global instance for easy access
_generator = None

def get_generator(provider: str = None):
    global _generator
    if _generator is None or (provider and _generator.provider != provider):
        _generator = TextGenerator(provider)
    return _generator

# Convenience functions
def generate_dialogue(character_name: str, character_description: str, 
                     situation: str, other_characters: List[str],
                     recent_memories: List[str] = None, provider: str = None) -> str:
    return get_generator(provider).generate_character_dialogue(
        character_name, character_description, situation, other_characters, recent_memories
    )

def generate_action(character_name: str, character_description: str,
                   location: str, goals: List[str], current_mood: str,
                   other_characters: List[str] = None, provider: str = None) -> str:
    return get_generator(provider).generate_character_action(
        character_name, character_description, location, goals, current_mood, other_characters
    )

def analyze_sentiment(interaction_text: str, provider: str = None) -> Dict[str, float]:
    return get_generator(provider).analyze_interaction_sentiment(interaction_text)

def generate_new_character(existing_characters: List[Dict], story_theme: str, 
                         available_locations: List[str], provider: str = None) -> Dict:
    return get_generator(provider).generate_new_character_profile(
        existing_characters, story_theme, available_locations
    )