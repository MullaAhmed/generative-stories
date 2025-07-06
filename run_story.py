#!/usr/bin/env python3
"""
Simple runner script for Generative Stories with Space Opera Configuration
"""

import os
import sys
from src.utils.data_loaders import list_saved_simulations
from src.config.settings import settings

# Add stories directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Base simulation configuration (replaces config/simulation_config.json)
CUSTOM_BASE_CONFIG = {
    "simulation": {
        "max_time_steps": 100,
        "time_unit": "hour",
        "auto_save_interval": 10,
        "random_seed": None
    },
    "story": {
        "theme": "space_opera_drama",
        "genre": "space_opera",
        "target_length": "long",
        "ending_conditions": {
            "max_interactions": 300,
            "satisfaction_threshold": 0.8,
            "stagnation_threshold": 0.3,
            "min_story_length": 30
        }
    },
    "memory": {
        "max_memories_per_agent": 150,
        "compression_threshold": 120,
        "compression_ratio": 0.6,
        "memory_types": [
            "interaction",
            "observation",
            "thought",
            "emotion",
            "goal_update",
            "technological_enhancement",
            "political_development"
        ]
    },
    "text_generation": {
        "model": "gemini-flash",
        # "max_tokens": ,
        "temperature": 1,
        "response_format": "natural"
    }
}

# Sarah J. Maas inspired space opera configuration
CUSTOM_CHARACTER_DATA = {
    "agents": [
        {
            "name": "Zara Voidheart",
            "description": "A fierce Stellar Operative with cybernetic violet eyes that can interface directly with quantum networks. Once a baseline human from the Outer Rim colonies, she was enhanced with experimental nanotechnology during the Void War. Her beauty is striking yet artificial - perfect features sculpted by genetic modification, with neural interface ports along her temples that glow softly when active. Intricate bio-luminescent tattoos map her body, each one representing a mission completed or a life saved.",
            "personality_traits": ["fierce", "protective", "stubborn", "loyal", "quick-tempered", "compassionate", "strategic", "tech-savvy"],
            "background": "Born on a mining colony in the Kepler Sector, Zara was recruited by the Shadow Fleet after her family was killed in a corporate raid. She volunteered for the experimental Void Walker program, trading her baseline humanity for enhanced abilities and a chance at revenge. Now she serves as a liaison between the major galactic powers while hunting for the truth behind the ancient AI prophecies that seem to predict galactic war.",
            "starting_location": "Shadow Fleet Command",
            "goals": ["protect the Outer Rim colonies from corporate exploitation", "master her quantum enhancement abilities", "uncover the truth about the AI prophecies", "forge peace between the galactic powers"],
            "fears": ["losing her remaining humanity to the enhancements", "her past being used against innocent people", "the quantum void consuming her consciousness", "failing those who depend on her"],
            "technological_abilities": ["quantum phase shifting", "enhanced reflexes and strength", "truth-detection algorithms", "consciousness projection"],
            "relationships": {"Kai": 0.3, "Sera": -0.2, "Thane": 0.1}
        },
        {
            "name": "Kai Shadowborn",
            "description": "The enigmatic Admiral of the Shadow Fleet, with jet-black hair and cybernetic eyes that shift between deep blue and silver depending on his neural activity. His presence commands both fear and respect, his body enhanced with military-grade augmentations that make him faster and stronger than baseline humans. Decades of command show in his bearing, and his hands bear scars from both physical battles and neural interface burns. His smile can be devastatingly charming or coldly calculating, depending on the situation.",
            "personality_traits": ["calculating", "protective", "mysterious", "charismatic", "ruthlessly efficient", "deeply loyal", "burdened by command"],
            "background": "Born in the deep space stations of the Shadow Sector, Kai rose through the ranks during the Corporate Wars, becoming the youngest Admiral in Shadow Fleet history. His fleet specializes in intelligence gathering and covert operations, but also in protecting colonies that can't protect themselves. He carries the burden of classified knowledge about ancient alien threats and rogue AIs that still lurk in the dark between stars.",
            "starting_location": "Shadow Fleet Command",
            "goals": ["protect the Shadow Sector from corporate and alien threats", "maintain the balance of power between galactic factions", "train Zara in quantum combat", "prevent the awakening of the Void Entities"],
            "fears": ["his fleet being corrupted by alien influence", "losing his crew to endless wars", "the ancient alien darkness returning", "becoming the tyrant others believe him to be"],
            "technological_abilities": ["quantum stealth systems", "neural firewalls", "instantaneous fleet communication", "void energy manipulation", "tactical precognition"],
            "relationships": {"Zara": 0.4, "Sera": -0.5, "Thane": 0.2}
        },
        {
            "name": "Sera Lightbringer",
            "description": "The radiant Chancellor of the Solar Federation, with golden hair enhanced with fiber-optic strands that shimmer with data streams, and amber eyes that burn with both intelligence and righteous fury. Her beauty is enhanced but not artificial - genetic optimization rather than crude modification. She wears flowing robes embedded with holographic displays and energy conduits, and her presence seems to brighten any room through both charisma and actual light-manipulation technology. Despite her elegant appearance, she's a skilled combatant who fights with plasma weapons and energy shields.",
            "personality_traits": ["righteous", "determined", "prideful", "just", "sometimes inflexible", "passionate", "natural leader", "technologically gifted"],
            "background": "Sera rose to power after her mentor was assassinated during the Corporate Wars, chosen by the Federation's AI Council for her incorruptible moral code and brilliant strategic mind. She has spent years rebuilding the Federation and establishing it as a beacon of hope and order in the galaxy. However, she struggles with the moral compromises that galactic politics demands. Her Federation values transparency, justice, and the protection of all sentient life.",
            "starting_location": "Solar Federation Embassy",
            "goals": ["establish lasting peace between all galactic powers", "root out corporate corruption", "prove the Federation's moral authority", "protect colony worlds from exploitation"],
            "fears": ["compromising her principles for political expediency", "the Federation being seen as weak", "the return of the Corporate Wars", "failing to live up to her mentor's legacy"],
            "technological_abilities": ["solar energy manipulation", "nano-medical systems", "truth-verification algorithms", "defensive energy shields", "data purification protocols"],
            "relationships": {"Zara": -0.1, "Kai": -0.4, "Thane": 0.3}
        },
        {
            "name": "Thane Ironforge",
            "description": "A gruff but honorable General from the Titan Consortium, with rust-colored hair and cybernetic amber eyes that can analyze battlefield conditions in real-time. His body bears the scars of countless battles and the ports of military-grade augmentations. He's built like a fortress but moves with the fluid grace of someone trained in zero-gravity combat. His deep voice carries the authority of command, and he favors practical military gear in earth tones, adorned with the symbols of his house - crossed hammers and a stellar forge.",
            "personality_traits": ["honorable", "straightforward", "protective", "sometimes hot-headed", "deeply loyal", "practical", "values military tradition", "engineering-minded"],
            "background": "Thane serves as the Titan Consortium's military commander and diplomatic liaison. He comes from an ancient line of military engineers who have served the Consortium for generations. His family's territories border the dangerous Void Sectors, making him one of the few leaders who regularly deals with alien threats and understands their dangers. He lost his younger sister in the Void War and has dedicated his life to preventing such tragedies.",
            "starting_location": "Titan Military Complex",
            "goals": ["strengthen military alliances between factions", "honor his fallen sister's memory", "protect the border sectors", "train the next generation of void fighters"],
            "fears": ["another galactic war", "failing to protect those under his command", "the Consortium being drawn into corporate conflicts", "losing more family to politics and war"],
            "technological_abilities": ["gravitational field manipulation", "enhanced physical systems", "weapon system integration", "tactical battlefield analysis", "quantum communication arrays"],
            "relationships": {"Zara": 0.2, "Kai": 0.1, "Sera": 0.4}
        }
    ]
}

CUSTOM_WORLD_DATA = {
    "locations": [
        {
            "name": "Shadow Fleet Command",
            "description": "A massive space station constructed from dark metamaterials that absorb sensor scans, creating an almost invisible presence in space. The walls are lined with quantum processors that display the real-time status of the entire Shadow Fleet, and the floors are made of polished void-glass that seems to contain swirling galaxies. Massive viewports offer breathtaking views of nebulae and distant star systems. The command center features a holographic ceiling that shows the actual positions of all fleet assets across the galaxy. Secret sections and classified chambers are woven throughout the structure, accessible only to those with the highest clearance codes.",
            "type": "military_command_station",
            "technological_properties": ["quantum stealth fields", "truth-detection algorithms in briefing rooms", "time-dilation training chambers", "long-range quantum communication arrays"],
            "atmosphere": "mysterious and militarily powerful",
            "notable_features": ["the Void Chamber for classified meetings", "the Archive of Shadows containing alien intelligence", "zero-gravity combat training facilities"]
        },
        {
            "name": "Solar Federation Embassy",
            "description": "An elegant orbital platform constructed from crystalline solar collectors that glow with captured starlight. Golden energy conduits run through the transparent walls, and the architecture features soaring energy arches and delicate spires that reach toward nearby stars. Hydroponic gardens surrounding the embassy bloom with genetically enhanced flowers that never wilt, their petals shimmering with bioluminescent patterns. The interior is filled with warm, natural light that banishes shadows and creates an atmosphere of openness and transparency. Harmonic resonators throughout the building generate soft, melodic frequencies that promote peace and mental clarity.",
            "type": "diplomatic_station",
            "technological_properties": ["truth-enhancement neural fields", "emotional stabilization systems", "defensive energy barriers", "quantum communication networks"],
            "atmosphere": "serene and inspiring",
            "notable_features": ["the Hall of Galactic Accords for treaty negotiations", "zero-gravity meditation gardens", "the Solar Observatory for important announcements"]
        },
        {
            "name": "Titan Military Complex",
            "description": "A massive fortress-station built from reinforced titanium-steel alloys and quantum-hardened ceramics, designed for both defense and industrial production. The complex is surrounded by automated defense platforms and manufacturing bays that glow with the light of stellar forges. Training areas feature various gravitational obstacles and weapon testing ranges, while the main hall houses a massive holographic fireplace where soldiers gather to share stories and plan campaigns. The architecture emphasizes strength and functionality, with thick armor plating and blast doors that could withstand a fleet bombardment.",
            "type": "military_industrial_complex",
            "technological_properties": ["weapon enhancement forges", "tactical planning rooms with battlefield simulation", "medical nano-bays", "defensive gravitational shields"],
            "atmosphere": "martial and industrious",
            "notable_features": ["the Memorial Hall honoring fallen soldiers", "quantum-enhanced armory", "strategy rooms with real-time galactic maps"]
        },
        {
            "name": "The Nexus Station",
            "description": "A neutral meeting ground where representatives from all galactic powers can gather safely. The station exists in a stable wormhole junction accessible through various hyperspace routes, featuring a circular chamber made of quantum crystal that refracts energy into spectacular light displays. The deck is covered in materials from each faction's home worlds, and the air itself hums with protective energy fields that prevent violence and encourage honest communication. Holographic trees from each faction's territories grow here, their light-roots intertwined as a symbol of potential unity.",
            "type": "neutral_diplomatic_station",
            "technological_properties": ["violence-suppression fields", "truth-verification algorithms", "universal translation matrices", "temporal stabilization generators"],
            "atmosphere": "neutral and diplomatic",
            "notable_features": ["the Circle of Voices for formal negotiations", "quantum memory banks that record agreements", "the Harmony Chamber for private conversations"]
        },
        {
            "name": "The Void Sectors",
            "description": "A mysterious border region between known space and the dark void beyond, where space-time becomes unstable and dangerous. The stellar geography shifts constantly, showing glimpses of different galactic regions or unknown dimensions depending on the observer's quantum state. Ancient alien ruins dot the area - remnants of civilizations that existed before current galactic powers. Space itself shimmers with unstable energy, and travelers report seeing visions of possible futures or forgotten pasts. This is where the barriers between dimensions are thinnest.",
            "type": "border_void_region",
            "technological_properties": ["space-time distortion", "prophetic quantum echoes", "dimensional instability", "ancient alien technology remnants"],
            "atmosphere": "dangerous and unpredictable",
            "notable_features": ["the Oracle Array for seeking quantum visions", "ruins of the First Empire", "the Resonance Crystals that hold ancient memories"]
        },
        {
            "name": "Frontier Colony Alpha-7",
            "description": "A small human settlement that exists on the edge of known space, where colonists who know about the galactic powers live under special protections. The colony features a mix of standard human architecture and advanced alien-influenced technology - defensive barriers for protection, but also gardens that bloom with impossible alien beauty. The inhabitants are a mix of humans who have dealt with various galactic powers, refugees from corporate wars, and a few hybrid individuals trying to find their place between different worlds. The colony serves as a crucial meeting point for diplomatic relations.",
            "type": "frontier_colony",
            "technological_properties": ["defensive energy barriers", "truth-detection sensors", "quantum communication relays", "medical nano-gardens"],
            "atmosphere": "cautious but hopeful",
            "notable_features": ["the Sanctuary Hub for travelers", "the Galactic Trade Center", "the Memorial Plaza for those lost to corporate conflicts"]
        }
    ],
    "location_connections": [
        {"from": "Shadow Fleet Command", "to": "The Nexus Station", "bidirectional": True, "travel_method": "quantum jump portal"},
        {"from": "Solar Federation Embassy", "to": "The Nexus Station", "bidirectional": True, "travel_method": "solar wind highway"},
        {"from": "Titan Military Complex", "to": "The Nexus Station", "bidirectional": True, "travel_method": "gravitational slingshot route"},
        {"from": "The Nexus Station", "to": "The Void Sectors", "bidirectional": True, "travel_method": "dimensional gateway"},
        {"from": "The Void Sectors", "to": "Frontier Colony Alpha-7", "bidirectional": True, "travel_method": "reality anchor bridge"},
        {"from": "Shadow Fleet Command", "to": "The Void Sectors", "bidirectional": True, "travel_method": "stealth corridor"},
        {"from": "Solar Federation Embassy", "to": "Frontier Colony Alpha-7", "bidirectional": True, "travel_method": "diplomatic hyperspace lane"},
        {"from": "Titan Military Complex", "to": "Frontier Colony Alpha-7", "bidirectional": True, "travel_method": "patrol route"}
    ],
    "world_state": {
        "current_galactic_cycle": "Post-Corporate War Era, Cycle 2387",
        "political_climate": "tense but stable",
        "technological_conditions": "heightened due to approaching quantum convergence",
        "recent_events": ["peace treaty negotiations between galactic powers", "reports of void entities near border sectors", "discovery of ancient alien artifacts"],
        "ongoing_conflicts": ["territorial disputes over resource-rich systems", "trade disagreements over quantum technology", "differing views on AI rights and alien contact"],
        "prophecies": ["The Void-touched shall unite the powers when darkness rises", "Three fleets shall stand as one against the ancient return"]
    }
}

CUSTOM_NARRATOR_DATA = {
    "style": "space_opera",
    "tone": "dramatic and immersive",
    "intervention_frequency": "high",
    "intervention_threshold": {
        "low": 0.2,
        "medium": 0.5,
        "high": 2
    },
    "preferred_themes": ["political intrigue", "romantic tension", "technological conflicts", "personal growth", "sacrifice and loyalty", "alien mysteries"],
    "event_types": [
        "quantum_phenomena",
        "political_revelations", 
        "romantic_moments",
        "combat_encounters",
        "prophecy_fulfillment",
        "galactic_intrigue",
        "technological_manifestations",
        "alien_encounters"
    ],
    "preferred_story_elements": [
        "character_development",
        "galactic_politics",
        "technological_advancement",
        "alien_mysteries",
        "romantic_relationships",
        "moral_dilemmas"
    ],
    "narrative_focus": "character development through conflict and choice",
    "pacing": "builds tension gradually with explosive climactic moments",
    "description_style": "rich sensory details with emphasis on technological and cosmic elements"
}

CUSTOM_OVERSEER_DATA = {
    "documentation_style": "galactic_chronicle",
    "chapter_structure": "follows character arcs and interstellar political developments",
    "focus_areas": ["character relationships", "political maneuvering", "technological development", "world-building details", "alien mysteries"],
    "narrative_voice": "omniscient chronicler with deep knowledge of galactic history",
    "story_elements_tracking": [
        "romantic relationships and tension",
        "political alliances and betrayals", 
        "technological enhancement and challenges",
        "prophecy fulfillment progress",
        "galactic power dynamics and conflicts",
        "alien artifact discoveries"
    ],
    "ending_criteria": {
        "character_development_threshold": 0.8,
        "relationship_complexity_minimum": 3,
        "political_resolution_required": True,
        "technological_arc_completion": True,
        "alien_mystery_resolution": True
    },
    "story_quality_metrics": ["emotional depth", "political complexity", "technological consistency", "character growth", "world immersion", "cosmic scope"]
}

def main():
    print("🎭 Generative Stories Runner - Space Opera Edition")
    print("=" * 50)
    
    # Display available LLM providers
    available_providers = []
    if settings.OPENAI_API_KEY:
        available_providers.append("openai")
    if settings.GROQ_API_KEY:
        available_providers.append("groq")
    if settings.GOOGLE_API_KEY:
        available_providers.append("gemini")
    
    if available_providers:
        print(f"🤖 Available LLM providers: {', '.join(available_providers)}")
        print(f"🎯 Default provider: {settings.DEFAULT_LLM_PROVIDER}")
    else:
        print("⚠️ No LLM providers configured. Using mock responses.")
    
    # Check for saved simulations
    saved_sims = list_saved_simulations()
    load_from_save = None
    
    if saved_sims:
        print(f"\n📂 Found {len(saved_sims)} saved simulations:")
        for i, save_file in enumerate(saved_sims[:5], 1):  # Show up to 5 most recent
            print(f"  {i}. {save_file}")
        
        choice = input("\nWould you like to (n)ew simulation or (l)oad saved? (n/l): ").strip().lower()
        
        if choice in ['l', 'load']:
            try:
                save_choice = input("Enter save number (1-5) or filename: ").strip()
                if save_choice.isdigit():
                    save_index = int(save_choice) - 1
                    if 0 <= save_index < len(saved_sims):
                        load_from_save = saved_sims[save_index]
                    else:
                        print("Invalid save number, starting new simulation.")
                else:
                    load_from_save = save_choice
            except:
                print("Invalid input, starting new simulation.")
    
    try:
        # Import the main function from stories
        from src.main import run_simulation
        
        # Run the simulation with custom space opera data
        story_path = run_simulation(
            base_config=CUSTOM_BASE_CONFIG,
            save_name="galactic_convergence_saga",
            verbose=True,
            character_data=CUSTOM_CHARACTER_DATA,
            world_data=CUSTOM_WORLD_DATA,
            narrator_data=CUSTOM_NARRATOR_DATA,
            overseer_data=CUSTOM_OVERSEER_DATA,
            load_from_save=load_from_save
        )
        
        if story_path:
            print(f"\n🌟 Space Opera story generated successfully!")
            print(f"📖 Your galactic saga is available at: {story_path}")
            
            # Ask if user wants to read the story
            read_choice = input("\nWould you like to read the story now? (y/n): ").strip().lower()
            if read_choice in ['y', 'yes']:
                try:
                    with open(story_path, 'r', encoding='utf-8') as f:
                        story_content = f.read()
                    print("\n" + "=" * 60)
                    print("🚀 YOUR GENERATED SPACE OPERA STORY 🚀")
                    print("=" * 60)
                    print(story_content)
                    print("=" * 60)
                except Exception as e:
                    print(f"Error reading story file: {e}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed:")
        print("pip install google-generativeai python-dotenv")
        
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()