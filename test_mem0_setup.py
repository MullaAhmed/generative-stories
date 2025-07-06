#!/usr/bin/env python3
"""
Test script to verify mem0ai setup and configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mem0_installation():
    """Test if mem0ai is properly installed"""
    print("🔍 Testing mem0ai installation...")
    try:
        from mem0 import Memory
        print("✅ mem0ai is installed and importable")
        return True
    except ImportError as e:
        print(f"❌ mem0ai import failed: {e}")
        print("💡 Install with: pip install mem0ai")
        return False

def test_openai_api_key():
    """Test if OpenAI API key is available"""
    print("\n🔍 Testing OpenAI API key...")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY found in environment")
        print(f"   Key starts with: {openai_key[:10]}...")
        return True
    else:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Set OPENAI_API_KEY in your .env file")
        return False

def test_mem0_config():
    """Test if mem0 config file exists and is valid"""
    print("\n🔍 Testing mem0 configuration...")
    config_path = "config/mem0_config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Config file loaded: {config_path}")
        
        # Check required sections
        required_sections = ['vector_store', 'llm', 'embedder']
        for section in required_sections:
            if section in config:
                print(f"   ✅ {section}: {config[section].get('provider', 'unknown')}")
            else:
                print(f"   ❌ Missing section: {section}")
                return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False

def test_mem0_initialization():
    """Test if mem0 can be initialized with the config"""
    print("\n🔍 Testing mem0ai initialization...")
    
    try:
        from mem0 import Memory
        import json
        
        # Load config
        with open("config/mem0_config.json", 'r') as f:
            config = json.load(f)
        
        # Try to initialize
        memory = Memory(config=config)
        print("✅ mem0ai Memory instance created successfully")
        
        # Test basic functionality
        test_user_id = "test_user"
        test_messages = [{"role": "user", "content": "This is a test memory for setup verification"}]
        
        print("🔍 Testing memory add operation...")
        result = memory.add(
            messages=test_messages,
            user_id=test_user_id
        )
        print(f"✅ Memory added successfully: {result.get('id', 'unknown_id')}")
        
        print("🔍 Testing memory retrieval...")
        memories = memory.get_all(user_id=test_user_id)
        print(f"✅ Retrieved {len(memories)} memories for test user")
        
        print("🔍 Testing memory search...")
        search_results = memory.search(query="test memory", user_id=test_user_id, limit=1)
        print(f"✅ Search returned {len(search_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ mem0ai initialization failed: {e}")
        print("💡 Common issues:")
        print("   - Invalid OpenAI API key")
        print("   - Insufficient OpenAI credits")
        print("   - Network connectivity issues")
        print("   - Invalid configuration")
        return False

def test_memory_manager():
    """Test the custom MemoryManager class"""
    print("\n🔍 Testing MemoryManager class...")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        from src.utils.memory_management import MemoryManager, AgentMemoryInterface
        
        # Test MemoryManager initialization
        memory_manager = MemoryManager()
        print("✅ MemoryManager initialized successfully")
        
        # Test AgentMemoryInterface
        agent_memory = AgentMemoryInterface("test_agent", memory_manager)
        print("✅ AgentMemoryInterface created successfully")
        
        # Test basic operations
        print("🔍 Testing memory operations...")
        
        # Add a memory
        memory_id = agent_memory.remember_thought("This is a test thought for verification")
        print(f"✅ Thought remembered: {memory_id}")
        
        # Get recent memories
        recent_memories = agent_memory.get_recent_memories(limit=5)
        print(f"✅ Retrieved {len(recent_memories)} recent memories")
        
        # Get memory summary
        summary = agent_memory.get_memory_summary()
        print(f"✅ Memory summary: {summary.get('total_memories', 0)} total memories")
        
        return True
        
    except Exception as e:
        print(f"❌ MemoryManager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 mem0ai Setup Verification Test")
    print("=" * 50)
    
    tests = [
        ("mem0ai Installation", test_mem0_installation),
        ("OpenAI API Key", test_openai_api_key),
        ("mem0 Configuration", test_mem0_config),
        ("mem0ai Initialization", test_mem0_initialization),
        ("MemoryManager Class", test_memory_manager)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! mem0ai is properly configured.")
        print("🚀 You can now run the story simulation with working memory.")
    else:
        print("⚠️ Some tests failed. Please fix the issues above before running the simulation.")
        print("💡 Check the error messages and suggestions for each failed test.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)