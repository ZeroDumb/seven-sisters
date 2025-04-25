import os
import sys
import subprocess
import importlib

# Add the project root to Python path to ensure imports work
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Print diagnostic information
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Try to import pkg_resources, with a fallback
try:
    import pkg_resources
    PKG_RESOURCES_AVAILABLE = True
    # pkg_resources doesn't have __version__ attribute
    print("pkg_resources is available")
except ImportError:
    PKG_RESOURCES_AVAILABLE = False
    print("⚠️ pkg_resources not available. Will use basic package checking.")

# Required Python packages
REQUIRED_PACKAGES = {
    "zmq": "ZeroMQ for IPC communication",
    "flask": "Web interface (optional)",
    "requests": "HTTP requests",
    "colorama": "Terminal colors",
    "psutil": "Process management"
}

# Required system tools
REQUIRED_TOOLS = {
    "bash": "Bash shell for tool execution",
    "python": "Python interpreter",
    "git": "Version control (optional)"
}

def check_python_packages():
    """Check if required Python packages are installed."""
    missing_packages = []
    
    for package, description in REQUIRED_PACKAGES.items():
        try:
            print(f"\nChecking package: {package}")
            # First try importing
            module = importlib.import_module(package)
            print(f"✅ Successfully imported {package}")
            print(f"Module location: {module.__file__}")
            
            # Then verify it's installed via pkg_resources if available
            if PKG_RESOURCES_AVAILABLE:
                try:
                    if package == "zmq":
                        pkg_resources.require("pyzmq")
                    else:
                        pkg_resources.require(package)
                    print(f"✅ pkg_resources verified {package}")
                except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
                    print(f"⚠️ Package version check failed for {package}: {str(e)}")
                    # Don't add to missing packages if import worked
        except ImportError as e:
            missing_packages.append((package, description))
            print(f"❌ Package check failed for {package}: {str(e)}")
            # Try to get more information about the import error
            try:
                if package == "zmq":
                    subprocess.run([sys.executable, "-m", "pip", "show", "pyzmq"], check=True)
                else:
                    subprocess.run([sys.executable, "-m", "pip", "show", package], check=True)
            except subprocess.CalledProcessError:
                print(f"Package {package} not found in pip")
    
    return missing_packages

def check_system_tools():
    """Check if required system tools are available."""
    missing_tools = []
    
    for tool, description in REQUIRED_TOOLS.items():
        if os.name == 'nt':  # Windows
            try:
                result = subprocess.run(['where', tool], capture_output=True, text=True)
                if result.returncode != 0:
                    missing_tools.append((tool, description))
            except:
                missing_tools.append((tool, description))
        else:  # Unix-like
            try:
                result = subprocess.run(['which', tool], capture_output=True, text=True)
                if result.returncode != 0:
                    missing_tools.append((tool, description))
            except:
                missing_tools.append((tool, description))
    
    return missing_tools

def install_python_package(package):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_dependencies():
    """Check all dependencies and prompt for installation if needed."""
    missing_packages = check_python_packages()
    missing_tools = check_system_tools()
    
    if not missing_packages and not missing_tools:
        print("✅ All required dependencies are installed.")
        return True
    
    # Report missing dependencies
    if missing_packages:
        print("\n⚠️ Missing Python packages:")
        for package, description in missing_packages:
            print(f"  - {package}: {description}")
    
    if missing_tools:
        print("\n⚠️ Missing system tools:")
        for tool, description in missing_tools:
            print(f"  - {tool}: {description}")
    
    # Ask user if they want to install missing packages
    if missing_packages:
        print("\nWould you like to install the missing Python packages?")
        response = input("Install missing packages? (y/n): ").lower()
        
        if response in ['y', 'yes']:
            print("\nInstalling missing packages...")
            for package, _ in missing_packages:
                print(f"Installing {package}...")
                if install_python_package(package):
                    print(f"✅ {package} installed successfully.")
                else:
                    print(f"❌ Failed to install {package}.")
                    return False
        else:
            print("Skipping package installation.")
    
    # For missing system tools, we can't install them automatically
    if missing_tools:
        print("\n⚠️ Some system tools are missing.")
        print("Please install them manually or provide their paths.")
        
        # Ask if user wants to proceed anyway
        response = input("\nProceed without missing system tools? (y/n): ").lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled. Please install required system tools.")
            return False
    
    return True

if __name__ == "__main__":
    # Test the dependency checker
    check_dependencies() 