""" Filename:     NSP.py
    Author(s):    Thomas Bellucci
    Description:  Implementation of a BERT-based next sentence prediction
                  (NSP) transformer built on Huggingface transformers.
    Date created: Nov. 11th, 2021
"""

import numpy as np
import torch
from cltl.commons.casefolding import (casefold_capsule)
from transformers import (BertForNextSentencePrediction, BertTokenizer)

from cltl.thoughts.api import ThoughtSelector


class NSP(ThoughtSelector):
    def __init__(self, filename):
        """Initializes an instance of BERT for Next Sentence Prediction (NSP).

        params
        str filename: path to a pretrained NSP BERT nsp_model

        returns: None
        """
        super().__init__()

        self.__tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.__model = BertForNextSentencePrediction.from_pretrained(filename)

        self.__device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        self.__model.to(self.__device)

    def score_response(self, context, response):
        """Predicts for a (context, response) pair their likelihood according to
        the nsp_model.

        returns: Softmax likelihood
        """
        X_batch = self.__tokenizer.batch_encode_plus(
            [[context, response]], padding=True, truncation=True, return_tensors="pt"
        )

        X_batch["input_ids"] = X_batch["input_ids"].to(self.__device)
        X_batch["token_type_ids"] = X_batch["token_type_ids"].to(self.__device)
        X_batch["attention_mask"] = X_batch["attention_mask"].to(self.__device)

        # Forward pass
        outputs = self.__model(**X_batch)
        logits = outputs.logits.detach().cpu().numpy()[0]

        # Prob(is_next) using softmax
        return np.exp(logits[0]) / np.sum(np.exp(logits))

    def select(self, thoughts):
        thoughts = self._preprocess(thoughts)

        # Score phrasings of thoughts
        scores = []
        for thought_type, thought_info in thoughts.items():
            # preprocess
            thought_info = casefold_capsule(thought_info, format="natural")

            # Score response (context is thought type and sentence to score is combined thought info)
            score = self.score_response(thought_info[0], thought_type)
            scores.append((thought_type, thought_info[0], score))

        scores.sort(key=lambda x: x[2], reverse=True)

        # Safe processing
        thought_type, thought_info = self._postprocess(thoughts, scores[0][0])
        return {thought_type: thought_info}
