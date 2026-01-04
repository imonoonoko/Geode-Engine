import requests
import json
import time

class OllamaClient:
    """
    Client for interacting with local Ollama instance.
    Focuses on speed and error resilience.
    """
    def __init__(self, model="gemma2:2b", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.chat_endpoint = f"{host}/api/chat"
        self.timeout = 5.0 # Connection timeout (seconds)

    def is_alive(self) -> bool:
        """ Check if Ollama is running """
        try:
            # Simple GET to root usually returns 200 "Ollama is running"
            resp = requests.get(self.host, timeout=1.0)
            return resp.status_code == 200
        except:
            return False

    def generate(self, prompt: str, system: str = "", stream: bool = True) -> str:
        """
        Generate text from Ollama using Chat API (better for personas).
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7,
            }
        }
        
        full_response = ""
        start_time = time.time()
        
        try:
            # We use stream=True to allow potential future real-time processing
            with requests.post(self.chat_endpoint, json=payload, stream=stream, timeout=self.timeout) as r:
                r.raise_for_status()
                
                if stream:
                    for line in r.iter_lines():
                        if line:
                            try:
                                body = json.loads(line)
                                if "message" in body and "content" in body["message"]:
                                    chunk = body["message"]["content"]
                                    full_response += chunk
                                if "done" in body and body["done"]:
                                    break
                            except json.JSONDecodeError:
                                pass
                else:
                    body = r.json()
                    full_response = body.get("message", {}).get("content", "")
                    
            duration = time.time() - start_time
            return full_response.strip()

        except requests.exceptions.RequestException as e:
            print(f"⚠️ [Ollama] Connection Error: {e}")
            return None
        except Exception as e:
            print(f"⚠️ [Ollama] Unexpected Error: {e}")
            return None

if __name__ == "__main__":
    # Quick Test
    client = OllamaClient()
    if client.is_alive():
        print("✅ Ollama is alive.")
        res = client.generate("こんにちは！", system="あなたは元気な少女です。タメ口で話して。")
        print(f"🤖 Response: {res}")
    else:
        print("❌ Ollama is NOT running.")
