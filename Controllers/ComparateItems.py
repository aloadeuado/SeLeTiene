from flask import request, jsonify
from app import app
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

@app.route('/api/getItemsComparate', methods=['GET'])
def getItemsComparate():
    # Crea una instancia del navegador
    driver = webdriver.Chrome()   
    response = driver.get('https://www.exito.com/?gclid=CjwKCAjw586hBhBrEiwAQYEnHR40dtblrsdx1_NwSzD2FA4j01gCpio6Vkdv5M555gEAzi2ZuvAX0xoCDI8QAvD_BwE&gclsrc=aw.ds')
    inputs = driver.find_elements(By.XPATH, '//input')
    buttons = driver.find_elements(By.XPATH, '//button')
    claseInput = inputs[0].get_attribute("class")
    claseButton = buttons[5].get_attribute("class")
    driver.execute_script(f'document.getElementsByClassName("{claseInput}")[0].value = "pollo"')
    buttons[1].click
    #driver.execute_script(f'document.getElementsByClassName("{claseButton}")[0].click();')
    #print(response.content)
    return {"status": "completo"}, 200