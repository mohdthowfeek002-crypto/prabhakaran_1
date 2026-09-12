import os
import sys
import ctypes
import random
from dotenv import load_dotenv
from google import genai
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QMovie, QPixmap

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip('\'"')
AMMAVAN_IDLE = (os.getenv("ammavan_idle") or os.getenv("AMMAVAN_IDLE", "")).strip('\'"')
AMMAVAN_TALK = (os.getenv("ammavan_talk") or os.getenv("AMMAVAN_TALK", "")).strip('\'"')
PHOTO_FALLBACK = (os.getenv("photo") or os.getenv("PHOTO_FALLBACK", "")).strip('\'"')

# 2. SETUP AI CLIENT
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Failed to initialize Gemini client: {e}")
    client = None

# Offline fallback library
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
            if not client:
                raise ValueError("AI Client not initialized")

            prompt = f"""
            You are a stereotypical, highly judgmental Kerala Ammavan. 
            I just opened an application related to '{self.target_app}'. 
            Give a short, funny, sarcastic, passive-aggressive comment judging me for using it. 
            Respond ONLY in Manglish (Malayalam written in English letters). 
            Do not provide English translations. Keep it short, maximum 2 sentences.
            """
            chat = client.chats.create(model="gemini-2.0-flash")
            response = chat.send_message(prompt)
            self.response_ready.emit(response.text.strip().replace('"', ''))
        except Exception as e:
            print(f"API Exception ({e}), serving fallback response.")
            quotes_pool = FALLBACK_QUOTES.get(self.target_app, FALLBACK_QUOTES["default"])
            self.response_ready.emit(random.choice(quotes_pool))

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

        # Speech Bubble
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

        # Character Sprite
        self.sprite = QLabel()
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load animations or fallback image
        if os.path.exists(AMMAVAN_IDLE) and os.path.exists(AMMAVAN_TALK):
            self.idle_movie = QMovie(AMMAVAN_IDLE)
            self.idle_movie.setScaledSize(QSize(150, 150))

            self.talk_movie = QMovie(AMMAVAN_TALK)
            self.talk_movie.setScaledSize(QSize(150, 150))

            self.sprite.setMovie(self.idle_movie)
            self.idle_movie.start()
            self.has_gifs = True
        else:
            # Fallback to static PNG if GIFs are missing
            pixmap = QPixmap(PHOTO_FALLBACK).scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.sprite.setPixmap(pixmap)
            self.has_gifs = False

        layout.addWidget(self.speech_bubble)
        layout.addWidget(self.sprite)
        self.setLayout(layout)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 250, screen.height() - 350, 200, 300)

        # Watch Timer
        self.watch_timer = QTimer(self)
        self.watch_timer.timeout.connect(self.judge_screen)
        self.watch_timer.start(4000)

        # Bubble Hide Timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.on_speech_finished)

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

        self.brain = AIBrainThread(found_target)
        self.brain.response_ready.connect(self.speak)
        self.brain.start()

    def speak(self, text):
        self.speech_bubble.setText(text)
        self.speech_bubble.show()

        if self.has_gifs:
            self.idle_movie.stop()
            self.sprite.setMovie(self.talk_movie)
            self.talk_movie.start()

        self.hide_timer.start(8000)

    def on_speech_finished(self):
        self.speech_bubble.hide()

        if self.has_gifs:
            self.talk_movie.stop()
            self.sprite.setMovie(self.idle_movie)
            self.idle_movie.start()

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