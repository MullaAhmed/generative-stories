# Data Loaders - Functions to load configuration data, initial world states, etc.

import json
import os
from typing import Dict, List, Any, Optional

class ConfigLoader:
    """
    Handles loading and parsing of configuration files
    """
    
    @staticmethod
    def load_simulation_config(config_path: str = "config/simulation_config.json") -> Dict[str, Any]:
        """
        Load the main simulation configuration
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing simulation configuration
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}")
            return ConfigLoader.get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            return ConfigLoader.get_default_config()
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """
        Get default configuration if file loading fails
        
        Returns:
            Default configuration dictionary
        """
        return {
            "simulation": {
                "max_time_steps": 100,
                "time_unit": "hour",
                "auto_save_interval": 10
            },
            "story": {
                "theme": "general",
                "genre": "drama",
                "target_length": "medium",
                "ending_conditions": {
                    "max_interactions": 200,
                    "satisfaction_threshold": 0.8,
                    "stagnation_threshold": 0.3
                }
            },
            "agents": [],
            "locations": [],
            "location_connections": [],
            "narrator": {
                "intervention_frequency": "medium",
                "event_types": ["relationship_catalyst", "information_reveal", "environmental_pressure"]
            },
            "memory": {
                "max_memories_per_agent": 100,
                "compression_threshold": 80,
                "compression_ratio": 0.6
            }
        }
    
    @staticmethod
    def load_character_templates(templates_path: str = "config/character_templates.json") -> Dict[str, Any]:
        """
        Load character templates for quick character creation
        
        Args:
            templates_path: Path to character templates file
            
        Returns:
            Dictionary containing character templates
        """
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return templates
        except FileNotFoundError:
            print(f"Character templates file not found: {templates_path}")
            return ConfigLoader.get_default_character_templates()
        except json.JSONDecodeError as e:
            print(f"Error parsing character templates: {e}")
            return ConfigLoader.get_default_character_templates()
    
    @staticmethod
    def get_default_character_templates() -> Dict[str, Any]:
        """
        Get default character templates
        
        Returns:
            Default character templates dictionary
        """
        return {
            "archetypes": {
                "hero": {
                    "personality_traits": ["brave", "determined", "compassionate"],
                    "typical_goals": ["protect others", "seek justice", "overcome challenges"],
                    "common_fears": ["failure", "letting others down"]
                },
                "mentor": {
                    "personality_traits": ["wise", "patient", "experienced"],
                    "typical_goals": ["guide others", "share knowledge", "ensure legacy"],
                    "common_fears": ["being forgotten", "students failing"]
                },
                "rebel": {
                    "personality_traits": ["independent", "questioning", "passionate"],
                    "typical_goals": ["challenge authority", "fight injustice", "prove themselves"],
                    "common_fears": ["conformity", "being controlled"]
                }
            },
            "personality_traits": [
                "brave", "cowardly", "kind", "cruel", "intelligent", "naive",
                "ambitious", "lazy", "honest", "deceptive", "loyal", "treacherous",
                "optimistic", "pessimistic", "patient", "impulsive", "calm", "anxious"
            ]
        }
    
    @staticmethod
    def load_world_templates(templates_path: str = "config/world_templates.json") -> Dict[str, Any]:
        """
        Load world/setting templates
        
        Args:
            templates_path: Path to world templates file
            
        Returns:
            Dictionary containing world templates
        """
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return templates
        except FileNotFoundError:
            print(f"World templates file not found: {templates_path}")
            return ConfigLoader.get_default_world_templates()
        except json.JSONDecodeError as e:
            print(f"Error parsing world templates: {e}")
            return ConfigLoader.get_default_world_templates()
    
    @staticmethod
    def get_default_world_templates() -> Dict[str, Any]:
        """
        Get default world templates
        
        Returns:
            Default world templates dictionary
        """
        return {
            "settings": {
                "small_town": {
                    "description": "A quiet small town where everyone knows everyone",
                    "typical_locations": [
                        {"name": "Town Square", "type": "public", "description": "The heart of the town where people gather"},
                        {"name": "Local Cafe", "type": "social", "description": "A cozy place for conversations over coffee"},
                        {"name": "Library", "type": "quiet", "description": "A peaceful place for reading and reflection"},
                        {"name": "Park", "type": "outdoor", "description": "A green space for relaxation and recreation"}
                    ],
                    "atmosphere": "peaceful",
                    "common_themes": ["community", "secrets", "relationships", "change"]
                },
                "fantasy_village": {
                    "description": "A medieval fantasy village with magic and adventure",
                    "typical_locations": [
                        {"name": "Village Inn", "type": "social", "description": "Where travelers rest and share tales"},
                        {"name": "Blacksmith Shop", "type": "work", "description": "Where weapons and tools are forged"},
                        {"name": "Magic Shop", "type": "mysterious", "description": "A place of wonder and arcane knowledge"},
                        {"name": "Forest Edge", "type": "outdoor", "description": "Where civilization meets the wild"}
                    ],
                    "atmosphere": "mystical",
                    "common_themes": ["adventure", "magic", "heroism", "mystery"]
                }
            }
        }


class StoryStateLoader:
    """
    Handles loading and saving of story states for continuation
    """
    
    @staticmethod
    def save_story_state(story_state: Dict[str, Any], save_path: str = "data/story_state.json") -> bool:
        """
        Save the current story state to file
        
        Args:
            story_state: Dictionary containing the complete story state
            save_path: Path where to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(story_state, f, indent=2, ensure_ascii=False)
            
            print(f"Story state saved to: {save_path}")
            return True
        except Exception as e:
            print(f"Error saving story state: {e}")
            return False
    
    @staticmethod
    def load_story_state(load_path: str = "data/story_state.json") -> Optional[Dict[str, Any]]:
        """
        Load a previously saved story state
        
        Args:
            load_path: Path to the saved state file
            
        Returns:
            Dictionary containing the story state, or None if loading fails
        """
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                story_state = json.load(f)
            
            print(f"Story state loaded from: {load_path}")
            return story_state
        except FileNotFoundError:
            print(f"Story state file not found: {load_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing story state file: {e}")
            return None
    
    @staticmethod
    def export_story_log(story_log: List[Dict], export_path: str = "data/story_log.json") -> bool:
        """
        Export story log to file
        
        Args:
            story_log: List of story events and interactions
            export_path: Path where to export the log
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(story_log, f, indent=2, ensure_ascii=False)
            
            print(f"Story log exported to: {export_path}")
            return True
        except Exception as e:
            print(f"Error exporting story log: {e}")
            return False


class ScenarioLoader:
    """
    Handles loading of pre-defined scenarios and story setups
    """
    
    @staticmethod
    def load_scenario(scenario_name: str, scenarios_dir: str = "config/scenarios/") -> Optional[Dict[str, Any]]:
        """
        Load a specific scenario configuration
        
        Args:
            scenario_name: Name of the scenario to load
            scenarios_dir: Directory containing scenario files
            
        Returns:
            Dictionary containing scenario configuration, or None if not found
        """
        scenario_path = os.path.join(scenarios_dir, f"{scenario_name}.json")
        
        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                scenario = json.load(f)
            
            print(f"Scenario '{scenario_name}' loaded successfully")
            return scenario
        except FileNotFoundError:
            print(f"Scenario file not found: {scenario_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing scenario file: {e}")
            return None
    
    @staticmethod
    def list_available_scenarios(scenarios_dir: str = "config/scenarios/") -> List[str]:
        """
        List all available scenarios
        
        Args:
            scenarios_dir: Directory containing scenario files
            
        Returns:
            List of available scenario names
        """
        try:
            if not os.path.exists(scenarios_dir):
                return []
            
            scenarios = []
            for filename in os.listdir(scenarios_dir):
                if filename.endswith('.json'):
                    scenario_name = filename[:-5]  # Remove .json extension
                    scenarios.append(scenario_name)
            
            return sorted(scenarios)
        except Exception as e:
            print(f"Error listing scenarios: {e}")
            return []
    
    @staticmethod
    def create_scenario_template(scenario_name: str, scenarios_dir: str = "config/scenarios/") -> bool:
        """
        Create a template scenario file
        
        Args:
            scenario_name: Name for the new scenario
            scenarios_dir: Directory to save the scenario
            
        Returns:
            True if successful, False otherwise
        """
        scenario_template = {
            "metadata": {
                "name": scenario_name,
                "description": "A new scenario template",
                "theme": "general",
                "genre": "drama",
                "estimated_duration": "medium"
            },
            "initial_setup": {
                "time": 0,
                "weather": "clear",
                "atmosphere": "neutral"
            },
            "locations": [
                {
                    "name": "Main Location",
                    "description": "The primary location for this scenario",
                    "type": "general"
                }
            ],
            "location_connections": [
                {
                    "from": "Main Location",
                    "to": "Main Location",
                    "bidirectional": True
                }
            ],
            "agents": [
                {
                    "name": "Character One",
                    "description": "The first character in this scenario",
                    "personality_traits": ["trait1", "trait2"],
                    "background": "Background story for character one",
                    "starting_location": "Main Location",
                    "goals": ["goal1", "goal2"],
                    "fears": ["fear1"]
                }
            ],
            "initial_events": [],
            "story_hooks": [
                "An interesting situation that could start the story"
            ]
        }
        
        try:
            os.makedirs(scenarios_dir, exist_ok=True)
            scenario_path = os.path.join(scenarios_dir, f"{scenario_name}.json")
            
            with open(scenario_path, 'w', encoding='utf-8') as f:
                json.dump(scenario_template, f, indent=2, ensure_ascii=False)
            
            print(f"Scenario template created: {scenario_path}")
            return True
        except Exception as e:
            print(f"Error creating scenario template: {e}")
            return False


# Convenience functions for easy access
def load_config(config_path: str = "config/simulation_config.json") -> Dict[str, Any]:
    """Load simulation configuration"""
    return ConfigLoader.load_simulation_config(config_path)

def load_scenario(scenario_name: str) -> Optional[Dict[str, Any]]:
    """Load a specific scenario"""
    return ScenarioLoader.load_scenario(scenario_name)

def save_story(story_state: Dict[str, Any], filename: str = None) -> bool:
    """Save current story state"""
    if filename:
        save_path = f"data/{filename}.json"
    else:
        save_path = "data/story_state.json"
    
    return StoryStateLoader.save_story_state(story_state, save_path)

def load_story(filename: str = None) -> Optional[Dict[str, Any]]:
    """Load a saved story state"""
    if filename:
        load_path = f"data/{filename}.json"
    else:
        load_path = "data/story_state.json"
    
    return StoryStateLoader.load_story_state(load_path)