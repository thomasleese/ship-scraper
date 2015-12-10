def connect_to_database():
    """Connect to the database."""

    print('Connecting to the database.')


def get_ships_with_missing_details(database):
    """
    Get an iterator over the MMSI and IMO of ships that have missing details.
    """

    print('Finding all ships with missing information.')

    return []


def scrape_information(mmsi, imo):
    """Scrape information about a particular ship."""

    print('Scraping information about ship: MMSI={0}, IMO={1}'
          .format(mmsi, imo))


def update_ship_information(database, mmsi, info):
    """Update the ship information in the database for a particular ship."""

    print('Updating ship information for ship: MMSI={0}, info={1}'
          .format(mmsi, info))


def main():
    """Run the script."""

    database = connect_to_database()
    for mmsi, imo in get_ships_with_missing_details(database):
        info = scrape_information(mmsi, imo)
        update_ship_information(database, mmsi, info)


if __name__ == '__main__':
    main()
