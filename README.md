# Generative Stories

A multi-agent narrative engine that creates dynamic stories through autonomous character interactions.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Run a story simulation:**
   ```bash
   python run_story.py
   ```

## Interactive Mode

The runner will start in interactive mode where you can:
- Choose from available scenarios
- Name your story
- Watch the simulation run in real-time

## Generated Stories

Stories are saved in `stories/data/generated_stories/` as text files.

## Configuration

Edit `stories/config/simulation_config.json` to customize:
- Characters and their personalities
- Locations and connections
- Story themes and settings
- Simulation parameters

## Features

- **Autonomous Agents**: Characters make their own decisions and interact naturally
- **Dynamic Storytelling**: Stories emerge from character interactions
- **Memory System**: Characters remember past interactions and experiences
- **Narrator Intervention**: AI narrator adds events to improve story flow
- **Multiple Formats**: Export stories as text, JSON, or markdown

## Example Output

The system generates complete stories with character development, dialogue, and narrative progression. Each story is unique based on the autonomous decisions of the AI characters.