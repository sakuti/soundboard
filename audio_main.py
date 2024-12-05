#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: github.com/sakuti

import os
import time
import json

# Hide pygame support prompt from the terminal
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer, midi

# Parameters
DEVICE_IS_NOT_FOR_TESTING = False		# Set this to True if you want to not play audio to this device when in testing mode 
DEFAULT_FADEOUT_DURATION = 500 			# Default audio fadeout duration in ms
MIDI_DEVICES = [1, 3] 							# [input, output] = MIDI device IDs
AUDIO_DEVICE = ""										# Output audio device name 

# Global variables
COLORS = {
	"red": 3,
	"orange": 31,
	"yellow": 62,
	"green": 60,
	"lightgreen": 56,
	"lightred": 1
}



### HELPER FUNCTIONS

# Function for reading previous values in the saved json data 
def read_prev_data():
	with open('controls.json', 'r') as file:
		json_object = json.load(file)
	return json_object

# Function for saving new data to the json file
def save_data(data):
	json_object = json.dumps(data, indent=4)
	with open("controls.json", "w") as file:
			file.write(json_object)



# Mixer class for handing audio and channels 
class Mixer:
	def __init__(self):
		self.device_name = AUDIO_DEVICE
		self.current_channel = 0

		mixer.init(devicename=self.device_name)
		
		# Create 8 different channels, you can switch 
		# between them using the channel rack buttons 
		self.channels = [mixer.Channel(i) for i in range(8)]
	
	# Pause currently selected channels audio
	def pause(self):
		self.channels[self.current_channel].pause()

	# Unpause currently selected channels audio
	def unpause(self):
		self.channels[self.current_channel].unpause()

	# Stop all audio files from the current channel
	def stop(self):
		self.channels[self.current_channel].stop()

	# Stop the audio by fading it out from the current channel
	def fadeout(self, duration=DEFAULT_FADEOUT_DURATION):
		self.channels[self.current_channel].fadeout(duration)

	# Play audio in the current channel, if test_only
	# is active, audio will be only played to devices which are for testing
	def play(self, audio=None, test_only=False):
		if DEVICE_IS_NOT_FOR_TESTING and test_only:
			return
		sound = mixer.Sound(f"./audio/{audio}")
		self.channels[self.current_channel].play(sound)



# Soundboard class for handing Launchpad colors,
# channels and all control related functionality
class Soundboard:
	def __init__(self):
		self.mixer = Mixer()
		self.input = None
		self.output = None
		self.unassigned = False
		self.selected_channel = 0
		self.testing_mode = False

	# Initialize the Soundboard
	def init(self):
		midi.init()
		self.input = midi.Input(MIDI_DEVICES[0])
		self.output = midi.Output(MIDI_DEVICES[1])
		self.turn_all_off()
		self.update_colors()
		self.update_colors(only_assigned_audios_as="orange")
		self.set_as_needs_to_be_assigned(False)
		self.update_channel_rack_colors()

	# Update selected channel to the Mixer and Soundboard
	def update_selected_channel(self, new_channel):
		self.selected_channel = new_channel
		self.mixer.current_channel = new_channel

	# Update channel rack by highlighting the active channel
	def update_channel_rack_colors(self, active_channel=0):
		channels = read_prev_data()["channel_rack"]

		for index, channel in enumerate(channels):
			if index == active_channel:
				self.set_color(channel[1], "lightgreen", channel[0])
			else:
				self.set_color(channel[1], "lightred", channel[0])

	# Update predefined colors, if only_assigned_audios_as is true
	# only audio file keys will be highlighted with the wanted color
	def update_colors(self, only_assigned_audios_as=False):
		keys = read_prev_data()["keys"].values()
		audios = read_prev_data()["audios"].values()
		
		if only_assigned_audios_as:
			for audio in audios:
				position = audio[1]
				self.set_color(position, only_assigned_audios_as)
		else:
			for key in keys:
				position, color = key[0][1], key[1]
				self.set_color(position, color)

	# Find control button from the key data  
	def find_control_by_data(self, data):
		try: 
			# what is this???? my python skills are clearly not at its highest right now 
			control = list(read_prev_data()["keys"].keys())[list([e[0] for e in read_prev_data()["keys"].values()]).index(data)]
			return control
		except ValueError:
			return False

	# Find audio button from the audio data 
	def find_audio_by_data(self, data):
		try: 
			audio = list(read_prev_data()["audios"].keys())[list(read_prev_data()["audios"].values()).index(data)]
			return audio
		except ValueError:
			return False

	# Find channel rack button from the channel rack data 
	def find_channel_by_data(self, data):
		try:
			channel = read_prev_data()["channel_rack"].index(data)
			return channel + 1
		except ValueError:
			return False
	
	# Set specific key's color. If wanted, override_id can be defined 
	def set_color(self, key, color, override_id=144):
		if color not in COLORS.keys(): 
			return
		self.output.write_short(override_id, key, COLORS[color])

	# Turn every key color to off by looping through them 
	def turn_all_off(self):
		channel_rack = read_prev_data()["channel_rack"]

		for channel in channel_rack: 
			self.output.write_short(channel[0], channel[1], 0)

		for i in range(128):
			self.output.write_short(144, i, 0)

	# Set key to "needs to be assigned". When this mode is active
	# assigned audio file keys will be highlighted red and the 
	# key that is waiting to be assigned will be highlighted green
	def set_as_needs_to_be_assigned(self, data):
		prev_data = read_prev_data()
		prev_data["needs_to_be_assigned"] = data
		save_data(prev_data)

		# Visualise the key that needs to be assigned
		if data != False:
			self.turn_all_off()
			self.update_colors(only_assigned_audios_as="red")
			self.set_color(data[1], "green")

	# Main loop
	def loop(self):
		# Check if MIDI input has new events available
		if self.input.poll(): 
			# Read maximum of 10 newest events from the input stream
			midi_events = self.input.read(10)

			# Loop through the events
			for event in midi_events:
				timestamp, data = event[1], event[0]
				control_name = self.find_control_by_data(data)

				# Check what control function should be triggered
				if control_name == "play_key":
					self.mixer.unpause()
				if control_name == "toggle_testmode_key":
					self.testing_mode = not self.testing_mode
					self.set_color(data[1], "green" if self.testing_mode else "red")
				elif control_name == "pause_key":
					self.mixer.pause()
				elif control_name == "stop_key":
					self.mixer.stop()
				elif control_name == "fadeout_key":
					self.mixer.fadeout()
				else:
					# If control button was not pressed we will check if had a audio file assigned
					audio_name = self.find_audio_by_data(data)

					if audio_name:
						# If it was assigned but the system was waiting for a new key to be assigned,
						# cancel the assignation and reload all of the interface key colors 
						if self.unassigned:
							print("Assignation cancelled. Reloading the interface.")

							# Reload the interface
							self.turn_all_off()
							self.update_colors()
							self.update_colors(only_assigned_audios_as="orange")
							self.set_as_needs_to_be_assigned(False)
							self.update_channel_rack_colors(self.selected_channel)
							self.unassigned = False
						else:
							# If audio file was found, play it on the selected channel 
							self.mixer.play(audio_name, test_only=self.testing_mode)
					elif data[2] != 0:
						# If we didn't find any audio or control matches we will check if 
						# event should trigger a channel rack related event
						channel = self.find_channel_by_data(data)

						if channel:
							# Verify that channel won't be changed to already selected channel
							if self.selected_channel-1 == channel:
								break

							# If event was a click in the channel rack, switch channel
							print(f"Channel switched from {self.selected_channel+1} to {channel}")
							self.update_channel_rack_colors(channel-1)
							self.update_selected_channel(channel-1)
						else:
							# If event was not found from audio files, channel rack or controls 
							# we want to start the assignation mode
							print('Control not found for, setting as "needs to be assigned"-key')
							self.set_as_needs_to_be_assigned(data)
							self.unassigned = True

	# Close all connections to input and output devices
	def close(self):
			self.input.close()
			self.output.close()
			midi.quit()



if __name__ == "__main__":
	soundboard = Soundboard()
	soundboard.init()
	time.sleep(1)
	
	print("Starting the main loop...")
	
	# Loop until keyboard interruption is detected
	try:
		while True:
			soundboard.loop()
			time.sleep(0.01)
	except KeyboardInterrupt:
		print("\nExiting...")
	finally:
		soundboard.close()