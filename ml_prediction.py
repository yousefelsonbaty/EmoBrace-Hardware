import joblib  # Use joblib for loading the scaler
import warnings
import time
import datetime
import board
import busio
import numpy as np
import pandas as pd
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Load the emotion prediction model
try:
    with open("final_emotion_model.pkl", "rb") as model_file:
        emotion_model = joblib.load(model_file)
except FileNotFoundError:
    raise FileNotFoundError("The file 'final_emotion_model.pkl' was not found. Ensure the model file is in the correct directory.")
except Exception as e:
    raise RuntimeError(f"An error occurred while loading the model: {e}")

# Load the scaler
try:
    scaler = joblib.load("scaler.pkl")
except FileNotFoundError:
    raise FileNotFoundError("The file 'scaler.pkl' was not found. Ensure the scaler file is in the correct directory.")
except Exception as e:
    raise RuntimeError(f"An error occurred while loading the scaler: {e}")

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115 directly on the I2C bus
ads = ADS.ADS1115(i2c)
ads.gain = 1  # Set gain for ADC
time.sleep(0.5)  # Allow ADC to stabilize

# Initialize LM35 temperature sensor (using A1 channel on ADS1115)
lm35 = AnalogIn(ads, ADS.P1)
time.sleep(0.5)

# Initialize AD8232 (ECG Sensor) using ADS1115 (using A0 channel)
ad8232 = AnalogIn(ads, ADS.P0)
time.sleep(0.5)

# Initialize GSR Sensor using ADS1115 (using A2 channel)
gsr_sensor = AnalogIn(ads, ADS.P2)
time.sleep(0.5)

# Define a mapping from numeric labels to emotion strings
label_to_emotion = {
    0: "Happy",
    1: "Sad",
    2: "Neutral",
    3: "Angry",
    4: "Anxious",
    5: "Stressed"
}

# Define emotions and their corresponding suggestions
suggestions = {
    "Happy": "Keep enjoying the moment!",
    "Sad": "Take some time to relax and focus on yourself.",
    "Neutral": "Maintain your calm and steady approach.",
    "Angry": "Take deep breaths and try stepping away.",
    "Anxious": "Focus on your breathing and grounding techniques.",
    "Stressed": "Consider taking short breaks to decompress."
}

# Function to create a composite output of emotion and suggestion
def create_composite_output(emotion_label):
    """Map numeric emotion label to string and return emotion with suggestion."""
    emotion = label_to_emotion.get(int(emotion_label), "Unknown")  # Map label to emotion
    if emotion == "Unknown":
        raise KeyError(f"Invalid emotion label: {emotion_label}")
    return {"Emotion": emotion, "Suggestion": suggestions[emotion]}

def read_temperature():
    """Read temperature from LM35 in Celsius using voltage directly."""
    voltage = lm35.voltage  # Voltage in volts
    temperature_celsius = (voltage * 1000) / 10.0  # Convert voltage to Celsius
    return temperature_celsius

def read_ecg():
    """Read ECG from AD8232."""
    return ad8232.voltage  # Use voltage directly

def read_gsr():
    """Read GSR sensor data."""
    return gsr_sensor.voltage  # Use voltage directly

def predict_output(temperature, ecg, gsr):
    """Predict emotion and suggestion based on sensor readings."""
    # Create input data as a DataFrame with feature names
    input_data = pd.DataFrame([[temperature, ecg, gsr]], columns=["Temperature", "ECG", "GSR"])
   
    # Scale the input data
    scaled_data = scaler.transform(input_data)
   
    # Predict the emotion label
    predicted_emotion_label = emotion_model.predict(scaled_data)[0]
   
    # Create the composite output using the predicted emotion label
    return create_composite_output(predicted_emotion_label)

def collect_data(duration=60, interval=6):
    """Collect sensor data, compute averages, and predict output."""
    start_time = time.time()
    temperature_sum = 0
    ecg_sum = 0
    gsr_sum = 0
    count = 0
   
    try:
        while time.time() - start_time < duration:
            temperature = read_temperature()
            ecg = read_ecg()
            gsr = read_gsr()
           
            temperature_sum += temperature
            ecg_sum += ecg
            gsr_sum += gsr
            count += 1
           
            timestamp = datetime.datetime.now()
           
            print(f"Timestamp: {timestamp}, Temp: {temperature:.2f}°C, ECG: {ecg:.2f}V, GSR: {gsr:.2f}V")
           
            time.sleep(interval)
       
        if count > 0:
            avg_temperature = temperature_sum / count
            avg_ecg = ecg_sum / count
            avg_gsr = gsr_sum / count
           
            output = predict_output(avg_temperature, avg_ecg, avg_gsr)
           
            print(f"Average Temp: {avg_temperature:.2f}°C, Average ECG: {avg_ecg:.2f}V, Average GSR: {avg_gsr:.2f}V, Output: {output}")
           
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting...")
    finally:
        print("Data collection complete.")

if __name__ == "__main__":
    print("Starting data collection...")
    collect_data()