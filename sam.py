from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QMovie, QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
import threading
from listener import listen
from commands import execute_command
from speak import speak
from wake_listener import detect_wake_word
from chat_ai import reset_chat_history

class SAM_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAM - AI Assistant")
        self.setGeometry(300, 100, 900, 500)
        self.setStyleSheet("background-color: black; color: cyan;")

        self.label = QLabel("🧠 Waiting for wake word: 'Hey SAM'")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Consolas", 14))

        self.anim_label = QLabel()
        self.anim = QMovie("assets/waveform.gif")
        self.anim_label.setMovie(self.anim)
        self.anim.stop()

        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("assets/background.png"))
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.anim_label)
        self.setLayout(layout)

        threading.Thread(target=self.wake_loop, daemon=True).start()

    def wake_loop(self):
        detect_wake_word(self.respond)

    def respond(self):
        self.label.setText("🎙 Listening...")
        self.anim.start()

        # Start a new thread for listening and processing
        threading.Thread(target=self.handle_user_command, daemon=True).start()

    def handle_user_command(self):
        while True:
            self.label.setText("🎙 Listening...")
            self.anim.start()

            reset_chat_history()  # Reset chat history for new session
            query = listen()  # This blocks until user finishes speaking
            self.anim.stop()

            if query:
                self.label.setText("🤖 Processing...")
                print(f"User said: {query}")
                speak("You said " + query)

                if "exit" in query.lower():
                    speak("Okay, going to sleep.")
                    break  # Exit loop, back to wake word mode

                execute_command(query, speak)
            else:
                self.label.setText("⚠️ I didn’t catch that.")
                speak("Sorry, I didn’t catch that.")

        # Only after exit
        self.label.setText("🧠 Waiting for wake word: 'Hey SAM'")
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SAM_GUI()
    gui.show()
    sys.exit(app.exec_())
