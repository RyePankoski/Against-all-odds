# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Running the Game:**
```bash
python game/main.py
```

**Running Tests:**
```bash
python -m pytest tests/
python tests/test_ship.py  # Run single test
```

**Performance Profiling:**
The main.py automatically runs cProfile profiler and outputs performance stats on exit.

## Architecture Overview

This is a real-time multiplayer Asteroids-style game built from scratch with custom networking. The architecture follows a client-server model with authoritative server design.

### Core Components

**Game Manager (game/game_manager.py):**
- Central state machine handling game flow: splash → menu → single_player/multiplayer → lobby → game
- Manages both client and server instances when hosting
- Handles input collection and state transitions
- Contains networking client logic for multiplayer connections

**Server (game/server.py):**
- UDP socket-based server on port 4242
- Handles lobby management and player connections
- Runs authoritative game simulation via ServerMainScene
- Manages player list synchronization

**Scene Architecture:**
- **Client Scenes** (client_scenes/): MainScene, MainMenu, Lobby, PauseMenu, etc.
- **Server Scenes** (server_scenes/): ServerMainScene for authoritative game logic
- Scenes are swappable components handling specific game states

**Entity System:**
- **entities/ships/**: Player ships, AI ships, battleships
- **entities/projectiles/**: Bullets, rockets with physics
- **entities/world_entities/**: Asteroids and world objects

**Rendering System:**
- **rendering/**: Camera system, sprite management, sound management
- Completely separate from game logic for clean client-server separation

### Key Technical Features

**Networking:**
- Custom UDP protocol with JSON message serialization
- Input timestamping and lag compensation system
- Deterministic shared logic between client and server
- Network simulation for testing latency (networking/network_simulator.py)

**Input System:**
- Discrete vs continuous input handling in collect_inputs()
- Input validation and rollback for multiplayer
- Mouse world position calculation via camera transforms

**AI System:**
- Intelligent AI agents in game/ai.py
- Can run 40+ concurrent AI entities

**Configuration:**
- All game constants in game/settings.py (colors, world dimensions, physics parameters)
- Modular design allows easy tweaking of game balance

### Development Patterns

**State Management:**
- Game state flows: splash → menu → [single_player | create_server | join_server] → lobby → in_game
- Server has separate state: lobby → in_game

**Networking Protocol:**
- Connection: JSON message with 'type': 'connect' and 'player_name'
- Game input: JSON with input data and timestamp
- Server responses: Player lists and game state updates

**Error Handling:**
- Socket timeouts and non-blocking I/O
- Connection failure recovery with cleanup
- Graceful handling of malformed JSON messages

### File Organization

- `game/`: Core game logic and main entry point
- `client_scenes/`: Client-side game states and UI
- `server_scenes/`: Server-side authoritative game logic  
- `entities/`: Game objects (ships, projectiles, world entities)
- `rendering/`: Graphics, camera, and audio systems
- `networking/`: Network utilities and simulation
- `ui_components/`: Reusable UI elements
- `shared_util/`: Utilities shared between client and server
- `lookup_tables/`: Precomputed data for performance
- Asset directories: `ship_sprites/`, `weapon_sprites/`, `ui_art/`, `sounds/`, `fonts/`

This architecture demonstrates production-ready multiplayer game development patterns with clean separation of concerns, deterministic simulation, and robust networking.