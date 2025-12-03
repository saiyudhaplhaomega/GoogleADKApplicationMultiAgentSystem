"""
Test WhatsApp Commands - COMPLETE WORKING VERSION
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.whatsapp_notifier import command_handler, notifier
    
    print("🧪 Testing WhatsApp Commands...\n")
    print(f"✅ notifier enabled: {notifier.enabled}")
    print(f"✅ command_handler available: {command_handler is not None}\n")
    
    if not command_handler:
        print("❌ command_handler is None - cannot proceed")
        sys.exit(1)
    
    # Test commands
    commands = [
        "10 data engineer germany",
        "5 devops remote berlin",
        "3 mlops aws"
    ]
    
    for cmd in commands:
        print(f"\n👤 YOU: {cmd}")
        print("-" * 60)
        try:
            result = command_handler.handle_command(cmd)
            print(f"✅ Command processed: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 60)
    
    print("\n🎉 Test complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure utils/whatsapp_notifier.py exists in parent directory!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
