# PBL-Game Copilot Instructions

## Project Overview
This is a Pygame-based educational game combining RPG field exploration with visual novel storytelling to teach high school students about space engineering and astrophysics. The game features scene-based architecture with three main states: title screen, RPG gameplay, and visual novel sequences.

## Architecture
- **Scene Management**: `App` class manages three scenes (SCENE_TITLE=0, SCENE_GAME=1, SCENE_VN=2) via `scene_state`. Each scene has dedicated update/draw logic.
- **Core Components**:
  - `Field`: Handles RPG map rendering, player movement, NPC interactions, and map transitions
  - `Talk`: Manages NPC dialogues and quiz systems with reward mechanics
  - `VisualNovel`: Controls VN sequences with background/character images and text windows
  - `System`: Provides save/load functionality and BGM control
- **Data Flow**: Pygame event loop → `_handle_events()` → `_update()` → `_draw()` per frame

## Key Workflows
- **Run Game**: `python -m src.main` (requires Python 3.13.9 + Pygame 2.6.1)
- **Save/Load**: Press 'S' in game to save to `save.json`; auto-loads on startup
- **Debug**: Check console for JSON load errors; use `traceback` in `main.py` for exceptions

## Coding Patterns
- **Resource Loading**: Use `resource_path()` from `utils.py` for cross-platform asset paths (e.g., `resource_path("assets/img/title.jpg")`)
- **Input Handling**: Use `KeyTracker` for press-once detection; keys mapped as `{"z": advance, "q": quit, "up/down": navigate}`
- **Data Management**: Store game data in JSON files under `assets/data/`; use `load_json()`/`save_json()` for persistence
- **UI Rendering**: Draw text windows with `draw_window()` from `ui.py`; position at bottom (320-448 y-coords)
- **Quiz System**: In `Talk`, handle multiple choice with arrow keys; correct answers add items to `app.items` list

## Integration Points
- **Asset Dependencies**: Images in `assets/img/`, sounds in `assets/sounds/`, data in `assets/data/`
- **External Libraries**: Pygame for graphics/audio; no web APIs or databases
- **Cross-Component Communication**: Components access shared `app` instance for state (e.g., `self.app.items`, `self.app.scene_state`)

## Examples
- Add new dialogue: Edit `assets/dialogues/dialogues.json` with quiz options and rewards
- Modify VN script: Update `assets/data/novel_scripts.json` with background/char image paths
- Extend inventory: Items stored as strings in `app.items`; display in game UI with comma separation