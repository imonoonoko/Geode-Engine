import tkinter as tk
import time
import math
import random
import threading
import pyautogui
import queue
import src.dna.config as config
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False
    print("⚠️ tkinterdnd2 not found. Drag & Drop disabled.")

class KanameBody:
    def __init__(self, brain_ref):
        print("👻 Initializing Kaname Body (Phase 10 Stable)...")
        self.brain = brain_ref
        self.is_alive = True
        
        # UI Queue for Thread Safety (Bounded Phase 16)
        self.ui_queue = queue.Queue(maxsize=100)
        
        # UI Setup (Must be on Main Thread)
        if _DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("Kaname - The Sedimentary AI")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{config.DEFAULT_X}+{config.DEFAULT_Y}")
        self.root.config(bg="black")
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(self.root, width=config.WINDOW_WIDTH, height=config.WINDOW_HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Graphics
        cx = config.WINDOW_WIDTH // 2
        cy = config.WINDOW_HEIGHT // 2
        r = config.BODY_ORB_RADIUS
        
        self.orb_id = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#00ffaa", outline="")
        ar = r + 10
        self.aura_id = self.canvas.create_oval(cx-ar, cy-ar, cx+ar, cy+ar, fill="", outline="#00ffaa", width=2)
        
        # Right Click Menu
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="🍽️ 食べさせる (Feed)", command=self._open_feed_dialog)
        self.context_menu.add_command(label="変態 (Metamorphosis)", command=self._metamorphosis)
        self.context_menu.add_separator()
        
        # Game Submenu
        self.game_menu = tk.Menu(self.context_menu, tearoff=0)
        self.game_menu.add_command(label="🧱 ブロック崩し (Breakout)", command=lambda: self._start_game("breakout"))
        self.game_menu.add_command(label="🐍 スネーク (Snake)", command=lambda: self._start_game("snake"))
        self.game_menu.add_command(label="🎯 シューティング (Shooter)", command=lambda: self._start_game("shooter"))
        self.game_menu.add_command(label="🎲 ランダム (Random)", command=lambda: self._start_game("random"))
        self.game_menu.add_separator()
        self.game_menu.add_command(label="�️ 観戦モード切替", command=self._toggle_spectate)
        self.game_menu.add_command(label="�🛑 やめる (Stop)", command=self._stop_game)
        self.context_menu.add_cascade(label="🎮 ゲームで遊ぶ (Games)", menu=self.game_menu)
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📊 ステータス (Status)", command=self._show_status)
        self.context_menu.add_command(label="💤 寝かしつける/起こす (Sleep/Wake)", command=self._toggle_sleep)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="おやすみ (Exit)", command=self._quit_app)
        
        # Game Player (Phase C)
        self.game_player = None
        
        # Drag & Drop Support
        if _DND_AVAILABLE:
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self._on_drop)
                print("✨ Drag & Drop Enabled!")
            except Exception as e:
                print(f"⚠️ DnD Bind Error: {e}")
        
        # Feed callback (set by main.py)
        self.on_feed_file = None

        # Mouse Events
        self.canvas.bind("<Button-1>", self._on_poke)
        self.root.bind("<B1-Motion>", self._on_move)

        # Physics State
        self.pos_x = config.DEFAULT_X
        self.pos_y = config.DEFAULT_Y
        self.target_x = config.DEFAULT_X
        self.target_y = config.DEFAULT_Y
        self.bubbles = []
        self.grid_motion = [[0.0 for _ in range(config.RETINA_MOTION_GRID_COLS)] for _ in range(config.RETINA_MOTION_GRID_ROWS)]
        
        self.cursor_history = []
        self.pet_counter = 0
        self.last_input_time = time.time()
        
        self.current_color = [100.0, 255.0, 170.0]  # float で管理（easing 演算用）
        
        # Chat UI (Phase 15 - Sticky Window)
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.overrideredirect(True)
        self.chat_window.attributes("-topmost", True)
        self.chat_window.config(bg="black")
        self.chat_window.withdraw() # Hide initially
        
        self.chat_entry = tk.Entry(self.chat_window, bg="black", fg="white", insertbackground="white", font=("MS Gothic", 12), bd=0, highlightthickness=1, highlightbackground="#444")
        self.chat_entry.pack(fill="both", expand=True)
        self.chat_entry.pack(fill="both", expand=True)
        self.chat_entry.bind("<Return>", self._on_chat_submit)
        self.chat_entry.bind("<Escape>", lambda e: self._hide_chat_force())
        self.chat_window.bind("<FocusOut>", self._on_focus_out)
        
        self.is_chat_visible = False
        
        # Start UI Queue Processing
        self._process_ui_queue()
        
        # Lock for Grid Motion (Phase 14 Fix)
        self.grid_lock = threading.Lock()
        
        # Lock for Physics State (Phase 19 Demon Phase 5)
        self.physics_lock = threading.Lock()

    def run_threads(self, immune_system=None):
        """ Start background physics/animation threads """
        if immune_system:
            print("🛡️ Body Threads Protected by Immune System.")
            target_drift = immune_system.protect_loop(self.drift_loop, name="Body-Physics")
            target_anim = immune_system.protect_loop(self.animation_loop, name="Body-Anim")
        else:
            print("⚠️ Body Threads Unprotected!")
            target_drift = self.drift_loop
            target_anim = self.animation_loop

        t_drift = threading.Thread(target=target_drift, daemon=True)
        t_anim = threading.Thread(target=target_anim, daemon=True)
        t_drift.start()
        t_anim.start()

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def _quit_app(self):
        print("Saving memories...")
        self.brain.save_memory(async_mode=False)
        self.is_alive = False
        self.root.destroy()

    def _metamorphosis(self):
        """ Hot Reload Config (Metamorphosis) """
        import importlib
        try:
            importlib.reload(config)
            print("🦋 Metamorphosis: Config reloaded.")
            print(f"   Current Mood Color: {config.COLOR_JOY}")
            
            # Visual Feedback
            # self.say("変態...完了...", 1.5) # User requested silence
            # Flash white (optional, but might conflict with animation loop so just say is enough)
            
        except Exception as e:
            print(f"⚠️ Metamorphosis Failed: {e}")
            # self.say("失敗...痛い...", 1.5)

    def _show_status(self):
        """ Show current biological status in a bubble """
        from src.body.hormones import Hormone
        with self.brain.lock:
            hp = int(self.brain.hormones.get(Hormone.GLUCOSE))
            dop = int(self.brain.hormones.get(Hormone.DOPAMINE))
            ser = int(self.brain.hormones.get(Hormone.SEROTONIN))
            state = "Sleeping" if self.brain.is_sleeping else "Awake"
        
        status_text = f"Health: {hp}%\nMood: {dop}%\nSanity: {ser}%\nState: {state}"
        self.say(status_text, 1.0)
        
    def _toggle_sleep(self):
        """ Force sleep toggle """
        with self.brain.lock:
            self.brain.is_sleeping = not self.brain.is_sleeping
            new_state = "Sleeping" if self.brain.is_sleeping else "Awake"
        self.say(f"...{new_state}...", 1.0)

    def _start_game(self, game_type: str = "random"):
        """ Start playing a game """
        import random as rand
        try:
            from src.games.game_player import GamePlayer
            
            if self.game_player and self.game_player.is_playing:
                # 既にプレイ中なら何もしない（固定セリフは言わない）
                print("⚠️ Already playing a game")
                return
            
            self.game_player = GamePlayer(brain=self.brain)
            
            # ゲーム種類ごとのアクションマッピング
            game_configs = {
                "breakout": {
                    "name": "breakout",
                    "mapping": {0: "noop", 1: "left", 2: "right"}
                },
                "snake": {
                    "name": "snake",
                    "mapping": {0: "noop", 1: "up", 2: "down", 3: "left", 4: "right"}
                },
                "shooter": {
                    "name": "shooter",
                    "mapping": {0: "noop", 1: "left", 2: "right", 3: "up", 4: "down", 5: "space"}
                },
                "generic": {
                    "name": "generic",
                    "mapping": {0: "noop", 1: "left", 2: "right", 3: "up", 4: "down", 5: "space", 6: "enter"}
                }
            }
            
            # ランダム選択
            if game_type == "random":
                game_type = rand.choice(["breakout", "snake", "shooter"])
            
            config = game_configs.get(game_type, game_configs["generic"])
            
            self.game_player.start_game(
                game_type=game_type,
                action_mapping=config["mapping"]
            )
            
            # 固定セリフは言わない（R15違反）
            print(f"🎮 Game started: {game_type}")
            
        except Exception as e:
            print(f"⚠️ Game start error: {e}")
    
    def _stop_game(self):
        """ Stop playing the current game """
        if self.game_player and self.game_player.is_playing:
            self.game_player.stop_game()
            print("🎮 Game stopped from context menu")
        else:
            print("⚠️ Not playing any game")
    
    def _toggle_spectate(self):
        """ Toggle between spectate mode and background mode """
        if self.game_player:
            new_headless = self.game_player.toggle_spectate()
            mode_str = "バックグラウンド" if new_headless else "観戦モード"
            print(f"👁️ Switched to: {mode_str}")

    def _animate_chew(self):
        """ Visual Pulse for Eating """
        def _pulse():
            for _ in range(3):
                try: self.ui_queue.put_nowait({"action": "pulse_ghost", "data": 15})
                except: pass
                time.sleep(0.15)
                try: self.ui_queue.put_nowait({"action": "pulse_ghost", "data": 0})
                except: pass
                time.sleep(0.15)
        threading.Thread(target=_pulse, daemon=True).start()

    def _open_feed_dialog(self):
        """ Open file dialog to feed a text file """
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="食べさせるファイルを選択",
            filetypes=[("Text & Markdown", "*.txt *.md"), ("All files", "*.*")]
        )
        if file_path and self.on_feed_file:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                # Callback to main system (hormone response handled there)
                self.on_feed_file(content)
                self._animate_chew()
                self.say("もぐもぐ...", 1.0)
            except Exception as e:
                print(f"⚠️ File Read Error: {e}")
                self.say("...読めない", 1.0)

    # ==========================================
    # 🖱️ Mouse Events & Input
    # ==========================================
    def _on_drop(self, event):
        """ Handle File Drop """
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        print(f"📥 Dropped File: {file_path}")
        
        if self.on_feed_file:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if self.on_feed_file(content):
                    self._animate_chew()
                    # self.ui_queue.put(("say", "ごちそうさま！")) # User requested silence
                    pass
            except Exception as e:
                print(f"⚠️ Drop Feed Error: {e}")
                # self.ui_queue.put(("say", "うぅ..."))

    def _on_poke(self, event):
        # Phase 8 Step 3: Event-Driven
        from src.body.events import Event
        self.brain.events.emit(Event.POKED)
        self.say("...!", 1.5)
        self.last_input_time = time.time()
        self._wake_up()

    def _on_move(self, event):
        new_x = self.root.winfo_x() + (event.x - 150) # 150 is half size
        new_y = self.root.winfo_y() + (event.y - 150)
        
        with self.physics_lock:
            self.pos_x = new_x
            self.pos_y = new_y
            self.target_x = new_x
            self.target_y = new_y
            
        self.root.geometry(f"+{int(new_x)}+{int(new_y)}")
    
    def get_center_pos(self):
        """ Thread-safe accessor for Brain/Senses """
        with self.physics_lock:
             # Window is 300x300 (or config size). Orb center is +150, +150 relative to window.
             # Wait, config.WINDOW_WIDTH is 400. Orb center logic in body.py (init) says:
             # create_oval(50, 50, 250, 250) -> Center is 150.
             # So center is always +150 unless config changed.
             # Let's trust the existing logic in main.py which used +150.
             return self.pos_x + 150, self.pos_y + 150

    def _process_ui_queue(self):
        """ [Phase 10] Main Thread UI Consumer (Throttled Phase 11) """
        processed_count = 0
        try:
            while processed_count < config.UI_QUEUE_BATCH_SIZE:
                # Process all pending tasks (non-blocking)
                task = self.ui_queue.get_nowait()
                if task:
                    action = task.get("action")
                    data = task.get("data")
                    
                    if action == "move_window":
                        self.root.geometry(data)
                    elif action == "update_color":
                        self.canvas.itemconfig(self.orb_id, fill=data)
                        self.canvas.itemconfig(self.aura_id, outline=data)
                    elif action == "create_bubble":
                        self._create_bubble_ui(data)
                    elif action == "update_bubbles":
                        self._update_bubbles_ui()
                    elif action == "pulse_ghost":
                        self._update_pulse_ui(data)
                    elif action == "show_chat":
                        if not self.is_chat_visible:
                            # Place chat window BELOW current body position
                            cx = self.root.winfo_x() + 50
                            cy = self.root.winfo_y() + 320
                            self.chat_window.geometry(f"300x30+{cx}+{cy}")
                            self.chat_window.deiconify()
                            self.chat_entry.focus_set()
                            self.is_chat_visible = True
                    elif action == "hide_chat":
                        # Only hide if NOT focused (User is not typing), unless forced
                        force_close = (data == "force")
                        try:
                            if force_close or self.root.focus_get() != self.chat_entry:
                                self.chat_window.withdraw()
                                self.is_chat_visible = False
                                # If forced, remove focus to prevent typing in hidden window
                                if force_close:
                                    self.root.focus_set()
                        except:
                             self.chat_window.withdraw()
                             self.is_chat_visible = False
                    
                    self.ui_queue.task_done()
                    processed_count += 1
                else: 
                    break
        except queue.Empty:
            pass
        
        # --- Minecraft Context Auto-Hide (Focus Based) ---
        try:
            is_mc_connected = hasattr(self.brain, 'minecraft') and self.brain.minecraft and self.brain.minecraft.current_state.get("connected")
            is_mc_focused = hasattr(self.brain, 'minecraft_action') and self.brain.minecraft_action and self.brain.minecraft_action.is_minecraft_focused()
            
            # Hide if MC is connected AND focused
            should_hide = is_mc_connected and is_mc_focused
            
            if should_hide:
                if self.root.state() != "withdrawn":
                    self.root.withdraw()
                    self.chat_window.withdraw()
                    print("👻 Minecraft focused: Hiding body UI.")
            else:
                # Show if MC is disconnected OR MC lost focus
                if self.root.state() == "withdrawn":
                    self.root.deiconify()
                    print("👻 Minecraft lost focus or disconnected: Showing body UI.")
        except:
            pass
        
        if self.is_alive:
            self.root.after(20, self._process_ui_queue)

    def _on_chat_submit(self, event):
        """ Handle Chat Input """
        text = self.chat_entry.get()
        if text.strip():
            print(f"User Said: {text}")
            self.brain.input_stimulus(text) # Send to Brain
            self.chat_entry.delete(0, tk.END)
            self._create_bubble_ui("...") # Feedback
            
            # Hide after send
            self._hide_chat_force()

    def _hide_chat_force(self):
        """ Force hide chat window """
        self.chat_window.withdraw()
        self.is_chat_visible = False
        self.root.focus_set()

    def _on_focus_out(self, event):
        """ Auto-hide when focus is lost (clicked away) """
        # Slight delay to allow focus transfer
        self.root.after(100, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        try:
            # If focus is NOT on entry anymore, hide.
            # Note: focus_get() returns widget object.
            focused = self.root.focus_get()
            if focused != self.chat_entry:
                print("👻 Chat lost focus, hiding.")
                self.chat_window.withdraw()
                self.is_chat_visible = False
        except:
            pass

    def update_state(self, heart_rate):
        """ Called from Core (Thread) -> Queue Update """
        # Logic runs in thread, UI update queued
        
        # Thread Safety Fix [Demon Audit]
        # Use as_dict for snapshot to avoid holding lock while calculating colors
        with self.brain.lock:
            chems = self.brain.hormones.as_dict()
            
        dop = chems.get("dopamine", 0) # 0-100
        ser = chems.get("serotonin", 50)
        adr = chems.get("adrenaline", 0)
        oxy = chems.get("oxytocin", 0)
        cort = chems.get("cortisol", 0) 
        
        # Scaling correction for color logic if needed. 
        # Existing logic seems to expect 0-1 ratio for some comparisons? 
        # Line 336: if oxy > 0.7: ...
        # If hormones are 0-100, checking > 0.7 is always true if > 1.
        # FIX: Normalize for color logic or update thresholds.
        # Let's normalize by dividing by 100.0 for the color logic block.
        
        dop /= 100.0
        ser /= 100.0
        adr /= 100.0
        oxy /= 100.0
        cort /= 100.0
        
        target = list(config.COLOR_NEUTRAL)
        
        # Pain has priority
        if cort > config.COLOR_THRESHOLD_PAIN:
             target = [100, 50, 100] # Pale Purple (Sick)
             if cort > config.COLOR_THRESHOLD_DYING: target = [50, 50, 50] # Gray (Dying)

        elif oxy > 0.7: target = list(config.COLOR_LOVE)
        elif dop > config.COLOR_THRESHOLD_HIGH: target = list(config.COLOR_JOY)
        elif adr > config.COLOR_THRESHOLD_HIGH and dop > config.COLOR_THRESHOLD_MEDIUM: target = [255, 180, 50]
        elif adr > config.COLOR_THRESHOLD_HIGH: target = list(config.COLOR_ANGER)
        elif ser > config.COLOR_THRESHOLD_HIGH: target = list(config.COLOR_RELAX)
        elif self.brain.is_sleeping: target = list(config.COLOR_SLEEP)
        elif self.brain.is_drowsy: target = [60, 60, 80]
        
        # Easing logic (simplified for thread)
        for i in range(3):
            self.current_color[i] += (target[i] - self.current_color[i]) * 0.1
            
        hex_color = f"#{int(self.current_color[0]):02x}{int(self.current_color[1]):02x}{int(self.current_color[2]):02x}"
        
        try:
            self.ui_queue.put_nowait({"action": "update_color", "data": hex_color})
        except queue.Full: pass



    def say(self, text, speed=1.0):
        """ Called from Core (Thread) -> Queue Bubble """
        if not text or text == "......": return
        try:
            self.ui_queue.put_nowait({"action": "create_bubble", "data": text})
        except queue.Full: pass

        
    def _update_pulse_ui(self, scale):
        """ Update Ghost Size (Main Thread) """
        base = config.BODY_ORB_RADIUS
        r = base + scale
        
        # Center dynamic calc
        cx = config.WINDOW_WIDTH // 2
        cy = config.WINDOW_HEIGHT // 2
        
        self.canvas.coords(self.orb_id, cx - r, cy - r, cx + r, cy + r)
        
        # Aura follows with delay? No, sync for now
        ar = r + 10 
        self.canvas.coords(self.aura_id, cx - ar, cy - ar, cx + ar, cy + ar)

    def _create_bubble_ui(self, text):
        """ Actual UI creation on Main Thread """
        cx = config.WINDOW_WIDTH // 2
        start_x = cx + random.randint(-50, 50)
        start_y = config.WINDOW_HEIGHT // 4 # Top area
        
        text_id = self.canvas.create_text(start_x, start_y, text=text, fill="white", font=("MS Gothic", 11, "bold"))
        self.bubbles.append({"id": text_id, "x": start_x, "y": start_y, "life": 80, "speed": random.uniform(0.3, 0.8)})

    def animation_loop(self):
        """ Animation Logic (Thread) -> Queue Updates """
        from src.body.hormones import Hormone  # Fix: Body-Anim Hormone import
        pulse_phase = 0.0
        
        while self.is_alive:
            # Debug heartbeat (every 100 frames approx 5 sec)
            # pulse_phase += 1
            # if pulse_phase % 100 == 0:
            #     print("🌀 Body-Anim Alive")
            # User Request: "Remove pulsing movement" -> Logic Disabled
            # We still need the loop for Bubbles and timing.
            
            # Send Pulse Data to UI Queue (Disabled Pulse, Keep Bubbles)
            try:
                # self.ui_queue.put_nowait({"action": "pulse_ghost", "data": scale})
                self.ui_queue.put_nowait({"action": "update_bubbles", "data": None})
            except queue.Full: pass
            
            # Phase 15: Visualizing Curiosity/Fear
            # Priority: Adrenaline (!) > Dopamine (?)
            adrenaline = self.brain.hormones.get(Hormone.ADRENALINE)
            dopamine = self.brain.hormones.get(Hormone.DOPAMINE)
            
            if adrenaline > 80.0:
                if random.random() < 0.05:
                    try: self.ui_queue.put_nowait({"action": "create_bubble", "data": "!"})
                    except: pass
            elif dopamine > 70.0:
                if random.random() < 0.05:
                    try: self.ui_queue.put_nowait({"action": "create_bubble", "data": "?"})
                    except: pass

            # Autonomous Timing (Heartbeat)
            # Adrenaline increases Frame Rate / Pulse Speed
            # FIX: Throttle to max 30 FPS (0.033s) to prevent UI Queue flood
            anim_delay = 0.05
            if self.brain.is_sleeping:
                anim_delay = 0.2 # Slow breathing
            else:
                adrenaline = self.brain.hormones.get(Hormone.ADRENALINE)
                # Old: max(0.015, 0.05 - (adrenaline * 0.03)) -> Max ~66 FPS
                # New: max(0.033, 0.06 - (adrenaline * 0.03)) -> Max ~30 FPS
                # Adrenaline is 0-100. 0.06 - (100 * 0.0003) = 0.03
                anim_delay = max(0.033, 0.06 - (adrenaline * 0.0003))

            time.sleep(anim_delay)
            
    def _update_bubbles_ui(self):
        """ Update bubble positions (Main Thread) """
        active = []
        for b in self.bubbles:
            b["y"] -= b["speed"]
            b["life"] -= 1
            self.canvas.coords(b["id"], b["x"], b["y"])
            
            # Fade out
            if b["life"] < 40:
                intensity = int(255 * (b["life"] / 40))
                intensity = max(0, min(255, intensity))
                hex_col = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                try: self.canvas.itemconfig(b["id"], fill=hex_col)
                except: pass
        
            if b["life"] > 0:
                active.append(b)
            else:
                self.canvas.delete(b["id"])
        self.bubbles = active

    def update_visual_senses(self, grid_motion):
        with self.grid_lock:
            self.grid_motion = grid_motion

    def drift_loop(self):
        """ 自律移動・物理演算ループ (Thread) """
        rows = config.RETINA_MOTION_GRID_ROWS
        cols = config.RETINA_MOTION_GRID_COLS
        self.grid_motion = [[0.0 for _ in range(cols)] for _ in range(rows)] 
        
        while self.is_alive:
            # Mouse Tracking
            try: cursor_x, cursor_y = pyautogui.position()
            except: cursor_x, cursor_y = self.screen_w//2, self.screen_h//2
            
            dist_to_cursor = math.sqrt((cursor_x - self.pos_x - 150)**2 + (cursor_y - self.pos_y - 150)**2)
            
            # Petting Detection
            if dist_to_cursor < 100:
                self.cursor_history.append((cursor_x, cursor_y))
                if len(self.cursor_history) > 20:
                    self.cursor_history.pop(0)
                    total_move = sum(math.sqrt((self.cursor_history[i][0]-self.cursor_history[i-1][0])**2 + (self.cursor_history[i][1]-self.cursor_history[i-1][1])**2) for i in range(1, len(self.cursor_history)))
                    if total_move > 100:
                        self.pet_counter += 1
                        if self.pet_counter > 10:
                            # Phase 8 Step 3: Event-Driven
                            from src.body.events import Event
                            self.brain.events.emit(Event.PETTED)
                            self.pet_counter = 0
                            self.last_input_time = time.time()
                            self._wake_up()
                            
                # Phase 15: Chat Hover Check
                # 距離が近い & まだ表示していない → つぶやきのようにチャットを出す (Mouse Hover)
                # ユーザーが入力中 (Focus) の場合は閉じないが、あまりに遠くに行ったら閉じる (Force Close)
                
                is_focused = False
                try: 
                    is_focused = (self.root.focus_get() == self.chat_entry)
                except: pass

                if dist_to_cursor < 150:
                    try: self.ui_queue.put_nowait({"action": "show_chat", "data": None})
                    except queue.Full: pass
                
                # Close Logic
                # Debug distance
                # if dist_to_cursor > 150: print(f"Dist: {dist_to_cursor:.1f}")

                if dist_to_cursor > 250: # Force Close Zone (Reduced from 300)
                    try: self.ui_queue.put_nowait({"action": "hide_chat", "data": "force"})
                    except queue.Full: pass
                elif dist_to_cursor > 200 and not is_focused: # Gentle Close Zone
                    try: self.ui_queue.put_nowait({"action": "hide_chat", "data": None})
                    except queue.Full: pass

                    
            else:
                self.cursor_history = []
                self.pet_counter = 0

            # Idle Check
            if time.time() - self.last_input_time > 600:
                pass 
            
            # Movement Target Logic
            # Using 0-100 scale for checks. 0.6 -> 60.0
            from src.body.hormones import Hormone
            
            dopamine = self.brain.hormones.get(Hormone.DOPAMINE)
            adrenaline = self.brain.hormones.get(Hormone.ADRENALINE)
            boredom = self.brain.hormones.get(Hormone.BOREDOM) # Phase 14
            
            found_target = False
            if dist_to_cursor < 300 and not self.brain.is_sleeping:
                if dopamine > config.THRESHOLD_HIGH: # Follow
                    self.target_x = cursor_x - 150
                    self.target_y = cursor_y - 150
                    found_target = True
                elif adrenaline > config.THRESHOLD_HIGH: # Flee
                    self.target_x = self.pos_x - (cursor_x - self.pos_x) * 0.5
                    self.target_y = self.pos_y - (cursor_y - self.pos_y) * 0.5
                    found_target = True
                
                if self.brain.is_sleeping:
                    self.target_x, self.target_y = self.pos_x, self.pos_y
                    found_target = True

            # Phase 14: Curiosity Engine
            # If bored, wander randomly (Active Inference for Exploration)
            if not found_target and not self.brain.is_sleeping:
                if boredom > config.THRESHOLD_MOVEMENT_BOREDOM:
                    if random.random() < 0.05: # Low probability per tick to change target
                        # Pick random point on screen
                        self.target_x = random.randint(0, self.screen_w - 300)
                        self.target_y = random.randint(0, self.screen_h - 300)
                        found_target = True
                        print(f"👻 Wandering due to Boredom ({boredom:.1f}%)")

            # Retina Guided Movement (Phase 14: Lowered Threshold)
            # 30.0 -> 15.0 to allow movement even in mild moods
            if not found_target and not self.brain.is_sleeping and dopamine > 15.0:
                max_move, max_gx, max_gy = 0.0, 1, 1
                
                with self.grid_lock:
                    local_grid = [row[:] for row in self.grid_motion] # Copy under lock
                
                for gy in range(config.RETINA_MOTION_GRID_ROWS):
                    for gx in range(config.RETINA_MOTION_GRID_COLS):
                        if local_grid[gy][gx] > max_move:
                            max_move = local_grid[gy][gx]
                            max_gx, max_gy = gx, gy
                
                if max_move > 0.01:
                    self.target_x = int(self.screen_w * (max_gx + 0.5) / config.RETINA_MOTION_GRID_COLS) - 150
                    self.target_y = int(self.screen_h * (max_gy + 0.5) / config.RETINA_MOTION_GRID_ROWS) - 150

            # Physics Update (Easing)
            # Use lock to prevent fighting with user drag logic
            with self.physics_lock:
                dist_to_target = math.sqrt((self.target_x - self.pos_x)**2 + (self.target_y - self.pos_y)**2)
                
                speed_factor = 0.05 
                
                glucose = self.brain.hormones.get(Hormone.GLUCOSE)
                dopamine = self.brain.hormones.get(Hormone.DOPAMINE)
                
                if glucose < config.THRESHOLD_LOW:
                    if dopamine > config.THRESHOLD_HIGH:
                         # Bravado
                         speed_factor = 0.08 
                    else:
                         # Lethargy
                         speed_factor = 0.01
                elif glucose > 80.0:
                    # Hyperactive
                    speed_factor = 0.07
                
                # Phase 14: Boredom increases fidget speed
                if boredom > 60.0:
                     speed_factor += 0.02

                if self.brain.is_sleeping: 
                    dx, dy = 0, 0
                elif dist_to_target > 5:  # 修正: 150→5 (脳からの微細な移動指令を受け付ける)
                    dx = (self.target_x - self.pos_x) * speed_factor
                    dy = (self.target_y - self.pos_y) * speed_factor
                    self.pos_x += dx
                    self.pos_y += dy
                else: 
                    dx, dy = 0, 0
                
                cur_x, cur_y = self.pos_x, self.pos_y # Copy for UI update outside lock (optional)

            # Floating Motion
            float_offset = self._calculate_floating_motion()
            
            with self.physics_lock:
                # Boundary Check
                self.pos_x = max(0, min(self.screen_w - 300, self.pos_x))
                self.pos_y = max(0, min(self.screen_h - 300, self.pos_y))
                final_x, final_y = self.pos_x, self.pos_y

            # Apply Position (Thread Safe Queue Update)
            geo_str = f"+{int(final_x)}+{int(final_y + float_offset)}"
            try: self.ui_queue.put_nowait({"action": "move_window", "data": geo_str})
            except queue.Full: pass
            
            
            # Autonomous Physics Rate (Reflexes)
            # FIX: Throttle to max 30 FPS (0.033s) to prevent Window Manager overload
            phy_delay = 0.05
            if self.brain.is_sleeping:
                phy_delay = 0.5 # Hibernate physics while sleeping
            else:
                # High Dopamine/Adrenaline = Faster reaction
                excitement = max(adrenaline, dopamine)
                # Adrenaline/Dopamine 0-100.
                # max(0.033, 0.08 - (100 * 0.0005)) = 0.03
                phy_delay = max(0.033, 0.08 - (excitement * 0.0005))
            
            # Phase 10: Micro-Movements (Fidgeting) - 生きている感を出す
            # ドーパミンが低くても少し動く (Brownian Motion)
            # Phase 14: Boredom increases fidget frequency
            fidget_chance = 0.1 + (boredom * 0.002) # Max +0.2 at 100% -> 0.3
            
            if not found_target and not self.brain.is_sleeping and random.random() < fidget_chance:
                fidget_x = random.randint(-2, 2)
                fidget_y = random.randint(-2, 2)
                with self.physics_lock:
                     self.target_x += fidget_x
                     self.target_y += fidget_y
            
            time.sleep(phy_delay)

    def _calculate_floating_motion(self):
        t = time.time()
        # Complex Breathing (Phase 19)
        # Y: 呼吸 (Breathing) - Sin wave
        offset_y = math.sin(t * 2) * 8
        # X: ゆらぎ (Sway) - Slower Cos wave
        offset_x = math.cos(t * 1.3) * 3
        
        # Merge into single offset (approximate for UI queue)
        # Note: UI queue expects single float for Y offset in current implementation?
        # Wait, move_window action takes geo_str. We can add X offset too.
        # But _calculate_floating_motion currently returns float.
        # Let's keep it simple for now and just return Y, but make it more organic.
        return offset_y + (math.sin(t * 0.5) * 2)  # Base breath + Deep breath

    def _wake_up(self):
         self.brain.is_sleeping = False

    def apply_force(self, fx, fy):
        """ 
        Active Inference Motor Command.
        Brain sends a force vector (-1.0 to 1.0).
        Body translates this into a Target Position Shift.
        """
        if self.brain.is_sleeping: return
        
        strength = 20.0 # Pixels per force unit per tick? No, this is called periodically.
        # If brain calls this every 1 sec, shift needs to be significant.
        # Let's say force 1.0 means "Move 50 pixels this way".
        
        scale = 50.0
        
        with self.physics_lock:
            # Update TARGET, not position, so physics easing handles the motion smoothing.
            # We add to current target to allow accumulation.
            self.target_x += fx * scale
            self.target_y += fy * scale
            
            # Clamp Target to Screen
            self.target_x = max(0, min(self.screen_w - 300, self.target_x))
            self.target_y = max(0, min(self.screen_h - 300, self.target_y))
