import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime

options = webdriver.ChromeOptions()
path_to_save = './'
prefs = {"download.default_directory": path_to_save,
        "safebrowsing.enabled": "false",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path='./chromedriver', options=options)

driver.get('https://beco.club/becoindex')

base_xpath = '(//div[@id="budgets"]/div)'
n_divs = len(driver.find_elements(By.XPATH, base_xpath))


CIAS = []
SITES_ALL = []
PRICES_ALL = []
DIFFS_ALL = []

for i in range(1, n_divs+1):
    xpath = base_xpath + '[{}]'.format(i)
    cia = driver.find_elements(By.XPATH, xpath + '/div')[0].text
    CIAS.append(cia)
    table_xpath = xpath + '/table'
    complete_table = driver.find_elements(By.XPATH, xpath + '/table/tbody/tr')
    nrows = len(complete_table)
    sites = []
    prices = []
    diffs = []
    for i in range(nrows):
        sites.append(complete_table[i].find_element(By.XPATH, './td/span[@class="buyer"]').text)
        prices.append(complete_table[i].find_element(By.XPATH, './td/div/span[@class="price"]').text)
        diffs.append(complete_table[i].find_element(By.XPATH, './td/div/span[@class="diff "]').text)
    SITES_ALL.append(sites)
    PRICES_ALL.append(prices)
    DIFFS_ALL.append(diffs)

data = pd.DataFrame(PRICES_ALL).T
data.columns = CIAS
data.index = SITES_ALL[0]

data = data.fillna('R$ 0,0')

for col in data.columns:
    data[col] = [tt[-1] if tt != None else 0 for tt in data[col].str.split(" ")]
    data[col] = data[col].str.replace(',', '.').astype(float)

today = datetime.now().strftime("%d-%m-%Y")
data = data.reset_index()
data.columns = ['site', 'latampass', 'smiles', 'latamplat', 'tapmilesego', 'tudoazul']
data.index = [today]*data.shape[0]

if os.path.isfile('./cotacao.csv'):
    print('ok')
    df = pd.read_csv('./cotacao.csv', index_col=0)
    data = pd.concat([df, data], axis=0)

data.to_csv('cotacao.csv')

print("Data collected and saved!!")

driver.quit()