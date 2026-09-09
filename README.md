# Offline Chatbot

A small desktop chatbot that runs locally on your computer. It supports:

- Text conversations with **Phi-3-mini-4k-instruct**.
- Image questions and image descriptions with **Moondream2**.
- A simple desktop interface built with HTML/CSS and `pywebview`.
- Offline inference after the Python dependencies and model files have been installed.

No cloud API key is required for chat or image understanding.

## Models Used

This project uses GGUF model files with `llama-cpp-python`:

### 1. Phi-3-mini-4k-instruct

- File: `Phi-3-mini-4k-instruct-q4.gguf`
- Purpose: Text-only chat and general questions.
- Behavior: Loaded when the application starts.
- Context size: 4096 tokens.

### 2. Moondream2 text model

- File: `moondream2-text-model-f16.gguf`
- Purpose: Generates responses for image-related prompts.
- Behavior: Loaded only when the first image is sent, so the application does not load the vision model unnecessarily.
- Context size: 2048 tokens.

### 3. Moondream2 vision projector

- File: `moondream2-mmproj-f16.gguf`
- Purpose: Connects the image input to the Moondream2 text model.
- This is the image-understanding component used together with the Moondream2 text model.

The Moondream2 text model and vision projector work together. Both files are required for image analysis.

## Why the `models` Folder Is Not Included on GitHub

The model files are very large compared with normal source-code files. GitHub has repository and individual-file size limits, and large model binaries can make cloning, pushing, and version control slow or fail completely. For that reason, the `models/` folder is intentionally excluded from the GitHub repository.

The source code is still complete, but each user must download the model files separately and place them in the expected local folders before running the application.

Do not commit the model files to GitHub. Use the official model hosting pages, such as the relevant Hugging Face repositories, to obtain the files and follow their model licenses and usage terms.

## Expected Local Folder Structure

After downloading the model files, arrange them like this:

```text
Offline_Chatbot/
├── index.html
├── main.py
├── requirements.txt
└── models/
    ├── Phi-3-mini-4k-instruct-q4.gguf
    └── vision2/
        ├── moondream2-text-model-f16.gguf
        └── moondream2-mmproj-f16.gguf
```

The filenames and folder names must match this structure because `main.py` uses these paths:

```text
models/Phi-3-mini-4k-instruct-q4.gguf
models/vision2/moondream2-text-model-f16.gguf
models/vision2/moondream2-mmproj-f16.gguf
```

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer recommended
- Enough RAM and disk space for the downloaded model files
- A working C/C++ build environment may be required by `llama-cpp-python` on some systems

## Installation

1. Clone or download this repository.

2. Create and activate a virtual environment:

   **Windows PowerShell:**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download the three model files from their official model pages and place them in the folder structure shown above.

5. Start the application:

   ```bash
   python main.py
   ```

## How It Works

- `index.html` provides the chat interface.
- `pywebview` displays the interface as a desktop window and exposes Python methods to JavaScript.
- `main.py` loads Phi-3 for normal text messages.
- When an image is selected, the image is converted to a clean JPEG data URL before inference.
- The Moondream2 model is initialized only when image analysis is first requested.
- `reset_chat()` clears the current text conversation history.

## Troubleshooting

### Model file not found

Check that the filenames and folders exactly match the expected structure. Start the application from the project directory:

```bash
python main.py
```

### Image analysis fails

Confirm that both Moondream2 files are present:

```text
models/vision2/moondream2-text-model-f16.gguf
models/vision2/moondream2-mmproj-f16.gguf
```

### Installation problems with `llama-cpp-python`

Upgrade packaging tools and try again:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

The exact installation command can depend on the operating system, Python version, and whether CPU or GPU acceleration is being used.

## Privacy

The application is designed for local inference. Prompts and images are processed by the local model files and are not sent to a hosted chatbot API by this project.

## License and Model Terms

This repository's source code and the downloaded models may have different licenses. Review the license for each model on its official download page before redistributing or packaging the model files.
