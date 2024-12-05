# Soundboard

This project is made entirely for my own use, but you can also use it yourself if this strange use case is right for you. The code has been implemented to be functional with only the Novation Launchpad MK1. You will need to change all MIDI event mappings for it to work correctly. It is by no means complete, but rather a prototype, with almost no testing or error catching.

### Required modules

This project is completely dependent on pygame. All MIDI and audio functionality is done using pygame's mixer, midi libraries. You will also need Flask for the web interface. You propably also want to use VB-Audio's Virtual Cable to use it as a soundboard through your microphone.

### How to use

You need to run two python scripts at the same time.
- `app.py` is for the web interface where you can check assigned key bindings and complete the new-key-assignation process.
- `audio_main.py` is the main functionality for controlling the launchpad and playing audio to output device using pygame.

If you want to route audio to two different devices e.g. Virtual Audio Cable AND your own headset at the same time you can just copy the `audio_main.py` file, change the variables to use different device and run two or more of them in the background at the same time. Just make sure to restart all of them if an error occurs or you have clicked any of the control/channel rack buttons. Run `app.py` interface in the background as well at the same time. After that you can access the web interface from http://127.0.0.1:5000 to view assigned audio files and assign new ones when the assignation mode is active. Create a audio folder if it does not exist yet and put or download your audio files there.

### New functionality/fix ideas

- Ability to record events and replay them
- Ability to change channel's volume 
- Multiple pages for the audio keys
- Optimising the code and just making it better 

### Author and usage

The code is awful. This was just a prototype for personal use of mine (sakuti). You can modify it however you like but do not expect it to work without any modifications.

<small>I don't even know why I am open sourcing this. You're welcome.</small>