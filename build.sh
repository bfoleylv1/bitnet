#!/bin/bash
# Simple BitNet build script - One command to build everything!
# Usage: ./build.sh [--model MODEL_NAME] [--skip-model]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Defaults
MODEL="microsoft/BitNet-b1.58-2B-4T"
SKIP_MODEL=false
LOG_DIR="logs"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL="$2"
            shift 2
            ;;
        --skip-model)
            SKIP_MODEL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--model MODEL_NAME] [--skip-model]"
            exit 1
            ;;
    esac
done

mkdir -p "$LOG_DIR"

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     BitNet Build Script (One-Command)     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Install GGUF package
echo -e "${YELLOW}[1/4] Installing GGUF package...${NC}"
if python -m pip install 3rdparty/llama.cpp/gguf-py > "$LOG_DIR/install_gguf.log" 2>&1; then
    echo -e "${GREEN}✓ GGUF installed${NC}"
else
    echo -e "${RED}✗ Failed to install GGUF${NC}"
    cat "$LOG_DIR/install_gguf.log"
    exit 1
fi

# Step 2: Generate code
echo -e "${YELLOW}[2/4] Generating optimized kernels...${NC}"
if python setup_env.py --hf-repo "$MODEL" --skip-download 2>&1 | tee "$LOG_DIR/codegen.log"; then
    echo -e "${GREEN}✓ Kernels generated${NC}"
else
    echo -e "${RED}✗ Failed to generate kernels${NC}"
    exit 1
fi

# Step 3: Compile
echo -e "${YELLOW}[3/4] Compiling with CMake...${NC}"
if cmake -B build \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Release > "$LOG_DIR/cmake_gen.log" 2>&1 && \
   cmake --build build --config Release > "$LOG_DIR/compile.log" 2>&1; then
    echo -e "${GREEN}✓ Compilation successful${NC}"
else
    echo -e "${RED}✗ Compilation failed${NC}"
    cat "$LOG_DIR/compile.log"
    exit 1
fi

# Step 4: Download model (optional)
if [ "$SKIP_MODEL" = false ]; then
    echo -e "${YELLOW}[4/4] Downloading model...${NC}"
    if python setup_env.py --hf-repo "$MODEL" --model-dir models 2>&1 | tee "$LOG_DIR/download_model.log"; then
        echo -e "${GREEN}✓ Model downloaded${NC}"
    else
        echo -e "${YELLOW}⚠ Model download skipped or failed (you can download later)${NC}"
    fi
else
    echo -e "${YELLOW}[4/4] Skipping model download${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Build Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Run inference:"
echo "     python run_inference.py -p 'Your prompt here'"
echo ""
echo "  2. Start server:"
echo "     python run_inference_server.py"
echo ""
echo -e "${YELLOW}Logs saved in: $LOG_DIR/${NC}"
