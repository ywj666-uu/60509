import os
import torch
from torch.utils.data import Dataset
import torchaudio
from preprocess import audio_to_mel_spectrogram
from config import CHAR_MAP, DATA_RAW_DIR


class BrailleAudioDataset(Dataset):
    """
    Expects data organized as: data/raw/{character}/*.wav
    e.g., data/raw/a/sample_001.wav
    """
    def __init__(self, root_dir=DATA_RAW_DIR, transform=None):
        self.samples = []
        self.transform = transform

        for idx, char in enumerate(CHAR_MAP):
            char_dir = os.path.join(root_dir, char)
            if not os.path.isdir(char_dir):
                continue
            for filename in os.listdir(char_dir):
                if filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
                    filepath = os.path.join(char_dir, filename)
                    self.samples.append((filepath, idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        filepath, label = self.samples[idx]
        mel_spec = audio_to_mel_spectrogram(filepath)

        if self.transform:
            mel_spec = self.transform(mel_spec)

        return mel_spec, label
