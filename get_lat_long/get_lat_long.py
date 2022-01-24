#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 19:33:16 2022

@author: alvaro

    This code was created to enable an address latitude and longitude extration 
from Goolge maps.

Version control:
Date        Rele
2022/01/19  /       - Original release
2022/01/23  1       - Solving a bug
                    Note:
                        - before this release, it was possible to run the code 
                        and obtain the wrong latitude and longitude to the given 
                        address. This revision was intent to solve it.

Notes for future improvements:
    1 - Enable partial correspondence
        Examples for parcial correspondence
            ", 0, BRASILANDIA, S.PAULO, SP"
            "RUA MONSENHOR ARISTÍDES SILVEIRA LEITE, 486, DISTRITO INDUSTRIAL, BEBEDOURO, SP"
            "ESTRADA vicinal benedito antonio brisola, 1, AREA RURAL, PILAR DO SUL, SP"
            ", 0, JARDIM PAULISTA, BARRINHA, SP"
            "ESTRADA saltinho maq arroz, 1, JD NOVA MERCEDES, CAMPINAS, SP"
            ", 0, ARUAN, CARAGUATATUBA, SP"
            "RUA JOSÉ R DE LIMA, 3207, VILA ESPERANÇA, PRESIDENTE EPITACIO, SP"
            "RODOVIA BR 381, 30, CHACARA DA COLINA, ATIBAIA, SP"
            ", 0, CUMBICA, GUARULHOS, SP"
            ", 0, JARDIM SAO PEDRO, AVARE, SP"
            "ALAMEDA CAMPINAS, 1533, JARDIM PAULISTA, S.PAULO, SP"

"""
import openpyxl
import pandas as pd
import time

import re
from unicodedata import normalize
from nltk.tokenize import RegexpTokenizer

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, InvalidElementStateException, NoSuchElementException, ElementNotInteractableException

def get_lat_long(driver, search_key, t_hold = 0.3):
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

    t_hold : float
        Value of trashold for cosine similarity comparison methodology
        The default is 0.3 based on developement tests.
        
    Returns
    -------
    TYPE
        lat :   float
            Latitude value
        long :  float
            Longitude value
        
        Note:
            If the value is not precise, the code will return 999
    '''
    slp = 1
    max_count =25
    cont_1 = 0
    while cont_1 <= max_count:      # this loop intents to surpass page loading time 
        driver.get('https://www.google.com.br/maps/')

        cur_url = driver.current_url
        inp = driver.find_element(By.ID,'searchboxinput')
        inp.clear()
        
        inp.send_keys(search_key)
        inp.send_keys(Keys.ENTER)
        
        # prepare search to compare
        search_inp = ' '.join(preprare_str(search_key))
        cosine_sim = 0
        cont_2 = 0
        while cosine_sim <  t_hold and cont_2 < max_count :
            try:
                # getting result text
                search_result = driver.find_element(By.CSS_SELECTOR, '*[class^="x3AX1-LfntMc-header-title"').text
                # prepare search result to compare
                search_result = ' '.join(preprare_str(search_result))
                
                # perform comparison by cosine similarity
                cosine_sim = compare_str(search_inp,search_result)
                # print(f'{cont_2}    {cosine_sim}')
                
                # if cosine_sim < t_hold:   # print debug to understand which are the data lwr than trashold
                    # print('menor')'
                time.sleep(slp)
                cont_2+=1
            except NoSuchElementException:
                time.sleep(slp)
                cont_2+=1

        cont_1 = 999
    
    cont_3 = 0
    while cont_3 <= max_count:
        try:
            new_url = driver.current_url
            regex = re.compile(r'[@][-]{0,1}[0-9]+.[0-9]+,[-]{0,1}[0-9]+.[0-9]+')
            lat, long = regex.findall(new_url)[0].replace('@','').split(',')
            cont_3 = 999
        
        except IndexError:
            cont_3+=1
            time.sleep(slp)
        
        if cosine_sim <  t_hold:
            lat = long = 999
        
    return float(lat), float(long), cosine_sim


def preprare_str(txt):
    """
    This function prepare a given text to be used on a comparison by:
        - remove number;
        - remove punctuation (eg.: ",", ".", ";", ":", "-", etc);
        - remove accentuation (eg. "¨", "`", "´", "^", "~");
        - Lower case the text;
        - tokenize the text to be returned to user

    Parameters
    ----------
    txt : string
        Text to be prepared and tokenized

    Returns
    -------
    tokenized_txt : list
        List of token strings 

    """
    ## preparing input data to comparison
    # creating tokenizer
    tokenizer = RegexpTokenizer((r'[aA-zZ]\w*'))
    # lower case
    new_txt = txt.lower()
    # removing accentuation
    new_txt = normalize('NFKD', new_txt).encode('ASCII','ignore').decode('ASCII')
    # tokenize the address
    tokenized_txt = tokenizer.tokenize(new_txt)
    
    return tokenized_txt
 

def compare_str(txt_1, txt_2):
    """
    This function perform a compareson if the 2 input text are similar using the 
cosine similarity methodology

ref.:
    https://towardsdatascience.com/calculating-string-similarity-in-python-276e18a7d33a
    
    Parameters
    ----------
    txt_1 : string
        Text to be compared
        
    txt_2 : string
        Text to be compared

    Returns
    -------
    TYPE
        csin : float
        The value of cosine comparison methodology between 2 string texts

    """
    vectorizer = CountVectorizer().fit_transform([txt_1,txt_2])
    vectors = vectorizer.toarray()
    
    csin = cosine_similarity(vectors[0].reshape(1,-1),
                             vectors[1].reshape(1,-1))
    
    return csin[0][0]


if __name__ =='__main__':
    # teste 01
    places = pd.read_excel('DadosBO_2021_11(HOMICÍDIO DOLOSO).xls',
                            sheet_name='DadosBO_2021_11(HOMICÍDIO DOLOSO)',
                            engine='xlrd')
    
    
    # places[['BO_INICIADO', 'BO_EMITIDO', 'DATAOCORRENCIA', 'HORAOCORRENCIA',
    #             'DATACOMUNICACAO', 'DATANASCIMENTO']]
    
    addresses = places[['LOGRADOURO', 'NUMERO', 'BAIRRO', 'CIDADE', 'UF']
                        ].fillna('')
    addresses[['LATITUDE', 'LONGITUDE']] = places[['LATITUDE', 'LONGITUDE']]
    #--------------------------------------------------------------------------
    # teste 02
    # places = [", 0, BRASILANDIA, S.PAULO, SP",
    #          "RUA MONSENHOR ARISTÍDES SILVEIRA LEITE, 486, DISTRITO INDUSTRIAL, BEBEDOURO, SP",
    #          "ESTRADA vicinal benedito antonio brisola, 1, AREA RURAL, PILAR DO SUL, SP",
    #          ", 0, JARDIM PAULISTA, BARRINHA, SP",
    #          "ESTRADA saltinho maq arroz, 1, JD NOVA MERCEDES, CAMPINAS, SP",
    #          ", 0, ARUAN, CARAGUATATUBA, SP",
    #          "RUA JOSÉ R DE LIMA, 3207, VILA ESPERANÇA, PRESIDENTE EPITACIO, SP",
    #          "RODOVIA BR 381, 30, CHACARA DA COLINA, ATIBAIA, SP",
    #          ", 0, CUMBICA, GUARULHOS, SP",
    #          ", 0, JARDIM SAO PEDRO, AVARE, SP",
    #          "ALAMEDA CAMPINAS, 1533, JARDIM PAULISTA, S.PAULO, SP"]
    
    # places = [x.split(', ') for x in places]
    # addresses = pd.DataFrame(places, columns=['LOGRADOURO', 'NUMERO', 'BAIRRO', 
    #                                           'CIDADE', 'UF'])

    driver = webdriver.Firefox()
    
    
    data = pd.DataFrame()
    for i in range(addresses.shape[0]):
        
        place = addresses.loc[i,['LOGRADOURO', 'NUMERO', 'BAIRRO', 
                                'CIDADE', 'UF']].tolist()
        to_drop = ['',0,'0',999,'999']
        place = [str(x) for x in place if x not in to_drop]
        place = ', '.join(place)
        loc = {}
        print('')
        print(place)
        lat, long, cosine_sim = get_lat_long(driver, place)
        loc['Place'] = place
        loc['Lat'] = lat
        loc['Long'] = long
        loc['cosine_sim'] = cosine_sim
        print(f'{lat}       {long}')
        
        data = data.append(loc, ignore_index=True)
