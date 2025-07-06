# Simulation Engine - Main simulation loop orchestrating interactions between agents and environment

import random
from typing import Dict, List, Any, Optional
from src.agents.story_agent import StoryAgent
from src.agents.narrator_agent import NarratorAgent
from src.agents.overseer_agent import OverseerAgent
from src.environment.environment_manager import EnvironmentStateManager
from src.utils.memory_management import MemoryManager, AgentMemoryInterface
from src.utils.text_generation import analyze_sentiment, generate_new_character

class SimulationEngine:
    """
    Main simulation loop, orchestrating the interactions between agents and the environment.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.environment = EnvironmentStateManager()
        self.narrator = NarratorAgent()
        self.overseer = OverseerAgent()
        self.memory_manager = MemoryManager(config.get('memory', {}))
        
        self.story_agents = []
        self.simulation_running = False
        self.max_time_steps = config.get('simulation', {}).get('max_time_steps', 100)
        self.current_step = 0
        
        # Story ending detection
        self.ending_metrics = {
            'character_satisfaction': 0,
            'conflict_resolution': 0,
            'narrative_coherence': 0,
            'story_momentum': 0
        }
        
        # Simulation state
        self.interactions_this_step = []
        self.events_this_step = []
        
    def initialize_simulation(self, initial_config: Dict):
        """Initialize the simulation with agents, locations, and initial state"""
        
        print("🎬 Initializing simulation...")
        
        # Create locations
        for location_data in initial_config.get('locations', []):
            self.environment.add_location(
                location_data['name'],
                location_data['description'],
                location_data.get('type', 'general')
            )
        
        # Connect locations
        for connection in initial_config.get('location_connections', []):
            self.environment.connect_locations(
                connection['from'],
                connection['to'],
                connection.get('bidirectional', True)
            )
        
        # Create story agents
        for agent_data in initial_config.get('agents', []):
            agent = StoryAgent(
                agent_data['name'],
                agent_data['description'],
                agent_data.get('personality_traits', []),
                agent_data.get('background', ''),
                agent_data['starting_location'],
                agent_data.get('goals', []),
                agent_data.get('fears', [])
            )
            
            # Set up memory interface for agent
            memory_interface = AgentMemoryInterface(agent.name, self.memory_manager)
            agent.set_memory_interface(memory_interface)
            
            self.story_agents.append(agent)
            self.environment.move_agent(agent, None, agent.location)
        
        # Initialize overseer
        self.overseer.story_metadata['start_time'] = 0
        
        print(f"✅ Initialized {len(self.story_agents)} agents in {len(self.environment.locations)} locations")
    
    def run_simulation_step(self) -> bool:
        """Execute one step of the simulation"""
        
        self.current_step += 1
        self.interactions_this_step = []
        self.events_this_step = []
        
        print(f"\n⏰ Step {self.current_step}")
        
        # Auto-save every 10 steps
        if self.current_step % 10 == 0:
            from src.utils.data_loaders import save_simulation_state
            save_simulation_state(self, f"auto_save_step_{self.current_step}")
            print(f"💾 Auto-saved at step {self.current_step}")
        
        # 1. Process scheduled events
        scheduled_events = self.environment.process_scheduled_events()
        for event in scheduled_events:
            self.process_event(event)
        
        # 2. Agent interaction phase
        self.process_agent_interactions()
        
        # 3. Agent action phase (for agents who didn't interact)
        self.process_agent_actions()
        
        # 4. Update agent emotional states
        self.update_agent_states()
        
        # 5. Narrator analysis and potential intervention
        self.narrator.analyze_story_state(self.story_agents, self.environment, self.current_step)
        intervention_level = self.narrator.evaluate_intervention_need()
        
        if intervention_level != "none":
            print(f"📝 Narrator intervention needed: {intervention_level}")
            self.process_narrator_intervention()
        
        # 5.5. Check if new character should be introduced
        if self.narrator.should_introduce_new_character(self.story_agents, self.environment, self.current_step):
            print("👤 Introducing new character to enhance story dynamics...")
            self.introduce_new_character()
        
        # 6. Overseer documentation
        for interaction in self.interactions_this_step:
            self.overseer.observe_interaction(interaction)
            
            # Track character development for each participant
            for participant_name in interaction.get('participants', []):
                participant_agent = next((agent for agent in self.story_agents if agent.name == participant_name), None)
                if participant_agent:
                    self.overseer.track_character_development(participant_agent, interaction)
        
        for event in self.events_this_step:
            self.overseer.observe_event(event)
        
        # 7. Check for dynamic chapter generation
        chapter_decision = self.overseer.should_end_current_chapter(self.current_step)
        
        if chapter_decision['should_end']:
            chapter = self.overseer.synthesize_chapter(self.current_step)
            print(f"📖 {chapter}")
            print(f"   📊 Chapter ended due to: {', '.join(chapter_decision['reasons'])}")
            print(f"   📈 Chapter significance: {chapter_decision.get('ending_score', 0):.2f}")
        
        # Force chapter generation every 500 steps as backup
        elif self.current_step % 500 == 0:
            chapter = self.overseer.synthesize_chapter(self.current_step, force_end=True)
            print(f"📖 {chapter}")
            print(f"   ⏰ Chapter ended due to step limit (500 steps)")
        
        # 8. Check for story ending conditions
        if self.check_ending_conditions():
            print("🎭 Story ending conditions met")
            self.conclude_story()
            return False
        
        # 9. Advance time
        self.environment.advance_time(1)
        
        return True
    
    def process_agent_interactions(self):
        """Process interactions between agents in the same locations"""
        
        # Track which agents have interacted this step
        interacted_agents = set()
        
        # Shuffle agents for random interaction order
        agents_copy = self.story_agents.copy()
        random.shuffle(agents_copy)
        
        for agent in agents_copy:
            if agent.name in interacted_agents:
                continue
            
            # Check if agent wants to initiate interaction
            if agent.should_initiate_interaction(self.story_agents, self.current_step):
                
                # Find available targets in same location
                available_targets = [
                    other for other in self.story_agents 
                    if (other.location == agent.location and 
                        other.name != agent.name and 
                        other.name not in interacted_agents)
                ]
                
                if available_targets:
                    target = agent.choose_interaction_target(available_targets)
                    
                    if target:
                        interaction = self.process_agent_interaction(agent, target)
                        if interaction:
                            self.interactions_this_step.append(interaction)
                            interacted_agents.add(agent.name)
                            interacted_agents.add(target.name)
                            
                            print(f"💬 {agent.name} → {target.name}: {interaction['content'][:50]}...")
    
    def process_agent_interaction(self, initiator: StoryAgent, target: StoryAgent) -> Optional[Dict]:
        """Process an interaction between two specific agents"""
        
        try:
            # Initiator starts the interaction
            interaction_data = initiator.initiate_interaction(target, self.environment, self.current_step)
            
            # Target responds
            response = target.respond_to_interaction(interaction_data, self.environment, self.current_step)
            
            # Complete interaction data
            interaction_data['response'] = response
            interaction_data['full_conversation'] = f"{interaction_data['content']} | {response}"
            
            # Analyze interaction sentiment
            sentiment = analyze_sentiment(interaction_data['full_conversation'])
            interaction_data['sentiment'] = sentiment
            
            # Update relationships based on sentiment
            relationship_change = sentiment.get('positive_sentiment', 0.5) - sentiment.get('negative_sentiment', 0.3)
            initiator.update_relationship(target.name, relationship_change)
            target.update_relationship(initiator.name, relationship_change)
            
            # Update memories
            if initiator.memory:
                initiator.memory.remember_interaction(
                    target.name, 
                    interaction_data['full_conversation'],
                    interaction_data['location'],
                    sentiment.get('emotional_intensity', 0.5)
                )
            
            if target.memory:
                target.memory.remember_interaction(
                    initiator.name,
                    interaction_data['full_conversation'], 
                    interaction_data['location'],
                    sentiment.get('emotional_intensity', 0.5)
                )
            
            # Track character development
            self.overseer.track_character_development(initiator, interaction_data)
            self.overseer.track_character_development(target, interaction_data)
            
            return interaction_data
            
        except Exception as e:
            print(f"Error processing interaction between {initiator.name} and {target.name}: {e}")
            return None
    
    def process_agent_actions(self):
        """Process actions for agents who didn't interact"""
        
        for agent in self.story_agents:
            # Skip agents who already interacted this step
            recent_interaction = any(
                interaction for interaction in self.interactions_this_step
                if agent.name in interaction.get('participants', [])
            )
            
            if not recent_interaction:
                # Agent decides on an action
                action = agent.decide_action(self.environment, self.current_step)
                
                if action and len(action.strip()) > 0:
                    print(f"🎯 {agent.name}: {action}")
                    
                    # Log action as memory
                    if agent.memory:
                        try:
                            agent.memory.remember_thought(f"I decided to: {action}")
                        except Exception as e:
                            print(f"Warning: Could not store thought for {agent.name}: {e}")
    
    def update_agent_states(self):
        """Update emotional states and other agent properties"""
        
        for agent in self.story_agents:
            # Update emotional state based on recent interactions
            recent_interaction = any(
                interaction for interaction in self.interactions_this_step
                if agent.name in interaction.get('participants', [])
            )
            
            if recent_interaction:
                agent.update_emotional_state(self.interactions_this_step[-1])
            else:
                agent.update_emotional_state()
    
    def process_narrator_intervention(self):
        """Process a narrator intervention to improve story flow"""
        
        event_candidates = self.narrator.generate_event_candidates(self.story_agents, self.environment)
        
        if event_candidates:
            selected_event = self.narrator.select_optimal_event(event_candidates, self.get_story_context())
            
            if selected_event:
                executed_event = self.narrator.execute_event(selected_event, self.environment)
                
                if executed_event:
                    self.events_this_step.append(executed_event)
                    print(f"🎪 Narrator Event: {executed_event.get('detailed_description', executed_event.get('description'))}")
                    
                    # Apply event effects to agents
                    self.apply_event_effects(executed_event)
    
    def apply_event_effects(self, event: Dict):
        """Apply the effects of a narrator event to agents"""
        
        affected_agents = event.get('affected_agents', [])
        event_type = event.get('type', 'general')
        
        for agent in self.story_agents:
            if agent in affected_agents or event.get('location') == 'all':
                
                # Log event in agent memory
                if agent.memory:
                    try:
                        agent.memory.remember_observation(
                            event.get('detailed_description', event.get('description', 'Something happened')),
                            agent.location
                        )
                    except Exception as e:
                        print(f"Warning: Could not store event memory for {agent.name}: {e}")
                
                # Apply specific event effects
                if event_type == 'relationship_catalyst':
                    # Increase likelihood of interaction
                    agent.energy_level = min(1.0, agent.energy_level + 0.2)
                
                elif event_type == 'environmental_pressure':
                    # Might change mood or stress
                    if 'storm' in event.get('description', '').lower():
                        agent.stress_level = min(1.0, agent.stress_level + 0.1)
    
    def introduce_new_character(self):
        """Introduce a new character to the story"""
        try:
            # Gather context for character generation
            existing_characters = []
            for agent in self.story_agents:
                existing_characters.append({
                    'name': agent.name,
                    'personality_traits': agent.personality_traits,
                    'location': agent.location
                })
            
            available_locations = list(self.environment.locations.keys())
            story_theme = self.config.get('story', {}).get('theme', 'general')
            
            # Generate new character profile
            character_data = generate_new_character(
                existing_characters, 
                story_theme, 
                available_locations
            )
            
            # Create new StoryAgent
            new_agent = StoryAgent(
                name=character_data['name'],
                description=character_data['description'],
                personality_traits=character_data.get('personality_traits', []),
                background=character_data.get('background', ''),
                starting_location=character_data.get('starting_location', available_locations[0]),
                goals=character_data.get('goals', []),
                fears=character_data.get('fears', [])
            )
            
            # Set up memory interface
            memory_interface = AgentMemoryInterface(new_agent.name, self.memory_manager)
            new_agent.set_memory_interface(memory_interface)
            
            # Initialize relationships with existing characters
            relationships = character_data.get('relationships', {})
            for existing_agent in self.story_agents:
                if existing_agent.name in relationships:
                    new_agent.relationships[existing_agent.name] = relationships[existing_agent.name]
                    existing_agent.relationships[new_agent.name] = relationships[existing_agent.name]
                else:
                    # Default neutral relationship
                    new_agent.relationships[existing_agent.name] = 0.0
                    existing_agent.relationships[new_agent.name] = 0.0
            
            # Add to simulation
            self.story_agents.append(new_agent)
            self.environment.move_agent(new_agent, None, new_agent.location)
            
            # Record the introduction
            self.narrator.record_character_introduction(self.current_step)
            
            # Create an introduction event
            introduction_event = {
                'type': 'character_introduction',
                'description': f"{new_agent.name} arrives at {new_agent.location}",
                'affected_agents': [new_agent],
                'location': new_agent.location,
                'execution_time': self.current_step
            }
            
            self.events_this_step.append(introduction_event)
            
            print(f"✨ New character introduced: {new_agent.name}")
            print(f"📍 Location: {new_agent.location}")
            print(f"🎭 Personality: {', '.join(new_agent.personality_traits[:3])}")
            
            # Add introduction memory for the new character
            if new_agent.memory:
                try:
                    new_agent.memory.remember_observation(
                        f"I have arrived at {new_agent.location} and am ready to begin my journey",
                        new_agent.location
                    )
                except Exception as e:
                    print(f"Warning: Could not store introduction memory for {new_agent.name}: {e}")
            
        except Exception as e:
            print(f"❌ Error introducing new character: {e}")
            import traceback
            traceback.print_exc()
    
    def process_event(self, event: Dict):
        """Process a general event in the simulation"""
        
        event_type = event.get('type', 'general')
        
        if event_type == 'narrator_intervention':
            self.handle_narrator_event(event)
        elif event_type == 'environmental':
            self.handle_environmental_event(event)
        
        self.environment.log_event(event)
        self.events_this_step.append(event)
    
    def handle_narrator_event(self, event: Dict):
        """Handle events generated by the narrator"""
        print(f"🎭 Narrator Event: {event.get('description', 'Something happens')}")
    
    def handle_environmental_event(self, event: Dict):
        """Handle environmental events (weather, time of day, etc.)"""
        print(f"🌍 Environmental Event: {event.get('description', 'The environment changes')}")
    
    def check_ending_conditions(self) -> bool:
        """Check if the story should end based on various metrics"""
        
        # Check maximum time steps
        if self.current_step >= self.max_time_steps:
            print(f"📏 Maximum time steps ({self.max_time_steps}) reached")
            return True
        
        # Check story ending readiness from overseer
        if self.overseer.detect_ending_readiness(self.story_agents, self.ending_metrics):
            print("📚 Story naturally ready to end")
            return True
        
        # Check for stagnation
        if self.narrator.detect_stagnation(self.story_agents, self.environment):
            if self.current_step > 20:  # Don't end too early
                print("😴 Story has stagnated")
                return True
        
        return False
    
    def conclude_story(self):
        """Handle the conclusion of the story"""
        
        print("\n🎬 Concluding story...")
        
        # Generate final chapter
        final_chapter = self.overseer.synthesize_chapter(self.current_step, max_interactions=20)
        print(f"📖 Final Chapter: {final_chapter}")
        
        self.simulation_running = False
    
    def get_story_context(self) -> Dict:
        """Get current story context for decision making"""
        return {
            'agents': [{'name': agent.name, 'location': agent.location} for agent in self.story_agents],
            'environment': self.environment,
            'current_time': self.environment.current_time,
            'step': self.current_step,
            'recent_interactions': self.interactions_this_step
        }
    
    def run_full_simulation(self) -> str:
        """Run the complete simulation from start to finish"""
        
        print("🎭 Starting full simulation...")
        self.simulation_running = True
        
        try:
            while self.simulation_running and self.current_step < self.max_time_steps:
                continue_simulation = self.run_simulation_step()
                if not continue_simulation:
                    break
                
                # Small delay for readability (remove in production)
                import time
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n⏹️ Simulation interrupted by user")
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
        
        # Generate final story
        final_story = self.overseer.export_story()
        
        print(f"\n✅ Simulation completed after {self.current_step} steps")
        print(f"📊 Final stats: {self.overseer.get_story_status()}")
        
        return final_story
    
    def get_simulation_status(self) -> Dict:
        """Get current simulation status"""
        return {
            'current_step': self.current_step,
            'max_steps': self.max_time_steps,
            'running': self.simulation_running,
            'agents': len(self.story_agents),
            'interactions_this_step': len(self.interactions_this_step),
            'events_this_step': len(self.events_this_step),
            'story_health': self.narrator.get_story_health_summary(),
            'overseer_status': self.overseer.get_story_status()
        }
    
    def to_dict(self) -> Dict:
        """Serialize the entire simulation to a dictionary"""
        return {
            'config': self.config,
            'current_step': self.current_step,
            'max_time_steps': self.max_time_steps,
            'simulation_running': self.simulation_running,
            'ending_metrics': self.ending_metrics.copy(),
            'interactions_this_step': self.interactions_this_step.copy(),
            'events_this_step': self.events_this_step.copy(),
            'environment': self.environment.to_dict(),
            'narrator': self.narrator.to_dict(),
            'overseer': self.overseer.to_dict(),
            'memory_manager': self.memory_manager.to_dict(),
            'story_agents': [agent.to_dict() for agent in self.story_agents]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SimulationEngine':
        """Reconstruct a simulation from a dictionary"""
        from src.utils.memory_management import AgentMemoryInterface
        
        # Create new simulation with config
        simulation = cls(data['config'])
        
        # Restore basic state
        simulation.current_step = data['current_step']
        simulation.max_time_steps = data['max_time_steps']
        simulation.simulation_running = data['simulation_running']
        simulation.ending_metrics = data['ending_metrics']
        simulation.interactions_this_step = data['interactions_this_step']
        simulation.events_this_step = data['events_this_step']
        
        # Restore components
        simulation.environment = EnvironmentStateManager.from_dict(data['environment'])
        simulation.narrator = NarratorAgent.from_dict(data['narrator'])
        simulation.overseer = OverseerAgent.from_dict(data['overseer'])
        simulation.memory_manager = MemoryManager.from_dict(data['memory_manager'])
        
        # Restore agents
        simulation.story_agents = []
        for agent_data in data['story_agents']:
            agent = StoryAgent.from_dict(agent_data)
            
            # Set up memory interface
            memory_interface = AgentMemoryInterface(agent.name, simulation.memory_manager)
            agent.set_memory_interface(memory_interface)
            
            simulation.story_agents.append(agent)
            
            # Add agent back to environment
            simulation.environment.move_agent(agent, None, agent.location)
        
        return simulation