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
from utils.data_loaders import load_config, load_scenario, save_story
from utils.memory_management import MemoryManager

# Hardcoded configuration variables
CONFIG_PATH = None  # Use default config
SCENARIO_NAME = None  # Use default scenario
SAVE_NAME = None  # Auto-generate save name
INTERACTIVE_MODE = True  # Run in interactive mode
VERBOSE = True  # Show detailed output

# Custom data dictionaries - modify these to customize your story
CUSTOM_CHARACTER_DATA = None  # Set to dict with 'agents' key containing list of character dicts
CUSTOM_WORLD_DATA = None      # Set to dict with 'locations', 'location_connections', etc.
CUSTOM_NARRATOR_DATA = None   # Set to dict with narrator configuration
CUSTOM_OVERSEER_DATA = None   # Set to dict with overseer configuration
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

def run_simulation(config_path: str = None, scenario_name: str = None, 
                  save_name: str = None, verbose: bool = True,
                  character_data: dict = None, world_data: dict = None,
                  narrator_data: dict = None, overseer_data: dict = None) -> str:
    """
    Run a complete story simulation
    
    Args:
        config_path: Path to configuration file (optional)
        scenario_name: Name of scenario to load (optional)
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
    
    # Load configuration
    if config_path:
        config = load_config(config_path)
    else:
        config = load_config()
    
    if verbose:
        print(f"📋 Configuration loaded: {config.get('story', {}).get('theme', 'general')}")
    
    # Load scenario if specified
    if scenario_name:
        scenario = load_scenario(scenario_name)
        if scenario:
            # Merge scenario into config
            config.update(scenario)
            if verbose:
                print(f"📖 Scenario loaded: {scenario_name}")
        else:
            if verbose:
                print(f"⚠️  Scenario '{scenario_name}' not found, using default config")
    
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

def interactive_mode():
    """Run the simulation in interactive mode"""
    print("🎭 Welcome to Generative Stories!")
    print("=" * 40)
    
    # Get user preferences
    print("\nAvailable scenarios:")
    from utils.data_loaders import ScenarioLoader
    scenarios = ScenarioLoader.list_available_scenarios()
    
    if scenarios:
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario}")
        print(f"  {len(scenarios) + 1}. Use default configuration")
        
        try:
            choice = input(f"\nSelect scenario (1-{len(scenarios) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(scenarios):
                scenario_name = scenarios[choice_num - 1]
            else:
                scenario_name = None
        except (ValueError, IndexError):
            scenario_name = None
    else:
        print("  No scenarios found, using default configuration")
        scenario_name = None
    
    # Get save name
    save_name = input("\nEnter a name for this story (optional): ").strip()
    if not save_name:
        save_name = None
    
    print("\n🎬 Starting simulation...")
    
    # Run the simulation
    story_path = run_simulation(
        scenario_name=scenario_name,
        save_name=save_name,
        verbose=True
    )
    
    if story_path:
        print(f"\n🎉 Story generation complete!")
        print(f"📖 Your story is available at: {story_path}")
        
        # Ask if user wants to read the story
        read_choice = input("\nWould you like to read the story now? (y/n): ").strip().lower()
        if read_choice in ['y', 'yes']:
            try:
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_content = f.read()
                print("\n" + "=" * 50)
                print("YOUR GENERATED STORY")
                print("=" * 50)
                print(story_content)
                print("=" * 50)
            except Exception as e:
                print(f"Error reading story file: {e}")

def main():
    """Main entry point"""
    # Set up environment
    setup_environment()
    
    if INTERACTIVE_MODE:
        interactive_mode()
    else:
        # Run with command line arguments
        verbose = VERBOSE
        
        story_path = run_simulation(
            config_path=CONFIG_PATH,
            scenario_name=SCENARIO_NAME,
            save_name=SAVE_NAME,
            verbose=verbose,
            character_data=CUSTOM_CHARACTER_DATA,
            world_data=CUSTOM_WORLD_DATA,
            narrator_data=CUSTOM_NARRATOR_DATA,
            overseer_data=CUSTOM_OVERSEER_DATA
        )
        
        if story_path and verbose:
            print(f"\n✨ Story generated successfully: {story_path}")

if __name__ == "__main__":
    main()