# Environment State Manager - Shared world model that tracks locations, objects, time, and events

from typing import Dict, List, Any, Optional

class Location:
    """Represents a location in the story world"""
    
    def __init__(self, name: str, description: str, location_type: str = "general"):
        self.name = name
        self.description = description
        self.location_type = location_type
        self.connected_locations = []
        self.objects = []
        self.current_agents = []
        self.atmosphere = "neutral"
        self.events_history = []
        
    def add_agent(self, agent):
        """Add an agent to this location"""
        if agent not in self.current_agents:
            self.current_agents.append(agent)
    
    def remove_agent(self, agent):
        """Remove an agent from this location"""
        if agent in self.current_agents:
            self.current_agents.remove(agent)
    
    def get_agents_present(self):
        """Get list of agents currently at this location"""
        return self.current_agents.copy()
    
    def get_agent_names(self) -> List[str]:
        """Get names of agents currently at this location"""
        return [agent.name for agent in self.current_agents]


class EnvironmentStateManager:
    """
    Shared world model that tracks locations, objects, time, and events.
    """
    
    def __init__(self):
        # Spatial model
        self.locations = {}
        self.location_graph = {}  # For tracking connections between locations
        
        # Temporal system
        self.current_time = 0
        self.time_unit = "hour"  # or "minute", "day", etc.
        self.scheduled_events = []
        
        # Object registry
        self.objects = {}
        self.object_locations = {}  # Track where objects are
        
        # Event history
        self.event_history = []
        self.interaction_history = []
        
        # World state
        self.world_state = {}
        self.weather = "clear"
        self.season = "spring"
        
    def add_location(self, name: str, description: str, location_type: str = "general") -> Location:
        """Add a new location to the world"""
        location = Location(name, description, location_type)
        self.locations[name] = location
        self.location_graph[name] = []
        return location
    
    def connect_locations(self, location1_name: str, location2_name: str, bidirectional: bool = True):
        """Create a connection between two locations"""
        if location1_name in self.locations and location2_name in self.locations:
            if location2_name not in self.location_graph[location1_name]:
                self.location_graph[location1_name].append(location2_name)
                self.locations[location1_name].connected_locations.append(location2_name)
            
            if bidirectional and location1_name not in self.location_graph[location2_name]:
                self.location_graph[location2_name].append(location1_name)
                self.locations[location2_name].connected_locations.append(location1_name)
    
    def move_agent(self, agent, from_location: Optional[str], to_location: str) -> bool:
        """Move an agent from one location to another"""
        try:
            # Remove from old location
            if from_location and from_location in self.locations:
                self.locations[from_location].remove_agent(agent)
            
            # Add to new location
            if to_location in self.locations:
                self.locations[to_location].add_agent(agent)
                agent.location = to_location
                return True
            else:
                print(f"Warning: Location '{to_location}' does not exist")
                return False
                
        except Exception as e:
            print(f"Error moving agent: {e}")
            return False
    
    def advance_time(self, time_units: int = 1):
        """Advance the world time"""
        self.current_time += time_units
        self.process_scheduled_events()
    
    def schedule_event(self, event: Dict, time_delay: int):
        """Schedule an event to occur after a time delay"""
        scheduled_time = self.current_time + time_delay
        self.scheduled_events.append((scheduled_time, event))
        self.scheduled_events.sort(key=lambda x: x[0])  # Sort by time
    
    def process_scheduled_events(self) -> List[Dict]:
        """Process any events scheduled for the current time"""
        events_to_process = []
        remaining_events = []
        
        for scheduled_time, event in self.scheduled_events:
            if scheduled_time <= self.current_time:
                events_to_process.append(event)
            else:
                remaining_events.append((scheduled_time, event))
        
        self.scheduled_events = remaining_events
        return events_to_process
    
    def log_interaction(self, interaction_data: Dict):
        """Log an interaction in the world history"""
        interaction_entry = {
            'time': self.current_time,
            'type': 'interaction',
            'data': interaction_data
        }
        self.interaction_history.append(interaction_entry)
    
    def log_event(self, event_data: Dict):
        """Log an event in the world history"""
        event_entry = {
            'time': self.current_time,
            'type': 'event',
            'data': event_data
        }
        self.event_history.append(event_entry)
    
    def get_agents_at_location(self, location_name: str) -> List:
        """Get all agents currently at a specific location"""
        if location_name in self.locations:
            return self.locations[location_name].get_agents_present()
        return []
    
    def get_location_info(self, location_name: str) -> Optional[Dict]:
        """Get detailed information about a location"""
        if location_name in self.locations:
            location = self.locations[location_name]
            return {
                'name': location.name,
                'description': location.description,
                'type': location.location_type,
                'agents_present': location.get_agent_names(),
                'connected_to': location.connected_locations,
                'atmosphere': location.atmosphere
            }
        return None
    
    def get_world_state_summary(self) -> Dict:
        """Get a summary of the current world state"""
        
        # Count agents per location
        location_populations = {}
        for location_name, location in self.locations.items():
            location_populations[location_name] = len(location.current_agents)
        
        summary = {
            'current_time': self.current_time,
            'total_locations': len(self.locations),
            'location_populations': location_populations,
            'total_interactions': len(self.interaction_history),
            'total_events': len(self.event_history),
            'weather': self.weather,
            'season': self.season,
            'scheduled_events': len(self.scheduled_events)
        }
        return summary
    
    def find_path_between_locations(self, start: str, end: str) -> Optional[List[str]]:
        """Find a path between two locations using simple BFS"""
        if start not in self.location_graph or end not in self.location_graph:
            return None
        
        if start == end:
            return [start]
        
        # Simple BFS pathfinding
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.location_graph[current]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
    
    def get_nearby_locations(self, location_name: str, max_distance: int = 1) -> List[str]:
        """Get locations within a certain distance"""
        if location_name not in self.location_graph:
            return []
        
        nearby = set()
        current_level = {location_name}
        
        for distance in range(max_distance + 1):
            if distance == 0:
                continue
            
            next_level = set()
            for loc in current_level:
                for neighbor in self.location_graph.get(loc, []):
                    if neighbor not in nearby and neighbor != location_name:
                        nearby.add(neighbor)
                        next_level.add(neighbor)
            
            current_level = next_level
        
        return list(nearby)
    
    def update_location_atmosphere(self, location_name: str, new_atmosphere: str):
        """Update the atmosphere of a location"""
        if location_name in self.locations:
            self.locations[location_name].atmosphere = new_atmosphere
    
    def add_object_to_location(self, object_name: str, location_name: str, description: str = ""):
        """Add an object to a specific location"""
        if location_name in self.locations:
            obj = {
                'name': object_name,
                'description': description,
                'location': location_name
            }
            self.objects[object_name] = obj
            self.object_locations[object_name] = location_name
            self.locations[location_name].objects.append(obj)
    
    def move_object(self, object_name: str, new_location: str) -> bool:
        """Move an object from one location to another"""
        if object_name not in self.objects:
            return False
        
        old_location = self.object_locations.get(object_name)
        
        # Remove from old location
        if old_location and old_location in self.locations:
            self.locations[old_location].objects = [
                obj for obj in self.locations[old_location].objects 
                if obj['name'] != object_name
            ]
        
        # Add to new location
        if new_location in self.locations:
            self.object_locations[object_name] = new_location
            self.objects[object_name]['location'] = new_location
            self.locations[new_location].objects.append(self.objects[object_name])
            return True
        
        return False
    
    def get_objects_at_location(self, location_name: str) -> List[Dict]:
        """Get all objects at a specific location"""
        if location_name in self.locations:
            return self.locations[location_name].objects.copy()
        return []
    
    def change_weather(self, new_weather: str):
        """Change the current weather"""
        old_weather = self.weather
        self.weather = new_weather
        
        # Log weather change as an event
        weather_event = {
            'type': 'environmental',
            'subtype': 'weather_change',
            'description': f"Weather changed from {old_weather} to {new_weather}",
            'time': self.current_time
        }
        self.log_event(weather_event)
    
    def get_environment_status(self) -> Dict:
        """Get comprehensive environment status"""
        return {
            'time': self.current_time,
            'weather': self.weather,
            'season': self.season,
            'locations': {name: self.get_location_info(name) for name in self.locations.keys()},
            'total_objects': len(self.objects),
            'scheduled_events': len(self.scheduled_events),
            'history_length': {
                'interactions': len(self.interaction_history),
                'events': len(self.event_history)
            }
        }