import sys
import pyperclip
import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
import threading

class ClipboardManager(QtWidgets.QWidget):
    # Define a signal to safely update the UI from a different thread
    trigger_ui = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.slots = ["" for _ in range(10)]  # Initialize 10 clipboard slots
        self.current_clipboard_content = ""  # Store the current clipboard content
        self.init_ui()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(400, 200, 800, 300)

        # Connect the custom signal to the show_ui method
        self.trigger_ui.connect(self.show_ui)

    def init_ui(self):
        self.layout = QtWidgets.QGridLayout()
        self.text_areas = []
        for i in range(10):
            text_area = QtWidgets.QTextEdit()
            text_area.setReadOnly(True)
            text_area.setStyleSheet("font-size: 14px; padding: 5px;")
            text_area.setText(f"Slot {i+1}: {self.slots[i]}")

            # Fix: Bind the current value of index to the lambda using a default argument
            text_area.mousePressEvent = self.create_mouse_press_event(i)

            self.layout.addWidget(text_area, i // 5, i % 5)
            self.text_areas.append(text_area)
        self.setLayout(self.layout)

    def create_mouse_press_event(self, index):
        def mouse_press_event(event):
            self.slot_selected(index)
        return mouse_press_event

    def update_ui(self):
        for i, text_area in enumerate(self.text_areas):
            content_preview = (self.slots[i][:50] + '...') if len(self.slots[i]) > 50 else self.slots[i]
            text_area.setText(f"Slot {i+1}:{content_preview}")

    def slot_selected(self, index):
        if self.mode == "copy":
            self.slots[index] = self.current_clipboard_content
            self.update_ui()
        elif self.mode == "paste":
            pyperclip.copy(self.slots[index])
        self.hide()

    def show_ui(self, mode):
        self.mode = mode
        if mode == "copy":
            self.current_clipboard_content = pyperclip.paste()
        self.update_ui()
        self.show()

# Set up the application
app = QtWidgets.QApplication(sys.argv)
manager = ClipboardManager()

# Function to handle hotkeys in a separate thread
def hotkey_listener():
    def copy_hotkey():
        manager.trigger_ui.emit("copy")  # Emit signal to show UI in copy mode

    def paste_hotkey():
        manager.trigger_ui.emit("paste")  # Emit signal to show UI in paste mode

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
