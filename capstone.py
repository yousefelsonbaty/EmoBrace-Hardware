import os
import json
import requests
import firebase_admin
import time
import datetime
import board
import busio
import joblib
import numpy as np
import pandas as pd
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from firebase_admin import credentials, auth
from google.cloud import firestore

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

# Firebase Authentication Setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/joe/Downloads/Capstone/serviceAccountKey.json"
db = firestore.Client()

cred = credentials.Certificate("/home/joe/Downloads/Capstone/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

auth_url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=INSERT_API_KEY_HERE'

data = {
    "email": "john.doe@example.com",
    "password": "123",
    "returnSecureToken": True
}

response = requests.post(auth_url, data=json.dumps(data))

if response.status_code == 200:
    id_token = response.json()['idToken']
    decoded_token = auth.verify_id_token(id_token)
    user_id = decoded_token['uid']
    print("User ID:", user_id)
else:
    print(response.json()['error']['message'])
    user_id = None

# Define emotion labels and suggestions
label_to_emotion = {
    0: "Happy",
    1: "Sad",
    2: "Neutral",
    3: "Angry",
    4: "Anxious",
    5: "Stressed"
}

suggestions = {
    "Happy": "Keep enjoying the moment!",
    "Sad": "Take some time to relax and focus on yourself.",
    "Neutral": "Maintain your calm and steady approach.",
    "Angry": "Take deep breaths and try stepping away.",
    "Anxious": "Focus on your breathing and grounding techniques.",
    "Stressed": "Consider taking short breaks to decompress."
}

# Function to create a composite output of emotion and suggestion
def create_composite_output(emotion):
    return {"Emotion": emotion, "Suggestion": suggestions[emotion]}

def read_temperature():
    """Read temperature from LM35."""
    voltage = lm35.voltage  # Read voltage from LM35
    temperature = (voltage * 1000) / 10.0  # Convert voltage to temperature in Celsius
    return temperature

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
    return create_composite_output(label_to_emotion[predicted_emotion_label])

def collect_data_and_save_to_firestore(duration=60, interval=6):
    """Collect sensor data, compute averages, predict output, and upload to Firestore."""
    start_time = time.time()
    temperature_sum = 0
    ecg_sum = 0
    gsr_sum = 0
    count = 0
    
    try:
        while time.time() - start_time < duration:
            # Read sensor data
            temperature = read_temperature()
            ecg = read_ecg()
            gsr = read_gsr()

            # Accumulate sensor data
            temperature_sum += temperature
            ecg_sum += ecg
            gsr_sum += gsr
            count += 1

            # Print live data (optional for debugging)
            timestamp = datetime.datetime.now()
            print(f"Timestamp: {timestamp}, Temp: {temperature:.2f}°C, ECG: {ecg:.2f}V, GSR: {gsr:.2f}V")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting...")
    finally:
        if count > 0:
            # Compute averages
            avg_temperature = temperature_sum / count
            avg_ecg = ecg_sum / count
            avg_gsr = gsr_sum / count

            # Predict output using average data
            output = predict_output(avg_temperature, avg_ecg, avg_gsr)

            # Print average data and output
            print(f"Average Temperature: {avg_temperature:.2f}°C")
            print(f"Average ECG: {avg_ecg:.2f}V")
            print(f"Average GSR: {avg_gsr:.2f}V")
            print(f"Output: {output}")

            # Save average data and output to Firestore
            if user_id:
                avg_doc_ref = db.collection(u'SensorData').document()
                avg_doc_ref.set({
                    "Timestamp": datetime.datetime.now(),
                    "userId": user_id,
                    "Temperature": avg_temperature,
                    "ECG": avg_ecg,
                    "GSR": avg_gsr,
                    "Output": output  # Composite attribute
                })
                print("Average data and output written to Firestore")

        print("Data collection complete.")

if __name__ == "__main__":
    print("Starting data collection...")
    collect_data_and_save_to_firestore()