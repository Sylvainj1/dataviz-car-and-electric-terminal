# -*coding:utf8 *-
import requests
import pandas as pd
from bs4 import BeautifulSoup


def scrap_EV(url):

    # url = urllib.request.urlopen(url)
    # data = url.read().decode('utf-8')
    request = requests.get(url) # on requete la page
    soup = BeautifulSoup(request.text,"html.parser") #on parse la page en utilisant le parser html par defaut de python
    ev_data_container = soup.find_all('div', class_ = "data-wrapper") # on créer une liste contenant toutes les données des voitures contenu chacune 
    # dans un bloc div avec la classe data-wrapper

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
        ev_name = ev_container.h2.a.text #extrait le nom grace à la hierarchy du html
        ev_battery = float(ev_container.find('span', class_ = 'battery').text) #extrait grace à une recherche sur la class du span
        ev_nb_of_seats = int(ev_container.find('span', attrs = {'title':'Number of seats'}).text)
        ev_acceleration = float((ev_container.find('span', class_ = 'acceleration').text).split(' ')[0]) #acceleration donne 8.0 sec donc on split pour prendre que le nombre et convert en float
        ev_top_speed = int((ev_container.find('span', class_ = 'topspeed').text).split(' ')[0])
        ev_range = int((ev_container.find('span', class_ = 'erange_real').text).split(' ')[0])
        ev_efficiency = float((ev_container.find('span', class_ = 'efficiency').text).split(' ')[0])
        
        # ev_fastcharge = int(ev_container.find('span', class_ = 'fastcharge_speed hidden').text)
        if ev_container.find('span', class_ = 'fastcharge_speed hidden').text != '':
            ev_fastcharge = int(ev_container.find('span', class_ = 'fastcharge_speed hidden').text)
        else:
            ev_fastcharge = 'N/A'

        if ev_container.find('span', attrs = {'title' : 'Price in Germany before incentives'}).text == 'N/A':
            ev_price = 'N/A'
        else:
            ev_price = float(ev_container.find('span', attrs = {'title' : 'Price in Germany before incentives'}).text.split('€')[1].replace(',','.')) #il faut replacer la virgule par unpoint pour pouvoir convertir en float


        ev_names.append(ev_name)
        ev_batteries.append(ev_battery)
        ev_number_of_seats.append(ev_nb_of_seats)
        ev_accelerations.append(ev_acceleration)
        ev_top_speeds.append(ev_top_speed)
        ev_ranges.append(ev_range)
        ev_efficiencies.append(ev_efficiency)
        ev_fastcharges.append(ev_fastcharge)
        ev_prices.append(ev_price)

    # on créer maintenant une dataframe avec nos données
    df = pd.DataFrame({
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

    #enfin, on converti notre df en csv
    print("converting dataframe to csv local file...")
    df.to_csv('electric_vehicules_dataset', sep = ';', index= False)
    print("conversion finished")



def main(url):
    scrap_EV(url)
    return None


if __name__ == '__main__':
    main('https://ev-database.org/compare/efficiency-electric-vehicle-most-efficient')