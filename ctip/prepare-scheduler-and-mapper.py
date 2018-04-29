#!/usr/bin/env python3
'''
This script copies the files that are needed from scheduler-and-mapper. If more
files are needed, please add them to FILES_TO_COPY.
'''
import os, shutil
FILES_TO_COPY = (
	"agency_common.py",
	"agency_nyu.py",
	"agency_walking.py",
	"agency_walking_dynamic.py",
	"agency_walking_static.py",
	"common.py",
	"common_nyu.py",
	"common_walking_static.py",
    "departure_lister.py",
	"itinerary_finder.py",
	"NYU.pickle",
	"Stop Locations.csv",
	"stops.py",
	"WalkingStatic.pickle",
)
SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "scheduler-and-mapper"
)
DESTINATION_DIR = os.path.join(
    os.path.dirname(__file__), 
    "scheduler-and-mapper"
)

def main():
    # Delete the destination folder.
    try:
        shutil.rmtree(DESTINATION_DIR)
    except FileNotFoundError:
        pass
    # Create the destination folder.
    os.mkdir(DESTINATION_DIR)
    # Copy the files.
    for filename in FILES_TO_COPY:
        shutil.copyfile(
            os.path.join(SOURCE_DIR, filename),
            os.path.join(DESTINATION_DIR, filename)
        )

if __name__ == "__main__":
    main()
