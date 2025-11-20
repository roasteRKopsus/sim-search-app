# utils.py
import re
import pandas as pd
from datetime import datetime

# def extract_longest_number(text):
#     numbers = re.findall(r'\d+', str(text))
#     pattern = r'08[1-9]\d{8,10}'
#     print(pattern)
#     if not numbers:
#         return re.findall(r'\d{10,}', str(text))
#         # return None
#     return max(numbers, key=len)

def extract_longest_number(text):
    if len(text) < 15:
        re.search(r'\D', text)
        # Case 1: Text is present (e.g., a URL) -> Find the mobile number
        
        # Regex for Indonesian mobile number (08[1-9] followed by 8-10 digits)
        mobile_pattern = r'8[1-9]\d{8,10}'
        mobile_matches = re.findall(mobile_pattern, text)
        
        if mobile_matches:
            print('here 2')
            return mobile_matches[0]
        else:
            # Fallback if text is present but no 08-number is found
            return None 

    else:
        # Case 2: Text is purely numeric -> Extract the fixed segment '016732045'
        
        # We assume the required number '016732045' is at a fixed position
        # in the pure number string '0015000016732045'.
        # '001500' (6 chars) + '016732045' (9 chars)
        # The required segment starts at index 6 and is 9 digits long.
        
        if len(text) >= 15:
            print('here the suns')
            text_itt = text[-11:]
            text_ret = '62{}'.format(text_itt)

            # Extract the 9 characters starting at index 6
            return text_ret
        else:
            return None

# utils.py
import re

def extract_numbers(text):
    """Extract ALL numbers from text (URL or plain number)"""
      # 10+ digits = phone/ICCID/SN

def map_columns(df):
    mapping = {}
    # Normalize by removing spaces, dashes, slashes for better matching
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