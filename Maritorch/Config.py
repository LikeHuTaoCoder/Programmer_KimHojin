from MarioRNN import MarioRNN
from mario_dataset import MarioDataset
import configparser
import sys

configFilename = "sample.cfg"

if len(sys.argv) >= 2:
    configFilename = sys.argv[1]

config = configparser.ConfigParser()
config.read(["defaults.cfg", configFilename])


def get_data(training):
    filenames = config.get("Data", "Filename").strip().split('\n')
    filenames = [f.strip().replace("\\", "/") for f in filenames]

    data = MarioDataset(
        filenames=filenames,
        sequence_len=int(config.get("Data", "SequenceLength")),
        batch_size=int(config.get("Data", "BatchSize")),
        num_passes=int(config.get("Train", "NumPasses")),
        train=training,
        recur_buttons=config.get("Data", "RecurButtons") == "True"
    )
    return data

def get_model(data):
    rnn_sizes = []
    layer = 1
    while True:
        try:
            size = int(config.get("RNN", "Layer" + str(layer)))
            if size < 1:
                break
            rnn_sizes.append(size)
            layer += 1
        except:
            break

    print("RNN Sizes: " + str(rnn_sizes))

    model = MarioRNN(
        input_size=data.input_size + data.output_size if data.recur_buttons else data.input_size,
        output_size=data.output_size,
        rnn_sizes=rnn_sizes,
        dropout_keep=float(config.get("Train", "DropoutKeep")),
        loss_function=config.get("Train", "LossFunction")
    )
    return model

def get_checkpoint_dir():
    return config.get("Checkpoint", "Dir").replace("\\", "/")

def get_validation_period():
    return float(config.get("Train", "ValidationPeriod"))
print("Config.py loaded.")