import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from model import BrailleAudioCNN
from dataset import BrailleAudioDataset
from config import (
    NUM_CLASSES, BATCH_SIZE, LEARNING_RATE, NUM_EPOCHS,
    TRAIN_SPLIT, MODEL_SAVE_DIR, DATA_RAW_DIR
)


def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    dataset = BrailleAudioDataset(root_dir=DATA_RAW_DIR)
    if len(dataset) == 0:
        print(f'No data found in {DATA_RAW_DIR}/. Please add audio samples.')
        print('Expected structure: data/raw/a/*.wav, data/raw/b/*.wav, ...')
        return

    train_size = int(len(dataset) * TRAIN_SPLIT)
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    model = BrailleAudioCNN(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    best_val_acc = 0.0
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    for epoch in range(NUM_EPOCHS):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

        train_acc = train_correct / train_total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = val_correct / val_total if val_total > 0 else 0
        scheduler.step(val_loss)

        print(f'Epoch [{epoch+1}/{NUM_EPOCHS}] '
              f'Train Loss: {train_loss/train_total:.4f} Train Acc: {train_acc:.4f} '
              f'Val Loss: {val_loss/val_total:.4f} Val Acc: {val_acc:.4f}')

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(MODEL_SAVE_DIR, 'best_model.pth'))
            print(f'  -> Saved best model (val_acc: {val_acc:.4f})')

    print(f'\nTraining complete. Best validation accuracy: {best_val_acc:.4f}')


if __name__ == '__main__':
    train()
