import gpiod
import time
import threading

def get_rpi_model():
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return model.strip('\x00')  # Remove null bytes at the end
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

model = get_rpi_model()
if model:
    print(f"Model detected: {model}")
    CHIP_NAME = get_gpio_chip(model)
    print(f"The GPIO chip for this model is: {CHIP_NAME}")
else:
    print("Model could not be determined.")
    CHIP_NAME = 'gpiochip0'  # Default fallback if the model cannot be determined

# Initialize the chip with the determined CHIP_NAME
chip = gpiod.Chip(CHIP_NAME)

INPUT_PINS = [17, 18, 23, 27]
OUTPUT_PIN = 22
RESET_TIME = 0.1  # Seconds

# Flag to control the main loop
running = True

# Function to wait for a stop command from the input prompt
def wait_for_stop_command():
    global running
    input("Press Enter to stop...")
    running = False

# Main program
def main():
    global running

    # Configure inputs with pull-up
    input_lines = chip.get_lines(INPUT_PINS)
    input_lines.request(consumer='example', type=gpiod.LINE_REQ_DIR_IN,
                        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

    # Configure output
    output_line = chip.get_line(OUTPUT_PIN)
    output_line.request(consumer='example', type=gpiod.LINE_REQ_DIR_OUT)

    # Start a thread that waits for user input
    stop_thread = threading.Thread(target=wait_for_stop_command)
    stop_thread.start()

    try:
        while running:
            # Example: Toggle OUTPUT_PIN
            output_line.set_value(1)
            time.sleep(RESET_TIME)
            output_line.set_value(0)
            time.sleep(RESET_TIME)

    except KeyboardInterrupt:
        running = False

    finally:
        # Ensure OUTPUT_PIN is high before the program ends
        output_line.set_value(1)

        # Release resources
        input_lines.release()
        output_line.release()

        # Wait until the stop thread has finished
        stop_thread.join()

        print("Program ended properly.")

if __name__ == "__main__":
    main()
