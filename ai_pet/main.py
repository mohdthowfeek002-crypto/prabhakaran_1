import os
import sys
import ctypes
import random
from pathlib import Path
from google import genai
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import dotenv

dotenv_path = Path(__file__).resolve().with_name(".env")
dotenv.load_dotenv(dotenv_path)

image_path = os.getenv("photo")


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
    # Browsers
    "chrome": BROWSER_QUOTES,
    "firefox": BROWSER_QUOTES,
    "edge": BROWSER_QUOTES,
    "brave": BROWSER_QUOTES,
    # File Explorer
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

# 2. THE BACKGROUND WORKER
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
                padding: 12px;
                font-family: Arial;
                font-size: 13px;
                font-weight: bold;
                color: #333;
            }
        """)
        self.speech_bubble.hide()
        
        from PyQt6.QtGui import QPixmap
        self.sprite = QLabel()
        
        
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            150, 150, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.sprite.setPixmap(scaled_pixmap)
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.speech_bubble)
        layout.addWidget(self.sprite)
        self.setLayout(layout)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 250, screen.height() - 350, 200, 300)
        
        self.watch_timer = QTimer(self)
        self.watch_timer.timeout.connect(self.judge_screen)
        self.watch_timer.start(4000) 
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.speech_bubble.hide)
    def judge_screen(self):
        if not self.speech_bubble.isHidden():
            return  
            
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
        
        # --- PREVENT THREAD GARBAGE COLLECTION BUG ---
        # Stop/cleanup existing worker if it's running
        if hasattr(self, 'brain') and self.brain.isRunning():
            self.brain.wait()

        self.brain = AIBrainThread(found_target) 
        self.brain.response_ready.connect(self.speak)
        self.brain.start()
                
    def speak(self, text):
        self.speech_bubble.setText(text)
        self.speech_bubble.show()
        self.hide_timer.start(8000) 
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.speak("Enne thodathe, enikku vere paniyund!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = AmmavanPet()
    pet.show()
    sys.exit(app.exec())