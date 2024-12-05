#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: github.com/sakuti

import os
import json
from flask import Flask, request, jsonify, render_template, url_for, redirect

# Initialize Flask
app = Flask(__name__, template_folder='views')



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



### PRIMARY FUNCTIONS 

# Function for retrieving only unassigned audio file names
def get_unassigned_audios():
	available_audios = os.listdir("./audio")
	assigned_audios = read_prev_data()["audios"].keys()

	return filter(lambda entry: entry not in assigned_audios, available_audios)

# Function for assigning an audio file for the unassigned key 
def update_unassigned_audio(audiofile):
	prev_data = read_prev_data()
	prev_data["audios"][audiofile] = prev_data["needs_to_be_assigned"]
	prev_data["needs_to_be_assigned"] = False
	save_data(prev_data)



### ROUTES ###

# GET method for the main page which renders HTML using Jinja templating enngine
@app.route('/', methods=['GET'])
def index():
	url_for('static', filename='style.css')
	return render_template('index.html', data=read_prev_data(), unassigned_audios=get_unassigned_audios())

# GET method route for retrieving assigned audio files as JSON
@app.route('/audios/assigned', methods=['GET'])
def audio():
		if request.method == 'GET':
			return jsonify(read_prev_data())

# GET method route for retrieving available audio files as JSON
@app.route('/audios/available', methods=['GET'])
def audios_available():
		if request.method == 'GET':
			return jsonify(os.listdir("./audio"))

# POST method route for assigning a specific audiofile to key
@app.route('/assign', methods=['POST'])
def assign_audio():
	if request.method == 'POST':
		update_unassigned_audio(request.form.get('audiofile'))
	return redirect(url_for('index'))