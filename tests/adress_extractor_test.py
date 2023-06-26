import unittest
from bs4 import BeautifulSoup
import re


import sys
sys.path.append("c:\\Users\\david\\Desktop\\Buisness_stuff\\localdominator\\Scrapper_demo_py\\service")

print(sys.path)

from google_serp_scrapper import GoogleSERPScraper

def extract_address(html):
    w4efsd_outer = html.find_all('div', class_='W4Efsd')

    if len(w4efsd_outer) >= 2:
        w4efsd_inner = w4efsd_outer[1].find('div', class_='W4Efsd')
        
        if w4efsd_inner:
            spans = w4efsd_inner.find_all('span')
            for span in spans:
                if span.get('aria-hidden') == "true" and span.text == '·':
                    next_span = span.find_next_sibling('span')
                    if next_span:
                        return next_span.text
    return None

class TestExtractAddress(unittest.TestCase):
    
    def test_extract_address(self):
        sample_html = '''
        <div class="UaQhfb fontBodyMedium"><div class="NrDZNb"><div class="dIDW9d"></div><span class="HTCGSb"></span><div class="qBF1Pd fontHeadlineSmall ">Dan Ryan Productions - Durham Magic shop, Tricks | Face paint, Clown supplies Ontario</div> <span class="muMOJe"></span></div><div class="section-subtitle-extension"></div><div class="W4Efsd"><div class="AJB7ye"><span class="wZrhX"></span> <span class="e4rVHe fontBodyMedium"><span role="img" class="ZkP5Je" aria-label="4.7 stars 7 Reviews"><span class="MW4etd" aria-hidden="true">4.7</span><div class="QBUL8c "></div><div class="QBUL8c "></div><div class="QBUL8c "></div><div class="QBUL8c "></div><div class="QBUL8c vIBWLc "></div><span class="UY7F9" aria-hidden="true">(7)</span></span></span></div></div><div class="W4Efsd"><div class="W4Efsd"><span><span>Magic store</span></span><span> <span aria-hidden="true">·</span> <span>42 MacDermott Dr</span></span></div><div class="W4Efsd"><span><span><span style="font-weight:400;color:rgba(24,128,56,1.00);">Open 24 hours</span></span></span><span> <span aria-hidden="true">·</span> <span>+1 416-418-8544</span></span></div></div></div>
        '''
        

        soup = BeautifulSoup(sample_html, 'html.parser')
        result = extract_address(soup)
        self.assertEqual(result, "42 MacDermott Dr")

if __name__ == '__main__':
    unittest.main()