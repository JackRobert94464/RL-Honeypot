import json
import time
import logging
from pathlib import Path
from multiprocessing import Process
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration constants
MODE = "unsock"
SNORT_CONFIG = "/etc/snort/rules/honeypotsdn.rules"
LOG_DIR = Path("/home/ubuntu/RL-Honeypot-linux/Development/TrainingCode/A2C_Subnet/tutorial-ryu/log/snort")
ALERT_FILE = LOG_DIR / "alert"
OUTPUT_JSON = "data-output.json"
LOG_FILE = "log-extract-data-process.txt"
INTERFACES = ["s111-eth1", "s111-eth2", "s111-eth3", "s111-eth4"]

def run_command(command):
    try:
        process = subprocess.run(command.split(), capture_output=True, text=True)
        process.check_returncode()
        return process.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command}' failed with error: {e}")
        raise

# sudo snort -i s111-eth1 -A unsock  -l /tmp -v -c /etc/snort/rules/honeypotsdn.rules
def start_snort(interface):
    command = f"snort -A {MODE} -c {SNORT_CONFIG} -l {LOG_DIR} -i {interface} -D"
    output = run_command(command)
    logging.info(f"Started snort on {interface}: {output}")

def process_alerts():
    try:
        output = []
        if not ALERT_FILE.exists():
            logging.warning("Alert file not found. Continuing...")
            return

        with ALERT_FILE.open('r') as file:
            for line in file:
                raw = line.split("[**]", 3)
                if len(raw) < 3:
                    continue
                time_stamp = raw[0]
                mes = raw[1].split("] ", 2)[1]
                dst = raw[2].split(" -> ", 2)[1].split(":")[0]
                src = raw[2].split(" -> ", 2)[0].split("} ", 2)[1].split(":")[0]

                entry = {
                    "time": time_stamp.strip(),
                    "mes": mes.strip(),
                    "dst": dst.strip(),
                    "src": src.strip()
                }

                output.append(entry)

        with open(OUTPUT_JSON, 'w') as json_file:
            json.dump(output, json_file, indent=4)

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"Data has been saved to {OUTPUT_JSON} at {current_time}\n")
        logging.info(f"Data has been saved to {OUTPUT_JSON}")

    except Exception as e:
        logging.error(f"An error occurred while processing alerts: {e}")

def monitor_file(filename):
    if not os.path.exists(filename):
        logging.error(f"Error: File '{filename}' does not exist.")
        return

    last_modified_time = os.path.getmtime(filename)

    while True:
        current_modified_time = os.path.getmtime(filename)
        if current_modified_time != last_modified_time:
            last_modified_time = current_modified_time
            process_alerts()
        time.sleep(1)  # Check for changes every second

def main():
    try:
        run_command("rm /home/ubuntu/RL-Honeypot-linux/Development/TrainingCode/A2C_Subnet/tutorial-ryu/log/snort/alert")
        run_command("touch /home/ubuntu/RL-Honeypot-linux/Development/TrainingCode/A2C_Subnet/tutorial-ryu/log/snort/alert")
        run_command("rm data-output.json")
    except Exception as e:
        logging.warning(f"Failed to remove alert file: {e}")
    
    processes = []
    for interface in INTERFACES:
        p = Process(target=start_snort, args=(interface,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    logging.info("----------------------------------------------------------------")
    logging.info("-> Start monitoring alert file...")
    monitor_file(ALERT_FILE)

if __name__ == '__main__':
    main()
