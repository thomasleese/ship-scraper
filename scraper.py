import csv
import time

import lxml.html
import progressbar
import requests

from cache import Cache


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 ' \
             'Safari/537.36'

rate_limit_sleep_count = 0


def rate_limit_sleep():
    global rate_limit_sleep_count

    rate_limit_sleep_count += 1

    if rate_limit_sleep_count >= 100:
        time.sleep(1)
        rate_limit_sleep_count = 0


def find_ship_url(cache, mmsi):
    """Find the URL of a ship with this MMSI."""

    if cache.has('url', mmsi):
        return cache.get('url', mmsi)

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
            .replace('?', '') \
            .replace('>', '') \
            .replace('<', '') \
            .replace('$', '') \
            .replace('&', '') \
            .replace('%', '')

        url = 'https://www.vesselfinder.com/vessels/{0}-IMO-{1}-MMSI-{2}' \
            .format(name, data['IMO'], data['MMSI'])

    cache.set('url', mmsi, url)

    rate_limit_sleep()

    return url


def scrape_information(cache, mmsi, imo, name):
    """Scrape information about a particular ship."""

    if cache.has('ship', mmsi):
        return cache.get('ship', mmsi)

    url = find_ship_url(cache, mmsi)

    if url is None:
        return None

    print('>', 'Scraping:', url)

    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    response.raise_for_status()

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

    cache.set('ship', mmsi, info)

    rate_limit_sleep()

    return info


def main():
    """Run the script."""

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('input_csv')
    parser.add_argument('output_csv')
    args = parser.parse_args()

    done_ships = set()

    # first we load the existing data to see which ships we've already done
    with open(args.output_csv) as file:
        reader = csv.reader(file)
        for row in reader:
            mmsi = int(row[0])
            done_ships.add(mmsi)

    print(len(done_ships), 'ships already done.')

    # next we load up the cache
    cache = Cache()
    print(len(cache), 'cache entries.')

    # next we load the input file and start progressing through the scripts
    with open(args.input_csv) as infile, open(args.output_csv, 'a') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        rows = list(reader)

        progress = progressbar.ProgressBar(redirect_stdout=True)

        for row in progress(rows):
            mmsi = int(row[0])
            imo = int(row[1])
            name = row[2].strip()

            if mmsi in done_ships:
                continue

            info = scrape_information(cache, mmsi, imo, name)
            if info is None:
                print('!', mmsi, 'not found.')
            else:
                writer.writerow(info)


if __name__ == '__main__':
    main()
