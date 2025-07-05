#!/usr/bin/env python3
"""
Generative Stories - Multi-Agent Narrative Engine

Main entry point for running story simulations.
"""

import os
import sys
from datetime import datetime
from typing import Optional

# Add the stories directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.simulation_engine import SimulationEngine
from utils.data_loaders import save_story
from utils.memory_management import MemoryManager

def setup_environment():
    """Set up the environment and check dependencies"""
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in a .env file or environment variable")
    
    # Create necessary directories
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/generated_stories", exist_ok=True)
    os.makedirs("data/saves", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)

def run_simulation(base_config: dict, save_name: str = None, verbose: bool = True,
                  character_data: dict = None, world_data: dict = None,
                  narrator_data: dict = None, overseer_data: dict = None) -> str:
    """
    Run a complete story simulation
    
    Args:
        base_config: Base configuration dictionary (required)
        save_name: Name for saving the story (optional)
        verbose: Whether to print progress information
        character_data: Dictionary containing character definitions (optional)
        world_data: Dictionary containing world/location definitions (optional)
        narrator_data: Dictionary containing narrator configuration (optional)
        overseer_data: Dictionary containing overseer configuration (optional)
        
    Returns:
        Path to the generated story file
    """
    if verbose:
        print("🎭 Starting Generative Stories simulation...")
        print("=" * 50)
    
    # Start with the base configuration
    config = base_config.copy()
    
    if verbose:
        print(f"📋 Base configuration loaded: {config.get('story', {}).get('theme', 'general')}")
    
    # Apply custom data if provided
    if character_data:
        if verbose:
            print(f"👥 Applying custom character data ({len(character_data.get('agents', []))} characters)")
        config['agents'] = character_data.get('agents', [])
    
    if world_data:
        if verbose:
            print(f"🌍 Applying custom world data")
        # Merge world data into config
        for key in ['locations', 'location_connections', 'world_state', 'environment']:
            if key in world_data:
                config[key] = world_data[key]
    
    if narrator_data:
        if verbose:
            print(f"📝 Applying custom narrator configuration")
        config['narrator'] = narrator_data
    
    if overseer_data:
        if verbose:
            print(f"👁️ Applying custom overseer configuration")
        config['overseer'] = overseer_data
    
    # Initialize memory manager
    memory_config = config.get('memory', {})
    memory_manager = MemoryManager(memory_config)
    
    # Initialize simulation engine
    simulation = SimulationEngine(config)
    
    if verbose:
        print(f"🎬 Initializing simulation with {len(config.get('agents', []))} agents...")
    
    # Initialize the simulation
    simulation.initialize_simulation(config)
    
    if verbose:
        print("🚀 Running simulation...")
        print("-" * 30)
    
    # Run the simulation
    try:
        story_result = simulation.run_full_simulation()
        
        if verbose:
            print("-" * 30)
            print("✅ Simulation completed successfully!")
        
        # Save the story
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if save_name:
            filename = f"{save_name}_{timestamp}"
        else:
            filename = f"story_{timestamp}"
        
        story_path = f"data/generated_stories/{filename}.txt"
        
        # Save story to file
        os.makedirs(os.path.dirname(story_path), exist_ok=True)
        with open(story_path, 'w', encoding='utf-8') as f:
            f.write(story_result)
        
        # Also save the complete simulation state
        story_state = {
            'config': config,
            'final_story': story_result,
            'simulation_metadata': {
                'completion_time': datetime.now().isoformat(),
                'total_steps': simulation.current_step,
                'agents': [agent.name for agent in simulation.story_agents],
                'final_locations': {agent.name: agent.location for agent in simulation.story_agents}
            }
        }
        
        save_story(story_state, filename)
        
        if verbose:
            print(f"💾 Story saved to: {story_path}")
            print(f"📊 Simulation state saved to: data/{filename}.json")
        
        return story_path
        
    except KeyboardInterrupt:
        if verbose:
            print("\n⏹️  Simulation interrupted by user")
        return None
    except Exception as e:
        if verbose:
            print(f"❌ Simulation failed: {e}")
        raise

def main():
    """Main entry point - designed to be called from run_story.py"""
    # Set up environment
    setup_environment()
    
    print("🎭 Generative Stories Main Module")
    print("This module is designed to be called from run_story.py")
    print("Please run the simulation using run_story.py instead.")

if __name__ == "__main__":
    main()