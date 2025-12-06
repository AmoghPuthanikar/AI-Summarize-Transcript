# AI Transcription & Summarization Tool

A local, privacy-focused web application that uses advanced AI models to transcribe, differentiate speakers (diarization), and summarize audio/video content.

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed on your Windows system:

1.  **Python 3.8 to 3.11** (3.12 may have compatibility issues with some ML libraries)
    - [Download Python](https://www.python.org/downloads/)
2.  **MongoDB Community Server** (for database)
    - [Download MongoDB](https://www.mongodb.com/try/download/community)
    - Run the installer and ensure "Install MongoDB as a Service" is checked.
3.  **FFmpeg** (Required for processing audio files)
    - [Download FFmpeg](https://ffmpeg.org/download.html)
    - **Important**: You must add the `bin` folder of FFmpeg to your System PATH environment variable.
    - Type `ffmpeg -version` in CMD to verify.
4.  **NVIDIA CUDA Toolkit** (Optional, for GPU acceleration)
    - If you have an NVIDIA GPU, install CUDA 11.8 or 12.1 to speed up transcription by 10x-50x.
    - [Download CUDA](https://developer.nvidia.com/cuda-downloads)

## 🛠️ Installation Guide

1.  **Clone or Download the Project**

    ```powershell
    # Navigate to the project directory
    cd "path\to\AI-summerizztion"
    ```

2.  **Create a Virtual Environment**
    It's properly isolated dependencies.

    ```powershell
    # Create venv
    python -m venv venv

    # Activate venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```powershell
    pip install -r requirements.txt
    ```

4.  **Install PyTorch (GPU Version)**
    The default `pip install` might install the CPU version. To enable GPU support:

    ```powershell
    # For CUDA 11.8
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    # OR for CUDA 12.1
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```

5.  **HuggingFace Token (Optional)**
    For Speaker Diarization (`pyannote.audio`):
    - Create a `.env` file in the root.
    - Add: `HF_TOKEN=your_huggingface_token`
    - (Required only if you want to use gated models, though standard models might work without it).

## 🚀 How to Run

1.  **Start MongoDB**

    - It usually runs automatically as a Windows Service.
    - If not, start it manually: `net start MongoDB`.

2.  **Run the Application**
    Make sure your virtual environment is active (`(venv)` shows in terminal).

    ```powershell
    python app.py
    ```

3.  **Access the App**
    - Open your browser and go to: `http://127.0.0.1:5000`

## ⚠️ Common Issues & Fixes

- **`FileNotFoundError: [WinError 2] The system cannot find the file specified`**:
  - This means **FFmpeg** is missing or not in PATH. Install FFmpeg and add it to System Variables.
- **Application Crashing on Large Files**:
  - Ensure you have enough RAM (8GB+ recommended).
- **"Object of type ObjectId is not JSON serializable"**:
  - This bug was fixed in V1.0. If you see it, restart the server.

---

**Version**: 1.0
**Author**: Antigravity Agent
