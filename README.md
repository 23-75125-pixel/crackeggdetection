# EggGuard Pro - Egg Crack Detection System

An intelligent egg crack detection system using YOLOv8 computer vision and IoT integration for automated egg sorting.

## Features

- **Real-time Detection**: YOLOv8-based computer vision for accurate egg classification
- **Web Dashboard**: Live video feed and real-time statistics
- **Hardware Integration**: Arduino and ESP32 controller support for automated sorting
- **Detection History**: Track all detected eggs with timestamps and confidence scores
- **FPS Monitoring**: Real-time frame rate monitoring

## Project Structure

```
crackeggdetection/
├── app.py                      # Flask web application
├── main.py                     # Entry point
├── best.pt                     # YOLOv8 trained model
├── templates/
│   └── index.html             # Web dashboard
├── static/                    # Static assets (CSS, JS)
├── arduini_controller.ino      # Arduino sketch
├── esp32_controller.ino        # ESP32 sketch
├── eggcrackdetection.ipynb    # Jupyter notebook (training/data exploration)
└── requirements.txt            # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- Webcam/Camera
- Arduino or ESP32 (optional, for motor control)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd crackeggdetection
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Application

```bash
python main.py
```

The web dashboard will be available at `http://localhost:5000`

### Web Interface

- **Start Button**: Begin egg detection
- **Stop Button**: Stop detection
- **Reconnect Button**: Attempt to reconnect camera
- **Reset Button**: Clear statistics

### Hardware Configuration

#### Arduino Setup
- Edit `arduini_controller.ino` with your pin configuration
- Connect via USB (default: `/dev/ttyUSB0`)
- Upload sketch to Arduino board

#### ESP32 Setup
- Edit `esp32_controller.ino` with your WiFi credentials
- Update IP address in `app.py` (line 18): `ESP32_IP = "http://192.168.x.x/cracked"`
- Upload sketch to ESP32 board

## Configuration

### Model Path
Update `MODEL_PATH` in `app.py`:
```python
MODEL_PATH = "/path/to/best.pt"
```

### Camera Settings
```python
FRAME_W = 640      # Frame width
FRAME_H = 480      # Frame height
TARGET_FPS = 30    # Target frames per second
```

### Hardware Connection
```python
# Arduino serial connection
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# ESP32 HTTP endpoint
ESP32_IP = "http://192.168.1.50/cracked"
```

## API Endpoints

- `GET /` - Web dashboard
- `GET /video_feed` - Live video stream
- `POST /start_detection` - Start detection
- `POST /stop_detection` - Stop detection
- `GET /get_stats` - Get current statistics
- `POST /reset_stats` - Reset statistics
- `POST /reconnect_camera` - Attempt camera reconnection

## Troubleshooting

### Camera not detected
- Check your webcam connection
- Use `reconnect_camera` button to retry
- Verify camera permissions on your system

### Arduino/ESP32 not responding
- Check USB/network connection
- Verify IP address (ESP32)
- Check baud rate matches (Arduino default: 9600)

### Model not loading
- Ensure `best.pt` exists at specified path
- Check file is not corrupted
- Verify sufficient disk space

## System Requirements

- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB+
- **GPU**: NVIDIA GPU recommended (CUDA support)
- **Storage**: 1GB+ for model and dependencies

## Dependencies

See `requirements.txt` for complete list:
- Flask 2.3.3
- opencv-python 4.8.0
- ultralytics 8.0.190
- requests 2.31.0
- pyserial 3.5
- numpy 1.24.3

## License

[Add your license here]

## Author

[Your name/organization]

## Support

For issues and questions, please contact [your contact info]
