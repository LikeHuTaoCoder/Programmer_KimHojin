import torch
from torch.utils.data import DataLoader
import os
import time
import datetime
from Config import get_data, get_model, get_checkpoint_dir, get_validation_period

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)
# 설정 및 초기화
data = get_data(training=True)
model = get_model(data).to(device)
train_loader = DataLoader(data, batch_size=1, shuffle=False)
optimizer = torch.optim.Adam(model.parameters())
epochs = 100

checkpoint_dir = get_checkpoint_dir()
os.makedirs(checkpoint_dir, exist_ok=True)

best_cost = float('inf')
step = 0
last_validation = time.time() - get_validation_period()

# 검증 함수
def validate(model, sample):
    model.eval()
    x, y, w = sample
    x, y, w = x.squeeze(0).to(device), y.squeeze(0).to(device), w.squeeze(0).to(device)
    with torch.no_grad():
        output, _ = model(x)
        loss = model.compute_loss(output, y, w)
    return loss.item()

# 학습 루프
for epoch in range(epochs):
    for batch in train_loader:
        model.train()
        x, y, w = batch
        x, y, w = x.squeeze(0).to(device), y.squeeze(0).to(device), w.squeeze(0).to(device)

        output, _ = model(x)
        loss = model.compute_loss(output, y, w)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        optimizer.step()

        step += 1
        # 30초 마다 검증
        if time.time() - last_validation >= get_validation_period():
            val_loss = validate(model, batch)
            print(f"[{datetime.datetime.now()}] Step {step}, Val Loss: {val_loss:.4f}")
            last_validation = time.time()
            
            # loss가 적어졌으면 모델 저장
            if val_loss < best_cost:
                best_cost = val_loss
                torch.save(model.state_dict(), os.path.join(checkpoint_dir, "mario_best.pt"))
                print("✔ Best model saved.")
print(step)
print("✅ Training finished.")