import sys
import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

is_listening_for_key_chord = True

class ClipboardSlotWidget(QtWidgets.QWidget):
    def __init__(self, slot_index, parent=None):
        super().__init__(parent)
        self.slot_index = slot_index
        self.init_ui()

    def init_ui(self):
        # Use absolute positioning to overlay the slot_label
        # Label for content
        self.content_label = QtWidgets.QLabel(self)
        self.content_label.setGeometry(0, 0, self.width(), self.height())
        self.content_label.setStyleSheet("font-size: 12px; border: 1px solid gray; padding: 2px;")

        # Label for slot index
        self.slot_label = QtWidgets.QLabel(self)
        self.slot_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.slot_label.setStyleSheet("font-size: 14px; color: silver; margin: 0; background: transparent;")
        self.slot_label.setText(f"{self.slot_index + 1}")

        # Update label positions when the widget is resized
        self.resizeEvent = self.update_label_positions

    def update_label_positions(self, event):
        self.content_label.setGeometry(0, 0, self.width(), self.height())
        self.slot_label.move(self.width() - 20, self.height() - 20)

    def set_content(self, content):
        if isinstance(content, QtGui.QImage):
            pixmap = QtGui.QPixmap.fromImage(content)
            label_width = self.content_label.width()

            # Only scale down if the image width exceeds the label width
            if pixmap.width() > label_width:
                scaled_pixmap = pixmap.scaledToWidth(label_width, QtCore.Qt.SmoothTransformation)
            else:
                scaled_pixmap = pixmap  # Use the original size if smaller

            self.content_label.setPixmap(scaled_pixmap)
            self.content_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        elif isinstance(content, str):
            # Display text content
            self.content_label.setText(content)
            self.content_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.content_label.setStyleSheet("font-size: 12px; border: 1px solid gray; padding: 2px;")
        else:
            # Fallback for unsupported content types
            self.content_label.setText("Unsupported Content")
            self.content_label.setStyleSheet("color: red; font-size: 14px;")
            self.content_label.setAlignment(QtCore.Qt.AlignCenter)

class ClipboardManager(QtWidgets.QWidget):
    # Define a signal to safely update the UI from a different thread
    trigger_show_ui = QtCore.pyqtSignal(str)
    trigger_select_slot = QtCore.pyqtSignal(int)
    trigger_hide_ui = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.slots = [None for _ in range(10)]  # Initialize 10 clipboard slots
        self.current_clipboard_content = None  # Store the current clipboard content
        self.init_ui()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        dialog_width = self.screen().size().width() - 100
        dialog_height = 150
        dialog_x = (self.screen().size().width() // 2) - (dialog_width // 2)
        dialog_y = 0
        self.setGeometry(dialog_x, dialog_y, dialog_width, dialog_height)

        # Connect the custom signal to the show_ui method
        self.trigger_show_ui.connect(self.show_ui)
        self.trigger_select_slot.connect(self.slot_selected)
        self.trigger_hide_ui.connect(self.hide_ui)
        logging.debug("ClipboardManager initialized.")

    def init_ui(self):
        self.layout = QtWidgets.QGridLayout()
        self.slot_widgets = []
        for i in range(10):
            slot_widget = ClipboardSlotWidget(i)
            slot_widget.mousePressEvent = self.create_mouse_press_event(i)
            self.layout.addWidget(slot_widget, 1, i)
            self.slot_widgets.append(slot_widget)

        self.setLayout(self.layout)
        logging.debug("UI initialized.")

    def create_mouse_press_event(self, index):
        def mouse_press_event(event):
            logging.debug(f"Slot {index + 1} clicked.")
            self.slot_selected(index)
        return mouse_press_event

    def slot_selected(self, index):
        logging.debug(f"slot_selected called with mode: {self.mode}")
        self.disable_number_key_listeners()
        clipboard = QtWidgets.QApplication.clipboard()

        if self.mode == "copy":
            logging.debug(f"Copying to slot {index + 1}.")
            self.slots[index] = self.current_clipboard_content
            content = self.slots[index]
            slot_widget = self.slot_widgets[index]
            if isinstance(content, QtGui.QImage):
                slot_widget.set_content(content)
            elif isinstance(content, str):
                content_preview = (content[:500] + '...') if len(content) > 500 else content
                slot_widget.set_content(content_preview)
            else:
                slot_widget.set_content("")
            QtGui.QGuiApplication.processEvents()  # Update GUI to display changes
            time.sleep(0.5)  # Wait for user to see the new values before hiding
        elif self.mode == "paste":
            logging.debug(f"Pasting from slot {index + 1}.")
            content = self.slots[index]
            if isinstance(content, str):
                clipboard.setText(content)
            elif isinstance(content, QtGui.QImage):
                clipboard.setImage(content)
            else :
                clipboard.clear()
            QtWidgets.QApplication.processEvents()
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
        clipboard = QtWidgets.QApplication.clipboard()

        self.move_to_active_screen()

        if mode == "copy":
            logging.debug("Simulating Ctrl+C to copy selected text.")
            keyboard.press_and_release("ctrl+c")
            time.sleep(0.01)  # Allow time for clipboard to update
            QtWidgets.QApplication.processEvents()
            mime_data = clipboard.mimeData()

            if mime_data.hasText():
                self.current_clipboard_content = mime_data.text()
                logging.debug(f"Copied text: {self.current_clipboard_content}")
            elif mime_data.hasImage():
                self.current_clipboard_content = clipboard.image()
                logging.debug("Copied an image.")
            else:
                self.current_clipboard_content = None
                logging.debug("Unsupported clipboard content.")

        self.show()

    def move_to_active_screen(self):
        # Get the screen where the cursor is currently located
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
        if not screen:
            logging.warning("Could not determine the active screen. Falling back to primary screen.")
            screen = QtWidgets.QApplication.primaryScreen()

        # Explicitly set the window to appear on this screen
        logging.debug(f"self.windowHandle: {self.windowHandle()}")
        if not self.windowHandle():
            logging.debug("self.windowHandle is None. Attempting to ensure native window handle.")
            self.setAttribute(QtCore.Qt.WA_NativeWindow, True)
            QtWidgets.QApplication.processEvents()  # Process pending events including building the window.
            if not self.windowHandle():
                logging.error("Failed to get window handle after processEvents()")
                return

        logging.debug(f"setting screen to screen: {screen.name()}")
        self.windowHandle().setScreen(screen)
        logging.debug("about to get screen geometry.")
        screen_geometry = screen.geometry()
        logging.debug(f"Screen geometry: {screen_geometry}")

        dialog_width = screen_geometry.width() - 100
        dialog_height = 150
        dialog_x = screen_geometry.x() + (screen_geometry.width() // 2) - (dialog_width // 2)
        dialog_y = screen_geometry.y()  # Position at the top of the screen

        logging.debug(f"Setting window geometry: x={dialog_x}, y={dialog_y}, width={dialog_width}, height={dialog_height} on screen {screen.name()}")
        self.setGeometry(dialog_x, dialog_y, dialog_width, dialog_height)

    def hide_ui(self):
        logging.debug("hide_ui called.")
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
        keyboard.add_hotkey("1", type_number_hotkey, args=(0,), suppress=True)
        keyboard.add_hotkey("2", type_number_hotkey, args=(1,), suppress=True)
        keyboard.add_hotkey("3", type_number_hotkey, args=(2,), suppress=True)
        keyboard.add_hotkey("4", type_number_hotkey, args=(3,), suppress=True)
        keyboard.add_hotkey("5", type_number_hotkey, args=(4,), suppress=True)
        keyboard.add_hotkey("6", type_number_hotkey, args=(5,), suppress=True)
        keyboard.add_hotkey("7", type_number_hotkey, args=(6,), suppress=True)
        keyboard.add_hotkey("8", type_number_hotkey, args=(7,), suppress=True)
        keyboard.add_hotkey("9", type_number_hotkey, args=(8,), suppress=True)
        keyboard.add_hotkey("0", type_number_hotkey, args=(9,), suppress=True)
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

        logging.debug(f"Number {key_value + 1} was pressed.")
        manager.trigger_select_slot.emit(key_value)  # Fires slot_selected()

    def esc_hotkey():
        manager.trigger_hide_ui.emit()  # Call hide_ui

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
