# Python

GOAL: implement a structured version of the EBDM task in Python based on the matlab implementation.

## Setup

This project uses `pipenv` to configure the local development in a virtual environment.
This ensures that dependencies are managed correctly across different installations.

First, make sure [Python version 3.10](https://www.python.org/downloads/release/python-3100/) is configured and [Pipenv](https://pipenv.pypa.io/en/latest/) is installed.

Then, go to this directory in a terminal and run `pipenv install`.

To add further dependencies, use `pipenv install <package>` with the necessary package - for example, `pipenv install pygame` would add the dependency for the [pygame](https://github.com/pygame/pygame) library which makes certain things like keyboard interactions very simple.

## Structure

TODO: define the main modules and functions of the task. As first version, only the logic, timings and log of the matlab version need to be implemented in python. This means that the graphical components will be handled in a second stage, as they are not strictly required for the VR implementation (the screen buffers will be developed by ENG). 

Example of structure definition - Decision-making phase
1. For Dur_PrepDM (e.g. 1s): check if either the left or right arrow are pressed
   1.1 If so, log the time of press and mark anticipation for the current trial
2. For maximum Dur_DM (e.g. 4s): check if either the left or right arrow are pressed
   2.1 If one of the keys has been pressed, log the time of press and the decision encoded
   2.2 Stop checking if the keys are pressed
3. For Dur_PostDecision (e.g. 1s): wait (in further development this will be the moment of displaying the selection)
4. Wait Dur_ITI
