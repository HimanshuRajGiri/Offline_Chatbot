import os
import sys
import base64
import io
import webview
from PIL import Image
from llama_cpp import Llama
from llama_cpp.llama_chat_format import MoondreamChatHandler
 
# --- Paths ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
 
TEXT_MODEL_PATH = resource_path(os.path.join("models", "Phi-3-mini-4k-instruct-q4.gguf"))
VISION_MODEL_PATH = resource_path(os.path.join("models", "vision2", "moondream2-text-model-f16.gguf"))
VISION_MMPROJ_PATH = resource_path(os.path.join("models", "vision2", "moondream2-mmproj-f16.gguf"))
HTML_PATH = resource_path("index.html")
 
# --- Load the text-only model at startup ---
print("Loading text model...")
text_llm = Llama(
    model_path=TEXT_MODEL_PATH,
    n_ctx=4096,
    verbose=False,
)
print("Text model loaded.")
 
# --- The vision model is loaded lazily (only when first image is sent) ---
vision_llm = None
 
def get_vision_model():
    global vision_llm
    if vision_llm is None:
        print("Loading vision model, this may take a moment...")
        chat_handler = MoondreamChatHandler(clip_model_path=VISION_MMPROJ_PATH)
        vision_llm = Llama(
            model_path=VISION_MODEL_PATH,
            chat_handler=chat_handler,
            n_ctx=2048,
            verbose=False,
        )
        print("Vision model loaded.")
    return vision_llm
 
 
def clean_image_data_url(image_base64):
    """
    Takes whatever data URL the browser sent, decodes it, re-encodes it as a
    clean JPEG data URL. This fixes cases where the original bytes were
    slightly mangled in transit (a common cause of 'failed to create bitmap').
    """
    # Strip the "data:image/xxx;base64," prefix if present
    if "," in image_base64:
        header, encoded = image_base64.split(",", 1)
    else:
        encoded = image_base64
 
    raw_bytes = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(raw_bytes))
    img = img.convert("RGB")  # drops alpha channel / weird color modes
 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    clean_bytes = buffer.getvalue()
    clean_b64 = base64.b64encode(clean_bytes).decode("utf-8")
 
    return f"data:image/jpeg;base64,{clean_b64}"
 
 
class Api:
    """
    Exposed to JavaScript as window.pywebview.api.<method_name>(...)
    """
 
    def __init__(self):
        self.text_history = []
 
    def send_message(self, user_text):
        """Plain text chat — uses the fast small text model."""
        self.text_history.append({"role": "user", "content": user_text})
        try:
            result = text_llm.create_chat_completion(
                messages=self.text_history,
                temperature=0.7,
                max_tokens=512,
            )
            reply = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            reply = f"Error while generating a response: {e}"
 
        self.text_history.append({"role": "assistant", "content": reply})
        return reply
 
    def send_message_with_image(self, user_text, image_base64):
        """
        Image + text chat — uses the Moondream2 vision model.
        image_base64 should be a data URL, e.g. 'data:image/png;base64,....'
        """
        try:
            cleaned_image = clean_image_data_url(image_base64)
            llm = get_vision_model()
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text or "Describe this image."},
                        {"type": "image_url", "image_url": {"url": cleaned_image}},
                    ],
                }
            ]
            result = llm.create_chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=512,
            )
            reply = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            reply = f"Error while analyzing the image: {e}"
 
        return reply
 
    def reset_chat(self):
        self.text_history = []
        return True
 
 
if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Local Chat — Phi-3 + Moondream",
        HTML_PATH,
        js_api=api,
        width=900,
        height=700,
        min_size=(500, 500),
    )
    webview.start()
 
