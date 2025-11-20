# utils.py
import re
import pandas as pd
from datetime import datetime



def extract_longest_number(text):
    if len(text) < 15:
        re.search(r'\D', text)
        
        mobile_pattern = r'8[1-9]\d{8,10}'
        mobile_matches = re.findall(mobile_pattern, text)
        
        if mobile_matches:
            print('here 2')
            return mobile_matches[0]
        else:
            return None 

    else: 
        if len(text) >= 15:
            print('here the suns')
            text_itt = text[-11:]
            text_ret = '62{}'.format(text_itt)
         
            return text_ret
        else:
            return None

# utils.py
import re

def extract_numbers(text):
    """Extract ALL numbers from text (URL or plain number)"""


def map_columns(df):
    mapping = {}
    cols = [col.lower().replace(' ', '').replace('-', '').replace('/', '') for col in df.columns]
    col_map = dict(zip(df.columns, cols))

    for orig, lower in col_map.items():
        if any(k in lower for k in ['sn', 'serial']):
            mapping['sn'] = orig
        elif 'iccid' in lower:
            mapping['iccid'] = orig
        elif any(k in lower for k in ['msisdn', 'phone', 'number']):
            mapping['msisdn'] = orig
        elif 'imsi' in lower:
            mapping['imsi'] = orig
    return mapping