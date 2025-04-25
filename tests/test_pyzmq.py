import sys
import subprocess

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Try to import zmq directly
try:
    import zmq
    print(f"✅ Successfully imported zmq")
    print(f"ZMQ version: {zmq.__version__}")
    print(f"ZMQ module location: {zmq.__file__}")
except ImportError as e:
    print(f"❌ Failed to import zmq: {e}")

# Try to install pyzmq if import failed
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyzmq"], check=True)
    print("✅ Installed pyzmq")
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to install pyzmq: {e}")

# Try to import zmq again after installation
try:
    import zmq
    print(f"✅ Successfully imported zmq after installation")
    print(f"ZMQ version: {zmq.__version__}")
    print(f"ZMQ module location: {zmq.__file__}")
except ImportError as e:
    print(f"❌ Failed to import zmq after installation: {e}")

# Check if pyzmq is in pip list
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    if "pyzmq" in result.stdout:
        print("✅ pyzmq is in pip list")
    else:
        print("❌ pyzmq is not in pip list")
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to run pip list: {e}") 