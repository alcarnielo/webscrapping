#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 19:33:16 2022

@author: alvaro
"""
import openpyxl
import pandas as pd
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, InvalidElementStateException, NoSuchElementException, ElementNotInteractableException


def get_lat_long(driver, search_key):
    '''
    This function performs search by the address in the "search_key" input on 
google maps site ("https://www.google.com.br/maps/") and returns the latitude
(lat) and longitude (long) for the given address

    Parameters
    ----------
    driver : selenium webdriver element
        Selenium webdriver element to connect internet and navigate through a 
        given site

    search_key : string
        String containing the adress that is intent to search the latitude and
        longitude directions

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    delay = 15
    slp = 3
    max_count =25
    cont_1 = 0
    while cont_1 <= max_count:
        driver.get('https://www.google.com.br/maps/')
        
        
        # try:
        cur_url = driver.current_url
        inp = driver.find_element(By.ID,'searchboxinput')
        inp.clear()
        
        inp.send_keys(search_key)
        inp.send_keys(Keys.ENTER)
        time.sleep(slp)
        cont_1 = 999
                
        # except:
            # This section will be updated according possible errors
        print()
    
    cont_2 = 0
    while cont_2 <= max_count:
        try:
            new_url = driver.current_url
            regex = re.compile(r'[@][-]{0,1}[0-9]+.[0-9]+,[-]{0,1}[0-9]+.[0-9]+')
            lat, long = regex.findall(new_url)[0].replace('@','').split(',')
            cont_2 = 999
        
        except IndexError:
            cont_2+=1
            time.sleep(slp)
        
    return float(lat), float(long)


if __name__ =='__main__':
    places = pd.read_excel('DadosBO_2021_11(HOMICÍDIO DOLOSO).xls',
                            sheet_name='DadosBO_2021_11(HOMICÍDIO DOLOSO)',
                            engine='xlrd')
    
    
    # places[['BO_INICIADO', 'BO_EMITIDO', 'DATAOCORRENCIA', 'HORAOCORRENCIA',
    #             'DATACOMUNICACAO', 'DATANASCIMENTO']]
    
    adresses = places[['LOGRADOURO', 'NUMERO', 'BAIRRO', 'CIDADE', 'UF']
                       ].fillna('')
    adresses[['LATITUDE', 'LONGITUDE']] = places[['LATITUDE', 'LONGITUDE']
                                                  ].fillna(0)
    
    

    driver = webdriver.Firefox()
    
    
    data = pd.DataFrame()
    for i in range(adresses.shape[0]):
        
        place = adresses.loc[i,['LOGRADOURO', 'NUMERO', 'BAIRRO', 
                                'CIDADE', 'UF']].tolist()
        place = [str(x) for x in place if x!= '' or x!=0]
        place = ', '.join(place)
        loc = {}
        print('')
        print(place)
        lat, long = get_lat_long(driver, place)
        loc['Place'] = place
        loc['Lat'] = lat
        loc['Long'] = long
        print(f'{lat}       {long}')
        
        data = data.append(loc, ignore_index=True)
