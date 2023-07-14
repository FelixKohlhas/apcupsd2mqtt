import re
import argparse
import subprocess
import json
import paho.mqtt.client as mqtt

# Command-line argument parsing
parser = argparse.ArgumentParser(
    prog='apcupsd2mqtt',
    description='Send apcupsd data to MQTT'
)

# Add command-line arguments
parser.add_argument('-b', '--broker', default="localhost", help='MQTT broker address')
parser.add_argument('-p', '--port', default="1883", help='MQTT broker port')
parser.add_argument('-c', '--client-id', default="apcupsd2mqtt", help='MQTT client ID')
parser.add_argument('-t', '--topic-prefix', default="apcupsd2mqtt/", help='MQTT topic prefix')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

args = parser.parse_args()

# MQTT client setup
client = mqtt.Client(args.client_id)
client.connect(args.broker, int(args.port))

# Run apcaccess command and capture the output
apcaccess_command = ['/usr/sbin/apcaccess']
result = subprocess.run(apcaccess_command, capture_output=True, text=True)
data = result.stdout

# Define a regular expression pattern to extract field-value pairs
pattern = r"(\w+)\s+:\s+(.*)"
matches = re.findall(pattern, data)

data_dict = {}

# Process each field-value pair
for field, value in matches:
    value = value.strip()

    if field == "SERIALNO":
        topic = value

    if field == "STATUS":
        data_dict["status"] = value

    if field == "LOADPCT":
        value = float(value.split()[0])  # Convert to plain number
        data_dict["load_percent"] = value

    if field == "BCHARGE":
        value = float(value.split()[0])  # Convert to plain number
        data_dict["battery_charge_percent"] = value

    if field == "LINEV":
        value = float(value.split()[0])  # Convert to plain number
        data_dict["line_voltage_volts"] = value

    if field == "BATTV":
        value = float(value.split()[0])  # Convert to plain number
        data_dict["battery_voltage_volts"] = value

    if field == "TIMELEFT":
        value = float(value.split()[0])  # Convert to plain number
        data_dict["time_left_minutes"] = value

    if field == "NOMPOWER":
        value = float(value.split()[0])  # Convert to plain number
        try:
            data_dict["load_watts"] = data_dict["load_percent"] * value / 100
        except:
            pass

# Print verbose output if enabled
if args.verbose:
    print("TOPIC:", "%s%s" % (args.topic_prefix, topic))
    print("DATA:", json.dumps(data_dict))

# Publish data to MQTT topic
if topic:
    client.publish("%s%s" % (args.topic_prefix, topic), json.dumps(data_dict))