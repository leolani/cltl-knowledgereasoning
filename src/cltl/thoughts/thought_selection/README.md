## Overview

In this folder, the code base for the `NSPReplier` is given. In order to run the NSP method, please download the pretrained NSP model from the following [Google Drive link](https://drive.google.com/drive/folders/10GEpnjqXn4DfyKjFjJG7KbJEygvdAI2J?usp=sharing) and replace the `models/` folder.

| Files/folders    | Description   |
| ---------------- |:-------------|
| nsp.py           | Implementation of the Next Sentence Prediction selector. In order to run the NSP method, please download the pretrained NSP model from the following [Google Drive link](https://drive.google.com/drive/folders/10GEpnjqXn4DfyKjFjJG7KbJEygvdAI2J?usp=sharing) and replace the `models/` folder. |
| model/           | Folder in which the pytorch NSP model is stored |
| rl.py            | Implementation of the UCB reinforcement learning algorithm used by the RLReplier. |
| thoughts.json    | JSON file containing the learned utility values used to score thoughts by the RLReplier. |
