import os
import random
import numpy as np
import torch

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def count_trainable_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
