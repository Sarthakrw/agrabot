from sentence_transformers import CrossEncoder

# Load the model, here we use our base sized model
model = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-2-v2") # 17 MegaByte !!