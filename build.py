#!/usr/bin/env python3
"""
BitNet Build Script - Simple one-command build for all platforms
Usage: python build.py [--model MODEL_NAME] [--skip-model] [--threads N]
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("bitnet-build")

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.GREEN}{'='*50}{Colors.END}")
    print(f"{Colors.GREEN}{text:^50}{Colors.END}")
    print(f"{Colors.GREEN}{'='*50}{Colors.END}\n")

def run_cmd(cmd, description, log_file=None):
    """Run a command and handle errors."""
    logger.info(f"Running: {description}")
    try:
        if log_file:
            with open(log_file, 'w') as f:
                subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT, shell=isinstance(cmd, str))
        else:
            subprocess.run(cmd, check=True)
        logger.info(f"✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed")
        if log_file and os.path.exists(log_file):
            logger.error(f"See logs: {log_file}")
        return False
    except Exception as e:
        logger.error(f"✗ {description} failed: {e}")
        return False

def check_requirements():
    """Check if required tools are installed."""
    logger.info("Checking requirements...")
    
    required = {
        "cmake": ["cmake", "--version"],
        "python": ["python", "--version"],
    }
    
    # Check for C++ compiler (clang or MSVC)
    compiler_found = False
    compiler_name = None
    
    for compiler_cmd in ["clang", "clang-cl", "cl"]:
        try:
            subprocess.run([compiler_cmd, "--version"], capture_output=True, check=True, timeout=5)
            compiler_found = True
            compiler_name = compiler_cmd
            logger.info(f"Found C++ compiler: {compiler_cmd}")
            break
        except:
            pass
    
    if not compiler_found:
        logger.error("No C++ compiler found (need clang, clang-cl, or MSVC cl)")
        logger.error("Please install Visual Studio with C++ tools or install LLVM Clang")
        return False
    
    missing = []
    for tool, cmd in required.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except:
            missing.append(tool)
    
    if missing:
        logger.error(f"Missing required tools: {', '.join(missing)}")
        logger.error("Please install them and try again.")
        return False
    
    logger.info("✓ All requirements met")
    return True, compiler_name

def setup_logging(log_dir):
    """Setup logging directory."""
    Path(log_dir).mkdir(exist_ok=True)
    return log_dir

def main():
    parser = argparse.ArgumentParser(
        description='BitNet One-Command Build',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                           # Build with default model
  python build.py --model 1bitLLM/bitnet_b1_58-large  # Build specific model
  python build.py --skip-model              # Build without downloading model
  python build.py --threads 4               # Use 4 threads for compilation
        """
    )
    
    parser.add_argument('--model', default='microsoft/BitNet-b1.58-2B-4T',
                       help='HuggingFace model to use (default: microsoft/BitNet-b1.58-2B-4T)')
    parser.add_argument('--skip-model', action='store_true',
                       help='Skip model download')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip installing Python dependencies')
    parser.add_argument('--threads', type=int, default=None,
                       help='Number of threads for compilation')
    parser.add_argument('--log-dir', default='logs',
                       help='Directory for logs')
    
    args = parser.parse_args()
    log_dir = setup_logging(args.log_dir)
    
    print_header("BitNet Build Script")
    logger.info(f"Model: {args.model}")
    logger.info(f"Log directory: {log_dir}")
    
    # Check requirements
    requirements = check_requirements()
    if isinstance(requirements, bool) and not requirements:
        return 1
    elif isinstance(requirements, tuple):
        _, compiler_name = requirements
    else:
        return 1
    
    # Step 1: Install Python dependencies
    if not args.skip_deps:
        logger.info("\n[1/4] Installing dependencies...")
        req_file = Path("3rdparty/llama.cpp/gguf-py")
        if req_file.exists():
            if not run_cmd([sys.executable, "-m", "pip", "install", str(req_file)],
                          "Installing GGUF package",
                          os.path.join(log_dir, "install_deps.log")):
                logger.warning("Failed to install GGUF, continuing anyway...")
        else:
            logger.warning(f"GGUF directory not found: {req_file}")
    else:
        logger.info("\n[1/4] Skipping dependency installation")
    
    # Step 2: Generate kernels
    logger.info("\n[2/4] Generating optimized kernels...")
    if not run_cmd([sys.executable, "setup_env.py", "--hf-repo", args.model],
                  "Generating kernels",
                  os.path.join(log_dir, "codegen.log")):
        logger.warning("Kernel generation had issues, but continuing...")
    
    # Step 3: Compile
    logger.info("\n[3/4] Compiling BitNet...")
    
    build_dir = "build"
    
    # Detect compiler and set appropriate flags
    if compiler_name in ["clang", "clang-cl"]:
        cmake_cmd = [
            "cmake", "-B", build_dir,
            "-DCMAKE_C_COMPILER=clang",
            "-DCMAKE_CXX_COMPILER=clang++",
            "-DCMAKE_BUILD_TYPE=Release",
        ]
    else:
        # Use MSVC (Visual Studio generator)
        logger.info("Using MSVC compiler (Visual Studio)")
        cmake_cmd = [
            "cmake", "-B", build_dir,
            "-G", "Visual Studio 17 2022",
        ]
    
    if not run_cmd(cmake_cmd,
                  "Generating CMake build files",
                  os.path.join(log_dir, "cmake_gen.log")):
        logger.error("CMake configuration failed")
        return 1
    
    build_cmd = ["cmake", "--build", build_dir, "--config", "Release"]
    if args.threads:
        build_cmd.extend(["--parallel", str(args.threads)])
    
    if not run_cmd(build_cmd,
                  "Compiling",
                  os.path.join(log_dir, "compile.log")):
        logger.error("Compilation failed")
        return 1
    
    # Step 4: Download model
    if not args.skip_model:
        logger.info("\n[4/4] Downloading model...")
        if not run_cmd([sys.executable, "setup_env.py", "--hf-repo", args.model,
                       "--model-dir", "models"],
                      "Downloading model",
                      os.path.join(log_dir, "download_model.log")):
            logger.warning("Model download failed (you can download later)")
    else:
        logger.info("\n[4/4] Skipping model download")
    
    # Success!
    print_header("Build Complete! 🎉")
    logger.info("Next steps:")
    logger.info("  1. Run inference:")
    logger.info("     python run_inference.py -p 'Your prompt here'")
    logger.info("")
    logger.info("  2. Start server:")
    logger.info("     python run_inference_server.py")
    logger.info("")
    logger.info(f"Logs saved in: {log_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
