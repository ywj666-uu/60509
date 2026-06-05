import os
import torch
from model import BrailleAudioCNN
from config import NUM_CLASSES, MODEL_SAVE_DIR


def export_to_torchscript():
    model = BrailleAudioCNN(num_classes=NUM_CLASSES)

    model_path = os.path.join(MODEL_SAVE_DIR, 'best_model.pth')
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        print(f'Loaded weights from {model_path}')
    else:
        print('No trained model found. Exporting with random weights for testing.')

    model.eval()

    # Trace with example input: (batch=1, channels=1, n_mels=64, time_frames=128)
    example_input = torch.randn(1, 1, 64, 128)
    traced_model = torch.jit.trace(model, example_input)

    output_path = os.path.join(MODEL_SAVE_DIR, 'braille_cnn.pt')
    traced_model.save(output_path)
    print(f'Model exported to {output_path}')


if __name__ == '__main__':
    export_to_torchscript()
