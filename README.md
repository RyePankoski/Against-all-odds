# Multiplayer Asteroids

A networked multiplayer asteroids game built in Python with Pygame, featuring deterministic client-server architecture and realistic network simulation.

## Features

### Networking Architecture
- **Authoritative Server**: Server maintains canonical game state with client input validation
- **Deterministic Simulation**: Shared game logic ensures identical calculations on client and server
- **Network Simulation**: Realistic latency modeling (20-40ms) with variable delay for testing
- **Input Timestamping**: Precise timing for lag compensation foundation

### Gameplay
- Real-time multiplayer asteroids with ships, projectiles, and destructible asteroids
- Radar system for detecting nearby objects
- Weapon systems (bullets and missiles) with ammunition management
- Shield and health systems with regeneration mechanics

### Technical Implementation
- Clean separation between client rendering and server authority
- Message-based communication with structured input/state packets
- Collision detection and physics simulation
- Camera system with smooth following

## Architecture

```
Client ←→ NetworkSimulator ←→ Server
   ↓              ↓              ↓
Rendering    Latency Model   Game Logic
Input        Message Queue   State Auth
```

### Key Components
- **Client**: Handles input collection, rendering, and local prediction
- **Server**: Authoritative game state, input processing, collision detection
- **NetworkSimulator**: Realistic network conditions with configurable latency
- **Shared Logic**: Deterministic game rules used by both client and server

## Code Structure

```
├── client.py              # Client-side game logic and rendering
├── server.py              # Authoritative server implementation  
├── entities/
│   └── ship.py            # Ship entity with state management
├── networking/
│   └── network_simulator.py  # Latency simulation and message queue
├── shared_util/           # Deterministic game logic
└── rendering/             # Client-side rendering utilities
```

## Technical Highlights

- **Deterministic Physics**: Identical simulation on client and server prevents desync
- **Network Abstraction**: Clean interface allows easy transition to real networking
- **State Management**: Proper separation of rendering state vs authoritative state
- **Input Handling**: Structured input collection with timing data for future lag compensation

## Running the Game

```bash
python main.py
```

## Technical Notes

This project demonstrates the foundational architecture for advanced networking features like client-side prediction, rollback networking, and lag compensation. The deterministic shared logic and network simulation layer provide a solid base for implementing these features.

The focus was on building robust client-server communication and state synchronization rather than visual polish, making it a strong example of systems programming and network architecture.

## Technologies Used

- **Python 3.x**
- **Pygame** for rendering and input handling
- **Custom networking simulation** for realistic latency testing

---

*Built as a learning project to explore networked game development and client-server architecture.*
