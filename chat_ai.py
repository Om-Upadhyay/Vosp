from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

chat_history_ids = None  # This will be reset after every wake word

def generate_reply(user_input):
    global chat_history_ids

    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

    # No history since we reset after every wake word
    bot_input_ids = new_input_ids

    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=60,
        top_p=0.95
    )

    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response

def reset_chat_history():
    global chat_history_ids
    chat_history_ids = None
