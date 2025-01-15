import sys
import pyperclip
import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

is_listening_for_key_chord = True

class ClipboardManager(QtWidgets.QWidget):
    # Define a signal to safely update the UI from a different thread
    trigger_show_ui = QtCore.pyqtSignal(str)
    trigger_select_slot = QtCore.pyqtSignal(int)
    trigger_hide_ui = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.slots = ["" for _ in range(10)]  # Initialize 10 clipboard slots
        self.current_clipboard_content = ""  # Store the current clipboard content
        self.init_ui()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(1600, 400, 800, 300)

        # Connect the custom signal to the show_ui method
        self.trigger_show_ui.connect(self.show_ui)
        self.trigger_select_slot.connect(self.slot_selected)
        self.trigger_hide_ui.connect(self.hide_ui)
        logging.debug("ClipboardManager initialized.")

    def init_ui(self):
        self.layout = QtWidgets.QGridLayout()
        self.text_areas = []
        for i in range(10):
            text_area = QtWidgets.QTextEdit()
            text_area.setReadOnly(True)
            text_area.setStyleSheet("font-size: 14px; padding: 5px;")
            text_area.setText(f"Slot {i+1}: {self.slots[i]}")

            # Bind the current value of index to the lambda using a default argument
            text_area.mousePressEvent = self.create_mouse_press_event(i)

            self.layout.addWidget(text_area, i // 5, i % 5)
            self.text_areas.append(text_area)
        self.setLayout(self.layout)
        logging.debug("UI initialized.")

    def create_mouse_press_event(self, index):
        def mouse_press_event(event):
            logging.debug(f"Slot {index+1} clicked.")
            self.slot_selected(index)
        return mouse_press_event

    def update_ui(self):
        for i, text_area in enumerate(self.text_areas):
            content_preview = (self.slots[i][:50] + '...') if len(self.slots[i]) > 50 else self.slots[i]
            text_area.setText(f"Slot {i+1}:{content_preview}")
        logging.debug("UI updated with current slots.")
        QtGui.QGuiApplication.processEvents()  # update gui so that pyqt app loop completes and displays frame to user


    def slot_selected(self, index):
        logging.debug(f"slot_selected called with mode: {self.mode}")
        self.disable_number_key_listeners()
        if self.mode == "copy":
            logging.debug(f"Copying to slot {index+1}: {self.current_clipboard_content}")
            self.slots[index] = self.current_clipboard_content
            self.update_ui()
            time.sleep(0.5)  # wait a bit for user to see the new values before hiding.
        elif self.mode == "paste":
            logging.debug(f"Pasting from slot {index+1}: {self.slots[index]}")
            pyperclip.copy(self.slots[index])
            logging.debug("Simulating Ctrl+V to paste selected text.")
            keyboard.press_and_release("ctrl+v")
        self.hide()

    def disable_number_key_listeners(self):
        global is_listening_for_key_chord
        logging.debug("disable_number_key_listeners for 0 through 9, and ESC")
        keyboard.remove_hotkey("1")
        keyboard.remove_hotkey("2")
        keyboard.remove_hotkey("3")
        keyboard.remove_hotkey("4")
        keyboard.remove_hotkey("5")
        keyboard.remove_hotkey("6")
        keyboard.remove_hotkey("7")
        keyboard.remove_hotkey("8")
        keyboard.remove_hotkey("9")
        keyboard.remove_hotkey("0")
        keyboard.remove_hotkey("esc")
        is_listening_for_key_chord = True

    def show_ui(self, mode):
        logging.debug(f"show_ui called with mode: {mode}")
        self.mode = mode
        if mode == "copy":
            logging.debug(f"current_clipboard_content: {self.current_clipboard_content}")
            logging.debug("Simulating Ctrl+C to copy selected text.")
            keyboard.press_and_release("ctrl+c")
            time.sleep(0.01)  # Allow time for clipboard to update
            self.current_clipboard_content = pyperclip.paste()
            logging.debug(f"Clipboard updated: {self.current_clipboard_content}")
            self.update_ui()
        self.show()

    def hide_ui(self):
        logging.debug("hide_ui called. ")
        self.disable_number_key_listeners()
        self.hide()

# Set up the application
app = QtWidgets.QApplication(sys.argv)
manager = ClipboardManager()

# Function to handle hotkeys in a separate thread
def hotkey_listener():
    def copy_hotkey():
        global is_listening_for_key_chord
        if not is_listening_for_key_chord:
            return

        is_listening_for_key_chord = False
        logging.debug("Ctrl+Shift+C pressed.")
        # Ensure no keys are pressed before sending Ctrl+C
        logging.debug("Ensuring no keys are pressed before copying.")
        while keyboard.is_pressed("ctrl") or keyboard.is_pressed("shift") or keyboard.is_pressed("c"):
            time.sleep(0.01)  # Wait until all keys are released

        enable_number_key_listeners()

        manager.trigger_show_ui.emit("copy")  # Emit signal to show_ui() in copy mode

    def enable_number_key_listeners():
        logging.debug("enable_number_key_listeners for 0 through 9, and ESC")
        keyboard.add_hotkey("1", type_number_hotkey, args=tuple("0"), suppress=True)
        keyboard.add_hotkey("2", type_number_hotkey, args=tuple("1"), suppress=True)
        keyboard.add_hotkey("3", type_number_hotkey, args=tuple("2"), suppress=True)
        keyboard.add_hotkey("4", type_number_hotkey, args=tuple("3"), suppress=True)
        keyboard.add_hotkey("5", type_number_hotkey, args=tuple("4"), suppress=True)
        keyboard.add_hotkey("6", type_number_hotkey, args=tuple("5"), suppress=True)
        keyboard.add_hotkey("7", type_number_hotkey, args=tuple("6"), suppress=True)
        keyboard.add_hotkey("8", type_number_hotkey, args=tuple("7"), suppress=True)
        keyboard.add_hotkey("9", type_number_hotkey, args=tuple("8"), suppress=True)
        keyboard.add_hotkey("0", type_number_hotkey, args=tuple("9"), suppress=True)
        keyboard.add_hotkey("esc", esc_hotkey, suppress=True)

    def paste_hotkey():
        global is_listening_for_key_chord
        if not is_listening_for_key_chord:
            return

        is_listening_for_key_chord = False
        logging.debug("Ctrl+Shift+V pressed.")
        enable_number_key_listeners()
        manager.trigger_show_ui.emit("paste")  # Emit signal to show_ui() in paste mode

    def type_number_hotkey(key_value):
        global is_listening_for_key_chord
        if is_listening_for_key_chord:
            return

        logging.debug(f"Number {key_value} was pressed.")
        manager.trigger_select_slot.emit(int(key_value)) # fires slot_selected()

    def esc_hotkey():
        manager.trigger_hide_ui.emit() # call hide_ui

    keyboard.add_hotkey("ctrl+shift+c", copy_hotkey)
    keyboard.add_hotkey("ctrl+shift+v", paste_hotkey)

    logging.debug("Hotkeys registered. Waiting for input...")
    keyboard.wait()

# Run the hotkey listener in a separate thread
hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
hotkey_thread.start()

# Run the application
try:
    logging.debug("Application started.")
    sys.exit(app.exec_())
except KeyboardInterrupt:
    logging.debug("Application interrupted. Cleaning up...")
    keyboard.unhook_all_hotkeys()
