import time
import datetime
import csv
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Define emotions
emotions = ["Happy", "Sad", "Neutral", "Angry", "Anxious", "Stressed"]

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115
ads = ADS.ADS1115(i2c)
ads.gain = 1  
time.sleep(0.5)  

# Initialize sensors
lm35 = AnalogIn(ads, ADS.P1)  # Temperature Sensor (LM35)
ad8232 = AnalogIn(ads, ADS.P0)  # ECG Sensor (AD8232)
gsr_sensor = AnalogIn(ads, ADS.P2)  # GSR Sensor

def read_temperature():
    """Read temperature from LM35 in Celsius using voltage directly."""
    # Read the voltage directly from the sensor
    voltage = lm35.voltage  # Voltage in volts

    # Convert voltage to Celsius using the LM35 formula (10 mV per degree Celsius)
    temperature_celsius = (voltage * 1000) / 10.0

    return temperature_celsius

def read_ecg():
    """Read ECG from AD8232."""
    return ad8232.voltage

def read_gsr():
    """Read GSR sensor data."""
    return gsr_sensor.voltage  

def collect_data_and_save_to_csv(filename, interval=6, samples_per_emotion=167, break_time=60, avg_samples=10):
    """Collect sensor data, compute averages, and save to CSV without invalid values."""
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Temperature", "ECG", "GSR", "Emotion"])
            
            for emotion in emotions:
                print(f"Collecting data for emotion: {emotion}")
                
                temp_buffer = []
                ecg_buffer = []
                gsr_buffer = []
                
                for i in range(samples_per_emotion * avg_samples):  
                    temperature = read_temperature()
                    ecg = read_ecg()
                    gsr = read_gsr()
                    
                    # Store valid data (temperature, ECG, GSR)
                    temp_buffer.append(temperature)
                    ecg_buffer.append(ecg)
                    gsr_buffer.append(gsr)
                    
                    if len(temp_buffer) == avg_samples:
                        avg_temp = np.mean(temp_buffer)
                        avg_ecg = np.mean(ecg_buffer)
                        avg_gsr = np.mean(gsr_buffer)
                        timestamp = datetime.datetime.now()
                        
                        writer.writerow([timestamp, avg_temp, avg_ecg, avg_gsr, emotion])
                        print(f"{timestamp}, Temp: {avg_temp:.2f}°C, ECG: {avg_ecg:.2f}V, GSR: {avg_gsr:.2f}V, Emotion: {emotion}")
                        
                        temp_buffer.clear()
                        ecg_buffer.clear()
                        gsr_buffer.clear()
                    
                    time.sleep(interval)
                
                print(f"Completed data collection for {emotion}. Taking a short break...\n")
                time.sleep(break_time)
                
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting...")
    finally:
        print(f"Data collection complete. Data saved to '{filename}'")

if __name__ == "__main__":
    print("Starting in 10 seconds...")
    time.sleep(10)
    print("Starting data collection...")
    collect_data_and_save_to_csv("sensor_data.csv")