import requests
from bs4 import BeautifulSoup, NavigableString


def get_bands():
    print("Gotta go get a dictionary by year from https://www.houseofmetal.se/en/history/")

    source = requests.get('https://www.houseofmetal.se/en/history/').text
    soup = BeautifulSoup(source, 'html.parser')
    elements = soup.select('div.et_pb_text_inner')
    bandsByYear = {}
    for element in elements:
        year = element.find('strong')

        if (year == None):
            continue

        bands = element.find('p')

        bandList = []
        for b in bands:
            if (isinstance(b, NavigableString)):
                bandList.append(b)

        bandsByYear[year.text] = bandList

    return bandsByYear


def print_bands(bands_by_year):
    for year, bands in bands_by_year.items():
        print(year)
        for band in bands:
            print(band)


if __name__ == '__main__':
    bands_by_year = get_bands()
    print_bands(bands_by_year)
