# -*coding:utf8 *-
"""
author : Jeremy Surget and Sylvain Jiang
pylint 8.91/10
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup


def scrap_ev(url, proxy):
    """
    scraping des données des véhicules electriques
    depuis un site web
    return : une dataframe des données
    """

    request = requests.get(url, proxies=proxy) # on requete la page

    #on parse la page en utilisant le parser html par defaut de python
    soup = BeautifulSoup(request.text, "html.parser")

    #on créer une liste contenant toutes les données des voitures contenu chacune
    #dans un bloc div avec la classe data-wrapper
    ev_data_container = soup.find_all('div', class_="data-wrapper")

    ev_names = []
    ev_batteries = []
    ev_number_of_seats = []
    ev_accelerations = []
    ev_top_speeds = []
    ev_ranges = []
    ev_efficiencies = []
    ev_fastcharges = []
    ev_prices = []

    for ev_container in ev_data_container:
        #extrait le nom grace à la hierarchy du html
        ev_name = ev_container.h2.a.text

        #extrait grace à une recherche sur la class du span
        ev_battery = float(ev_container.find('span', class_='battery').text)
        ev_nb_of_seats = int(ev_container.find('span', attrs={'title':'Number of seats'}).text)

        #acceleration donne 8.0 sec donc on split pour prendre que le nombre et convert en float
        ev_acceleration = float((ev_container.find('span', class_='acceleration').text).split(' ')[0])
        ev_top_speed = int((ev_container.find('span', class_='topspeed').text).split(' ')[0])
        ev_range = int((ev_container.find('span', class_='erange_real').text).split(' ')[0])
        ev_efficiency = float((ev_container.find('span', class_='efficiency').text).split(' ')[0])

        # ev_fastcharge = int(ev_container.find('span', class_ = 'fastcharge_speed hidden').text)
        if ev_container.find('span', class_='fastcharge_speed hidden').text != '':
            ev_fastcharge = int(ev_container.find('span', class_='fastcharge_speed hidden').text)
        else:
            ev_fastcharge = 'N/A'

        if ev_container.find('span', attrs={'title' : 'Price in Germany before incentives'}).text == 'N/A':
            ev_price = 'N/A'
        else:
            #il faut replacer la virgule par un point pour pouvoir convertir en float
            ev_price = float(ev_container.find('span', attrs={'title' : 'Price in Germany before incentives'}).text.split('€')[1].replace(',', '.'))


        ev_names.append(ev_name)
        ev_batteries.append(ev_battery)
        ev_number_of_seats.append(ev_nb_of_seats)
        ev_accelerations.append(ev_acceleration)
        ev_top_speeds.append(ev_top_speed)
        ev_ranges.append(ev_range)
        ev_efficiencies.append(ev_efficiency)
        ev_fastcharges.append(ev_fastcharge)
        ev_prices.append(ev_price)

    #on créer maintenant une dataframe avec nos données
    df_vehicules = pd.DataFrame({
        'name' : ev_names,
        'battery' : ev_batteries,
        'seats' : ev_number_of_seats,
        'acceleration' : ev_accelerations,
        'topspeed' : ev_top_speeds,
        'range' : ev_ranges,
        'efficiency' : ev_efficiencies,
        'fastcharge' : ev_fastcharges,
        'price' : ev_prices
    })

    return df_vehicules



if __name__ == '__main__':
    DATAFRAME = scrap_ev('https://ev-database.org/compare/efficiency-electric-vehicle-most-efficient', proxy={})

    #enfin, on converti notre df en csv (si besoin)
    #dans le projet python nous avons directement utilisé la dataframe
    #plutot que de convertir en csv
    print("converting dataframe to csv local file...")
    DATAFRAME.to_csv('electric_vehicules_dataseeeeeet.csv', sep=';', index=False)
    print("conversion finished")
