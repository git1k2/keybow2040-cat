Aimport board
import busio
import re
import time

from keybow2040 import Keybow2040

class FTdx10:
    def __init__(self):

        # Setup up UART
        self.uart = busio.UART(board.TX, board.RX, baudrate=38400, timeout=0.050)

        # CAT commands
        self.cat_commands = {
            "BI": {"description": "Break-in", "on": "1",   "off": "0", "answer": "BI[0-9];"},
            "BS": {"description": "Band select"},a
            "CO02": {"description": "APF", "on": "0001", "off": "0000", "fill": 4, "answer": "CO02000[0-1];"},
            "KR": {"description": "Keyer", "on": "1",   "off": "0", "answer": "KR[0-9];"},
            "KS": {"description": "Keyer speed", "max": 60, "min": 4, "fill": 3, "answer": "KS0[0-6][0-9];"},
            "PC": {"description": "Power control", "max": 100, "min": 5, "fill": 3, "answer": "PC[0-1][0-9][0-9];"},
            "ZI": {"description": "Zero in"},


        }

        # Key mapping
        self.key_mapping = {
            0: {"cat_command": "ZI", "preset": "0"},
            1: {"cat_command": "KR", "operation": "toggle"},
            3: {"cat_command": "BS", "preset": "01"},

            4: {"cat_command": "CO02", "operation": "toggle"},
            5: {"cat_command": "BI", "operation": "toggle"},
            7: {"cat_command": "BS", "preset": "03"},

            8: {"cat_command": "KS", "operation": "down"},
            9: {"cat_command": "KS", "operation": "up"},
            11: {"cat_command": "BS", "preset": "05"},

            12: {"cat_command": "PC", "operation": "down"},
            13: {"cat_command": "PC", "operation": "up"},
            15: {"cat_command": "BS", "preset": "09"},
        }

        # Get identification
        found = False
        while found is False:
            match = re.search("ID0761;", self.send_cat(command="ID;"))
            if match:
                print(f"Yaesu FTdx10 found.")
                found = True
            else:
                print("Radio not connected? Trying again...")
                time.sleep(1)

        # Get state for configured cat commands.
        command = []
        for cat_cmd, config in self.cat_commands.items():
            if "answer" in config:
                command.append(cat_cmd)
            commands_deduplicated = list(set(command))
        self.update_cat_state(command=commands_deduplicated)


    def send_cat(self, command=None):
        send_command = f"{command};"
        if isinstance(command, list):
            send_command = ""
            for item in command:
                send_command += f"{item};"
        print(f"Sending command: {send_command}")

        self.uart.write(bytes(send_command, "ascii"))

        data = self.uart.read()
        datastr = ""
        if data != None:
            datastr = ''.join([chr(b) for b in data])
        print(f"Received: {datastr}")
        if datastr == "":
            return ""
        else:
            return datastr

    def update_cat_state(self, command=None):
        if isinstance(command, str):
            command = [command]

        response = self.send_cat(command=command)

        for item in command:
            try:
                match = re.search(self.cat_commands[item]["answer"], response)
                if match:
                    state = match.group(0)[len(item):].rstrip(";")
                    self.cat_commands[item]["state"] = state
            except KeyError as e:
                print(f"KeyError: {e}")


def key_press(key_obj=None, hold=None):
    step = 1
    if hold:
        step = 10
    try:
        key_config = ftdx10.key_mapping[key_obj.number]
        key_cat_command = key_config["cat_command"]

        if "operation" in key_config:
            key_operation = key_config["operation"]

            cat_state = ftdx10.cat_commands[key_cat_command]["state"]

            if key_operation == "toggle":
                fill = 0
                if "fill" in ftdx10.cat_commands[key_cat_command]:
                    fill = int(ftdx10.cat_commands[key_cat_command]["fill"])
                on = ftdx10.cat_commands[key_cat_command]["on"]
                off = ftdx10.cat_commands[key_cat_command]["off"]

                if cat_state == on:
                    new_state = f"{int(off):0{fill}}"
                    ftdx10.send_cat(command=f"{key_cat_command}{new_state}")
                    ftdx10.update_cat_state(command=key_cat_command)
                if cat_state == off:
                    new_state = f"{int(on):0{fill}}"
                    ftdx10.send_cat(command=f"{key_cat_command}{new_state}")
                    ftdx10.update_cat_state(command=key_cat_command)

            if key_operation == "up" or key_operation == "down":
                min = int(ftdx10.cat_commands[key_cat_command]["min"])
                max = int(ftdx10.cat_commands[key_cat_command]["max"])
                fill = int(ftdx10.cat_commands[key_cat_command]["fill"])

                if key_operation == "up" and int(cat_state) < max:
                    new_speed = f"{int(cat_state) + step:0{fill}}"
                    ftdx10.send_cat(command=f"{key_cat_command}{new_speed}")
                    ftdx10.update_cat_state(command=key_cat_command)
                if key_operation == "down" and int(cat_state) > min:
                    new_speed = f"{int(cat_state) - step:0{fill}}"
                    ftdx10.send_cat(command=f"{key_cat_command}{new_speed}")
                    ftdx10.update_cat_state(command=key_cat_command)

        if "preset" in key_config:
            preset = key_config["preset"]
            ftdx10.send_cat(command=f"{key_cat_command}{preset}")

    except KeyError as e:
        print(f"KeyError: {e}")

def set_state_color(key_obj=None):
    try:
        if key_obj.number in ftdx10.key_mapping:
            key_config = ftdx10.key_mapping[key_obj.number]
            key_cat_command = key_config["cat_command"]

            if "operation" in key_config:
                key_operation = key_config["operation"]

                if key_operation == "toggle":
                    cat_state = ftdx10.cat_commands[key_cat_command]["state"]
                    on = ftdx10.cat_commands[key_cat_command]["on"]
                    off = ftdx10.cat_commands[key_cat_command]["off"]

                    if cat_state == on:
                        key_obj.set_led(*state_on)
                    if cat_state == off:
                        key_obj.set_led(*state_off)

                if key_operation == "up" or  key_operation == "down":
                    key_obj.set_led(*range_color)

            if "preset" in key_config:
                key_obj.set_led(*preset_color)

    except KeyError as e:
        print(f"KeyError: {e}")

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Colors
state_on = (255, 0, 0)    # red
state_off = (0, 255, 0)   # green
range_color = (0, 0, 255) # blue
preset_color = (0, 50, 50)
keypress_color = (255, 255, 0) # yellow

# Set up the radio
ftdx10 = FTdx10()
for cmd, config in ftdx10.cat_commands.items():
    try:
        print(f"{config["description"]} {config["state"]}")
    except KeyError as e:
        pass

for key in keys:
    set_state_color(key_obj=key)

    @keybow.on_press(key)
    def press_handler(key):
        key.set_led(*keypress_color)
        key_press(key_obj=key)

    @keybow.on_release(key)
    def release_handler(key):
        key.led_off()
        set_state_color(key_obj=key)

    @keybow.on_hold(key)
    def hold_handler(key):
        key_press(key_obj=key, hold=True)


while True:
    # Always remember to call keybow.update()!
    keybow.update()
