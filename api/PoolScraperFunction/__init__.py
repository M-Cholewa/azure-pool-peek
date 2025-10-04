import datetime
import logging
import os
import requests
from bs4 import BeautifulSoup
from azure.data.tables import TableServiceClient

# Logika Timer Trigger musi akceptować obiekt timer
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info('Python timer trigger function started at %s', utc_timestamp)

    try:
        # 1. Scrapowanie Strony
        # UWAGA: URL strony basenu musi być poprawny!
        POOL_URL = "https://twoj-basen-url.com/licznik"
        response = requests.get(POOL_URL)
        soup = BeautifulSoup(response.content, 'html.parser')

        # TUTAJ MUSISZ ZMIENIĆ SELEKTOR HTML
        # Znajdź element HTML, który zawiera liczbę osób, np. po id="licznik"
        counter_element = soup.find(id="licznik")
        
        if counter_element:
            people_count = int(counter_element.text.strip())
        else:
            logging.error("Nie znaleziono elementu licznika.")
            return

        # 2. Zapis do Azure Table Storage
        # Wymaga zmiennej środowiskowej 'AZURE_STORAGE_CONNECTION_STRING'
        connection_string = os.environ["AzureWebJobsStorage"] 
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service_client.get_table_client(table_name="PoolCounterData")

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        entity = {
            # PartitionKey: Użyj daty, aby łatwo pobierać dane dzienne
            "PartitionKey": current_date, 
            # RowKey: Użyj odwróconego timestampu, aby sortowanie było chronologiczne
            "RowKey": str(datetime.datetime.now().timestamp()), 
            "PeopleCount": people_count,
            "Timestamp": current_time
        }

        table_client.create_entity(entity=entity)
        logging.info("Zapisano dane: Liczba osób: %d", people_count)

    except Exception as e:
        logging.error("Wystąpił błąd podczas scrapowania/zapisu: %s", str(e))