# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Game
```bash
# Start the game
python main.py

# Interactive configuration setup
python main.py config

# Debug mode
python main.py --debug

# Validate configuration
python main.py --validate-config
```

### Testing and Validation
```bash
# Check dependencies
pip list | grep requests

# View logs for debugging
ls -la logs/
tail -50 logs/trpg_game_*.log

# Quick system test
python main.py --help
```

## High-Level Architecture

### Core System Structure
This is an AI-TRPG (Tabletop Role-Playing Game) system built with a modular architecture:

- **Entry Point**: `main.py` - CLI interface with argument parsing
- **Core Engine**: `ai_trpg/core/game_engine.py` - Main game loop and coordination
- **State Management**: `ai_trpg/core/game_state.py` - Game state and history tracking
- **AI Integration**: `ai_trpg/ai/model_client.py` - Unified interface for multiple AI backends
- **Utility Modules**: `ai_trpg/utils/` - Intent analysis, action dispatch, logging

### AI Backend Support
The system supports two AI backends with automatic switching:
- **Ollama**: Local open-source models (32K context, qwen2.5:3b default)
- **LM Studio**: GUI-managed models (128K context, hermes models recommended)

### Configuration System
- **Main Config**: `config/game_config.json` - AI backend, model settings, game parameters
- **Auto-detection**: System automatically adjusts context limits based on chosen backend
- **Interactive Setup**: `python main.py config` provides guided configuration

### Key Game Flow
1. **User Input** → **Intent Analysis** (AI call) → **Action Dispatch** → **Scene Generation** (AI call) → **State Update** → **Display**
2. **Dual AI Architecture**: Separate models for intent analysis and scene generation
3. **Smart Context Management**: Automatically trims history based on model capabilities

## Current Development Status

### Known Issues (Priority fixes needed)
1. **AI Result Avoidance** (`ai_trpg/ai/model_client.py:80-109`): Scene generation AI doesn't provide concrete action results
2. **JSON Parsing**: Fixed but needs testing verification (`ai_trpg/core/game_engine.py:265-306`)

### Development Phases
- **v1.0**: Basic TRPG system (completed)
- **v1.1**: Fix prompt engineering for concrete results
- **v2.0**: RAG integration for long-term memory (planned)

### Important Files for Development
- `ai_trpg/ai/model_client.py` - Core AI prompt engineering
- `ai_trpg/core/game_engine.py` - Main game loop and context handling
- `docs/QUICK_START.md` - Detailed current status and immediate tasks
- `docs/SYSTEM_DESIGN.md` - Complete technical architecture

### Logging and Debugging
- **Log Location**: `logs/trpg_game_YYYYMMDD_HHMMSS.log`
- **Log Levels**: Search for "模型输入", "模型输出", "出错", "意图分类"
- **Context Debugging**: Use `--debug` flag for detailed AI interaction logs

## Code Conventions
- **Language**: Python 3.8+, Chinese comments and documentation
- **Architecture**: Modular design with clear separation of concerns
- **Error Handling**: Comprehensive error catching with user-friendly messages
- **AI Integration**: Always validate config before making API calls
- **State Management**: Immutable state updates with history tracking