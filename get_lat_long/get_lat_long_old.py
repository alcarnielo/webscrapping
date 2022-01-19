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
    delay = 15
    slp = 3
    max_count =25
    cont_1 = 0
    while cont_1 <= max_count:
        driver.get('https://www.google.com.br/maps/')
        
        
        try:
            cur_url = driver.current_url
            inp = driver.find_element_by_id('searchboxinput')
            inp.clear()
            
            inp.send_keys(search_key)
            inp.send_keys(Keys.ENTER)
            time.sleep(slp)
            cont_1 = 999
                
        except:
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

def get_lat_long_old(driver, search_key):
    
    delay = 15
    slp = 1
    max_count= 25
    go = False
    cont_1 = 0
    while cont_1 <= max_count:
        driver.get('https://www.google.com.br/maps/')
        
        go = False
        cont=0
        while not go:
            try:
                inp = driver.find_element_by_id('searchboxinput')
                inp.clear()
                go = True
                
            except InvalidElementStateException:
                cont+=1
                time.sleep(slp)
                if cont > max_count:
                    raise InvalidElementStateException('InvalidElementStateException: Unable to locate element')
                    
        
        cont_2=0
        while cont_2 <= max_count:
            try:
                cur_url = driver.current_url
                inp = driver.find_element_by_id('searchboxinput')
                inp.send_keys(search_key)
                inp.send_keys(Keys.ENTER)
                
                # Wait page to load
                WebDriverWait(driver, delay).until(EC.url_changes(cur_url))
                
                # Wait element show
                directions = driver.find_element_by_css_selector('*[class^="siAUzd-neVct siAUzd-neVct-yIbDgf-fozPsf-t6UvL siAUzd-neVct-Q3DXx-BvBYQ siAUzd-neVct-Q3DXx-horizontal"')
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                                                                                    '*[class^="siAUzd-neVct siAUzd-neVct-yIbDgf-fozPsf-t6UvL siAUzd-neVct-Q3DXx-BvBYQ siAUzd-neVct-Q3DXx-horizontal"')))
                count_1 = count_2 = max_count
            
            except TimeoutException:
                cont_2+=1
                print('')
                print('TimeoutException')
                print(cont_2)
                time.sleep(slp)
                if cont_2 > max_count:
                    raise TimeoutException('TimeoutException: wait to long to get information')
                    
            except InvalidElementStateException:
                cont_2+=1
                print('')
                print('InvalidElementStateException')
                print(cont_2)
                time.sleep(slp)
                if cont_2 > max_count:
                    raise InvalidElementStateException('InvalidElementStateException: Element is disabled: <input id="searchboxinput"') 
    
            except ElementNotInteractableException:
                cont_2+=1
                print('')
                print('ElementNotInteractableException')
                print(cont_2)
                time.sleep(slp)
                if cont_2 > max_count:
                    raise ElementNotInteractableException('ElementNotInteractableException: Element is not reachable by keyboard"') 
                                    
            except NoSuchElementException:
                cont_2+=1
                print('')
                print('NoSuchElementException')
                print(cont_2)
                time.sleep(slp)
                # inp = driver.find_element_by_id('searchboxinput')
                # inp.clear()
                # driver.get('https://www.google.com.br/maps/')
                # # Wait page to load
                # WebDriverWait(driver, delay).until(EC.url_changes(cur_url))
                
                # # Wait element show
                # WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 
                #                                                                     'searchboxinput')))
                
                if cont_2 > max_count:
                    raise NoSuchElementException('NoSuchElementException: Unable to locate element')
        
        cont_1 +=1
        
    go = False
    cont=0
    while not go:
        try:
            new_url = driver.current_url
            lat,long = new_url.split('@')[1].split(',')[:2]
            
            go = True
            
        except:
            cont+=1
            time.sleep(slp)
            if cont > max_count:
                print()

                
    return float(lat), float(long)


    
    

def main():
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
    return data

if __name__ =='__main__':
    data = main()
