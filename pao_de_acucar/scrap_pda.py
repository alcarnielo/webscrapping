#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 16:46:47 2022
@author: alvaro

About:
This code aims to extract all desired products information from an specific 
supermarket site from Brasil.

Version control:
    / -    Original reliese

Notes:
    - Think about create a more general way to extract product information from 
    other supermarket sites (not only Pão de Açucar);

"""
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


def product_extract_pda(produto):
    """
    This function extracts the desired product information from Pão de Açucar
    supermarket.

    Parameters
    ----------
    produto     - str
                Product description to be searched and extracted.

    Raises
    ------
    TimeoutException
        DESCRIPTION.
    StaleElementReferenceException
        DESCRIPTION.

    Returns
    -------
    products_list   - list
                    - List of string containing the product name and its price
                    at the supermarket 
    """
    driver = webdriver.Firefox()
    t=1
    cont = 0
    go=False
    while not go:
        try:
            driver.get('https://www.paodeacucar.com/')
            busca = driver.find_element_by_css_selector('input')
            busca.send_keys(produto)
            body = driver.find_element_by_css_selector('body')
            body.send_keys(Keys.ENTER)
            go=True
        
        except TimeoutException:
            cont+=1
            if cont >10:
                raise TimeoutException('TimeoutException: Fail to load the site')
        
    products_list = []
    
    go = False
    cont = 0
    while not go:
        try:
            products_0 = driver.find_elements_by_css_selector('*[class^="product-cardstyles__Container-sc-1uwpde0-1 hNTkow"')
            products_list+=[item.text for item in products_0]
            go=True
    
        except StaleElementReferenceException:
            cont+=1
            if cont >10:
                raise StaleElementReferenceException('StaleElementReferenceException: The element reference is not available')
    
    go = True
    cont = 0
    while go:
        try:
            products_1 = driver.find_elements_by_css_selector('*[class^="product-cardstyles__Container-sc-1uwpde0-1 hNTkow"')
            if (products_1 == products_0):
                body.send_keys(Keys.PAGE_UP)
                for i in range(5):
                    time.sleep(t)
                    body.send_keys(Keys.PAGE_DOWN)
                cont+=1
                
                if cont > 5:
                    go = False
            
            else:
                products_to_add = [item for item in products_1 if item not in products_0]
                products_list += [item.text for item in products_to_add]
                cont = 0
            products_0 = products_1
            
        except StaleElementReferenceException:
            cont+=1
            if cont >10:    
                raise StaleElementReferenceException('StaleElementReferenceException: The element reference is not available')
    
    driver.close()
    return products_list


def convert_real_to_float(s):
    """
    This function convert price strings to float.

    Parameters
    ----------
    s : str
        String containing the product price.
        Note:
            If the price is "INDISPONÍVEL", the value will be modified to "-1"

    Returns
    -------
    f : float
        Price float number.

    """
    s = s.split('R$')[-1].replace('.','').replace(',','.').replace('INDISPONÍVEL','-1')
    f = float(s)
    return f


def main(produtos):
    """
    This function aims to manage the data extraction of products from the site 
    of a supermarket.

    Parameters
    ----------
    produtos : list
        List of products to be searched and extracted.

    Returns
    -------
    data : list
        List of lists coontaining the extracted data from the product list

    """
    df_search = pd.DataFrame()
    for prod in produtos:
        data = product_extract_pda(prod)
        data = [x.split('\n') for x in data]
        data = pd.DataFrame(data)
              
        df_search['prod_nome'] = data[0]
        df_search['preco_original'] = data[1].map(convert_real_to_float)
                                                  
        preco_novo_1 = data.loc[data[2].str.contains('R\$').fillna(False),2]
        preco_novo_2 = data.loc[data[3].str.contains('R\$').fillna(False),3]
        df_search['preco_com_desconto'] = preco_novo_1.map(convert_real_to_float)
        df_search['preco_com_desconto'] = preco_novo_2.map(convert_real_to_float)
        df_search['prod_busca'] = prod
        
    
    df_search.to_csv('busca_produtos.csv', sep=';')
    
    return data

if __name__ == '__main__':
    produto = ['sadia']
    data = main(produto)