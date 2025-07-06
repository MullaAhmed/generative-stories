# Data Loaders - Functions for saving and loading story states

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.utils.documentation_manager import DocumentationManager

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

def load_simulation_state(filename: str) -> Optional[Dict[str, Any]]:
    """Load a saved simulation state for resuming"""
    try:
        # First try to load from new documentation system
        simulation_data = DocumentationManager.load_simulation_from_directory(filename)
        if simulation_data:
            print(f"📂 Simulation state loaded from story directory: {filename}")
            return simulation_data
        
        # Fall back to old system
        try:
            # Try different possible paths
            possible_paths = [
                f"data/saves/{filename}",
                f"data/saves/{filename}.json",
                filename  # In case full path is provided
            ]
            
            load_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    load_path = path
                    break
            
            if not load_path:
                print(f"❌ Save file not found: {filename}")
                return None
            
            with open(load_path, 'r', encoding='utf-8') as f:
                simulation_data = json.load(f)
            
            print(f"📂 Simulation state loaded from legacy save: {load_path}")
            return simulation_data
            
        except Exception as e:
            print(f"❌ Error loading from legacy saves: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Error loading simulation state: {e}")
        return None

def list_saved_simulations() -> List[str]:
    """List all available saved simulations (both new and legacy)"""
    saved_simulations = []
    
    # Get story directories from new system
    story_dirs = DocumentationManager.list_story_directories()
    saved_simulations.extend(story_dirs)
    
    # Get legacy saves
    saves_dir = "data/saves"
    if os.path.exists(saves_dir):
        for filename in os.listdir(saves_dir):
            if filename.endswith('.json'):
                saved_simulations.append(f"[LEGACY] {filename}")
    
    return sorted(saved_simulations, reverse=True)  # Most recent first
# Convenience functions for easy access
def save_generated_story_text(story_state: Dict[str, Any], filename: str = None) -> bool:
    """Save generated story text (renamed from save_story)"""
    if filename:
        save_path = f"data/{filename}.json"
    else:
        save_path = "data/story_state.json"
    
    return StoryStateLoader.save_story_state(story_state, save_path)

def load_generated_story_text(filename: str = None) -> Optional[Dict[str, Any]]:
    """Load a saved story text (renamed from load_story)"""
    if filename:
        load_path = f"data/{filename}.json"
    else:
        load_path = "data/story_state.json"
    
    return StoryStateLoader.load_story_state(load_path)

def save_simulation_state(simulation_engine, filename: str) -> bool:
    """Save the complete simulation state for resuming"""
    try:
        # Create saves directory if it doesn't exist
        os.makedirs("data/saves", exist_ok=True)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"data/saves/{filename}_{timestamp}.json"
        
        # Serialize the simulation
        simulation_data = simulation_engine.to_dict()
        
        # Add metadata
        simulation_data['save_metadata'] = {
            'save_time': datetime.now().isoformat(),
            'version': '1.0',
            'save_type': 'simulation_state',
            'step': simulation_engine.current_step,
            'agents': [agent.name for agent in simulation_engine.story_agents]
        }
        
        # Save to file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(simulation_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Simulation state saved to: {save_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving simulation state: {e}")
        return False