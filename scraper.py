import csv
import sys
import time

import lxml.html
import progressbar
import requests

from cache import Cache


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 ' \
             'Safari/537.36'
RATE_LIMIT_SLEEP = 0.01
CACHE = Cache()


def find_ship_url(mmsi):
    """Find the URL of a ship with this MMSI."""

    if CACHE.has('url', mmsi):
        return CACHE.get('url', mmsi)

    print('>', 'Finding ship:', mmsi)

    url = 'https://www.vesselfinder.com/vessels/livesearch'
    params = {'term': str(mmsi)}
    headers = {'User-Agent': USER_AGENT}

    response = requests.get(url, params=params, headers=headers)
    json = response.json()

    def find_result():
        for result in json['list']:
            if result['MMSI'] == str(mmsi):
                return result

    data = find_result()

    if data is None:
        url = None
    else:
        name = data['NAME'] \
            .replace(' & ', '-') \
            .replace(' ', '-') \
            .replace(':', '-') \
            .replace('+', '-') \
            .replace('.', '') \
            .replace('!', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace('*', '') \
            .replace(',', '') \
            .replace('/', '') \
            .replace('\\', '') \
            .replace("'", '') \
            .replace('"', '') \
            .replace('#', '') \
            .replace('=', '') \
            .replace('[', '') \
            .replace(']', '') \
            .replace('^', '') \
            .replace(';', '') \
            .replace('?', '')

        url = 'https://www.vesselfinder.com/vessels/{0}-IMO-{1}-MMSI-{2}' \
            .format(name, data['IMO'], data['MMSI'])

    CACHE.set('url', mmsi, url)

    time.sleep(RATE_LIMIT_SLEEP)  # rate limiting

    return url


def scrape_information(mmsi, imo, name):
    """Scrape information about a particular ship."""

    if CACHE.has('ship', mmsi):
        return CACHE.get('ship', mmsi)

    url = find_ship_url(mmsi)

    if url is None:
        return None

    print('>', 'Scraping:', url)

    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    content = response.content

    page = lxml.html.fromstring(content)

    vehicle = page.xpath('//article[@itemtype="http://schema.org/Vehicle"]')[0]

    vesselfinder_name = vehicle.xpath('//h1[@itemprop="name"]')[0].text_content()
    gross_tonnage = vehicle.xpath('//*[@itemprop="weight"]')[0].text_content()
    net_tonnage = vehicle.xpath('//*[@itemprop="cargoVolume"]')[0].text_content()

    imo = None if imo == 0 else imo
    gross_tonnage = None if gross_tonnage == 'N/A' else int(gross_tonnage[:-2])
    net_tonnage = None if net_tonnage == 'N/A' else int(net_tonnage[:-2])

    info = (mmsi, imo, name, vesselfinder_name, gross_tonnage, net_tonnage)

    CACHE.set('ship', mmsi, info)

    time.sleep(RATE_LIMIT_SLEEP)  # rate limiting

    return info


def main():
    """Run the script."""

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('input_csv')
    parser.add_argument('output_csv')
    args = parser.parse_args()

    with open(args.input_csv) as infile, open(args.output_csv, 'w') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        rows = list(reader)

        progress = progressbar.ProgressBar(redirect_stdout=True)

        for row in progress(rows):
            mmsi = int(row[0])
            imo = int(row[1])
            name = row[2].strip()

            info = scrape_information(mmsi, imo, name)
            if info is None:
                print('!', mmsi, 'not found.')
            else:
                writer.writerow(info)

            sys.stdout.flush()


if __name__ == '__main__':
    main()
