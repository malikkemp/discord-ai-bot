from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model and tokenizer
MODEL_NAME = "google/gemma-3-270m"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Use CPU (or GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

app = FastAPI()

class RequestBody(BaseModel):
    prompt: str
    max_new_tokens: int = 128

@app.post("/generate")
async def generate_text(req: RequestBody):
    inputs = tokenizer(req.prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=req.max_new_tokens)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
