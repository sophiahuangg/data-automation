import requests
from bs4 import BeautifulSoup
import time

print('Beginning file download with requests')

#using requests to download code from: https://stackabuse.com/download-files-with-python/


url = 'https://www.dof.ca.gov/Forecasting/Demographics/Estimates'
r = requests.get(url)
html = r.text

soup = BeautifulSoup(html, 'html.parser')

a_tags = soup.select('h2 + ul > li > ul > li > a')

e4_hrefs = []
for a_tag in a_tags:
    time.sleep(6)
    if 'e-4' or 'E-4' in a_tag.get('href'):
        e4_hrefs.append(a_tag.get('href'))

print('e4 links = ', e4_hrefs)


#have not downloaded the files yet and SSL Open Certificate issue still there