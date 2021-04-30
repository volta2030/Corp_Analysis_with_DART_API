import xml.etree.ElementTree as ET
import os

tree = ET.parse(os.path.join(os.path.abspath(''),'corp_num', 'CORPCODE.xml'))
root = tree.getroot()

def find(find_name):
    for country in root.iter("list"):
        if country.findtext("corp_name") == find_name:
            return country.findtext("corp_code"), country.findtext("stock_code")
