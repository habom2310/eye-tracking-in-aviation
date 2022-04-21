from pyairtable import Table


class AirTableClient:
    def __init__(self, api_key, base_id, table):
        self.client = Table(api_key, base_id, table)

    def add_row(self, row):
        self.client.create(row)