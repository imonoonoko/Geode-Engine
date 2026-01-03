import time
import threading
import random

try:
    import pyautogui
    # Fail-Safe: Mouse to corner will abort
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None
    print("⚠️ 'pyautogui' library is missing. Physical actions disabled.")

try:
    # Optional: For window focus checking
    # On Windows, ctypes is built-in
    import ctypes
    user32 = ctypes.windll.user32
except:
    user32 = None

class MinecraftActionModule:
    """
    The Hands & Feet of Geode for Minecraft.
    Uses PyAutoGUI to simulate physical inputs.
    
    SAFETY FIRST:
    - Will ONLY act if Minecraft window is focused.
    - Panic Button: Move mouse to corner to kill.
    """
    def __init__(self, brain=None):
        self.brain = brain
        self.is_active = True
        self.last_action_time = time.time()
        
        # Calibration (Sensitivity)
        # Assuming defaults, modify based on testing
        self.mouse_sensitivity = 1.0 
        
    def is_minecraft_focused(self) -> bool:
        """Check if Minecraft is the active window (Windows only)"""
        if not user32: return True
        
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        raw_title = buff.value
        title = raw_title.lower()
        
        # Check against known Minecraft titles
        # Bedrock: "Minecraft"
        # Java: "Minecraft* "
        focused = "minecraft" in title
        
        # Logging disabled to reduce spam
        
        return focused

    def act(self, intent: str, **kwargs):
        """
        Execute an action based on intent.
        intent: "MOVE_FORWARD", "STOP", "LOOK_RIGHT", "ATTACK", "JUMP"
        """
        if not pyautogui: return
        if not self.is_active: return
        
        # 1. Safety Check (Focus)
        focused = self.is_minecraft_focused()
        
        if not focused:
            # Optional: Add small log if we were supposed to act but didn't
            return

        print(f"🕹️ [MOTOR] Executing: {intent}")

        # 2. Execute
        try:
            if intent == "MOVE_FORWARD":
                duration = kwargs.get("duration", 0.5)
                # Hold W
                pyautogui.keyDown('w')
                time.sleep(duration)
                pyautogui.keyUp('w')
                
            elif intent == "MOVE_BACK":
                pyautogui.keyDown('s')
                time.sleep(kwargs.get("duration", 0.5))
                pyautogui.keyUp('s')
                
            elif intent == "TURN_RIGHT":
                strength = kwargs.get("strength", 100)
                # Relative Move
                pyautogui.moveRel(int(strength * self.mouse_sensitivity), 0)
                
            elif intent == "TURN_LEFT":
                strength = kwargs.get("strength", 100)
                pyautogui.moveRel(int(-strength * self.mouse_sensitivity), 0)
                
            elif intent == "JUMP":
                pyautogui.press('space')
                
            elif intent == "ATTACK":
                pyautogui.click() # Left click
            
            elif intent == "USE":
                pyautogui.click(button='right')
                
            self.last_action_time = time.time()
            
        except pyautogui.FailSafeException:
            print("🚨 FAIL-SAFE TRIGGERED. Stopping Action Module.")
            self.is_active = False
        except Exception as e:
            print(f"⚠️ Action Error: {e}")

    def stop(self):
        self.is_active = False
        if pyautogui:
            pyautogui.keyUp('w')
            pyautogui.keyUp('s')
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')
