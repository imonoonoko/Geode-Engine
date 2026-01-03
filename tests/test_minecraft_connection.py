import asyncio
import unittest
import json
import threading
import time
from unittest.mock import MagicMock
import websockets

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.games.minecraft.manager import MinecraftManager

class TestMinecraftSenses(unittest.TestCase):
    def setUp(self):
        # Mock Brain
        self.mock_brain = MagicMock()
        self.manager = MinecraftManager(brain=self.mock_brain, port=8081) # Use different port for testing
        self.manager.start()
        time.sleep(1) # Wait for server start

    def tearDown(self):
        self.manager.stop()

    def test_connection_and_subscription(self):
        async def run_client():
            uri = "ws://localhost:8081"
            async with websockets.connect(uri) as websocket:
                # 1. Expect Subscription Command
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"📥 Received from Server: {data}")
                self.assertEqual(data["header"]["messagePurpose"], "subscribe")
                self.assertIn("PlayerTravelled", data["body"]["eventName"])

                # 2. Send Sensory Event (Travel)
                event_data = {
                    "header": {
                        "messagePurpose": "event",
                        "eventName": "PlayerTravelled"
                    },
                    "body": {
                        "player": {
                            "position": {"x": 100, "y": 64, "z": 200}
                        }
                    }
                }
                await websocket.send(json.dumps(event_data))
                
                # Check if Manager updated state
                time.sleep(0.5)
                state = self.manager.get_sense_data()
                print(f"🧠 Manager State: {state}")
                
                self.assertTrue(state["connected"])
                self.assertEqual(state["position"]["x"], 100)

        # Run Async Test
        asyncio.run(run_client())

if __name__ == "__main__":
    unittest.main()
