# EmoBrace

EmoBrace is a wearable device project designed to monitor physiological signals and predict the user's emotional state. By leveraging sensor data and machine learning, EmoBrace provides real-time emotion detection and personalized suggestions to improve emotional well-being.

## Features

- **Emotion Detection**: Predicts emotions such as Happy, Sad, Neutral, Angry, Anxious, and Stressed using physiological signals.
- **Sensor Integration**: Reads data from:
  - LM35 Temperature Sensor
  - AD8232 ECG Sensor
  - GSR Sensor
- **Machine Learning**: Utilizes a pre-trained model (`final_emotion_model.pkl`) and a scaler (`scaler.pkl`) for emotion prediction.
- **Data Collection**: Collects and stores sensor data for analysis and training.
- **Firebase Integration**: Uploads processed data and predictions to Firestore for real-time storage and analysis.

## Project Structure

```
.gitignore
capstone.py
data_collection.py
google-services.json
ml_prediction.py
serviceAccountKey.json
```

### File Descriptions

- **`capstone.py`**: Main script for real-time data collection, emotion prediction, and uploading results to Firestore.
- **`data_collection.py`**: Script for collecting labeled sensor data and saving it to a CSV file for training purposes.
- **`ml_prediction.py`**: Script for testing the emotion prediction model with live sensor data.
- **`serviceAccountKey.json`**: Firebase service account key for authentication (ignored by .gitignore).
- **`google-services.json`**: Firebase configuration file (ignored by .gitignore).
- **`.gitignore`**: Specifies files to exclude from version control.

## Prerequisites

1. **Hardware**:
   - LM35 Temperature Sensor
   - AD8232 ECG Sensor
   - GSR Sensor
   - ADS1115 ADC Module
   - Raspberry Pi or compatible microcontroller with I2C support

2. **Software**:
   - Python 3.x
   - Required Python libraries (install via `pip`):
     ```
     pip install numpy pandas joblib adafruit-circuitpython-ads1x15 firebase-admin google-cloud-firestore
     ```

3. **Firebase Setup**:
   - Create a Firebase project.
   - Download the `serviceAccountKey.json` and `google-services.json` files and place them in the project directory.

4. **Machine Learning Model**:
   - Ensure `final_emotion_model.pkl` and `scaler.pkl` are in the project directory.
  
## Hardware Design

### Block Diagram

![WhatsApp Image 2025-03-30 at 21 26 15](https://github.com/user-attachments/assets/a04022f0-6343-42a5-9250-15e36f859575)

### Schematic Diagram

![WhatsApp Image 2025-03-30 at 21 26 28](https://github.com/user-attachments/assets/94881702-2641-4d0d-b6d1-300e99224665)

### Wiring Diagram

![WhatsApp Image 2025-03-30 at 21 26 36](https://github.com/user-attachments/assets/78314169-d2be-4e47-9775-2cf8c2cd04b5)

## Usage

### 1. Real-Time Emotion Detection
Run the main script to collect sensor data, predict emotions, and upload results to Firestore:
```bash
python capstone.py
```

### 2. Data Collection for Training
Collect labeled sensor data for training the emotion prediction model:
```bash
python data_collection.py
```

### 3. Test Emotion Prediction
Test the pre-trained model with live sensor data:
```bash
python ml_prediction.py
```

## Emotion Labels and Suggestions

| Emotion   | Suggestion                                      |
|-----------|------------------------------------------------|
| Happy     | Keep enjoying the moment!                      |
| Sad       | Take some time to relax and focus on yourself. |
| Neutral   | Maintain your calm and steady approach.        |
| Angry     | Take deep breaths and try stepping away.       |
| Anxious   | Focus on your breathing and grounding techniques. |
| Stressed  | Consider taking short breaks to decompress.    |

## Notes

- Ensure all hardware components are properly connected before running the scripts.
- The `serviceAccountKey.json` and `google-services.json` files are sensitive and should not be shared publicly.

## Acknowledgments

- Adafruit for the ADS1115 library.
- Firebase for real-time database services.
- Scikit-learn for machine learning tools.## Emotion Labels and Suggestions
