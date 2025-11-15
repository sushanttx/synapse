"""
Compatibility patch for websockets.asyncio import issue with realtime
This patches websockets to add the asyncio module that realtime expects
"""
import sys
import types

# Import websockets before realtime tries to
import websockets
import websockets.client

# Create a proper package structure for websockets.asyncio
asyncio_package = types.ModuleType('websockets.asyncio')
asyncio_package.__path__ = []  # Make it a package
asyncio_package.__package__ = 'websockets.asyncio'

# Create the client submodule
client_module = types.ModuleType('websockets.asyncio.client')
client_module.__package__ = 'websockets.asyncio.client'

# Copy the ClientConnection class from websockets.client
# In websockets 11+, ClientConnection is in websockets.client
if hasattr(websockets.client, 'ClientConnection'):
    client_module.ClientConnection = websockets.client.ClientConnection
else:
    # Fallback: try to import from the right place
    try:
        from websockets.client import ClientConnection
        client_module.ClientConnection = ClientConnection
    except ImportError:
        # Last resort: create a dummy class
        class ClientConnection:
            pass
        client_module.ClientConnection = ClientConnection

# Attach client to asyncio package
asyncio_package.client = client_module

# Register both modules in sys.modules
sys.modules['websockets.asyncio'] = asyncio_package
sys.modules['websockets.asyncio.client'] = client_module

# Also patch the websockets module directly
websockets.asyncio = asyncio_package

