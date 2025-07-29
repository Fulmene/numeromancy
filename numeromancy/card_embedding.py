import torch
import torch.nn as nn
from torch.utils.data import Dataset
import numpy as np
from transformers import AutoTokenizer, AutoModel


class CardEmbedding(nn.Module):
    def __init__(self):
        super(CardEmbedding, self).__init__()
        self.tokenize = AutoTokenizer.from_pretrained("FacebookAI/roberta-base")
        self.transformer = AutoModel.from_pretrained("FacebookAI/roberta-base")
        self.embedder = nn.Sequential(
                nn.Linear(799, 64),
                nn.ReLU(),
                nn.Dropout(0.2))

    def mean_pooling(self, token_embeddings, attention_mask):
        mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * mask, dim=1)
        sum_mask = mask.sum(dim=1).clamp(min=1e-9)
        return sum_embeddings / sum_mask

    def forward(self, props, text):
        device = next(self.parameters()).device
        props = props.to(device)

        text = self.tokenize(text, padding=True, truncation=True, return_tensors="pt", max_length=50).to(device)
        encoded = {k: v.to(device) for k,v in text.items()}

        output = self.transformer(**text)
        pooled = self.mean_pooling(output.last_hidden_state, encoded['attention_mask'])
        embedding = self.embedder(torch.cat((props, pooled), dim=1))
        return embedding


class CardDataset(Dataset):
    def __init__(self, props, text, cmc):
        self.props = props
        self.text = text
        self.cmc = cmc

    def __len__(self):
        return len(self.cmc)

    def __getitem__(self, idx):
        return self.props[idx], self.text[idx], self.cmc[idx]


class EmbeddedCardDataset(Dataset):
    def __init__(self, emb, cmc):
        self.emb = emb
        self.cmc = cmc

    def __len__(self):
        return len(self.cmc)

    def __getitem__(self, idx):
        return self.emb[idx], self.cmc[idx]
