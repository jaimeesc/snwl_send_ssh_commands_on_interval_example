# This tool automatically sends commands to a firewall over SSH management.
#
# Setup:
# 1. Install the latest version of Python 3.
# 2. Use 'pip' or 'pip3' to install the necessary modules.
#	-- pip install paramiko
#	-- pip install schedule
# 3. In this script, configure the IP, SSH mgmt port, and management credentials below.
# 4. Set 'scheduleTimer' to a desired interval in seconds (300 by default). Save the changes.
# 5. Launch the script from the command line

# Import these modules
import paramiko # Used for SSH client communication
import time # Used for the sleep functionality
from datetime import datetime, timezone # Used for the generateTimestamp() function.
import schedule # Used for managing the scheduled routine


# Firewall login information
fwIp = '10.10.10.1' # Enter the IP of the firewall.
fwSshPort = '22' # Enter a custom SSH port if needed.
fwUser = 'admin' # Enter the user name between the ''.
fwPass = 'password' # Enter the password between the ''.

# Configure how often to SSH in and pull the buffer and connection information.
scheduleTimer = 10 # Minutes


# Function to generate a timestamp.
def generateTimestamp():
	currentTime = datetime.now(timezone.utc).astimezone()
	currentTime = str(currentTime)
	return currentTime


# Connect via SSH, send the command, and do any other work.
# This routine will run on an interval
def routine():
	try:
	# SSH connection setup.
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(fwIp, port=fwSshPort, username=fwUser, password=fwPass, look_for_keys=False)
	# Creates a channel.
		sendchannel = client.invoke_shell()
		print("-- Executing routine at", generateTimestamp(), "--")
	# Send the command.
		sendchannel.sendall('show status\rq')
	# Sleep for 4 seconds to wait for the response data.
	# Sleeping for 4 sec to give the response enough time to come in.
		time.sleep(4)
	# Pull the received data from the channel and decode, then split it into a list object
		sc = sendchannel.recv(7500)
		sc = sc.decode('ASCII')
		sc = sc.split('\r\n')
	#	sc = sc.split('--MORE--[8D[K')
	# Iterate through the received data list object, and print out the buffer statistics
		for i in sc:
			i.replace("  ", "")
			if "Serial Number:" in i:
				print(str(i.replace("  ", "")).lstrip('--MORE--[8D[K'))
			if "System Time:" in i:
				print(str(i.replace("  ", "")).lstrip('--MORE--[8D[K'))
			if "Up Time:" in i:
				print(str(i.replace("  ", "")).lstrip('--MORE--[8D[K'))
			if "Connections:" in i:
				print(str(i.replace("  ", "")).lstrip('--MORE--[8D[K'))
#			print(str(i).lstrip('--MORE--[8D[K'))
	# Send the next command.
		sendchannel.sendall('\rshow high-availability status')
	# Send the next command.
		sendchannel.sendall('\rrestart\ryes\r')
	# Sleep for 1 second to receive data.
	# Only sleeping 1 second because the expected data is in a much smaller response.
		time.sleep(1)
	# Pull the received data from the channel. Decode and split it.
		sc = sendchannel.recv(700)
		sc = sc.decode('ASCII')
		sc = sc.split('\r\n')
	# Iterate through the response data. Print out the connection statistics.
		for i in sc:
			if "HA Mode:" in i:
				print(i.replace("  ", ""))
			if "Status:" in i:
				print(i.replace("  ", ""))
			if "Primary State:" in i:
				print(i.replace("  ", ""))
			if "Secondary State:" in i:
				print(i.replace("  ", ""))
			if "Active Up Time:" in i:
				print(i.replace("  ", ""))
			if "Stateful HA Synchronized:" in i:
				print(i.replace("  ", ""))
	# Close the channel
		sendchannel.close()
#		print("\")
	except KeyboardInterrupt:
		exit()
	finally:
	# Close the SSH client connection.
		client.close()
		print("--", generateTimestamp(), "Connection closed. --\n-- Please wait for the firewall to reboot. Sleeping until next scheduled run. --")


# This function starts the schedule timer and runs the routine.
def startRoutine():
	try:
		schedule.every(scheduleTimer).minutes.do(routine)
		while True:
			schedule.run_pending()
			time.sleep(1)
	except KeyboardInterrupt:
		exit()


# Starts the scheduled routine on launch of the script.
# Runs the routine once initially before starting the loop.
if __name__ == '__main__':
	routine()
	startRoutine()
