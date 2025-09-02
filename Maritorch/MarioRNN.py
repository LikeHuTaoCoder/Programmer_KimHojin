import torch
import torch.nn as nn

class MarioRNN(nn.Module):
    def __init__(self, input_size, output_size, rnn_sizes, dropout_keep, loss_function):
        super(MarioRNN, self).__init__()

        self.input_size = input_size
        self.output_size = output_size
        self.rnn_sizes = rnn_sizes
        self.num_layers = len(rnn_sizes)
        self.loss_function_name = loss_function.lower()

        self.dropout = nn.Dropout(1.0 - dropout_keep) if self.num_layers > 1 else nn.Identity()

        self.layers = nn.ModuleList()

        pre_size = input_size
        for size in rnn_sizes:
            lstm = nn.LSTM(
                input_size=pre_size,
                hidden_size=size,
            )
            self.layers.append(lstm)
            pre_size = size

        self.fc = nn.Linear(rnn_sizes[-1], output_size)
        self.sigmoid = nn.Sigmoid()

        if self.loss_function_name == "mean squared error":
            self.criterion = nn.MSELoss(reduction='none')
        elif self.loss_function_name == "cross entropy":
            self.criterion = nn.BCEWithLogitsLoss(reduction='none')
        else:
            raise ValueError(f"No such loss function: {loss_function}")

    def forward(self, x, hidden=None):
        new_hidden = []
        if hidden is None:
            hidden = [None] * self.num_layers
        for i, lstm in enumerate(self.layers):
            x, h = lstm(x, hidden[i])
            x = self.dropout(x)
            new_hidden.append(h)
        
        x = self.fc(x)
        if self.loss_function_name != "cross entropy":
            x = self.sigmoid(x)
        return x, new_hidden

    def predict(self, x, hidden=None):
        self.eval()
        with torch.no_grad():
            out, hidden = self.forward(x, hidden)
            if self.loss_function_name == "cross entropy":
                out = self.sigmoid(out)
        return out, hidden

    def compute_loss(self, predictions, targets, weights):
        loss = self.criterion(predictions, targets)
        weighted_loss = loss * weights
        return weighted_loss.mean()
print("MarioRNN.py loaded.")