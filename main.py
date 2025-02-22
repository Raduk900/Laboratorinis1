import sys
import audioProcessing
import wavDispaly
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from constants import (
    STATUS_BAR_MESSAGES, ICONS, AUDIO_EDITOR, LOAD_AUDIO_FILE, SAVE_HIGHLIGHTED_REGION, NO_FILE_LOADED,
    OPEN_AUDIO_FILE, WAVE_FILES, PLAY, CLEAR_CURRENT_SELECTION, PLAY_SELECTED
)

class AudioEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio = None
        self.waveform_display = None
        self.setWindowTitle(AUDIO_EDITOR)
        self.setGeometry(100, 100, 1000, 700)

        self.setFont(QFont("Segoe UI", 10))

        with open("styles.css", "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel(AUDIO_EDITOR)
        self.title_label.setObjectName("title_label")
        self.title_layout.addWidget(self.title_label)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.setMenuWidget(self.title_bar)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage(STATUS_BAR_MESSAGES["READY"])

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.load_button = QPushButton(LOAD_AUDIO_FILE, self)
        self.load_button.setIcon(QIcon(ICONS["LOAD"]))
        self.load_button.clicked.connect(self.load_audio_file)
        self.layout.addWidget(self.load_button, 0, 0)

        self.save_button = QPushButton(SAVE_HIGHLIGHTED_REGION, self)
        self.save_button.setIcon(QIcon(ICONS["SAVE"]))
        self.save_button.clicked.connect(self.save_highlighted_region)
        self.save_button.setVisible(False)
        self.layout.addWidget(self.save_button, 0, 1)

        self.play_button = QPushButton(PLAY, self)
        self.play_button.setIcon(QIcon(ICONS["PLAY"]))
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setVisible(False)
        self.layout.addWidget(self.play_button, 0, 2)

        self.play_selected_button = QPushButton(PLAY_SELECTED, self)
        self.play_selected_button.setIcon(QIcon(ICONS["PLAY_SELECTED"]))
        self.play_selected_button.clicked.connect(self.play_selected_audio)
        self.play_selected_button.setVisible(False)
        self.layout.addWidget(self.play_selected_button, 0, 3)

        self.clear_current_selection_button = QPushButton(CLEAR_CURRENT_SELECTION, self)
        self.clear_current_selection_button.setIcon(QIcon(ICONS["CLEAR"]))
        self.clear_current_selection_button.clicked.connect(self.clear_current_selection)
        self.clear_current_selection_button.setVisible(False)
        self.layout.addWidget(self.clear_current_selection_button, 0, 4)

        self.file_label = QLabel(NO_FILE_LOADED, self)
        self.file_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.file_label, 1, 0, 1, 5)

        self.audio_info_label = QLabel("", self)
        self.audio_info_label.setStyleSheet("font-size: 12px;")
        self.layout.addWidget(self.audio_info_label, 2, 0, 1, 5)

        self.layout.setRowStretch(3, 1)

    def load_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, OPEN_AUDIO_FILE, "", WAVE_FILES)
        if file_path:
            self.clear_audio()
            self.file_label.setText(f"Loaded: {self.extract_name_from_path(file_path)}")
            self.audio = audioProcessing.AudioProcessing(file_path)
            self.display_waveform(self.audio)
            self.play_button.setVisible(True)
            self.clear_current_selection_button.setVisible(True)
            self.display_audio_info()

    def display_audio_info(self):
        sample_rate = self.audio.get_sample_rate()
        num_channels = self.audio.get_num_channels()
        bit_depth = self.audio.get_bit_depth()
        self.audio_info_label.setText(f"Sample Rate: {sample_rate} Hz, Channels: {num_channels}, Bit Depth: {bit_depth}")

    def save_highlighted_region(self):
        start, end = self.waveform_display.get_highlighted_region()
        if start is None or end is None:
            self.status_bar.showMessage(STATUS_BAR_MESSAGES["NO_REGION"])
            return
        file_path, _ = QFileDialog.getSaveFileName(self, SAVE_HIGHLIGHTED_REGION, "", WAVE_FILES)
        if file_path:
            self.audio.save_highlighted_region(start, end, file_path)
            self.status_bar.showMessage(f"{STATUS_BAR_MESSAGES['SAVED']} to {file_path}")

    def display_waveform(self, audio):
        if self.waveform_display:
            self.layout.removeWidget(self.waveform_display)
            self.waveform_display.deleteLater()
        self.waveform_display = wavDispaly.WaveformDisplay(self)
        self.waveform_display.plot_waveform(audio)
        self.layout.addWidget(self.waveform_display, 3, 0, 1, 5)

    def extract_name_from_path(self, path):
        return path.split("/")[-1]

    def play_audio(self):
        if self.audio:
            self.audio.play_audio()

    def play_selected_audio(self):
        if self.audio:
            start, end = self.waveform_display.get_highlighted_region()
            if start is not None and end is not None:
                self.audio.play_audio(start, end)

    def clear_current_selection(self):
        self.waveform_display.remove_highlighted_region()
        self.waveform_display.reset_highlighted_region()
        self.play_selected_button.setVisible(False)

    def update_play_selected_button(self, state):
        self.play_selected_button.setVisible(state)
        self.save_button.setVisible(state)

    def clear_audio(self):
        if self.waveform_display:
            self.layout.removeWidget(self.waveform_display)
            self.waveform_display.deleteLater()
            self.waveform_display = None
        self.audio = None
        self.file_label.setText(NO_FILE_LOADED)
        self.play_button.setVisible(False)
        self.play_selected_button.setVisible(False)
        self.save_button.setVisible(False)
        self.clear_current_selection_button.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioEditorApp()
    window.show()
    sys.exit(app.exec_())