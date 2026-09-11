import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

# Dictionary mapping keywords to Ammavan's quotes
AMMAVAN_LOGIC = {
    "youtube": "Padikkan ulla time il cinema kaanunno? Oru collector aavan ullathalle?",
    "netflix": "Padikkan ulla time il cinema kaanunno? Oru collector aavan ullathalle?",
    "code": "Rathri urangande? Kannu kedu varum. Ithaanu ee computer-inte oru kozhappam.",
    "terminal": "Rathri urangande? Kannu kedu varum. Ithaanu ee computer-inte oru kozhappam.",
    "steam": "Valya pillarayille, iniyum ithum kalich nadakkuvaano? Vallathum vallavarkum upakarapedunna karyam cheythoode?",
    "amazon": "Cash onnum illelum chilavakkalinu oru kuravum illa. Nammude kaalathokke...",
    "flipkart": "Cash onnum illelum chilavakkalinu oru kuravum illa. Nammude kaalathokke..."
}

def get_active_window_title():
    try:
        # Talks directly to the Windows API to get the frontmost window
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.lower()
    except Exception:
        return ""

class AmmavanPet(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 1. Setup Frameless, Always-on-Top, and Transparent Window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        
        # 2. Setup Speech Bubble
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
        
        # 3. Setup Ammavan Sprite
        self.sprite = QLabel("👨🏽‍🦳")
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite.setStyleSheet("font-size: 70px;")
        
        # Tip: Replace the emoji with an actual image like this:
        # from PyQt6.QtGui import QPixmap
        # self.sprite.setPixmap(QPixmap('path/to/ammavan.png'))
        
        layout.addWidget(self.speech_bubble)
        layout.addWidget(self.sprite)
        self.setLayout(layout)
        
        # Move window to bottom right corner of the primary screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 250, screen.height() - 350, 200, 300)
        
        # 4. Timers for Logic
        self.watch_timer = QTimer(self)
        self.watch_timer.timeout.connect(self.judge_screen)
        self.watch_timer.start(3000)  # Check the active window every 3 seconds
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.speech_bubble.hide)
        
    def judge_screen(self):
        if not self.speech_bubble.isHidden():
            return  # Let him finish talking first
            
        active_window = get_active_window_title()
        if not active_window:
            return
            
        for keyword, quote in AMMAVAN_LOGIC.items():
            if keyword in active_window:
                self.speak(quote)
                break
                
    def speak(self, text):
        self.speech_bubble.setText(text)
        self.speech_bubble.show()
        self.hide_timer.start(7000)  # Make the speech bubble disappear after 7 seconds
        
    def mousePressEvent(self, event):
        # Bonus: Poke the Ammavan
        if event.button() == Qt.MouseButton.LeftButton:
            self.speak("Enne thodathe, enikku vere paniyund!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = AmmavanPet()
    pet.show()
    sys.exit(app.exec())