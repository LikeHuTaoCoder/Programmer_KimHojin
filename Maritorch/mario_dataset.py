import torch
from torch.utils.data import Dataset

def contains_negative(buttons):
    return any(b < 0 for b in buttons)

def unmix(buttons):
    return [0 if b < 0 else b for b in buttons]

class MarioDataset(Dataset):
    def __init__(self, filenames, sequence_len, batch_size, num_passes, train=True, recur_buttons=False):
        self.sequence_len = sequence_len
        self.batch_size = batch_size
        self.num_passes = num_passes
        self.recur_buttons = recur_buttons
        self.train = train

        # 파싱 후 데이터는 [num_batches, seq_len, batch, dim]으로 생성
        self.data, self.labels, self.costs = self._load_data(filenames)
        self.num_batches = len(self.data)

    def _load_data(self, filenames):
        all_frames = []
        for filename in filenames:
            sessions = self._get_sessions(filename.strip())
            if sessions is not None:
                all_frames += sessions

        input_size = len(all_frames[0][0])
        output_size = len(all_frames[0][1])

        if self.recur_buttons:
            input_size += output_size
            for i in range(len(all_frames)):
                screen, buttons = all_frames[i]
                if i == 0:
                    prev_buttons = [-1] * output_size
                screen += prev_buttons
                prev_buttons = unmix(buttons)
                all_frames[i] = (screen, buttons)

        # batch 단위로 자르기
        total_seq_len = len(all_frames) // self.batch_size
        sequences = [
            all_frames[i * total_seq_len:(i + 1) * total_seq_len]
            for i in range(self.batch_size)
        ]

        num_steps = self.sequence_len
        batches_per_pass = total_seq_len // num_steps - 2
        data, labels, costs = [], [], []

        for _ in range(self.num_passes):
            for batch_idx in range(batches_per_pass):
                x, y, w = [], [], []
                for t in range(num_steps):
                    step_input = []
                    step_label = []
                    step_cost = []
                    for seq in sequences:
                        screen, buttons = seq[batch_idx * num_steps + t]
                        step_input.append(screen)
                        step_label.append(buttons)
                        if contains_negative(buttons):
                            step_cost.append([0] * output_size)
                        else:
                            step_cost.append([1] * output_size)
                    x.append(step_input)
                    y.append(step_label)
                    w.append(step_cost)
                data.append(torch.tensor(x, dtype=torch.float32))      # [seq_len, batch, input]
                labels.append(torch.tensor(y, dtype=torch.float32))    # [seq_len, batch, output]
                costs.append(torch.tensor(w, dtype=torch.float32))     # [seq_len, batch, output]

        return data, labels, costs

    def _get_sessions(self, filename):
        with open(filename) as f:
            lines = f.readlines()

        lines = [line.strip() for line in lines if line.strip()]
        header = lines[0].split(" ")
        self.input_width = int(header[0])
        self.input_height = int(header[1])
        self.extra_inputs = int(header[2])
        self.input_size = self.input_width * self.input_height + self.extra_inputs
        self.output_size = int(header[3])
        self.header = header

        frames = []
        i = 1
        while i < len(lines):
            if lines[i].startswith("Session"):
                i += 1
                continue
            screen = []
            while len(screen) < self.input_size:
                screen += list(map(float, lines[i].split()))
                i += 1
            buttons = list(map(float, lines[i].split()))
            i += 1
            frames.append((screen, buttons))
        return frames

    def __len__(self):
        return self.num_batches

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx], self.costs[idx]
print("mario_dataset.py loaded")