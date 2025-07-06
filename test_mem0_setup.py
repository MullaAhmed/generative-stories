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
    print("🔍 Testing mem0 installation...")
    try:
        from mem0 import MemoryClient
        print("✅ mem0 is installed and importable")
        return True
    except ImportError as e:
        print(f"❌ mem0 import failed: {e}")
        print("💡 Install with: pip install mem0ai")
        return False

def test_mem0_api_key():
    """Test if MEM0 API key is available"""
    print("\n🔍 Testing MEM0 API key...")
    mem0_key = os.getenv("MEM0_API_KEY")
    if mem0_key:
        print("✅ MEM0_API_KEY found in environment")
        print(f"   Key starts with: {mem0_key[:10]}...")
        return True
    else:
        print("❌ MEM0_API_KEY not found in environment")
        print("💡 Set MEM0_API_KEY in your .env file")
        print("💡 Get your API key from https://app.mem0.ai/")
        return False

def test_mem0_initialization():
    """Test if mem0 MemoryClient can be initialized with the config"""
    print("\n🔍 Testing mem0 MemoryClient initialization...")
    
    try:
        from mem0 import MemoryClient
        
        # Get API key
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            print("❌ MEM0_API_KEY not found, cannot test initialization")
            return False
        
        # Try to initialize
        memory = MemoryClient(api_key=api_key)
        print("✅ mem0 MemoryClient instance created successfully")
        
        # Test basic functionality
        test_user_id = "test_user"
        test_message = "This is a test memory for setup verification"
        
        print("🔍 Testing memory add operation...")
        result = memory.add(test_message, user_id=test_user_id)
        memory_id = result.get('id', 'unknown_id') if isinstance(result, dict) else 'unknown_id'
        print(f"✅ Memory added successfully: {memory_id}")
        
        print("🔍 Testing memory retrieval...")
        memories = memory.get_all(user_id=test_user_id, limit=10)
        print(f"✅ Retrieved {len(memories)} memories for test user")
        
        print("🔍 Testing memory search...")
        search_results = memory.search("test memory", user_id=test_user_id, limit=1)
        print(f"✅ Search returned {len(search_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ mem0 MemoryClient initialization failed: {e}")
        print("💡 Common issues:")
        print("   - Invalid MEM0 API key")
        print("   - Insufficient mem0 credits")
        print("   - Network connectivity issues")
        print("   - mem0 service unavailable")
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
        ("MEM0 API Key", test_mem0_api_key),
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