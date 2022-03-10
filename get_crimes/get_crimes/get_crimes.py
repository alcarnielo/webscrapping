#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 13:18:45 2022
@author: alvaro

This program was created to automatically collect the crimes registered by the
São Paulo State Military Police in the site:
    http://www.ssp.sp.gov.br/transparenciassp/

Version control:
    /           2022-01-30  developping version
                                Improvements:
                                    - NA
    1.0         2022-03-06  First release
                                Improvements:
                                    - /

Improvements:
    - run selenium on headless mode
    - check if it is possible to avoid selenium on this webpage to improve the 
    extraction time.
    - Generalize the function iterate_page to use also on the data extractio (?)

"""
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (TimeoutException, StaleElementReferenceException, 
                                        ElementClickInterceptedException, NoSuchElementException)

def iterate_page(driver, blk_class_name, btn_class_name, iterable):
    """
    This function performs an iteration over the page that is intent to collect 
information

    Parameters
    ----------
    blk_class_name : str
        The class name that is intent to be find
        Note:
            The search is done by CSS_SELECTOR because the class_name that of
            interest present space or separators on it
        
    btn_class_name : str
        The class name that is intent to be find
        
    iterable : selenium.webdriver element
        Element that will be manipulated on the function

    Returns
    -------
    btn_iterable : selenium.webdriver element
        Button to download the documents

    """
    count = 0
    while count < 10:
        try:
            iterable.click()
                        
            blk_iterable = driver.find_element(By.CSS_SELECTOR, blk_class_name)
            btn_iterable = blk_iterable.find_elements(By.CLASS_NAME, btn_class_name)                    
            
            count = 999
            
            return btn_iterable
        except StaleElementReferenceException:
            count+=1
            time.sleep(3)
            
        except ElementClickInterceptedException:
            count+=1
            time.sleep(3)

def refresh_items(driver, blk_class_name, btn_class_name):
    """
    This function refreshes the site items after finishing the iteration. 
    
    It necessary to refresh the items of the site because, when some iteration 
is performed, it is not possible to interact with elements that have been lost.
Them, to make possible access these elements agaim, it is necessary to interact 
with the items.

    Parameters
    ----------
    driver : selenium.webdriver element
        Selenium webdriver element 
        
    blk_class_name : str
        The class name that is intent to be find
        Note:
            The search is done by CSS_SELECTOR because the class_name that of
            interest present space or separators on it
        
    btn_class_name : str
        The class name that is intent to be find

    Returns
    -------
    btn_iterable : selenium.webdriver element
        Refreshed selenium.webdriver iterables

    """
    blk_iterable = driver.find_element(By.CSS_SELECTOR, blk_class_name)
    btn_iterable = blk_iterable.find_elements(By.CLASS_NAME, btn_class_name) 
    return btn_iterable

def main():
    """
    This code navigates through the SSP-SP (Secretaria de Segurança Puplica do
Estado de São Paulo) site to collect all king of crime reisters.

    Notes:
        I didn't managed to perform a download with Firefox, only with Chrome

    Returns
    -------
    None.

    """
    # SSP site
    url = 'https://www.ssp.sp.gov.br/transparenciassp/'
    t = 3
    
    # Set Google Chrome options to avoid the download pop-up.
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': '/home/alvaro/Documentos/Alvaro/Estudos_Python/get_crimes'}
    options.add_experimental_option('prefs',prefs)
    
    # open the navigator
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    
    # find all crimes classifications and extract the texts from their buttons
    crime_class = driver.find_elements(By.CSS_SELECTOR, '*[class^="btnNat dynWidth block"')
    crime_class_text = [crime_class[i].text for i in  range(len(crime_class))]
    
    # Loop on the crime buttons
    for c in range(len(crime_class_text)):
        if (crime_class[c].text == 'NOTA EXPLICATIVA' or
            crime_class[c].text == 'TAXA DE HOMICÍDIO' or
            crime_class[c].text == 'ESTATÍSTICA' or
            crime_class[c].text == 'MORTE DECORRENTE DE INTERVENÇÃO POLICIAL' or
            crime_class[c].text == ''):
            # These buttons must be avoided because:
            #     1 - The button doen't have the kind of information we are 
            #         looking for, or
            #     2 - The link is crashed 
            #           (MORTE DECORRENTE DE INTERVENÇÃO POLICIAL)
            pass
        
        else:
            # Get the years from the register
            print(crime_class[c].text)
            years_btn = iterate_page(driver,
                                     '*[class^="nav nav-tabs anoNav"',
                                     'block',
                                     crime_class[c])
            # Loop on the registered years
            for y, year in enumerate(years_btn):
                # Get the months from the register
                months_btn = iterate_page(driver,
                                          '*[class^="nav nav-pills mesNav"',
                                          'block',
                                          years_btn[y])
                
                # Loop on the registered months
                for m, month in enumerate(months_btn):
                    count = 0
                    
                    # This try is a process I created to avoid the timeout and 
                    # reduce the chance of crash the code
                    # Note:
                    #   I kept the possibility to stop the code if it fails 
                    #   after a great amount of tries
                    while count < 10:
                        try:
                            months_btn[m].click()
                            try:
    
                                btn_export = driver.find_element(By.ID, 'cphBody_ExportarBOLink').click()
                            
                            except NoSuchElementException:
                                # this try is necessary because the button in "REGISTRO DE ÓBITOS" presents a different ID.
                                btn_export = driver.find_element(By.ID, 'cphBody_ExportarIMLButton').click()
                                
                            
                            months_btn = refresh_items(driver,
                                                       '*[class^="nav nav-pills mesNav"', 
                                                       'block')
                            
                            count = 999
    
                        except StaleElementReferenceException:
                            count+=1
                            time.sleep(3)
    
                        except ElementClickInterceptedException:
                            count+=1
                            time.sleep(3)
    
                years_btn = refresh_items(driver,
                                          '*[class^="nav nav-tabs anoNav"', 
                                          'block')
    
            crime_class = driver.find_elements(By.CSS_SELECTOR, '*[class^="btnNat dynWidth block"')
    driver.close()
    

if __name__ == '__main__':
    main()
