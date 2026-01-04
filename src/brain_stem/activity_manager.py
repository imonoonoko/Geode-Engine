import time
import enum
import random
import threading
from src.dna import config
from src.dna.enums import ActivityState

class ActivityManager:
    """
    Kaname Activity Manager (Phase 3)
    
    責務:
    - カナメの「行動状態」を管理する
    - ホルモン状態やコマンドに基づいて、適切なアクティビティを開始・終了する
    - 排他制御（ゲーム中に勉強はできない等）
    
    States:
    - IDLE: 待機中（退屈が増える）
    - GAME: ゲーム中（ドーパミン↑、グルコース↓）
    - LESSON: レッスン中（知識↑、グルコース↓）
    - SLEEP: 睡眠中
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.lock = threading.Lock()
        self.current_state = ActivityState.IDLE
        self.last_state_change = time.time()
        
        # Cooldowns (秒)
        self.min_duration = 30.0  # 最低継続時間
        self.cooldown_lesson = 600.0 # 勉強間隔 (10分)
        self.last_lesson_time = 0.0
        
        print("🏃 ActivityManager Initialized.")
        
    def update(self):
        """ Main Loop から定期的に呼ばれる (e.g. 1Hz) """
        with self.lock:
            # 1. 状態ごとの更新
            if self.current_state == ActivityState.GAME:
                self._update_game()
            elif self.current_state == ActivityState.LESSON:
                self._update_lesson()
            elif self.current_state == ActivityState.IDLE:
                self._check_triggers()
            
            # 2. 強制終了チェック (生存本能)
            self._check_survival()

    def _check_triggers(self):
        """ IDLE時に何か始めるかチェック """
        try:
            from src.body.hormones import Hormone
            boredom = self.brain.hormones.get(Hormone.BOREDOM)
            glucose = self.brain.hormones.get(Hormone.GLUCOSE)
            
            now = time.time()
            
            # A. Game Trigger (退屈、かつ元気)
            if boredom > 80.0 and glucose > 30.0:
                # 確率でスタート
                if random.random() < 0.05:
                    self.start_activity(ActivityState.GAME)
                    return

            # B. Lesson Trigger (適度な退屈、Agniがいる、クールダウン済み)
            # Boredom > 60
            if boredom > 60.0 and glucose > 40.0:
                if now - self.last_lesson_time > self.cooldown_lesson:
                    if self.brain.mentor and self.brain.mentor.connected:
                         if random.random() < 0.02:
                             self.start_activity(ActivityState.LESSON)
                             return
        except Exception as e:
            print(f"⚠️ Activity Trigger Error: {e}")

    def _update_game(self):
        """ ゲーム中の監視 """
        # GamePlayer側で勝手に終わることもあるので、状態同期する
        # しかし GamePlayer は Body 側にあることが多い...
        # ここでは Brain 側から stop 指示を出すロジックのみ持つ
        pass 

    def _update_lesson(self):
        """ レッスン中の進行 """
        # LessonRoom は Brain.lesson_room にある想定
        if hasattr(self.brain, 'lesson_room'):
            self.brain.lesson_room.update()
            
            # レッスン終了判定
            if not self.brain.lesson_room.is_active:
                self.stop_activity()

    def _check_survival(self):
        """ 生存本能による強制中断 """
        # Glucose low -> Stop everything
        from src.body.hormones import Hormone
        glucose = self.brain.hormones.get(Hormone.GLUCOSE)
        
        if self.current_state in [ActivityState.GAME, ActivityState.LESSON]:
             if glucose < 20.0:
                 print("⚠️ Activity Stoped due to Hunger!")
                 self.stop_activity()
                 if hasattr(self.brain, 'input_stimulus'):
                     self.brain.input_stimulus("お腹が空いて...もう無理...")

    def request_activity(self, activity_name):
        """ ユーザー/外部コマンドによる要求 """
        activity_name = activity_name.upper()
        
        if activity_name == "GAME":
            print(f"👉 Request: GAME")
            return self.start_activity(ActivityState.GAME)
        elif activity_name == "LESSON":
            print(f"👉 Request: LESSON")
            return self.start_activity(ActivityState.LESSON)
        elif activity_name == "STOP":
            print(f"👉 Request: STOP")
            return self.stop_activity()
            
        return False

    def start_activity(self, state: ActivityState):
        """ アクティビティ開始処理 """
        with self.lock:
            if self.current_state == state:
                return False
            
            # 排他制御: 他のアクティビティ中は切り替え不可（STOPしてから）
            if self.current_state != ActivityState.IDLE:
                print(f"⚠️ Cannot start {state} while {self.current_state}")
                return False
                
            print(f"🏃 Starting Activity: {state.value}")
            
            if state == ActivityState.GAME:
                # Body側のGamePlayerを起動する必要がある。
                # Brain -> Body への指令は EventBus または直接参照で行う。
                # ここでは BodyHAL 経由か、Brain.body_ref を使う。
                if hasattr(self.brain, 'body_hal') and self.brain.body_hal:
                     # GamePlayer is usually on Body. 
                     # We can trigger it via an Event or a direct call if we have reference.
                     # Let's assume Brain has a way to signal Body.
                     pass
                     # For now, we rely on the implementation in main.py loop or a callback?
                     # Better: ActivityManager manages the logic, main.py observes it.
                     pass 
                     
            elif state == ActivityState.LESSON:
                if hasattr(self.brain, 'lesson_room'):
                    self.brain.lesson_room.start_lesson_metrics() # Reset metrics
                    # Note: We need a Non-Blocking start
                    self.brain.lesson_room.is_active = True
                    self.last_lesson_time = time.time()
            
            self.current_state = state
            self.last_state_change = time.time()
            return True

    def stop_activity(self):
        """ アクティビティ終了処理 """
        with self.lock:
            if self.current_state == ActivityState.IDLE:
                return
            
            print(f"🛑 Stopping Activity: {self.current_state.value}")
            
            if self.current_state == ActivityState.GAME:
                # Signal Body to stop game
                 # Implement via Event?
                 pass
                 
            elif self.current_state == ActivityState.LESSON:
                if hasattr(self.brain, 'lesson_room'):
                    self.brain.lesson_room.is_active = False

            self.current_state = ActivityState.IDLE
            return True
