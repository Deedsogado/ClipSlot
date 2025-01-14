import sys
import pyperclip
import keyboard
from PyQt5 import QtWidgets, QtCore

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
            self.layoutDirection()
        self.setLayout(self.layout)

    def update_ui(self):
        for i, button in enumerate(self.buttons):
            button.setText(f"Slot {i+1}: {self.slots[i]}")

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
        QtCore.QTimer.singleShot(500, self.hide)

# Set up the application
app = QtWidgets.QApplication(sys.argv)
manager = ClipboardManager()

# Hotkey listeners
def copy_hotkey():
    manager.show_ui("copy")

def paste_hotkey():
    manager.show_ui("paste")

keyboard.add_hotkey("ctrl+shift+c", copy_hotkey)
keyboard.add_hotkey("ctrl+shift+v", paste_hotkey)

# Run the application
try:
    sys.exit(app.exec_())
except KeyboardInterrupt:
    keyboard.unhook_all_hotkeys()
