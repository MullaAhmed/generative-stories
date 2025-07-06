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
   # Edit .env and add your API keys
   ```

   **Supported LLM Providers:**
   - **Gemini** (Google): Set `GOOGLE_API_KEY` or `GEMINI_API_KEY`
   - **OpenAI**: Set `OPENAI_API_KEY`
   - **Groq**: Set `GROQ_API_KEY`
   
   You can set `DEFAULT_LLM_PROVIDER` to choose your preferred provider (gemini, openai, or groq).

3. **Configure memory system:**
   The system requires mem0 for memory management. Ensure the configuration in `config/mem0_config.json` is properly set up for your environment.

4. **Run a story simulation:**
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

### Memory System Setup

The system **requires** mem0 for memory management:

```bash
pip install mem0
```

**Important:** Configure mem0 by editing `config/mem0_config.json` to set up your preferred vector store and LLM provider for memory operations. The simulation will not run without a properly configured memory system.

### Story Configuration

Edit `stories/config/simulation_config.json` to customize:
- Characters and their personalities
- Locations and connections
- Story themes and settings
- Simulation parameters

## Features

- **Autonomous Agents**: Characters make their own decisions and interact naturally
- **Dynamic Storytelling**: Stories emerge from character interactions
- **Advanced Memory System**: Characters remember past interactions and experiences using mem0
- **Narrator Intervention**: AI narrator adds events to improve story flow
- **Multiple Formats**: Export stories as text, JSON, or markdown
- **Dynamic Character Generation**: System can introduce new characters to enhance story dynamics
- **Multiple LLM Providers**: Support for Gemini, OpenAI, and Groq models
- **Save/Resume**: Save story progress and resume from any point

## Example Output

The system generates complete stories with character development, dialogue, and narrative progression. Each story is unique based on the autonomous decisions of the AI characters.