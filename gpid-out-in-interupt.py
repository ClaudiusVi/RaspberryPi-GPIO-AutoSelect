"""
Raspberry Pi GPIO Auto-Select Utility

This Python script is designed to facilitate GPIO programming on various Raspberry Pi models by automatically identifying the correct GPIO chip based on the Raspberry Pi model in use. It simplifies the process of setting up GPIO pins for both input and output purposes, making it easier to develop hardware-interfacing projects.

Key Features:
- Dynamically determines the Raspberry Pi model and selects the appropriate GPIO chip.
- Configures specified GPIO pins as inputs with pull-up resistors, suitable for buttons or switches.
- Toggles an output GPIO pin (GPIO 22) to create a pulsing effect, demonstrating how to control an output.
- Monitors the state of input GPIO pins (GPIO 21 and 20) and prints changes to the console.
- Implements a simple form of interrupt detection by monitoring GPIO 20 for a low state and triggering a predefined routine.

Usage:
The script sets up GPIO 21 and 20 as inputs with pull-up resistors, monitoring their state for any changes. When GPIO 21 changes state, it prints the new state to the console. If GPIO 20 goes low, it simulates an interrupt routine by printing a message. Meanwhile, GPIO 22 is used to demonstrate output control by pulsing it on and off.

Terminal Output:
Model detected: Raspberry Pi 5 Model B Rev 1.0
The GPIO chip for this model is: gpiochip4
GPIO 21 is now: 0
GPIO 21 is now: 1
GPIO 21 is now: 0
GPIO 21 is now: 1
Interrupt on line 20

Note:
This script is intended for educational and development purposes and demonstrates basic GPIO programming concepts on the Raspberry Pi using the 'gpiod' library. It may need modifications for use in production environments or in applications with specific hardware requirements.

Author: Claudius Viviani
Contact: cv@ntx.ch
"""

import gpiod
import time
import threading

def get_rpi_model():
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip('\x00')  # Remove null bytes at the end
        return model
    except Exception as e:
        print(f"Error reading model: {e}")
        return None

def get_gpio_chip(model):
    if 'Raspberry Pi 3' in model:
        return 'gpiochip1'
    elif 'Raspberry Pi 4' in model:
        return 'gpiochip3'
    elif 'Raspberry Pi 5' in model:
        return 'gpiochip4'
    else:
        return 'gpiochip0'  # Default assumption for older models

def monitor_gpio21(line, last_state):
    current_state = line.get_value()
    if current_state != last_state[0]:
        print(f"GPIO 21 is now: {current_state}")
        last_state[0] = current_state  # Update the last known state

def interrupt_routine():
    print("Interrupt on line 20")

def main():
    model = get_rpi_model()
    if model:
        print(f"Model detected: {model}")
        CHIP_NAME = get_gpio_chip(model)
        print(f"The GPIO chip for this model is: {CHIP_NAME}")
    else:
        print("Model could not be determined.")
        CHIP_NAME = 'gpiochip0'  # Default fallback

    chip = gpiod.Chip(CHIP_NAME)

    # Initialize GPIO 21 and 20 as inputs with pull-up
    gpio21_line = chip.get_line(21)
    gpio21_line.request(consumer='example', type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
    
    gpio20_line = chip.get_line(20)
    gpio20_line.request(consumer='example', type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

    # Initialize GPIO 22 as output
    output_line = chip.get_line(22)
    output_line.request(consumer='example', type=gpiod.LINE_REQ_DIR_OUT)

    last_state_gpio21 = [gpio21_line.get_value()]  # List to hold the last state of GPIO 21

    try:
        while True:
            # Toggle GPIO 22
            output_line.set_value(1)
            time.sleep(0.01)  # Pulse length
            output_line.set_value(0)
            time.sleep(0.01)  # Pulse length

            # Monitor GPIO 21 for state changes
            monitor_gpio21(gpio21_line, last_state_gpio21)

            # Check GPIO 20 for interrupt condition
            if gpio20_line.get_value() == 0:
                interrupt_routine()

    except KeyboardInterrupt:
        print("Program terminated by user.")

    finally:
        # Clean up
        gpio21_line.release()
        gpio20_line.release()
        output_line.release()
        print("GPIO resources released.")

if __name__ == "__main__":
    main()
