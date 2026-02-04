from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QPushButton,
)
from PyQt5.QtGui import QFont
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
        self.setWindowTitle("RAJ - AI Assistant")
        self.setGeometry(300, 100, 980, 560)
        self.setStyleSheet(
            """
            QWidget {
                background: #0b0f1a;
                color: #e6f1ff;
                font-family: "Segoe UI";
            }
            QFrame#card {
                background: #121a2b;
                border: 1px solid #1f2a44;
                border-radius: 16px;
            }
            QLabel#title {
                font-size: 26px;
                font-weight: 600;
            }
            QLabel#subtitle {
                color: #9fb3d9;
                font-size: 13px;
            }
            QLabel#statusBadge {
                background: #1b2a4a;
                border-radius: 12px;
                padding: 6px 12px;
                color: #d6e4ff;
            }
            QLabel#pulse {
                background: #1f6feb;
                border-radius: 8px;
                min-width: 16px;
                max-width: 16px;
                min-height: 16px;
                max-height: 16px;
            }
            QLabel#waveform {
                font-size: 18px;
                color: #7aa2ff;
                letter-spacing: 3px;
            }
            QPushButton#actionButton {
                background: #1f6feb;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton#ghostButton {
                background: transparent;
                border: 1px solid #2b3b5e;
                border-radius: 10px;
                padding: 10px 16px;
                color: #c9d5ee;
            }
            """
        )

        header = QLabel("RAJ Assistant")
        header.setObjectName("title")

        subtitle = QLabel("Always-on desktop companion for Windows")
        subtitle.setObjectName("subtitle")

        title_layout = QVBoxLayout()
        title_layout.addWidget(header)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(4)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.status_badge = QLabel("Waiting for wake word: 'Hey SAM'")
        self.status_badge.setObjectName("statusBadge")

        self.pulse = QLabel()
        self.pulse.setObjectName("pulse")

        pulse_layout = QHBoxLayout()
        pulse_layout.addWidget(self.pulse)
        pulse_layout.addWidget(self.status_badge)
        pulse_layout.addStretch()
        pulse_layout.setSpacing(10)

        self.waveform = QLabel("▁ ▂ ▃ ▄ ▅ ▆ ▇ ▆ ▅ ▄ ▃ ▂ ▁")
        self.waveform.setObjectName("waveform")
        self.waveform.setAlignment(Qt.AlignCenter)

        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        status_layout.addLayout(title_layout)
        status_layout.addSpacing(12)
        status_layout.addLayout(pulse_layout)
        status_layout.addSpacing(24)
        status_layout.addWidget(self.waveform)
        status_layout.addStretch()

        activity_card = QFrame()
        activity_card.setObjectName("card")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.addWidget(self._section_title("Recent activity"))
        activity_layout.addWidget(self._activity_row("• Waiting for your command"))
        activity_layout.addWidget(self._activity_row("• Wake word: Hey Raj"))
        activity_layout.addWidget(self._activity_row("• Mode: Background listening"))
        activity_layout.addSpacing(18)
        activity_layout.addWidget(self._section_title("Quick controls"))

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self._action_button("Mute Mic"))
        controls_layout.addWidget(self._ghost_button("Settings"))
        quit_button = self._ghost_button("Quit")
        quit_button.clicked.connect(self.close)
        controls_layout.addWidget(quit_button)
        activity_layout.addLayout(controls_layout)
        activity_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(status_card, 3)
        main_layout.addWidget(activity_card, 2)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 24, 24, 24)

        self.setLayout(main_layout)

        self.update_state("🧠 Waiting for wake word: 'Hey Raj'", "#1f6feb")

        threading.Thread(target=self.wake_loop, daemon=True).start()

    def wake_loop(self):
        detect_wake_word(self.respond)

    def respond(self):
        self.update_state("🎙 Listening...", "#19c37d")

        # Start a new thread for listening and processing
        threading.Thread(target=self.handle_user_command, daemon=True).start()

    def handle_user_command(self):
        while True:
            self.update_state("🎙 Listening...", "#19c37d")

            reset_chat_history()  # Reset chat history for new session
            query = listen()  # This blocks until user finishes speaking

            if query:
                self.update_state("🤖 Processing...", "#f59e0b")
                print(f"User said: {query}")
                speak("You said " + query)

                if "exit" in query.lower():
                    speak("Okay, going to sleep.")
                    break  # Exit loop, back to wake word mode

                execute_command(query, speak)
            else:
                self.update_state("⚠️ I didn’t catch that.", "#ef4444")
                speak("Sorry, I didn’t catch that.")

        # Only after exit
        self.update_state("🧠 Waiting for wake word: 'Hey raj'", "#1f6feb")

    def update_state(self, text, color):
        self.status_badge.setText(text)
        self.pulse.setStyleSheet(f"background: {color}; border-radius: 8px;")
        if "Listening" in text:
            self.waveform.setText("▁ ▃ ▅ ▇ █ ▇ ▅ ▃ ▁")
        elif "Processing" in text:
            self.waveform.setText("▂ ▃ ▄ ▅ ▆ ▇ ▆ ▅ ▄ ▃ ▂")
        else:
            self.waveform.setText("▁ ▂ ▃ ▄ ▅ ▆ ▇ ▆ ▅ ▄ ▃ ▂ ▁")

    def _section_title(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        return label

    def _activity_row(self, text):
        label = QLabel(text)
        label.setObjectName("subtitle")
        return label

    def _action_button(self, text):
        button = QPushButton(text)
        button.setObjectName("actionButton")
        return button

    def _ghost_button(self, text):
        button = QPushButton(text)
        button.setObjectName("ghostButton")
        return button
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SAM_GUI()
    gui.show()
    sys.exit(app.exec_())
