# YOLO Vehicle Detection and Safety System

This project implements a vehicle detection and safety system using YOLO (You Only Look Once) for real-time object detection and various models for risk analysis and vehicle speed prediction.

## Project Structure

- **src/**: Contains the main application code.
  - **rhinomain.py**: Main entry point for the application.
  - **models/**: Contains model definitions and trained weights.
    - **risk_seq_model.py**: LSTM model for risk prediction.
    - **velocity_model.py**: Model for predicting vehicle speed.
  - **detection/**: Implements vehicle detection and tracking.
    - **yolo_detector.py**: YOLO detection logic.
    - **vehicle_tracker.py**: Logic for tracking detected vehicles.
  - **sensors/**: Handles sensor data and camera input.
    - **serial_handler.py**: Communication with serial devices.
    - **camera_handler.py**: Manages camera input.
  - **safety/**: Analyzes risk levels and detects collisions.
    - **risk_analyzer.py**: Risk level analysis.
    - **collision_detector.py**: Collision detection logic.
  - **utils/**: Utility functions and configuration management.
    - **config.py**: Configuration management utilities.
    - **helpers.py**: Helper functions.

- **models/**: Contains trained model weights and YOLOv8 model.
  - **risk_seq_model.pth**: Weights for the risk sequence model.
  - **velocity_model.pth**: Weights for the velocity model.
  - **yolov8n.pt**: Pre-trained YOLOv8 model weights.

- **data/**: Contains test videos and calibration data.
  - **test_videos/**: Directory for test video files.
  - **calibration/**: Directory for calibration data.

- **configs/**: Configuration files for models and system settings.
  - **model_config.yaml**: Model configuration settings.
  - **system_config.yaml**: System-level configuration settings.

- **requirements.txt**: Lists project dependencies.

- **setup.py**: Packaging and installation management.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd yolo
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the necessary models in the `models/` directory.

## Usage

Run the main application:
```
python src/rhinomain.py
```

The system will start processing video input and analyzing vehicle data for safety and risk assessment.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.