# telemetry_server.py
# Geode Brain Telemetry WebSocket Server

import asyncio
import json
import threading
import time
import websockets

class TelemetryServer:
    def __init__(self, brain_ref, host="localhost", ws_port=8765, http_port=8080):
        self.brain = brain_ref
        self.host = host
        self.ws_port = ws_port
        self.http_port = http_port
        self.clients = set()
        self.is_running = False
        
    async def handler(self, websocket):
        """Handle WebSocket connections"""
        self.clients.add(websocket)
        print(f"📡 Dashboard connected! ({len(self.clients)} clients)")
        try:
            async for message in websocket:
                # Handle incoming messages (commands from dashboard)
                try:
                    cmd = json.loads(message)
                    if cmd.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                except:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"📡 Dashboard disconnected. ({len(self.clients)} clients)")

    def get_telemetry(self):
        """Extract brain state as JSON-serializable dict"""
        if not self.brain:
            return {}
        
        try:
            with self.brain.lock:
                # Phase 8: HormoneManager Integration
                # Use as_dict() to get a safe snapshot
                chems_snapshot = self.brain.hormones.as_dict()

                data = {
                    "chemicals": chems_snapshot,
                    "status": {
                        "is_sleeping": self.brain.is_sleeping,
                        "is_drowsy": self.brain.is_drowsy,
                        "geo_y": self.brain.current_geo_y,
                        "strategy": getattr(self.brain, 'current_action_strategy', 'RESONATE'),
                    },
                    "memory": {
                        "concepts_count": len(self.brain.memory.concepts) if self.brain.memory else 0,
                        "sediments_count": len(self.brain.cortex.all_fragments) if self.brain.cortex else 0,
                    },
                    "timestamp": time.time()
                }
                
                # Feeder stats if available
                if hasattr(self.brain, 'translator') and hasattr(self.brain.translator, 'feeder'):
                    stats = self.brain.translator.feeder.get_stats()
                    data["feeder"] = stats
                
                # RNN training status
                if hasattr(self.brain, 'translator') and hasattr(self.brain.translator, 'model'):
                    model = self.brain.translator.model
                    
                    # Basic stats
                    rnn_data = {
                        "vocab_size": getattr(model, 'vocab_size', 0),
                        "hidden_size": getattr(model, 'hidden_size', 0),
                    }
                    
                    # Terrain stats (weight matrix analysis)
                    if model.params:
                        import numpy as np
                        try:
                            # Energy: Mean absolute value of weights
                            wxh = model.params.get("Wxh", np.array([]))
                            whh = model.params.get("Whh", np.array([]))
                            why = model.params.get("Why", np.array([]))
                            
                            if wxh.size > 0:
                                energy = float(np.mean(np.abs(wxh)) + np.mean(np.abs(whh)))
                                rnn_data["terrain_energy"] = round(energy, 4)
                            
                            if whh.size > 0:
                                # Roughness: Standard deviation (higher = more diverse patterns)
                                roughness = float(np.std(whh))
                                rnn_data["terrain_roughness"] = round(roughness, 4)
                            
                            if why.size > 0:
                                # Output complexity
                                output_energy = float(np.mean(np.abs(why)))
                                rnn_data["output_energy"] = round(output_energy, 4)
                            
                            # Weight sample for oscilloscope (32 values from Whh diagonal)
                            if whh.size > 0:
                                diag = np.diag(whh)[:32] if whh.shape[0] >= 32 else np.diag(whh)
                                normalized = (diag / (np.max(np.abs(diag)) + 1e-8)).tolist()
                                rnn_data["weight_sample"] = [round(v, 4) for v in normalized]
                                
                        except Exception as e:
                            pass
                    
                    data["rnn"] = rnn_data
                
                # Vital Signs (heart rate, respiration derived from chemicals)
                import random
                import math
                # Use the snapshot!
                chemicals = chems_snapshot
                
                # HRV (Heart Rate Variability) - natural fluctuation
                # Perlin-like smooth noise using sine waves
                t = time.time()
                hrv = (
                    math.sin(t * 0.5) * 2 +       # Slow wave (~0.08 Hz)
                    math.sin(t * 1.2) * 1.5 +     # Medium wave
                    random.uniform(-1.5, 1.5)      # Random noise
                )
                
                # Heart Rate: 70 BPM base, modulated by emotions + HRV
                # Scale Correction: Adrenaline 0-100, use 0-1 factor or adjust coeff
                # Old was "adrenaline" (0-1) * 30. Now is 0-100.
                # Adjusting coefficients: * 0.3
                base_hr = 70
                hr_mod = (
                    chemicals.get("adrenaline", 0) * 0.3 +  # Excitement increases HR
                    chemicals.get("cortisol", 0) * 0.2 -    # Stress increases HR
                    (chemicals.get("serotonin", 50) - 50) * 0.2 - # Calm decreases HR
                    (15 if self.brain.is_drowsy else 0)    # Drowsiness decreases HR
                )
                heart_rate = max(50, min(120, base_hr + hr_mod + hrv))
                
                # Respiration with slight fluctuation
                base_resp = 16
                resp_mod = (
                    chemicals.get("adrenaline", 0) * 0.08 +
                    chemicals.get("cortisol", 0) * 0.04 -
                    (4 if self.brain.is_sleeping else 0)
                )
                resp_noise = math.sin(t * 0.3) * 0.8 + random.uniform(-0.3, 0.3)
                respiration = max(10, min(30, base_resp + resp_mod + resp_noise))
                
                # Body Temperature with micro-fluctuation
                temp_base = 36.5 + chemicals.get("adrenaline", 0) * 0.005 # +0.5C at 100
                temp_noise = math.sin(t * 0.1) * 0.1 + random.uniform(-0.05, 0.05)
                temp = temp_base + temp_noise
                
                data["vitals"] = {
                    "heart_rate": round(heart_rate, 1),
                    "respiration": round(respiration, 1),
                    "temperature": round(temp, 2),
                }
                    
            return data
        except Exception as e:
            print(f"Telemetry Error: {e}")
            return {}

    async def broadcast_loop(self):
        """Periodically send telemetry to all clients"""
        while self.is_running:
            if self.clients:
                data = self.get_telemetry()
                message = json.dumps({"type": "telemetry", "data": data})
                
                # Send to all connected clients (iterate over copy to prevent mutation error)
                disconnected = set()
                for client in list(self.clients):
                    try:
                        await client.send(message)
                    except:
                        disconnected.add(client)
                
                self.clients -= disconnected
                
            await asyncio.sleep(0.5)  # 2 updates per second

    async def start_ws_server(self):
        """Start WebSocket server"""
        self.is_running = True
        
        # Retry logic for port binding
        for offset in range(10):
            try:
                port = self.ws_port + offset
                async with websockets.serve(self.handler, self.host, port):
                    print(f"📡 Telemetry WebSocket: ws://{self.host}:{port}")
                    self.ws_port = port # Update actual port
                    await self.broadcast_loop()
                break # Exit loop if serve returns (stopped)
            except OSError:
                print(f"⚠️ Telemetry Port {port} busy, trying next...")
                continue
            except Exception as e:
                print(f"❌ Telemetry Server Failed: {e}")
                break

    def run_in_thread(self):
        """Run WebSocket server in a separate thread"""
        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_ws_server())
        
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        print(f"🚀 Telemetry Server Started on port {self.ws_port}")
        return thread

    def stop(self):
        self.is_running = False
