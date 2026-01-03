import asyncio
import json
import threading
import time
from typing import Set, Dict, Any, Optional

# Try importing websockets (Must be installed by user)
try:
    import websockets
except ImportError:
    websockets = None
    print("⚠️ 'websockets' library is missing. Please run: pip install websockets")

class MinecraftManager:
    """
    Minecraft Bedrock Edition Connection Manager
    Uses WebSocket to receive sensory data (EVENTS) and send commands.
    """
    def __init__(self, brain=None, port=8080):
        self.brain = brain
        self.port = port
        self.loop = None
        self.thread = None
        self.running = False
        self.connected_clients = set()
        
        # Latest Sensory Data
        self.current_state = {
            "position": None, # {"x": 0, "y": 0, "z": 0}
            "biome": "Unknown",
            "last_pain": 0,
            "connected": False
        }

    def start(self):
        """
        Start the WebSocket server in a separate daemon thread.
        This prevents blocking the main Brain loop.
        """
        if not websockets:
            print("❌ Cannot start MinecraftManager: 'websockets' lib missing.")
            return

        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_server_thread, daemon=True)
        self.thread.start()
        print(f"⛏️ Minecraft Sense Server preparing on port {self.port}...")

    def stop(self):
        """Stop the server (Graceful shutdown)"""
        self.running = False
        # Note: True async shutdown requires access to the loop, 
        # which is tricky from another thread. We rely on daemon thread for now.

    def _run_server_thread(self):
        """Entry point for the background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Try to bind to ports
        for i in range(5): # Try 5 ports starting from self.port
            try:
                target_port = self.port + i
                # Note: "0.0.0.0" is better than "localhost" to avoid IPv6 issues
                start_server = websockets.serve(self._handler, "0.0.0.0", target_port)
                self.loop.run_until_complete(start_server)
                
                print(f"✅ Minecraft WebSocket listening at ws://0.0.0.0:{target_port}")
                print(f"============================================================")
                print(f"👉 Please type '/connect localhost:{target_port}' in Minecraft Chat.")
                print(f"============================================================")
                self.connected_port = target_port
                break
            except OSError as e:
                print(f"⚠️ Port {target_port} is busy. Trying next...")
                if i == 4:
                    print(f"❌ Could not find open port for Minecraft Manager.")
                    return

        self.loop.run_forever()

    async def _handler(self, websocket, path):
        """Handle a new connection from Minecraft"""
        print(f"🔗 Minecraft Client Connected!")
        self.connected_clients.add(websocket)
        self.current_state["connected"] = True
        
        # 1. Subscribe to Events
        await self._subscribe_events(websocket)
        
        # 2. TEST COMMAND: Say hello to verify output
        await self.send_command(websocket, "say 🔗 Kaname AI System Linked. Protocol Debugging Mode.")
        
        # 3. Command & Event Loop
        try:
            async for message in websocket:
                # Log raw for debugging (comment out if too spammy)
                # print(f"📩 Raw: {message[:100]}") 
                try:
                    data = json.loads(message)
                    await self._process_incoming_data(data)
                except json.JSONDecodeError:
                    print(f"⚠️ Failed to parse JSON: {message}")
                except Exception as e:
                    print(f"⚠️ Error processing data: {e}")
        except Exception as e:
            print(f"⚠️ Minecraft Connection Error: {e}")
        finally:
            print("🔌 Minecraft Client Disconnected.")
            self.connected_clients.remove(websocket)
            self.current_state["connected"] = False

    async def send_command(self, websocket, cmd_text):
        """Send a slash command to Minecraft"""
        import uuid
        msg = {
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "commandRequest",
                "version": 1,
                "messageType": "commandRequest"
            },
            "body": {
                "origin": {"type": "player"},
                "commandLine": cmd_text,
                "version": 1
            }
        }
        await websocket.send(json.dumps(msg))

    async def _subscribe_events(self, websocket):
        """Tell Minecraft what events we want to hear"""
        # Some versions prefer simpler IDs, some prefer UUID.
        # Let's try simple strings as IDs first for stability.
        events = [
            "PlayerTravelled", 
            "PlayerMessage",   
            "BlockBroken",
            "BlockPlaced"
        ]
        
        print(f"   📡 Subscribing to {len(events)} events (Legacy Compatibility Mode)...")
        for i, event in enumerate(events):
            msg = {
                "header": {
                    "requestId": f"sub-{i}",
                    "messagePurpose": "subscribe",
                    "version": 1,
                    # For some Bedrock versions, eventName must be in the header too
                    "eventName": event 
                },
                "body": {
                    "eventName": event
                }
            }
            await websocket.send(json.dumps(msg))
            await asyncio.sleep(0.3)

    async def _process_incoming_data(self, data):
        """Parse JSON from Minecraft"""
        header = data.get("header", {})
        body = data.get("body", {})
        
        msg_purpose = header.get("messagePurpose")
        
        # DEBUG: 届いたデータすべてを記録（スパム回避のため短縮）
        # print(f"DEBUG raw: {msg_purpose} / {header.get('eventName')}")
        
        # Verbose: Log everything for debugging
        # print(f"🔍 Received {msg_purpose}")

        if msg_purpose == "event":
            event_name = header.get("eventName")
            if event_name:
                print(f"📡 Event Received: {event_name}") # Essential for debug
            
            if event_name == "PlayerTravelled":
                self._handle_travelled(body)
                # Metabolic Impact: Every significant movement consumes energy but rewards exploration
                if self.brain:
                    # Minecraft units are roughly meters. 
                    # We can use this to trigger small metabolic changes.
                    pos = body.get("player", {}).get("position", {})
                    self.brain.receive_sense("MC_TRAVEL", {
                        "x": pos.get("x"), 
                        "y": pos.get("y"), 
                        "z": pos.get("z"),
                        "dist_increase": 1.0
                    })
                    
            elif event_name == "PlayerMessage":
                self._handle_chat(body)
                if self.brain:
                    # Social Impact
                    self.brain.receive_sense("MC_CHAT", {"sender": body.get("sender")})
                    
            elif event_name == "BlockBroken":
                if self.brain:
                    # Effort Impact: Breaking things consumes glucose but provides satisfaction (resource intake)
                    print(f"⛏️ Block Broken at {body.get('player', {}).get('position')}")
                    self.brain.receive_sense("MC_ACTION_SUCCESS", {"type": "BREAK"})
        
        elif msg_purpose == "commandResponse":
             # Subscription confirmation or command result
             status = body.get("statusCode")
             if status != 0:
                 msg = body.get("statusMessage", "Unknown Error")
                 print(f"⚠️ Minecraft CMD Error [Status {status}]: {msg}")
             else:
                 # Success
                 req_id = header.get("requestId")
                 print(f"✅ Minecraft CMD Success: {req_id}")
             
             # If it was a response to an event subscription, it might have details
             if "events" in body:
                 print(f"📝 Subscribed events: {body.get('events')}")

    def _handle_travelled(self, body):
        """Update Proprioception (Body Position)"""
        pos = body.get("player", {}).get("position", {})
        # x, y, z = pos.get("x"), pos.get("y"), pos.get("z")
        
        # Store in state
        self.current_state["position"] = pos
        
        # Debug Log (Rate Limited)
        if int(time.time() * 10) % 50 == 0: # approx every 5 sec
             print(f"📍 MC Coords: {pos}")
        
        # Only if Brain is connected, send valid signal
        if self.brain and hasattr(self.brain, 'receive_sense'):
           self.brain.receive_sense({"minecraft_pos": pos})

    def _handle_chat(self, body):
        """Hearing"""
        msg = body.get("message")
        sender = body.get("sender")
        if sender != "External": # Ignore self
            print(f"👂 MC Chat [{sender}]: {msg}")

    # --- Public Access for Brain ---
    def get_sense_data(self):
        """Brain calls this to get latest minecraft state"""
        return self.current_state
