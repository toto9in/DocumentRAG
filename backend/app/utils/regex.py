import re

def extract_value(s):
    match = re.search(r'R\$ [\dX\.]*,[\dX]{2}', s)
    if match:
        return match.group(0)
    else:
        return None

def convert_currency_to_number(currency):
    # Remove os caracteres não numéricos
    number = re.sub(r'[^\d,]', '', currency)
    # Substitui a vírgula por um ponto
    number = number.replace(',', '.')
    # Converte a string em um número
    number = float(number)
    return number

