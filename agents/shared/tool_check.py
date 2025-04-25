import os
from output_handler import write_output

def verify_tools(tools, agent_name, speak):
    """Verify that all required tools exist and have content"""
    missing_tools = []
    empty_tools = []
    
    for tool in tools:
        if not os.path.exists(tool):
            missing_tools.append(tool)
            write_output(agent_name, "unknown", f"❌ Tool not found: {tool}")
        elif os.path.getsize(tool) == 0:
            empty_tools.append(tool)
            write_output(agent_name, "unknown", f"❌ Tool is empty: {tool}")
    
    if missing_tools or empty_tools:
        if missing_tools:
            speak(f"❌ Missing tools: {', '.join(missing_tools)}")
        if empty_tools:
            speak(f"❌ Empty tools: {', '.join(empty_tools)}")
        return False, missing_tools + empty_tools
    return True, []

# Global dictionary of required tools for each sister
TOOL_REQUIREMENTS = {
    "Alice": ["tools/alice_recon.sh"],
    "Harley": ["tools/boom.sh"],
    "Lisbeth": ["tools/ghost.sh"],
    "Luna": ["tools/starlight.sh"],
    "Marla": ["tools/chaos.sh"],
    "Seven": ["tools/assimilate.sh"],
    "Bride": ["tools/vengeance.sh"]
}

def scan_all_tools():
    """Scan all sisters' tools and report status"""
    print("\n🔍 Seven is checking everyone's gear...")
    
    missing_tools_by_sister = {}
    empty_tools_by_sister = {}
    total_sisters = len(TOOL_REQUIREMENTS)
    sisters_with_tools = 0
    
    for sister, tools in TOOL_REQUIREMENTS.items():
        missing_tools = []
        empty_tools = []
        for tool in tools:
            if not os.path.exists(tool):
                missing_tools.append(tool)
            elif os.path.getsize(tool) == 0:
                empty_tools.append(tool)
        
        if missing_tools:
            missing_tools_by_sister[sister] = missing_tools
        if empty_tools:
            empty_tools_by_sister[sister] = empty_tools
        if not missing_tools and not empty_tools:
            sisters_with_tools += 1
    
    # Calculate percentage of sisters with tools
    percentage = (sisters_with_tools / total_sisters) * 100
    
    if percentage == 100:
        print("✅ All sisters have their tools. The Sisterhood is ready.")
        return True
    
    # If some tools are missing or empty, show status and ask if user wants to proceed
    print(f"\n⚠️ Only {sisters_with_tools}/{total_sisters} sisters have their tools ({percentage:.0f}% complete)")
    
    if missing_tools_by_sister:
        print("\nMissing tools by sister:")
        for sister, tools in missing_tools_by_sister.items():
            print(f"  {sister}: {', '.join(tools)}")
    
    if empty_tools_by_sister:
        print("\nEmpty tools by sister:")
        for sister, tools in empty_tools_by_sister.items():
            print(f"  {sister}: {', '.join(tools)}")
    
    # Ask user if they want to proceed
    while True:
        response = input("\n⚠️ Some sisters are missing or have empty tools. Do you wish to proceed anyway? (y/n): ").lower()
        if response in ['y', 'yes']:
            print("🔄 Proceeding with partial toolset...")
            
            # Ask for custom path
            custom_path = input("\nEnter the path to your tools directory (or press Enter to skip): ").strip()
            if custom_path:
                print(f"\n🔍 Checking tools in: {custom_path}")
                for sister, tools in TOOL_REQUIREMENTS.items():
                    for tool in tools:
                        tool_name = os.path.basename(tool)
                        custom_tool = os.path.join(custom_path, tool_name)
                        if os.path.exists(custom_tool):
                            if os.path.getsize(custom_tool) > 0:
                                print(f"✅ Found {tool_name} for {sister}")
                            else:
                                print(f"❌ {tool_name} is empty for {sister}")
                        else:
                            print(f"❌ {tool_name} not found for {sister}")
            else:
                print("Skipping custom path check.")
            
            # Final check after custom path
            all_tools_found = True
            for sister, tools in TOOL_REQUIREMENTS.items():
                for tool in tools:
                    if not os.path.exists(tool) or os.path.getsize(tool) == 0:
                        all_tools_found = False
                        break
            
            if all_tools_found:
                print("\n✅ All tools found and valid after custom path check!")
            else:
                print("\n⚠️ Some tools are still missing or empty. The sisters may not function properly.")
            
            return True
        elif response in ['n', 'no']:
            print("❌ Operation cancelled. Please ensure all required tools are present and valid.")
            return False
        else:
            print("Please answer 'y' or 'n'")
