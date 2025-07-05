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
SAVE_NAME = "fae_courts_saga"  # Name for this epic fantasy story
INTERACTIVE_MODE = False  # Run directly with custom data
VERBOSE = True  # Show detailed output

# Custom data dictionaries - modify these to customize your story

# Sarah J. Maas inspired fantasy world configuration
CUSTOM_CHARACTER_DATA = {
    "agents": [
        {
            "name": "Lyralei Nightwhisper",
            "description": "A fierce High Fae warrior with violet eyes that seem to hold starlight. Once a mortal huntress, she was Made into Fae during the War of Shadows. Her beauty is otherworldly, with pointed ears and an ethereal grace that belies her deadly skills with twin daggers. She bears intricate tattoos that tell the story of her transformation and the bargains she's made.",
            "personality_traits": ["fierce", "protective", "stubborn", "loyal", "quick-tempered", "compassionate", "strategic"],
            "background": "Born in a mortal village on the border between the human lands and the Spring Court, Lyralei was trained as a huntress from childhood. During a brutal attack by shadow creatures, she made a desperate bargain with a High Lord to save her younger sister, trading her mortality for power. Now she serves as an emissary between courts while searching for a way to break the magical bonds that tie her fate to ancient prophecies.",
            "starting_location": "Night Court Palace",
            "goals": ["protect her sister from court politics", "master her newfound Fae powers", "uncover the truth about the prophecy", "forge alliances between courts"],
            "fears": ["losing her humanity completely", "her sister being used as leverage", "the darkness within her magic consuming her", "failing those she's sworn to protect"],
            "magical_abilities": ["shadow manipulation", "enhanced speed and strength", "truth-sensing", "dream-walking"],
            "relationships": {"Kael": 0.3, "Seraphina": -0.2, "Thorne": 0.1}
        },
        {
            "name": "Kael Shadowmere",
            "description": "The enigmatic High Lord of the Night Court, with midnight-black hair and eyes like dark sapphires that seem to see into one's very soul. His presence commands attention and respect, radiating power that makes the air itself seem to thrum with magic. Centuries old, he carries himself with the confidence of someone who has survived countless wars and political machinations. His hands bear scars from ancient battles, and his smile can be either devastatingly charming or terrifyingly cold.",
            "personality_traits": ["calculating", "protective", "mysterious", "charismatic", "ruthless when necessary", "deeply loyal", "burdened by responsibility"],
            "background": "Born into power during the Age of Legends, Kael has ruled the Night Court for over 500 years. He survived the War of Shadows that nearly destroyed all Fae courts, emerging as one of the most powerful High Lords. His court is known for its spies and information networks, but also for protecting those who cannot protect themselves. He bears the weight of ancient magic and terrible knowledge about threats that still lurk in the shadows.",
            "starting_location": "Night Court Palace",
            "goals": ["protect his court from ancient threats", "maintain the delicate balance between courts", "train Lyralei in her powers", "prevent the return of the Shadow King"],
            "fears": ["the corruption of his court", "losing those he cares about to war", "the ancient darkness breaking free", "becoming the monster others believe him to be"],
            "magical_abilities": ["darkness manipulation", "mind shields", "winnowing (teleportation)", "death magic", "court magic"],
            "relationships": {"Lyralei": 0.4, "Seraphina": -0.5, "Thorne": 0.2}
        },
        {
            "name": "Seraphina Dawnbreaker",
            "description": "The radiant High Lady of the Dawn Court, with golden hair that seems to capture sunlight and amber eyes that burn with inner fire. Her beauty is legendary even among the Fae, but it's her fierce intelligence and unwavering moral compass that make her truly formidable. She wears flowing gowns that seem to be woven from light itself, and her presence brings warmth to any room. Despite her ethereal appearance, she's a skilled warrior who fights with weapons forged from pure sunlight.",
            "personality_traits": ["righteous", "determined", "prideful", "just", "sometimes inflexible", "passionate", "natural leader"],
            "background": "Seraphina ascended to power after her predecessor fell in the War of Shadows, chosen by the court's magic itself for her pure heart and unwavering dedication to justice. She has spent decades rebuilding her court and establishing it as a beacon of hope and order. However, she struggles with the gray areas of politics and the sometimes necessary compromises that leadership demands. Her court values honor, truth, and the protection of the innocent above all else.",
            "starting_location": "Dawn Court Embassy",
            "goals": ["establish lasting peace between all courts", "root out corruption wherever it hides", "prove the Dawn Court's strength and legitimacy", "protect mortal lands from Fae conflicts"],
            "fears": ["compromising her principles for political gain", "her court being seen as weak", "the return of chaos and war", "failing to live up to her predecessor's legacy"],
            "magical_abilities": ["light manipulation", "healing magic", "truth compulsion", "protective wards", "purification magic"],
            "relationships": {"Lyralei": -0.1, "Kael": -0.4, "Thorne": 0.3}
        },
        {
            "name": "Thorne Ironwood",
            "description": "A gruff but honorable Fae lord from the Autumn Court, with russet hair and eyes the color of amber. His skin bears the marks of countless battles, and his hands are calloused from both sword work and his love of crafting. He's built like a warrior but moves with surprising grace, and his deep voice carries the authority of someone used to command. He favors practical clothing in earth tones, often adorned with the symbols of his house - oak leaves and crossed swords.",
            "personality_traits": ["honorable", "straightforward", "protective", "sometimes hot-headed", "deeply loyal", "practical", "values tradition"],
            "background": "Thorne serves as the Autumn Court's military commander and ambassador to other courts. He comes from an ancient line of Fae warriors who have served the Autumn Court for millennia. His family's lands border the mortal realm, making him one of the few High Fae who regularly interacts with humans and understands their struggles. He lost his younger brother in the War of Shadows and has dedicated his life to preventing such tragedies from happening again.",
            "starting_location": "Autumn Court Barracks",
            "goals": ["strengthen military alliances between courts", "honor his fallen brother's memory", "protect the border territories", "train the next generation of warriors"],
            "fears": ["another war breaking out", "failing to protect those under his command", "his court being drawn into conflicts", "losing more family to politics and war"],
            "magical_abilities": ["earth and plant manipulation", "enhanced physical abilities", "weapon enchantment", "tactical foresight", "nature communication"],
            "relationships": {"Lyralei": 0.2, "Kael": 0.1, "Seraphina": 0.4}
        }
    ]
}

CUSTOM_WORLD_DATA = {
    "locations": [
        {
            "name": "Night Court Palace",
            "description": "A magnificent palace carved from black stone that seems to absorb light, creating an otherworldly atmosphere. The walls are adorned with silver inlays that depict the history of the Night Court, and the floors are made of polished obsidian that reflects like dark mirrors. Massive windows offer breathtaking views of the mountain peaks and star-filled skies. The throne room features a ceiling enchanted to show the actual night sky, complete with moving constellations. Secret passages and hidden chambers are woven throughout the structure, accessible only to those who know the ancient passwords.",
            "type": "royal_residence",
            "magical_properties": ["enhanced privacy wards", "truth detection in certain rooms", "time dilation chambers", "scrying pools"],
            "atmosphere": "mysterious and powerful",
            "notable_features": ["the Star Chamber for important meetings", "the Library of Shadows containing forbidden knowledge", "training grounds with magical obstacles"]
        },
        {
            "name": "Dawn Court Embassy",
            "description": "An elegant building constructed from white marble that seems to glow with its own inner light. Golden veins run through the stone, and the architecture features soaring arches and delicate spires that reach toward the sky. Gardens surrounding the embassy bloom with flowers that never wilt, their petals shimmering with morning dew that never evaporates. The interior is filled with warm, natural light that banishes shadows and creates an atmosphere of openness and honesty. Fountains throughout the building play soft, melodic sounds that promote peace and clarity of thought.",
            "type": "diplomatic_building",
            "magical_properties": ["truth enhancement fields", "emotional calming effects", "protective light barriers", "communication crystals"],
            "atmosphere": "serene and inspiring",
            "notable_features": ["the Hall of Accords for treaty negotiations", "meditation gardens", "the Sunrise Balcony for important announcements"]
        },
        {
            "name": "Autumn Court Barracks",
            "description": "A sturdy complex built from warm brown stone and rich wood, designed for both function and comfort. The buildings are surrounded by ancient oak trees whose leaves remain in perpetual autumn colors - deep reds, golden yellows, and burnt oranges. Training yards feature various obstacles and weapon racks, while the main hall boasts a massive fireplace where warriors gather to share stories and plan strategies. The architecture emphasizes strength and permanence, with thick walls and reinforced doors that could withstand a siege.",
            "type": "military_facility",
            "magical_properties": ["weapon enhancement forges", "tactical planning rooms with illusion magic", "healing springs", "protective earth wards"],
            "atmosphere": "martial and traditional",
            "notable_features": ["the Hall of Heroes honoring fallen warriors", "enchanted armory", "strategy rooms with magical maps"]
        },
        {
            "name": "The Crossroads",
            "description": "A neutral meeting ground where representatives from all courts can gather safely. The area exists in a pocket dimension accessible through various portals, featuring a circular pavilion made of crystal that refracts light into rainbow patterns. The ground is covered in smooth stones from each court's territory, and the air itself seems to hum with protective magic that prevents violence and encourages honest discourse. Ancient trees from each court's lands grow here, their roots intertwined as a symbol of potential unity.",
            "type": "neutral_ground",
            "magical_properties": ["violence prevention wards", "truth compulsion fields", "universal translation magic", "temporal stability"],
            "atmosphere": "neutral and diplomatic",
            "notable_features": ["the Circle of Voices for formal negotiations", "memory pools that record important agreements", "the Harmony Grove for private conversations"]
        },
        {
            "name": "The Shadow Veil",
            "description": "A mysterious border region between the mortal world and the Fae realms, where reality becomes fluid and dangerous. The landscape shifts constantly, showing glimpses of different courts' territories or mortal lands depending on the observer's state of mind. Ancient ruins dot the area - remnants of civilizations that existed before the current court system. The air shimmers with unstable magic, and travelers report seeing visions of possible futures or forgotten pasts. This is where the barriers between worlds are thinnest.",
            "type": "border_realm",
            "magical_properties": ["reality distortion", "prophetic visions", "dimensional instability", "ancient magic remnants"],
            "atmosphere": "dangerous and unpredictable",
            "notable_features": ["the Oracle's Pool for seeking visions", "ruins of the First Palace", "the Whispering Stones that hold ancient memories"]
        },
        {
            "name": "Mortal Border Town",
            "description": "A small human settlement that exists on the edge of Fae territory, where mortals who know about the Fae world live under special protections. The town features a mix of human architecture and subtle Fae influences - iron gates for protection, but also gardens that bloom with impossible beauty. The inhabitants are a mix of humans who have dealt with the Fae, those seeking refuge from the magical world, and a few half-Fae individuals trying to find their place between two worlds. The town serves as a crucial meeting point for diplomatic relations.",
            "type": "border_settlement",
            "magical_properties": ["protective iron barriers", "truth-seeing wells", "communication stones", "healing herbs"],
            "atmosphere": "cautious but hopeful",
            "notable_features": ["the Sanctuary Inn for travelers", "the Market of Two Worlds", "the Memorial Garden for those lost to Fae conflicts"]
        }
    ],
    "location_connections": [
        {"from": "Night Court Palace", "to": "The Crossroads", "bidirectional": true, "travel_method": "winnowing portal"},
        {"from": "Dawn Court Embassy", "to": "The Crossroads", "bidirectional": true, "travel_method": "light bridge"},
        {"from": "Autumn Court Barracks", "to": "The Crossroads", "bidirectional": true, "travel_method": "earth path"},
        {"from": "The Crossroads", "to": "The Shadow Veil", "bidirectional": true, "travel_method": "dimensional gateway"},
        {"from": "The Shadow Veil", "to": "Mortal Border Town", "bidirectional": true, "travel_method": "reality bridge"},
        {"from": "Night Court Palace", "to": "The Shadow Veil", "bidirectional": true, "travel_method": "shadow walk"},
        {"from": "Dawn Court Embassy", "to": "Mortal Border Town", "bidirectional": true, "travel_method": "diplomatic route"},
        {"from": "Autumn Court Barracks", "to": "Mortal Border Town", "bidirectional": true, "travel_method": "patrol path"}
    ],
    "world_state": {
        "current_season": "Late Autumn",
        "political_climate": "tense but stable",
        "magical_conditions": "heightened due to approaching celestial alignment",
        "recent_events": ["peace treaty negotiations between courts", "reports of shadow creatures near borders", "discovery of ancient artifacts"],
        "ongoing_conflicts": ["territorial disputes", "trade disagreements", "differing views on mortal relations"],
        "prophecies": ["The Starborn shall unite the courts when darkness rises", "Three courts shall stand as one against the shadow's return"]
    }
}

CUSTOM_NARRATOR_DATA = {
    "style": "epic_fantasy",
    "tone": "dramatic and immersive",
    "intervention_frequency": "high",
    "preferred_themes": ["political intrigue", "romantic tension", "magical conflicts", "personal growth", "sacrifice and loyalty"],
    "event_types": [
        "magical_phenomena",
        "political_revelations", 
        "romantic_moments",
        "combat_encounters",
        "prophecy_fulfillment",
        "court_intrigue",
        "power_manifestations"
    ],
    "narrative_focus": "character development through conflict and choice",
    "pacing": "builds tension gradually with explosive climactic moments",
    "description_style": "rich sensory details with emphasis on magical elements"
}

CUSTOM_OVERSEER_DATA = {
    "documentation_style": "epic chronicle",
    "chapter_structure": "follows character arcs and political developments",
    "focus_areas": ["character relationships", "political maneuvering", "magical development", "world-building details"],
    "narrative_voice": "omniscient chronicler with deep knowledge of Fae history",
    "story_elements_tracking": [
        "romantic relationships and tension",
        "political alliances and betrayals", 
        "magical power growth and challenges",
        "prophecy fulfillment progress",
        "court dynamics and conflicts"
    ],
    "ending_criteria": {
        "character_development_threshold": 0.8,
        "relationship_complexity_minimum": 3,
        "political_resolution_required": true,
        "magical_arc_completion": true
    },
    "story_quality_metrics": ["emotional depth", "political complexity", "magical consistency", "character growth", "world immersion"]
}
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