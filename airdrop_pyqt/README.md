# ARCHITECTURE – Wi-Fi P2P Chat App
## WHYSAPP
```css
┌────────────┐       UDP Broadcast       ┌───────────-─┐
│  Device A  │ <---------------------->  │  Device B   │
│            │                           │             │
└─────┬──────┘                           └─────-┬──────┘
      │           TCP / WebSocket               │
      └──────── Direct Communication ───────────┘

```
- No Internet
- No Central Server
- Fully Peer-to-Peer (LAN)

## 1. Application Layers
```css
UI Layer
│
State Management Layer
│
Networking Layer
│
Discovery Layer
│
System / Platform Layer

```

## 2. UI Layer
```css
Splash Screen
↓
Username Setup Screen
↓
Nearby Devices Screen (AirDrop-like)
↓
Chat Screen
```
### Responsibilities:
- Show connected users
- Show messages
- Send text / files
- Display connection status

## 3.State Management Layer

### Use:
Provider / Riverpod / Bloc (your choice)

### Holds:

- List of discovered devices
- Current chat messages
- Connection state

## 4. Discovery Layer (MOST IMPORTANT)

This is what makes your app AirDrop-like.

### How Discovery Works (UDP)
- Each device:
- Sends a broadcast message
- Listens for broadcasts from others

### Discovery Packet (JSON)
```json
{
  "type": "DISCOVER",
  "username": "Ashith",
  "deviceId": "abc123",
  "ip": "192.168.1.5",
  "port": 5000
}

```
### Discovery flow
```json
Every 2 seconds:
  ↓
Send UDP broadcast
  ↓
Receive others’ broadcasts
  ↓
Update nearby users list

```

## 5. Networking Layer (Chat & Files)

### Connection Type
| Feature     | Protocol        |
| ----------- | --------------- |
| Discovery   | UDP             |
| Messaging   | TCP / WebSocket |
| Media files | TCP             |

### TCP Chat Flow
```json
User taps device
↓
TCP socket created
↓
JSON message sent
↓
Receiver parses & displays

```
### Message Format
```json
{
  "type": "TEXT",
  "from": "Ashith",
  "message": "Hello!"
}
```

## 6. File Transfer Architecture (Phase 2)
```json
File
↓
Split into chunks
↓
Send over TCP
↓
Receiver reassembles

```
### File Metadata Packet
```json
{
  "type": "FILE_META",
  "fileName": "image.jpg",
  "fileSize": 245678
}
```
### Chunk Transfer
```json
{
  "type": "FILE_CHUNK",
  "data": "base64_encoded_chunk"
}
```

## 7. Platform Layer (Android + iOS)
Flutter needs native permissions:

### Android
- Local network access
- Wi-Fi state
- Foreground service (optional)

### iOS
- Local Network permission (mandatory)
- Bonjour permission (even for UDP)



## 8. Exact Folder Structure
```json
airdrop_pyqt/
│── main.py
│
├── ui/
│   ├── main_window.py
│   ├── device_tile.py
│   └── chat_window.py
│
├── network/
│   ├── discovery.py      # UDP broadcast
│   ├── server.py         # TCP receiver
│   └── client.py         # TCP sender
│
├── models/
│   └── device.py
│
├── utils/
│   └── system_info.py
│
└── assets/
    └── icons/


```
## 9. Complete Data Flow (End-to-End)
```json
App starts
↓
Discovery service starts UDP broadcast
↓
Nearby users discovered
↓
User selects a device
↓
TCP connection established
↓
Text message sent
↓
Receiver displays message
```
## Main thing to note during development 
- Real desktop app architecture
- Threads & signals
- Network discovery
- Cross-platform packaging

### High-Level Design (Important)
```python
Each device:
 ├─ UDP → discovery (already done)
 ├─ TCP Server → listens for messages
 └─ TCP Client → sends messages
```