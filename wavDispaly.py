from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from constants import STATUS_BAR_MESSAGES, BUTTON_PRESS_EVENT

class WaveformDisplay(FigureCanvas):
    def __init__(self, audio_editor_app):
        self.audio_editor_app = audio_editor_app
        self.figure = Figure()
        super().__init__(self.figure)
        self.axes = []
        self.highlighted_region = []
        self.x_one_coords = None
        self.x_two_coords = None
        self.connect_events()

    def plot_waveform(self, audio):
        self.figure.clear()
        self.axes = []
        self.highlighted_region = []

        time_in_ms = audio.get_time_in_ms()
        data = audio.get_data()
        num_channels = audio.get_num_channels()

        mono_color = 'blue'
        stereo_colors = ['red', 'blue']

        for i in range(num_channels):
            ax = self.figure.add_subplot(num_channels, 1, i + 1)
            self.axes.append(ax)
            self.highlighted_region.append(None)
            if num_channels == 1:  # Mono
                ax.plot(time_in_ms, data, color=mono_color, linewidth=0.5)
                ax.set_ylabel('Amplitude')
            else:  # Stereo
                ax.plot(time_in_ms, data[:, i], label=f'Channel {i + 1}', color=stereo_colors[i % len(stereo_colors)], linewidth=0.5)
                ax.set_ylabel(f'Channel {i + 1} Amplitude')
            if i == num_channels - 1:
                ax.set_xlabel('Time (ms)')
        self.draw()

    def connect_events(self):
        self.mpl_connect(BUTTON_PRESS_EVENT, self.on_click)

    def on_click(self, event):
        if event.inaxes in self.axes and event.button == MouseButton.LEFT:
            if self.x_one_coords is None:
                self.x_one_coords = event.xdata
            else:
                self.x_two_coords = event.xdata
                if self.x_one_coords is not None and self.x_two_coords is not None:
                    self.remove_highlighted_region()
                    self.highlight_region(self.x_one_coords, self.x_two_coords)
                    self.audio_editor_app.update_play_selected_button(True)

    def highlight_region(self, start, end):
        if start is None or end is None:
            return

        for i in range(len(self.axes)):
            if self.highlighted_region[i]:
                self.highlighted_region[i].remove()
            self.highlighted_region[i] = self.axes[i].axvspan(start, end, color='red', alpha=0.3)
        self.draw()
        self.audio_editor_app.status_bar.showMessage(STATUS_BAR_MESSAGES["HIGHLIGHTED"])

    def get_highlighted_region(self):
        return self.x_one_coords, self.x_two_coords

    def reset_highlighted_region(self):
        self.x_one_coords = None
        self.x_two_coords = None

    def remove_highlighted_region(self):
        for i in range(len(self.axes)):
            if self.highlighted_region[i]:
                self.highlighted_region[i].remove()
                self.highlighted_region[i] = None
        self.draw()
        self.audio_editor_app.status_bar.showMessage(STATUS_BAR_MESSAGES["HIGHLIGHT_REMOVED"])
        self.audio_editor_app.update_play_selected_button(False)
