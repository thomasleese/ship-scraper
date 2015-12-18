import lxml.html
import requests


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 ' \
             'Safari/537.36'


def connect_to_database():
    """Connect to the database."""

    print('Connecting to the database.')


def get_ships_with_missing_details(database):
    """
    Get an iterator over the MMSI and IMO of ships that have missing details.
    """

    print('Finding all ships with missing information.')

    return []




def scrape_information(name, mmsi, imo):
    """Scrape information about a particular ship."""

    print('Scraping information about ship: Name={0}, MMSI={1}, IMO={2}'
          .format(name, mmsi, imo))

    name = name.upper().replace('/', '')
    imo = 0 if imo is None else imo

    url = 'https://www.vesselfinder.com/vessels/{0}-IMO-{1}-MMSI-{2}' \
        .format(name, imo, mmsi)

    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    page = lxml.html.fromstring(response.content)

    vehicle = page.xpath('//article[@itemtype="http://schema.org/Vehicle"]')[0]

    gross_tonnage = vehicle.xpath('//*[@itemprop="weight"]')[0].text_content()

    return gross_tonnage



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

    print(scrape_information('QUO/VADIS', 244710370, None))



if __name__ == '__main__':
    main()
