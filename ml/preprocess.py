import torch
import torchaudio
import torchaudio.transforms as T
import numpy as np
from config import SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH, TARGET_LENGTH

SILENCE_THRESHOLD_DB = -40
NOISE_BURST_THRESHOLD = 3.0
FRAME_DURATION_MS = 20
MIN_CLEAN_DURATION_S = 0.1


def _compute_frame_energy(waveform, frame_size):
    signal = waveform.squeeze()
    num_frames = len(signal) // frame_size
    if num_frames == 0:
        return torch.tensor([signal.pow(2).mean()])
    frames = signal[:num_frames * frame_size].reshape(num_frames, frame_size)
    return frames.pow(2).mean(dim=1)


def _trim_silence(waveform, sample_rate):
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
    start_sample = active[0].item() * frame_size
    end_sample = min((active[-1].item() + 1) * frame_size, waveform.shape[-1])
    return waveform[..., start_sample:end_sample]


def _remove_noise_bursts(waveform, sample_rate):
    frame_size = int(sample_rate * FRAME_DURATION_MS / 1000)
    energy = _compute_frame_energy(waveform, frame_size)
    if len(energy) < 3:
        return waveform
    mean_energy = energy.mean()
    std_energy = energy.std()
    if std_energy == 0:
        return waveform
    burst_mask = energy > (mean_energy + NOISE_BURST_THRESHOLD * std_energy)
    cleaned = waveform.clone()
    signal = cleaned.squeeze()
    num_frames = len(energy)
    i = 0
    while i < num_frames:
        if burst_mask[i]:
            burst_start = i
            while i < num_frames and burst_mask[i]:
                i += 1
            if (i - burst_start) <= 3:
                s = burst_start * frame_size
                e = min(i * frame_size, len(signal))
                signal[s:e] = 0
        else:
            i += 1
    return cleaned


def _extract_clean_segments(waveform, sample_rate):
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
        is_clean = energy_db[i] >= silence_threshold and energy[i] <= burst_threshold
        if is_clean and current_start is None:
            current_start = i
        elif not is_clean and current_start is not None:
            if (i - current_start) >= min_frames:
                s = current_start * frame_size
                e = min(i * frame_size, len(signal))
                segments.append(signal[s:e])
            current_start = None
    if current_start is not None and (len(energy) - current_start) >= min_frames:
        segments.append(signal[current_start * frame_size:])
    if not segments:
        return waveform
    return torch.cat(segments).unsqueeze(0)


def prefilter_audio(waveform, sample_rate):
    """Full pre-filtering: trim silence → remove bursts → extract clean segments."""
    waveform = _trim_silence(waveform, sample_rate)
    waveform = _remove_noise_bursts(waveform, sample_rate)
    waveform = _extract_clean_segments(waveform, sample_rate)
    return waveform


def audio_to_mel_spectrogram(audio_path, apply_prefilter=True):
    waveform, sample_rate = torchaudio.load(audio_path)

    if sample_rate != SAMPLE_RATE:
        resampler = T.Resample(sample_rate, SAMPLE_RATE)
        waveform = resampler(waveform)

    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    if apply_prefilter:
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

    # Pad or truncate to fixed length
    if mel_spec.shape[-1] < TARGET_LENGTH:
        pad = TARGET_LENGTH - mel_spec.shape[-1]
        mel_spec = torch.nn.functional.pad(mel_spec, (0, pad))
    else:
        mel_spec = mel_spec[..., :TARGET_LENGTH]

    return mel_spec


def augment_waveform(waveform, sample_rate):
    augmentations = []

    # Time stretch
    stretch_factor = np.random.uniform(0.8, 1.2)
    stretched = torchaudio.functional.speed(waveform, sample_rate, stretch_factor)[0]
    augmentations.append(stretched)

    # Add noise
    noise = torch.randn_like(waveform) * 0.005
    noisy = waveform + noise
    augmentations.append(noisy)

    # Volume change
    gain = np.random.uniform(0.7, 1.3)
    gained = waveform * gain
    augmentations.append(gained)

    return augmentations
