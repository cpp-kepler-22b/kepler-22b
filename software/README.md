# Dependencies
pip install -r requirements.txt

# Base Station
Running guiClient.py creates the GUI to communicate to the Raspberry Pi and Display the video received during operations. The GUI will await connection before allowing any message to be sent or video to be displayed.

# Raspberry Pi Scripts
main.py will begin video transimission and handle messages received from the base station. This will also handle the gimble communication being sent to the microcontroller. 