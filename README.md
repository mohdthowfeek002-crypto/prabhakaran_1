<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />



# Portable Ammavan (AaaS: Ammavan-as-a-Service) 🎯

## Basic Details

### Team Name: The Procrastination Police

### Team Members

* Team Lead: thowfeek - [gec thrissur]
* Member 2: jeevan - [gec thrissur]

### Project Description

Portable Ammavan is a transparent, draggable desktop virtual pet designed for hostelers and students living away from home who suffer from a severe deficiency of unsolicited family judgment. Utilizing low-level Windows APIs and Gemini AI, this desktop pet monitors your active foreground windows in real time and relentlessly roasts your life choices in authentic Manglish.

### The Problem (that doesn't exist)

College students staying in hostels, PGs, and shared flats suffer from an unnatural state of inner peace. Without a nosy Kerala Ammavan lurking over their shoulders to ask *"Padutham okke engane ponu?"* or judge them for watching Netflix at 2:00 AM, students risk developing dangerous levels of unbothered happiness and guilt-free leisure.

### The Solution (that nobody asked for)

We engineered a desktop companion that acts as a portable, surveillance-grade relative right on your screen. He paces around your taskbar, falls asleep if your cursor goes idle, gets furious if you try to drag him across the screen, and sends active application titles to an LLM to generate passive-aggressive, culturally pinpoint Manglish commentary with dynamic comic-style typewriter bubbles.

---

## Technical Details

### Technologies/Components Used

For Software:

* **Languages used:** Python 3.12+
* **Frameworks used:** PyQt6 (Frameless, translucent desktop overlay UI)
* **Libraries used:**
* `google-genai` (Google Gemini 2.5 Flash SDK)
* `python-dotenv` (Environment variable management)
* `ctypes` (Win32 API bindings: `user32.dll` for window inspection & cursor polling)


* **Tools used:** VS Code, Git, Photopea / EZGIF (Sprite transparency & frame disposal processing)

For Hardware:

* *N/A (Pure Software Desktop Application)*

---

### Implementation

For Software:

# Installation

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/portable-ammavan.git
cd portable-ammavan

# 2. Set up virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# 3. Install required dependencies
pip install PyQt6 google-genai python-dotenv

```

# Setup Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY="your_gemini_api_key_here"
standing="assets/standing.png"
walking_left="assets/walking_left.gif"
walking_right="assets/walking_right.gif"
peeing="assets/peeing.gif"
sleeping="assets/sleeping.gif"
reading="assets/reading.gif"
angry="assets/angry.png"

```

# Run

```bash
python mainapi.py

```

---

### Project Documentation

For Software:

# Screenshots
[srceen shorts]

*Ammavan detecting an active YouTube window and generating a sarcastic Manglish scolding bubble.*


*Switching dynamically to the angry sprite state with an immediate 'videda enne' protest upon left-click drag.*


*Ammavan dozing off after detecting 30 seconds of system cursor inactivity.*

# Diagrams


*App architecture: Win32 API window title hook -> Target sanitizer/whitelist -> Async QThread -> Gemini 2.5 Flash -> Typewriter PyQt6 speech overlay with offline fallback handling.*

For Hardware:

* *Not Applicable (Software Solution)*

---

### Project Demo

# Video

[(https://drive.google.com/drive/folders/1MJ-gXHGoznx9xhDCe0UTYVJN8pCVvnED)]
*Demonstrates foreground application detection, typewriter dialogue rendering, state-based animations, cursor idle detection, and manual drag handling.*

# Additional Demos

* Built-in offline resilience: Disconnecting the internet immediately switches Ammavan to a hardcoded dictionary of classic Malayali Ammavan roasts, ensuring continuous moral judgment during network blackouts.

---

## Team Contributions

* **thowfeek:** Core desktop pet architecture, PyQt6 transparent GUI, Win32 window polling integration, and Gemini AI prompt engineering.State engine implementation (sleeping/pacing/dragging logic).
* **jeevan:** Sprite asset creation, frame extraction, transparency conversion, and offline fallback quote collection.
 typewriter bubble geometry adjustments, and testing.

Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)



