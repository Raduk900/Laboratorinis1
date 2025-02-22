from scipy.io import wavfile
import numpy as np
import pygame
import os

class AudioProcessing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sample_rate, self.data = wavfile.read(self.file_path)
        self.data = self.data / 32768
        self.milliseconds = self.samples_to_milliseconds(len(self.data))
        self.dtype = self.data.dtype
        pygame.mixer.init()

    def get_sample_rate(self):
        return self.sample_rate

    def get_data(self):
        return self.data

    def get_duration(self):
        return len(self.data) / self.sample_rate

    def get_num_samples(self):
        return len(self.data)

    def get_num_channels(self):
        return len(self.data.shape)

    def get_bit_depth(self):
        return self.data.itemsize * 8
    
    def get_milliseconds(self):
        return self.milliseconds
    
    def samples_to_milliseconds(self, sample):
        return sample * 1000 / self.sample_rate
    
    def get_time_in_ms(self):
        return [self.samples_to_milliseconds(i) for i in range(len(self.data))]
    
    def save_highlighted_region(self, start, end, file_path):
        if start is None or end is None:
            return

        start_sample = int(start * self.sample_rate / 1000)
        end_sample = int(end * self.sample_rate / 1000)

        if len(self.data.shape) == 1:  # Mono
            highlighted_data = self.data[start_sample:end_sample]
        else:  # Stereo
            highlighted_data = self.data[start_sample:end_sample, :]

        highlighted_data = (highlighted_data * 32768).astype('int16')

        wavfile.write(file_path, self.sample_rate, highlighted_data)

    
    def play_audio(self, start=None, end=None):
        if start is not None and end is not None:
            start_sample = int(start * self.sample_rate / 1000)
            end_sample = int(end * self.sample_rate / 1000)
            audio_data = self.data[start_sample:end_sample]
            temp_path = "temp_highlighted.wav"
            wavfile.write(temp_path, self.sample_rate, audio_data)
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            self.cleanup_temp_files()
        else:
            print(self.file_path)
            pygame.mixer.music.load(self.file_path)
            pygame.mixer.music.play()
            self.cleanup_temp_files()

    def stop_audio(self):
        pygame.mixer.music.stop()

    def cleanup_temp_files(self):
        temp_path = "temp_highlighted.wav"
        if os.path.exists(temp_path):
            os.remove(temp_path)
