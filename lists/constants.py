# Currencies
class Currency:
    def __init__(self, name, abbreviation, slice, format):
        self.abbreviation = abbreviation
        self.name = name
        self.string_slice = slice
        self.string_format = format

    def __str__(self):
        return '{name} ({abbreviation})'.format(abbreviation=self.abbreviation, name=self.name)

NZD = Currency(name='New Zealand Dollars', abbreviation='NZD', slice=slice(3, None, None), format='NZ${price:.2f}')
USD = Currency(name='USA Dollars', abbreviation='USD', slice=slice(3, None, None), format='US${price:.2f}')
GBP = Currency(name='Great Britain Pounds', abbreviation='GBP', slice=slice(1, None, None), format='£{price:.2f}')
CZK = Currency(name='Czech Koruna', abbreviation='CZK', slice=slice(0, -3, None), format='{price:.2f} Kč')

CURRENCIES = {
    'NZD': NZD,
    'USD': USD,
    'GBP': GBP,
    'CZK': CZK,
}
