import os
import sys
import ctypes
import random
from pathlib import Path
from google import genai
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QMovie
import dotenv

dotenv_path = Path(__file__).resolve().with_name(".env")
dotenv.load_dotenv(dotenv_path)

# Load different GIF paths from .env
default_photo = os.getenv("photo")
IMAGE_PATHS = {
    "standing": os.getenv("standing", default_photo),
    "walking_left": os.getenv("walking_left", default_photo),
    "walking_right": os.getenv("walking_right", default_photo),
    "peeing": os.getenv("peeing", default_photo),
    "sleeping": os.getenv("sleeping", default_photo),
    "reading": os.getenv("reading", default_photo),
}

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("api_key")
if not api_key:
    raise RuntimeError(f"No API key found. Create {dotenv_path} with GEMINI_API_KEY=your_key_here")

# 1. SETUP THE AI CLIENT
client = genai.Client(api_key=api_key)

BROWSER_QUOTES = [
    "Net-il ingane veruthe thappi samayam kalayukayano? Vallathum upakarapedunnath nokkeda!",
    "Enthra tab-ukal aanu thurannu vechirikkunne! RAM motham theerkkum, computer kedu varum.",
    "Google-il entharanu ithra thappan ullath? Pusthakam thurannu vaayikkeda!",
    "Browser-il kidannu veruthe scrolling... oru bodhavum illa!"
]

EXPLORER_QUOTES = [
    "Folder-ukal anganum inganum aakki enthu search cheyyuva? File-ukal polum vrithikku vekkan ariyilla!",
    "Athil entha ithra thappan ullath? Veettile alamaara ithupole eppozhenkilum vrithiyaakkiyo?",
    "Enthokkeyo file thappi nadakkunnu... vallathum padikkan ullath undo athil?",
    "Ee folder motham kalapila aayi kidakkunnu. Nammude kaalathokke file vrithikku ketti vekkumaayirunnu."
]

FALLBACK_QUOTES = {
    "youtube": [
        "YouTube-il video kandu irunno... oru collector aavan vendi padikkan ullathalle?",
        "Ivide irunnu video kandu samayam kalayathe poyi vallathum padikku!",
        "YouTube kaanukayano? Ninakku ithinakathunnu paisa vallathum kitto?"
    ],
    "netflix": [
        "Cinema kandu jeevitham kalayukayano? Nammude kaalathonnum ingane samayam kalayan pattillayirunnu.",
        "Series theerkkanaano ithra thidukkam? Pusthakam thurannu nokkeda!",
        "Padikkan ulla time il cinema kaanunno? Naattukar enthu parayum!"
    ],
    "code": [
        "Rathri urangande? Kannu kedu varum. Ithaanu ee computer-inte oru kozhappam.",
        "Code adichu adichu oru vazhikkaayi. Vallathum labhamundo ithukondu?",
        "Enneravum ee tharakkathanathil thanne irunno... valla velichathilum irangikkoode?"
    ],
    "steam": [
        "Valiya kutti aayille, iniyum ithum kalichu nadakkuvaano? Vallavarkkum upakarapedunna karyam cheythoode?",
        "Game kalichu irunno, naale kalyana karyam parayumbol thala thaazhthi nilkendi varum.",
        "Padutham onnum ille? Computer game kalikkan maathram nalla thidukkam."
    ],
    "amazon": [
        "Cash onnum illelum chilavakkalinu oru kuravum illa. Nammude kaalathokke...",
        "Online shopping cheythu veettile paisa motham theerkkuvaano?",
        "Avashyamillatha sadhanam vangikootan aano nee padikkunne?"
    ],
    "instagram": [
        "Reels kandu kandu jeevitham theerkkumo nee? Naalathe karyam aalochikkunnundo?",
        "Aarkko like koduthu samayam kalayunnu... poyi valla joli cheyyeda!",
        "Phone-ilum computer-ilum reels thanne pani... oru bodhavum illa."
    ],
    "chrome": BROWSER_QUOTES,
    "firefox": BROWSER_QUOTES,
    "edge": BROWSER_QUOTES,
    "brave": BROWSER_QUOTES,
    "file explorer": EXPLORER_QUOTES,
    "explorer": EXPLORER_QUOTES,
    "default": [
        "Ee computer nokki samayam kalayathe valla nalla karyangalum cheythoode?",
        "Padikkan ulla samayathu ithokke aano cheyyunne? Naattukar enthu parayum!",
        "Enthokkeya ee computeril nadakkunne... onnum manassilavunnilla."
    ]
}

def get_active_window_title():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.lower()
    except Exception:
        return ""

class AIBrainThread(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, target_app):
        super().__init__()
        self.target_app = target_app
        
    def run(self):
        try:
            prompt = f"""
            You are a stereotypical, highly judgmental Kerala Ammavan. 
            I just opened a computer application related to '{self.target_app}'. 
            Give a short, funny, sarcastic, passive-aggressive comment judging me for using it. 
            Respond ONLY in Manglish (Malayalam written in English letters). 
            Do not use English translations. Keep it short, maximum 2 sentences.
            """
            chat = client.chats.create(model="gemini-2.5-flash")
            response = chat.send_message(prompt)           
            self.response_ready.emit(response.text.strip().replace('"', ''))
        except Exception as e:
            print(f"API Failed ({e}), switching to offline fallback.")
            quotes_pool = FALLBACK_QUOTES.get(self.target_app, FALLBACK_QUOTES["default"])
            chosen_quote = random.choice(quotes_pool)
            self.response_ready.emit(chosen_quote)

class AmmavanPet(QWidget):
    def __init__(self):
        super().__init__()
        self.last_judged_window = ""
        self.screen_geo = QApplication.primaryScreen().geometry()
        self.direction = 1  # 1 for moving right, -1 for moving left
        self.target_x = None  
        self.dragging = False
        self.drag_position = QPoint()
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        
        self.speech_bubble = QLabel("")
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 10px;
                font-family: Arial;
                font-size: 11px;
                font-weight: bold;
                color: #333;
            }
        """)
        self.speech_bubble.hide()
        
        self.sprite = QLabel()
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.speech_bubble)
        layout.addWidget(self.sprite)
        self.setLayout(layout)
        
        # Medium-small sizing
        self.setGeometry(self.screen_geo.width() - 200, self.screen_geo.height() - 280, 150, 220)
        
        self.set_animation("standing")
        
        # Timers
        self.watch_timer = QTimer(self)
        self.watch_timer.timeout.connect(self.judge_screen)
        self.watch_timer.start(4000) 
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.speech_bubble.hide)
        
        # Idle behavior timer
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.trigger_random_idle_behavior)
        self.idle_timer.start(20000) 

        # Movement timer for walking animations
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_position)

    def set_animation(self, state_name):
        path = IMAGE_PATHS.get(state_name, default_photo)
        if not path or not os.path.exists(path):
            return
            
        if hasattr(self, 'current_movie') and self.current_movie:
            self.current_movie.stop()
            
        self.current_movie = QMovie(path)
        self.current_movie.setScaledSize(QSize(96, 96))
        self.sprite.setMovie(self.current_movie)
        self.current_movie.start()

    def trigger_random_idle_behavior(self):
        if not self.speech_bubble.isHidden() or self.dragging:
            return

        behaviors = ["walking_left", "walking_right", "peeing", "sleeping", "reading"]
        chosen = random.choice(behaviors)

        if chosen == "walking_left":
            self.direction = -1
            self.target_x = random.randint(0, self.screen_geo.width() // 2)
            self.set_animation("walking_left")
            self.move_timer.start(40)
        elif chosen == "walking_right":
            self.direction = 1
            self.target_x = random.randint(self.screen_geo.width() // 2, self.screen_geo.width() - self.width())
            self.set_animation("walking_right")
            self.move_timer.start(40)
        else:
            self.move_timer.stop()
            self.set_animation(chosen)
            # Stay in this pose for at least 20 seconds
            QTimer.singleShot(20000, lambda: self.reset_to_standing_if_idle())

    def update_position(self):
        current_pos = self.pos()
        new_x = current_pos.x() + (self.direction * 4)
        
        reached_target = False
        if self.direction == 1:
            if new_x >= self.screen_geo.width() - self.width() or (self.target_x is not None and new_x >= self.target_x):
                reached_target = True
        else:
            if new_x <= 0 or (self.target_x is not None and new_x <= self.target_x):
                reached_target = True

        if reached_target:
            self.move_timer.stop()
            self.target_x = None
            self.set_animation("standing")
        else:
            self.move(new_x, current_pos.y())

    def reset_to_standing_if_idle(self):
        if self.speech_bubble.isHidden() and not self.dragging:
            self.move_timer.stop()
            self.set_animation("standing")

    def judge_screen(self):
        active_window = get_active_window_title()
        
        safe_targets = [
            "youtube", "netflix", "amazon", "instagram", "steam", "code",
            "file explorer", "explorer",
            "chrome", "firefox", "edge", "brave"
        ]
        
        found_target = None
        for target in safe_targets:
            if target in active_window:
                found_target = target
                break
                
        if not found_target or found_target == self.last_judged_window:
            return
            
        self.last_judged_window = found_target
        
        self.move_timer.stop()
        self.set_animation("standing")
        
        if hasattr(self, 'brain') and self.brain.isRunning():
            self.brain.wait()

        self.brain = AIBrainThread(found_target) 
        self.brain.response_ready.connect(self.speak)
        self.brain.start()
                
    def speak(self, text):
        self.move_timer.stop()
        self.set_animation("standing")
        self.speech_bubble.setText(text)
        self.speech_bubble.show()
        self.hide_timer.start(8000) 
        
    # --- MOUSE DRAGGING OVERRIDES ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.move_timer.stop()
            self.speak("videda enne")
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = AmmavanPet()
    pet.show()
    sys.exit(app.exec())
    