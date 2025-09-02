# Maritorch (Mario Kart AI with PyTorch)

**English**  
This project is a reproduction and improvement of **MariFlow**, an AI agent that automatically plays *Super Mario Kart*.  
The original implementation was based on TensorFlow, but it has been reimplemented in **PyTorch** for better flexibility and maintainability.  
The system captures game frames via BizHawk emulator and uses an LSTM-based model to predict controller inputs in real time.

---

**日本語**  
このプロジェクトは、*スーパーマリオカート* を自動で操作するAIエージェント **MariFlow** の再現および改良版です。  
元々は TensorFlow で実装されていましたが、より柔軟で保守しやすい **PyTorch** に移植しました。  
BizHawk エミュレータを通じてゲーム画面を取得し、LSTM ベースのモデルでリアルタイムに操作ボタンを予測します。  

---

## How It Works / 作動方式

- **Input (入力):**
  - Mario Kart gameplay screen, resized to **15×15**  
  - Current course ID (top 20 cells)  
  - Speed, item, reverse flag (bottom 3 cells)

- **Processing & Output (処理・出力):**
  - LSTM-based model extracts features from 248 input values  
  - Predicts **8 output values** (probability of pressing each button)  
  - Outputs are displayed via **pygame** in real time

- **Memory System (記憶構造):**
  - Long-term memory: Past gameplay analysis  
  - Short-term memory: Current state analysis  

---

## Code Structure / コード構成

- `RunByUser.py` : Remote control & data collection (captures gameplay, sends to server, logs dataset)  
- `RemotePlay.lua` : Sends game screen & state to server, receives predicted button input  
- `MarioDataset.py` : Defines dataset structure for training  
- `MarioRNN.py` : Model architecture (LSTM + Fully Connected + Sigmoid)  
- `Train.py` : Training script (uses ~15,000 frames ≈ 15 min gameplay data)  
- `RunLive.py` : Live inference (predicts buttons during gameplay)  
- `DisplayNetwork.py` : Visualization with pygame (draw inputs, state, outputs)  
- `Config.py` : Loads settings from `Sample.cfg`

---

## Demo Video / デモ動画
[![Watch the video](https://img.youtube.com/vi/2Q06KALGKx4/0.jpg)](https://youtu.be/2Q06KALGKx4)

**English**  
Click the thumbnail to watch the demo of Maritorch in action.  

**日本語**  
サムネイルをクリックすると、Maritorch の動作デモをご覧いただけます。  

---

## Technical Specs / 実行環境

- Python: 3.10.16  
- PyTorch: 2.7.0+cu118  
- CUDA: 11.8  
- cuDNN: 90100  
- GPU: NVIDIA GeForce RTX 4070  

---

## Notes / 備考
Parts of this README were drafted with the assistance of OpenAI's ChatGPT.  
本READMEの一部は、OpenAI の ChatGPT を利用して作成しました。  

---

## License / Copyright
MariFlow is Copyright © 2017 SethBling LLC
The LUA Socket Library is Copyright © 2004-2007 Diego Nehab. It falls under the MIT license, which means it's free to use for any purpose, with copyright notice.

---

## Trademark Notice
PyTorch is a trademark of Meta AI.  
BizHawk is maintained by its respective open-source community.  
Other names or brands may be claimed as the property of others.  

PyTorch は Meta AI の商標です。  
BizHawk はそのオープンソースコミュニティによって管理されています。  
その他の名称やブランドは、各社が所有する場合があります。  
