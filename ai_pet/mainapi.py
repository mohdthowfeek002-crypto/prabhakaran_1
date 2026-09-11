import sys
import ctypes
# We use the new import format here
from google import genai
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# 1. SETUP THE NEW AI CLIENT
client = genai.Client(api_key="")

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
    
    def __init__(self, window_title):
        super().__init__()
        self.window_title = window_title
        
    def run(self):
        try:
            prompt = f"""
            You are a stereotypical, highly judgmental Kerala Ammavan. 
            I just opened a computer application with the title '{self.window_title}'. 
            Give a short, funny, sarcastic, passive-aggressive comment judging me for using it. 
            Respond ONLY in Manglish (Malayalam written in English letters). 
            Do not use English translations. Keep it short, maximum 2 sentences.
            """
            
            # Fix 1 & 2: We use the newer model name and the Chat method to avoid warnings
            chat = client.chats.create(model="gemini-3.6-flash")
            response = chat.send_message(prompt)
            
            self.response_ready.emit(response.text.strip().replace('"', ''))
            
        except Exception as e:
            print(f"API ERROR: {e}") 
            self.response_ready.emit("Ee internetinte oru karyam... onnum thurakkunnilla.")

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
        image_path = r"C:\Users\Haris\tinkerhub\prabhakaran_avtr-removebg-preview.png"
        
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
        
        safe_targets = ["youtube", "netflix", "code", "steam", "amazon", "instagram"]
        
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
        self.hide_timer.start(8000) 
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.speak("Enne thodathe, enikku vere paniyund!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = AmmavanPet()
    pet.show()
    sys.exit(app.exec())