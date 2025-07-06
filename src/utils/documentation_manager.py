"""
Documentation Manager - Handles structured saving of story data for resumption and analysis
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class DocumentationManager:
    """
    Manages structured documentation and data storage for stories
    """
    
    def __init__(self, story_title: str = None):
        self.story_title = story_title or f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.base_directory = Path("data") / "stories" / self.story_title
        self.ensure_directory_structure()
    
    def ensure_directory_structure(self):
        """Create the directory structure for the story"""
        directories = [
            self.base_directory,
            self.base_directory / "raw_data",
            self.base_directory / "conversations",
            self.base_directory / "locations",
            self.base_directory / "characters",
            self.base_directory / "events",
            self.base_directory / "simulation_state",
            self.base_directory / "memory_data",
            self.base_directory / "relationships",
            self.base_directory / "narrative_output"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_simulation_state(self, simulation_engine) -> bool:
        """Save the complete simulation state for resumption"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save complete simulation state
            simulation_data = simulation_engine.to_dict()
            simulation_file = self.base_directory / "simulation_state" / f"simulation_{timestamp}.json"
            
            with open(simulation_file, 'w', encoding='utf-8') as f:
                json.dump(simulation_data, f, indent=2, ensure_ascii=False)
            
            # Save latest state as well for easy access
            latest_file = self.base_directory / "simulation_state" / "latest_state.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(simulation_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Simulation state saved to: {simulation_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving simulation state: {e}")
            return False
    
    def save_character_data(self, agents: List) -> bool:
        """Save detailed character data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save individual character files
            for agent in agents:
                character_data = {
                    'basic_info': {
                        'name': agent.name,
                        'description': agent.description,
                        'personality_traits': agent.personality_traits,
                        'background': agent.background,
                        'goals': agent.goals,
                        'fears': agent.fears
                    },
                    'current_state': {
                        'location': agent.location,
                        'current_mood': agent.current_mood,
                        'stress_level': agent.stress_level,
                        'energy_level': agent.energy_level,
                        'interaction_count': agent.interaction_count,
                        'last_interaction_time': agent.last_interaction_time
                    },
                    'relationships': agent.relationships.copy(),
                    'technological_abilities': getattr(agent, 'technological_abilities', []),
                    'memory_summary': None
                }
                
                # Get memory summary if available
                if agent.memory:
                    try:
                        character_data['memory_summary'] = agent.memory.get_memory_summary()
                    except Exception as e:
                        print(f"Warning: Could not get memory summary for {agent.name}: {e}")
                
                # Save character file
                char_file = self.base_directory / "characters" / f"{agent.name.replace(' ', '_')}_{timestamp}.json"
                with open(char_file, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, indent=2, ensure_ascii=False)
            
            # Save consolidated character data
            all_characters = {
                'timestamp': timestamp,
                'characters': [agent.to_dict() for agent in agents],
                'character_count': len(agents)
            }
            
            consolidated_file = self.base_directory / "characters" / f"all_characters_{timestamp}.json"
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(all_characters, f, indent=2, ensure_ascii=False)
            
            # Save latest characters
            latest_file = self.base_directory / "characters" / "latest_characters.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(all_characters, f, indent=2, ensure_ascii=False)
            
            print(f"👥 Character data saved for {len(agents)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Error saving character data: {e}")
            return False
    
    def save_location_data(self, environment) -> bool:
        """Save detailed location and environment data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save individual location files
            for location_name, location in environment.locations.items():
                location_data = {
                    'basic_info': {
                        'name': location.name,
                        'description': location.description,
                        'location_type': location.location_type,
                        'atmosphere': location.atmosphere
                    },
                    'connections': location.connected_locations.copy(),
                    'objects': location.objects.copy(),
                    'current_agents': location.get_agent_names(),
                    'events_history': location.events_history.copy(),
                    'technological_properties': getattr(location, 'technological_properties', []),
                    'notable_features': getattr(location, 'notable_features', [])
                }
                
                loc_file = self.base_directory / "locations" / f"{location_name.replace(' ', '_')}_{timestamp}.json"
                with open(loc_file, 'w', encoding='utf-8') as f:
                    json.dump(location_data, f, indent=2, ensure_ascii=False)
            
            # Save consolidated environment data
            environment_data = {
                'timestamp': timestamp,
                'environment_state': environment.to_dict(),
                'world_summary': environment.get_world_state_summary(),
                'location_count': len(environment.locations),
                'current_time': environment.current_time,
                'weather': environment.weather,
                'season': environment.season
            }
            
            env_file = self.base_directory / "locations" / f"environment_{timestamp}.json"
            with open(env_file, 'w', encoding='utf-8') as f:
                json.dump(environment_data, f, indent=2, ensure_ascii=False)
            
            # Save latest environment
            latest_file = self.base_directory / "locations" / "latest_environment.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(environment_data, f, indent=2, ensure_ascii=False)
            
            print(f"🌍 Location data saved for {len(environment.locations)} locations")
            return True
            
        except Exception as e:
            print(f"❌ Error saving location data: {e}")
            return False
    
    def save_conversation_data(self, overseer) -> bool:
        """Save all conversation and interaction data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save all interactions
            interactions_data = {
                'timestamp': timestamp,
                'total_interactions': len(overseer.interaction_history),
                'interactions': overseer.interaction_history.copy()
            }
            
            interactions_file = self.base_directory / "conversations" / f"interactions_{timestamp}.json"
            with open(interactions_file, 'w', encoding='utf-8') as f:
                json.dump(interactions_data, f, indent=2, ensure_ascii=False)
            
            # Save interactions by character pairs
            character_conversations = {}
            for interaction in overseer.interaction_history:
                participants = interaction.get('participants', [])
                if len(participants) >= 2:
                    # Create sorted key for consistent pairing
                    pair_key = tuple(sorted(participants[:2]))
                    if pair_key not in character_conversations:
                        character_conversations[pair_key] = []
                    character_conversations[pair_key].append(interaction)
            
            # Save individual conversation files
            for pair, conversations in character_conversations.items():
                pair_name = f"{pair[0]}_and_{pair[1]}".replace(' ', '_')
                conv_file = self.base_directory / "conversations" / f"{pair_name}_{timestamp}.json"
                
                conversation_data = {
                    'participants': list(pair),
                    'conversation_count': len(conversations),
                    'conversations': conversations
                }
                
                with open(conv_file, 'w', encoding='utf-8') as f:
                    json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            # Save latest interactions
            latest_file = self.base_directory / "conversations" / "latest_interactions.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(interactions_data, f, indent=2, ensure_ascii=False)
            
            print(f"💬 Conversation data saved: {len(overseer.interaction_history)} interactions")
            return True
            
        except Exception as e:
            print(f"❌ Error saving conversation data: {e}")
            return False
    
    def save_event_data(self, overseer, narrator) -> bool:
        """Save all event data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save overseer events
            overseer_events = {
                'timestamp': timestamp,
                'total_events': len(overseer.event_history),
                'major_events': overseer.story_metadata.get('major_events', []),
                'all_events': overseer.event_history.copy()
            }
            
            overseer_file = self.base_directory / "events" / f"overseer_events_{timestamp}.json"
            with open(overseer_file, 'w', encoding='utf-8') as f:
                json.dump(overseer_events, f, indent=2, ensure_ascii=False)
            
            # Save narrator events
            narrator_events = {
                'timestamp': timestamp,
                'event_history': narrator.event_history.copy(),
                'story_health_metrics': narrator.story_health_metrics.copy(),
                'intervention_history': {
                    'last_intervention_time': narrator.last_intervention_time,
                    'steps_since_last_event': narrator.steps_since_last_event,
                    'total_events': len(narrator.event_history)
                }
            }
            
            narrator_file = self.base_directory / "events" / f"narrator_events_{timestamp}.json"
            with open(narrator_file, 'w', encoding='utf-8') as f:
                json.dump(narrator_events, f, indent=2, ensure_ascii=False)
            
            # Save consolidated events
            all_events = {
                'timestamp': timestamp,
                'overseer_events': overseer_events,
                'narrator_events': narrator_events,
                'total_event_count': len(overseer.event_history) + len(narrator.event_history)
            }
            
            consolidated_file = self.base_directory / "events" / f"all_events_{timestamp}.json"
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(all_events, f, indent=2, ensure_ascii=False)
            
            # Save latest events
            latest_file = self.base_directory / "events" / "latest_events.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(all_events, f, indent=2, ensure_ascii=False)
            
            print(f"🎪 Event data saved: {len(overseer.event_history)} overseer events, {len(narrator.event_history)} narrator events")
            return True
            
        except Exception as e:
            print(f"❌ Error saving event data: {e}")
            return False
    
    def save_relationship_data(self, agents: List, overseer) -> bool:
        """Save detailed relationship data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Collect all relationship data
            relationship_data = {
                'timestamp': timestamp,
                'agent_relationships': {},
                'relationship_changes': overseer.character_relationship_changes.copy(),
                'relationship_matrix': {}
            }
            
            # Save individual agent relationships
            for agent in agents:
                relationship_data['agent_relationships'][agent.name] = {
                    'relationships': agent.relationships.copy(),
                    'relationship_count': len(agent.relationships),
                    'strongest_positive': max(agent.relationships.values()) if agent.relationships else 0,
                    'strongest_negative': min(agent.relationships.values()) if agent.relationships else 0
                }
            
            # Create relationship matrix
            agent_names = [agent.name for agent in agents]
            for i, agent1 in enumerate(agent_names):
                relationship_data['relationship_matrix'][agent1] = {}
                for j, agent2 in enumerate(agent_names):
                    if i != j:
                        # Get relationship score from agent1's perspective
                        agent1_obj = next((a for a in agents if a.name == agent1), None)
                        if agent1_obj:
                            score = agent1_obj.relationships.get(agent2, 0.0)
                            relationship_data['relationship_matrix'][agent1][agent2] = score
                        else:
                            relationship_data['relationship_matrix'][agent1][agent2] = 0.0
            
            # Save relationship data
            rel_file = self.base_directory / "relationships" / f"relationships_{timestamp}.json"
            with open(rel_file, 'w', encoding='utf-8') as f:
                json.dump(relationship_data, f, indent=2, ensure_ascii=False)
            
            # Save latest relationships
            latest_file = self.base_directory / "relationships" / "latest_relationships.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(relationship_data, f, indent=2, ensure_ascii=False)
            
            print(f"💕 Relationship data saved for {len(agents)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Error saving relationship data: {e}")
            return False
    
    def save_memory_data(self, memory_manager, agents: List) -> bool:
        """Save memory system data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save memory manager state
            memory_state = {
                'timestamp': timestamp,
                'memory_manager_state': memory_manager.to_dict(),
                'agent_memory_summaries': {}
            }
            
            # Get memory summaries for each agent
            for agent in agents:
                if agent.memory:
                    try:
                        memory_state['agent_memory_summaries'][agent.name] = agent.memory.get_memory_summary()
                    except Exception as e:
                        print(f"Warning: Could not get memory summary for {agent.name}: {e}")
                        memory_state['agent_memory_summaries'][agent.name] = {
                            'error': str(e),
                            'total_memories': 0
                        }
            
            # Save memory data
            memory_file = self.base_directory / "memory_data" / f"memory_state_{timestamp}.json"
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_state, f, indent=2, ensure_ascii=False)
            
            # Save latest memory state
            latest_file = self.base_directory / "memory_data" / "latest_memory_state.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(memory_state, f, indent=2, ensure_ascii=False)
            
            print(f"🧠 Memory data saved for {len(agents)} agents")
            return True
            
        except Exception as e:
            print(f"❌ Error saving memory data: {e}")
            return False
    
    def save_narrative_output(self, overseer) -> bool:
        """Save the narrative output (chapters and story)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save complete story
            story_text = overseer.generate_story_summary()
            story_file = self.base_directory / "narrative_output" / f"complete_story_{timestamp}.txt"
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(story_text)
            
            # Save story data
            story_data = {
                'timestamp': timestamp,
                'story_text': story_text,
                'chapters': overseer.chapters.copy(),
                'chapter_summaries': overseer.chapter_summaries.copy(),
                'story_metadata': overseer.story_metadata.copy(),
                'character_arcs': overseer.character_arcs.copy()
            }
            
            story_json_file = self.base_directory / "narrative_output" / f"story_data_{timestamp}.json"
            with open(story_json_file, 'w', encoding='utf-8') as f:
                json.dump(story_data, f, indent=2, ensure_ascii=False)
            
            # Save latest story
            latest_text_file = self.base_directory / "narrative_output" / "latest_story.txt"
            with open(latest_text_file, 'w', encoding='utf-8') as f:
                f.write(story_text)
            
            latest_json_file = self.base_directory / "narrative_output" / "latest_story_data.json"
            with open(latest_json_file, 'w', encoding='utf-8') as f:
                json.dump(story_data, f, indent=2, ensure_ascii=False)
            
            print(f"📖 Narrative output saved: {len(overseer.chapters)} chapters")
            return True
            
        except Exception as e:
            print(f"❌ Error saving narrative output: {e}")
            return False
    
    def save_raw_data_dump(self, simulation_engine) -> bool:
        """Save a complete raw data dump for debugging and analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create comprehensive raw data
            raw_data = {
                'timestamp': timestamp,
                'simulation_metadata': {
                    'current_step': simulation_engine.current_step,
                    'max_time_steps': simulation_engine.max_time_steps,
                    'simulation_running': simulation_engine.simulation_running,
                    'story_title': self.story_title
                },
                'complete_simulation_state': simulation_engine.to_dict(),
                'agent_details': [agent.to_dict() for agent in simulation_engine.story_agents],
                'environment_state': simulation_engine.environment.to_dict(),
                'narrator_state': simulation_engine.narrator.to_dict(),
                'overseer_state': simulation_engine.overseer.to_dict(),
                'memory_manager_state': simulation_engine.memory_manager.to_dict()
            }
            
            # Save raw data dump
            raw_file = self.base_directory / "raw_data" / f"complete_dump_{timestamp}.json"
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
            # Save latest raw data
            latest_file = self.base_directory / "raw_data" / "latest_complete_dump.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Raw data dump saved: {len(raw_data)} top-level keys")
            return True
            
        except Exception as e:
            print(f"❌ Error saving raw data dump: {e}")
            return False
    
    def save_documentation_index(self, simulation_engine) -> bool:
        """Save an index file that describes all saved data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create documentation index
            index_data = {
                'story_title': self.story_title,
                'creation_timestamp': timestamp,
                'story_metadata': {
                    'total_steps': simulation_engine.current_step,
                    'total_agents': len(simulation_engine.story_agents),
                    'total_locations': len(simulation_engine.environment.locations),
                    'total_interactions': simulation_engine.overseer.story_metadata['total_interactions'],
                    'total_chapters': len(simulation_engine.overseer.chapters),
                    'story_theme': simulation_engine.config.get('story', {}).get('theme', 'unknown')
                },
                'directory_structure': {
                    'raw_data': 'Complete simulation dumps for full state restoration',
                    'conversations': 'All character interactions and dialogue',
                    'locations': 'Environment and location data',
                    'characters': 'Character states, relationships, and development',
                    'events': 'All story events from narrator and overseer',
                    'simulation_state': 'Simulation engine state for resumption',
                    'memory_data': 'Memory system data and agent memories',
                    'relationships': 'Character relationship matrices and changes',
                    'narrative_output': 'Generated story text and chapters'
                },
                'resumption_files': {
                    'primary': 'simulation_state/latest_state.json',
                    'backup': f'raw_data/complete_dump_{timestamp}.json',
                    'character_data': 'characters/latest_characters.json',
                    'environment_data': 'locations/latest_environment.json',
                    'memory_data': 'memory_data/latest_memory_state.json'
                },
                'analysis_files': {
                    'conversations': 'conversations/latest_interactions.json',
                    'relationships': 'relationships/latest_relationships.json',
                    'events': 'events/latest_events.json',
                    'story_output': 'narrative_output/latest_story_data.json'
                }
            }
            
            # Save index
            index_file = self.base_directory / "README.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            # Also save as markdown for human readability
            readme_md = self.base_directory / "README.md"
            with open(readme_md, 'w', encoding='utf-8') as f:
                f.write(f"# {self.story_title}\n\n")
                f.write(f"Generated on: {timestamp}\n\n")
                f.write(f"## Story Statistics\n")
                f.write(f"- Total Steps: {simulation_engine.current_step}\n")
                f.write(f"- Characters: {len(simulation_engine.story_agents)}\n")
                f.write(f"- Locations: {len(simulation_engine.environment.locations)}\n")
                f.write(f"- Interactions: {simulation_engine.overseer.story_metadata['total_interactions']}\n")
                f.write(f"- Chapters: {len(simulation_engine.overseer.chapters)}\n\n")
                f.write(f"## Directory Structure\n")
                for dir_name, description in index_data['directory_structure'].items():
                    f.write(f"- `{dir_name}/`: {description}\n")
                f.write(f"\n## Key Files for Resumption\n")
                f.write(f"- Primary: `{index_data['resumption_files']['primary']}`\n")
                f.write(f"- Backup: `{index_data['resumption_files']['backup']}`\n")
                f.write(f"- Character Data: `{index_data['resumption_files']['character_data']}`\n")
                f.write(f"- Environment: `{index_data['resumption_files']['environment_data']}`\n")
            
            print(f"📋 Documentation index saved")
            return True
            
        except Exception as e:
            print(f"❌ Error saving documentation index: {e}")
            return False
    
    def save_complete_documentation(self, simulation_engine) -> bool:
        """Save all documentation and data"""
        print(f"\n📁 Saving complete documentation for '{self.story_title}'...")
        
        success_count = 0
        total_operations = 9
        
        operations = [
            ("Simulation State", lambda: self.save_simulation_state(simulation_engine)),
            ("Character Data", lambda: self.save_character_data(simulation_engine.story_agents)),
            ("Location Data", lambda: self.save_location_data(simulation_engine.environment)),
            ("Conversation Data", lambda: self.save_conversation_data(simulation_engine.overseer)),
            ("Event Data", lambda: self.save_event_data(simulation_engine.overseer, simulation_engine.narrator)),
            ("Relationship Data", lambda: self.save_relationship_data(simulation_engine.story_agents, simulation_engine.overseer)),
            ("Memory Data", lambda: self.save_memory_data(simulation_engine.memory_manager, simulation_engine.story_agents)),
            ("Narrative Output", lambda: self.save_narrative_output(simulation_engine.overseer)),
            ("Raw Data Dump", lambda: self.save_raw_data_dump(simulation_engine))
        ]
        
        for operation_name, operation_func in operations:
            try:
                if operation_func():
                    success_count += 1
                    print(f"  ✅ {operation_name}")
                else:
                    print(f"  ❌ {operation_name}")
            except Exception as e:
                print(f"  ❌ {operation_name}: {e}")
        
        # Always try to save the index
        try:
            if self.save_documentation_index(simulation_engine):
                success_count += 1
                print(f"  ✅ Documentation Index")
            else:
                print(f"  ❌ Documentation Index")
        except Exception as e:
            print(f"  ❌ Documentation Index: {e}")
        
        print(f"\n📊 Documentation saved: {success_count}/{total_operations + 1} operations successful")
        print(f"📂 Story directory: {self.base_directory}")
        
        return success_count >= (total_operations * 0.8)  # 80% success rate
    
    @classmethod
    def load_simulation_from_directory(cls, story_title: str) -> Optional[Dict]:
        """Load a simulation from a story directory"""
        try:
            base_directory = Path("data") / "stories" / story_title
            
            # Try to load from latest state first
            latest_state_file = base_directory / "simulation_state" / "latest_state.json"
            if latest_state_file.exists():
                with open(latest_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Try to load from raw data dump
            latest_dump_file = base_directory / "raw_data" / "latest_complete_dump.json"
            if latest_dump_file.exists():
                with open(latest_dump_file, 'r', encoding='utf-8') as f:
                    dump_data = json.load(f)
                    return dump_data.get('complete_simulation_state')
            
            print(f"❌ No loadable simulation state found in {base_directory}")
            return None
            
        except Exception as e:
            print(f"❌ Error loading simulation from directory: {e}")
            return None
    
    @classmethod
    def list_story_directories(cls) -> List[str]:
        """List all available story directories"""
        try:
            stories_dir = Path("data") / "stories"
            if not stories_dir.exists():
                return []
            
            story_dirs = []
            for item in stories_dir.iterdir():
                if item.is_dir():
                    story_dirs.append(item.name)
            
            return sorted(story_dirs, reverse=True)  # Most recent first
            
        except Exception as e:
            print(f"❌ Error listing story directories: {e}")
            return []