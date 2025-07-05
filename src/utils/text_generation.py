# Text Generation - Functions for interacting with Gemini-Flash LLM

import os
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Using mock responses.")

class TextGenerator:
    """
    Handles text generation using Gemini-Flash LLM
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            if not self.api_key:
                print("Warning: GEMINI_API_KEY not found. Using mock responses.")
    
    def generate_response(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """
        Generate a response using Gemini-Flash
        """
        if self.model:
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )
                return response.text.strip()
            except Exception as e:
                print(f"Error generating text: {e}")
                return self._mock_response(prompt)
        else:
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
        
        return self.generate_response(prompt, max_tokens=40, temperature=0.7)
    
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


# Global instance for easy access
_generator = None

def get_generator():
    global _generator
    if _generator is None:
        _generator = TextGenerator()
    return _generator

# Convenience functions
def generate_dialogue(character_name: str, character_description: str, 
                     situation: str, other_characters: List[str],
                     recent_memories: List[str] = None) -> str:
    return get_generator().generate_character_dialogue(
        character_name, character_description, situation, other_characters, recent_memories
    )

def generate_action(character_name: str, character_description: str,
                   location: str, goals: List[str], current_mood: str,
                   other_characters: List[str] = None) -> str:
    return get_generator().generate_character_action(
        character_name, character_description, location, goals, current_mood, other_characters
    )

def analyze_sentiment(interaction_text: str) -> Dict[str, float]:
    return get_generator().analyze_interaction_sentiment(interaction_text)