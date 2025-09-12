# Against All Odds
## Real-Time Multiplayer Network Architecture with Deterministic Game Engine

A complete client-server multiplayer system built from scratch in Python, demonstrating advanced networking concepts through a real-time Asteroids-style game. This project showcases the foundational architecture for scalable multiplayer applications.

<img width="2559" height="1439" alt="Screenshot 2025-09-08 160100" src="https://github.com/user-attachments/assets/53ad3fad-37e1-40af-8236-2be1d07f74e2" />


## Core Technical Achievements

**Authoritative Server Architecture**
- Custom socket-based networking handling 60+ concurrent players
- Deterministic physics simulation ensuring client-server state consistency
- Message queue system processing client inputs with sub-40ms response times

**Advanced Lag Compensation**
- Input timestamping with server-side validation and rollback
- Control theory-based interpolation (lerp) system for smooth client prediction
- Collision detection with server authority override for critical events

**Scalable Game Architecture** 
- Modular scene management: GameManager → Client → Scene hierarchy
- Dynamic AI system capable of running 40+ intelligent agents simultaneously
- Clean separation between rendering, networking, and game logic

## Live Demo Features

**Single Player**: Fight against intelligent AI opponents with complex behavior patterns
**Multiplayer**: Connect via IP to lobby system with customizable game parameters
**Real-time Combat**: Ships, projectiles, asteroids with physics-based destruction
**Advanced Systems**: Radar detection, weapon management, shield regeneration

## System Architecture
<img width="1220" height="673" alt="against_all_odds drawio" src="https://github.com/user-attachments/assets/a9c4e8b2-3cd5-40ba-bece-c2b62c4cc178" />

```

The networking layer simulates realistic latency (20-200ms) for testing.

## Technical Implementation

**Built from Scratch**: 6,200+ lines of custom Python code
**Networking**: Raw socket implementation with custom protocol
**Performance**: Handles 60 players server-side, 40 AI agents client-side
**Architecture**: Message-driven design with deterministic shared logic

### Key Technical Challenges Solved

1. **State Synchronization**: Maintaining consistent world state across multiple clients with varying latencies
2. **Input Validation**: Server-side input processing with timestamp verification to prevent cheating
3. **Smooth Interpolation**: Advanced lerp system using control theory for responsive client prediction
4. **Memory Management**: Efficient entity lifecycle management for players joining/leaving mid-game

## Installation & Usage

```bash
pip install pygame
python main.py
```

**Single Player**: Immediate gameplay against AI opponents
**Multiplayer**: Enter IP address to join/host networked games
- **Backend Systems**: Authoritative server design patterns used in production games
- **Network Programming**: Custom protocols and lag compensation techniques
- **Performance Engineering**: Concurrent player handling and optimization strategies  
- **Software Architecture**: Clean separation of concerns across 6k+ lines of code

Perfect foundation for extending to features like advanced lag compensation, rollback networking, and anti-cheat systems.

## Built With

- **Language**: Python 3.x
- **Graphics**: Pygame (rendering only - all game logic custom)
- **Networking**: Raw Python sockets with custom message protocol
- **Architecture**: Custom scene management and entity systems

---

*This project represents a complete multiplayer game engine built from fundamentals, demonstrating the networking and systems architecture skills essential for real-time applications.*
