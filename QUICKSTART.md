# BitNet Quick Start Guide

Get BitNet running in minutes with these simple commands!

## One-Command Build

### For Linux/macOS:
```bash
bash build.sh
```

### For Windows:
```bash
build.bat
```

### Cross-Platform (any OS):
```bash
python build.py
```

That's it! The build script will:
1. ✓ Install Python dependencies
2. ✓ Generate optimized kernels for your CPU
3. ✓ Compile the entire project
4. ✓ Download the model (optional)

---

## Build Script Options

### Python Build Script (Recommended)

```bash
# Basic build with defaults
python build.py

# Build with specific model
python build.py --model 1bitLLM/bitnet_b1_58-large

# Skip model download (build only)
python build.py --skip-model

# Use multiple threads for compilation
python build.py --threads 8

# Skip installing dependencies
python build.py --skip-deps
```

### Bash Build Script (Linux/macOS)

```bash
# Basic build
bash build.sh

# Build without model download
bash build.sh --skip-model

# Build with specific model
bash build.sh --model 1bitLLM/bitnet_b1_58-large
```

### Windows Batch Script

```cmd
# Basic build
build.bat

# Build without model download
build.bat --skip-model

# Build with specific model
build.bat --model 1bitLLM/bitnet_b1_58-large
```

---

## Supported Models

- `microsoft/BitNet-b1.58-2B-4T` (default, 2.4B params, ~5GB)
- `1bitLLM/bitnet_b1_58-large` (700M params)
- `1bitLLM/bitnet_b1_58-3B` (3.3B params)
- `HF1BitLLM/Llama3-8B-1.58-100B-tokens` (8B params)
- `tiiuae/Falcon3-1B-Instruct-1.58bit` (1B params)
- `tiiuae/Falcon3-3B-Instruct-1.58bit` (3B params)
- `tiiuae/Falcon3-7B-Instruct-1.58bit` (7B params)
- `tiiuae/Falcon3-10B-Instruct-1.58bit` (10B params)

---

## After Building

### Run Inference
```bash
python run_inference.py -p "What is machine learning?"
```

### Start Server
```bash
python run_inference_server.py
```

Then access the API at `http://127.0.0.1:8080/`

### Run Benchmark
```bash
python utils/e2e_benchmark.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf
```

---

## Requirements

- **Python**: >= 3.9
- **CMake**: >= 3.22
- **Clang**: >= 18
- **Git**: for submodule support

### Installation Instructions

#### Windows (with Visual Studio 2022)
In Visual Studio Installer, toggle:
- Desktop development with C++
- C++ CMake tools for Windows
- Clang compiler for Windows
- LLVM-Toolset MS-Build Support

#### macOS (with Homebrew)
```bash
brew install cmake clang llvm
```

#### Linux (Debian/Ubuntu)
```bash
curl https://apt.llvm.org/llvm.sh | bash
sudo apt-get install cmake
```

---

## Troubleshooting

### Build fails with CMake error
- Ensure `clang` is installed and in PATH
- Try: `clang --version`

### Python dependencies fail to install
- Try: `python -m pip install --upgrade pip`
- Run: `python -m pip install -r requirements.txt`

### Model download fails
- Download manually from HuggingFace
- Place in `models/` directory
- Use `--skip-model` flag when building

### Performance tips
- Use `--threads N` with N = number of CPU cores
- For ARM: optimal for Apple Silicon and Snapdragon
- For x86: optimal for Intel and AMD

---

## Manual Build (Advanced)

If the build scripts don't work, you can build manually:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt
pip install 3rdparty/llama.cpp/gguf-py

# 2. Download model
huggingface-cli download microsoft/BitNet-b1.58-2B-4T --local-dir models/BitNet-b1.58-2B-4T

# 3. Setup environment
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# 4. Compile
cmake -B build -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build --config Release

# 5. Run
python run_inference.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -p "Hello"
```

---

## Documentation

- **Setup Details**: See [README.md](README.md)
- **Optimization Guide**: See [src/README.md](src/README.md)
- **GPU Support**: See [gpu/README.md](gpu/README.md)
- **Technical Paper**: https://arxiv.org/abs/2410.16144

---

**Questions?** Check the FAQ in README.md or open an issue on GitHub.
