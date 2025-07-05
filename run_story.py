#!/usr/bin/env python3
"""
Simple runner script for Generative Stories
"""

import os
import sys

# Add stories directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stories'))

def main():
    print("🎭 Generative Stories Runner")
    print("=" * 40)
    
    try:
        # Import the main function from stories
        from main import main as stories_main
        
        # Run the simulation
        stories_main()
        
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