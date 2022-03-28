import sounddevice as sd
import librosa
import numpy as np
import glob
import datetime
import os

file_paths = glob.glob(os.path.join(os.path.dirname(__file__),'sound_samples/*.wav'))
# ["one.wav", "two.wav", "three.wav", "four.wav", "five.wav", "six.wav", "seven.wav", "eight.wav", "nine.wav"]

class Nback():
    def __init__(self, time_between_each_number = 1.5):
        self.audio_data, self.sample_rate = self.load_sounds()
        self.time_between_each_number = time_between_each_number

    def load_sounds(self):
        audio_data = []
        sample_rate = []

        for file_path in file_paths:
            data, sr = librosa.load(file_path)
            audio_data.append(data)
            sample_rate.append(sr)

        return audio_data, sample_rate

    def play_sound(self, index):
        size = int(self.sample_rate[index]*self.time_between_each_number)
        data = np.pad(self.audio_data[index], (0, size - len(self.audio_data[index])),"constant")
        sd.play(data, self.sample_rate[index], blocking=True)

        return datetime.datetime.now().timestamp()

    def play_nback_sequence(self, sequence):
        try:
            timestamp_arr = []
            for i in sequence:
                print(i)
                timestamp = self.play_sound(i-1)
                timestamp_arr.append(timestamp)
            return timestamp_arr
        except:
            print("Error")
            return None

# if __name__=="__main__":
#     nback = Nback()
#     nback.play_nback_sequence([1, 2, 3, 4, 5, 6, 7, 8, 9 ])
            
    