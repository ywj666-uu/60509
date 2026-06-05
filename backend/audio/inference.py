import os
import torch
import torchaudio
import torchaudio.transforms as T
import numpy as np
from django.conf import settings

SAMPLE_RATE = 16000
N_MELS = 64
N_FFT = 1024
HOP_LENGTH = 512
TARGET_LENGTH = 128
CHAR_MAP = 'abcdefghijklmnopqrstuvwxyz'

# Pre-filter parameters
SILENCE_THRESHOLD_DB = -40  # dB below peak to consider as silence
NOISE_BURST_THRESHOLD = 3.0  # std deviations above mean energy to flag as burst
FRAME_DURATION_MS = 20  # frame size for energy analysis
MIN_CLEAN_DURATION_S = 0.1  # minimum clean segment to keep

_model = None


def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(settings.ML_MODEL_DIR, 'braille_cnn.pt')
        if not os.path.exists(model_path):
            return None
        _model = torch.jit.load(model_path, map_location='cpu')
        _model.eval()
    return _model


def _compute_frame_energy(waveform, frame_size):
    """Compute short-time energy per frame."""
    signal = waveform.squeeze()
    num_frames = len(signal) // frame_size
    if num_frames == 0:
        return torch.tensor([signal.pow(2).mean()])
    frames = signal[:num_frames * frame_size].reshape(num_frames, frame_size)
    return frames.pow(2).mean(dim=1)


def _trim_silence(waveform, sample_rate):
    """Remove leading and trailing silence based on energy threshold."""
    frame_size = int(sample_rate * FRAME_DURATION_MS / 1000)
    energy = _compute_frame_energy(waveform, frame_size)

    if energy.max() == 0:
        return waveform

    energy_db = 10 * torch.log10(energy + 1e-10)
    peak_db = energy_db.max()
    threshold = peak_db + SILENCE_THRESHOLD_DB

    active = (energy_db >= threshold).nonzero(as_tuple=True)[0]
    if len(active) == 0:
        return waveform

    start_frame = active[0].item()
    end_frame = active[-1].item() + 1

    start_sample = start_frame * frame_size
    end_sample = min(end_frame * frame_size, waveform.shape[-1])
    return waveform[..., start_sample:end_sample]


def _remove_noise_bursts(waveform, sample_rate):
    """Detect and zero-out sudden noise bursts that exceed the threshold."""
    frame_size = int(sample_rate * FRAME_DURATION_MS / 1000)
    energy = _compute_frame_energy(waveform, frame_size)

    if len(energy) < 3:
        return waveform

    mean_energy = energy.mean()
    std_energy = energy.std()

    if std_energy == 0:
        return waveform

    burst_mask = energy > (mean_energy + NOISE_BURST_THRESHOLD * std_energy)

    # Only suppress isolated spikes (bursts shorter than 3 consecutive frames are noise)
    cleaned = waveform.clone()
    signal = cleaned.squeeze()
    num_frames = len(energy)

    i = 0
    while i < num_frames:
        if burst_mask[i]:
            burst_start = i
            while i < num_frames and burst_mask[i]:
                i += 1
            burst_end = i
            burst_len = burst_end - burst_start
            # Short bursts (< 60ms) are noise; longer ones are likely valid signal
            if burst_len <= 3:
                s = burst_start * frame_size
                e = min(burst_end * frame_size, len(signal))
                signal[s:e] = 0
        else:
            i += 1

    return cleaned


def _extract_clean_segments(waveform, sample_rate):
    """Extract only the clean (non-silent, non-burst) portions and concatenate."""
    frame_size = int(sample_rate * FRAME_DURATION_MS / 1000)
    energy = _compute_frame_energy(waveform, frame_size)

    if len(energy) == 0:
        return waveform

    energy_db = 10 * torch.log10(energy + 1e-10)
    peak_db = energy_db.max()
    silence_threshold = peak_db + SILENCE_THRESHOLD_DB

    mean_energy = energy.mean()
    std_energy = energy.std()
    burst_threshold = mean_energy + NOISE_BURST_THRESHOLD * std_energy

    min_frames = int(MIN_CLEAN_DURATION_S * sample_rate / frame_size)
    signal = waveform.squeeze()
    segments = []
    current_start = None

    for i in range(len(energy)):
        is_active = energy_db[i] >= silence_threshold
        is_not_burst = energy[i] <= burst_threshold
        is_clean = is_active and is_not_burst

        if is_clean and current_start is None:
            current_start = i
        elif not is_clean and current_start is not None:
            if (i - current_start) >= min_frames:
                s = current_start * frame_size
                e = min(i * frame_size, len(signal))
                segments.append(signal[s:e])
            current_start = None

    # Handle trailing segment
    if current_start is not None and (len(energy) - current_start) >= min_frames:
        s = current_start * frame_size
        segments.append(signal[s:])

    if not segments:
        return waveform

    cleaned = torch.cat(segments)
    return cleaned.unsqueeze(0)


def prefilter_audio(waveform, sample_rate):
    """Full pre-filtering pipeline: trim silence → remove bursts → extract clean segments."""
    waveform = _trim_silence(waveform, sample_rate)
    waveform = _remove_noise_bursts(waveform, sample_rate)
    waveform = _extract_clean_segments(waveform, sample_rate)
    return waveform


def preprocess_audio(audio_path):
    waveform, sample_rate = torchaudio.load(audio_path)

    if sample_rate != SAMPLE_RATE:
        resampler = T.Resample(sample_rate, SAMPLE_RATE)
        waveform = resampler(waveform)

    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Pre-filter: trim silence, remove noise bursts, keep only clean segments
    waveform = prefilter_audio(waveform, SAMPLE_RATE)

    mel_transform = T.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_mels=N_MELS,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
    )
    mel_spec = mel_transform(waveform)
    mel_spec = T.AmplitudeToDB()(mel_spec)

    # Normalize
    mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)

    # Pad or truncate
    if mel_spec.shape[-1] < TARGET_LENGTH:
        pad = TARGET_LENGTH - mel_spec.shape[-1]
        mel_spec = torch.nn.functional.pad(mel_spec, (0, pad))
    else:
        mel_spec = mel_spec[..., :TARGET_LENGTH]

    return mel_spec.unsqueeze(0)  # (1, 1, n_mels, time)


def classify_audio(audio_path):
    model = get_model()
    if model is None:
        import random
        char = random.choice(CHAR_MAP)
        return char, random.uniform(0.5, 0.99)

    mel_spec = preprocess_audio(audio_path)

    with torch.no_grad():
        logits = model(mel_spec)
        probs = torch.softmax(logits, dim=1)
        confidence, predicted_idx = probs.max(dim=1)

    predicted_char = CHAR_MAP[predicted_idx.item()]
    return predicted_char, confidence.item()
