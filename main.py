import sys
import pyperclip
import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
import threading

class ClipboardManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.slots = ["" for _ in range(10)]  # Initialize 10 clipboard slots
        self.init_ui()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(400, 200, 600, 400)

    def init_ui(self):
        self.layout = QtWidgets.QGridLayout()
        self.buttons = []
        for i in range(10):
            button = QtWidgets.QPushButton(f"Slot {i+1}: {self.slots[i]}")
            button.clicked.connect(lambda _, index=i: self.slot_selected(index))
            self.layout.addWidget(button, i // 5, i % 5)
            self.buttons.append(button)
        self.setLayout(self.layout)

    def update_ui(self):
        for i, button in enumerate(self.buttons):
            content_preview = (self.slots[i][:20] + '...') if len(self.slots[i]) > 20 else self.slots[i]
            button.setText(f"Slot {i+1}: {content_preview}")

    def slot_selected(self, index):
        if self.mode == "copy":
            self.slots[index] = pyperclip.paste()
            self.update_ui()
        elif self.mode == "paste":
            pyperclip.copy(self.slots[index])
        self.hide()

    def show_ui(self, mode):
        self.mode = mode
        self.update_ui()
        self.show()

# Set up the application
app = QtWidgets.QApplication(sys.argv)
manager = ClipboardManager()

# Function to handle hotkeys in a separate thread
def hotkey_listener():
    def copy_hotkey():
        QtCore.QMetaObject.invokeMethod(manager, "show_ui", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "copy"))

    def paste_hotkey():
        QtCore.QMetaObject.invokeMethod(manager, "show_ui", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "paste"))

    keyboard.add_hotkey("ctrl+shift+c", copy_hotkey)
    keyboard.add_hotkey("ctrl+shift+v", paste_hotkey)
    keyboard.wait()

# Run the hotkey listener in a separate thread
hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
hotkey_thread.start()

# Run the application
try:
    sys.exit(app.exec_())
except KeyboardInterrupt:
    keyboard.unhook_all_hotkeys()
