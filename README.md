# Ship Scraper

A Python tool to scrape ship information.

## Instructions

This tool accepts a CSV file containing a list of ships include their MMSI, IMO and name (in that order).

    $ pyvenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ python scraper.py input.csv output.csv

The resulting output file will include the ship MMSI, IMO, Name, VesselFinder Name, Gross Tonnage and Net Tonnage.
