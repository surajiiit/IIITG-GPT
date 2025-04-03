import torch
from transformers import AutoModel, AutoTokenizer

EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v2-moe"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBEDDING_MODEL, trust_remote_code=True).to(DEVICE)
model.eval()

inputs = tokenizer("test sentence", return_tensors="pt", padding=True, truncation=True).to(DEVICE)
with torch.no_grad():
    outputs = model(**inputs)
    print(outputs)  # Check the output structure