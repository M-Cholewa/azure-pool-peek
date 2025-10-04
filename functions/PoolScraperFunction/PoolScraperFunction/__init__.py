# import datetime
# import logging
# import os
# import requests
# from bs4 import BeautifulSoup
# from azure.data.tables import TableServiceClient
# # Import 'func' jest wymagany w Azure Functions w Pythonie
# import azure.functions as func 

# # Logika Timer Trigger musi akceptować obiekt timer
# def main(mytimer: func.TimerRequest) -> None:
#     utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
#     logging.info('Python timer trigger function started at %s', utc_timestamp)

#     try:
#         # 1. Scrapowanie Strony
#         POOL_URL = "https://gosirbochnia.pl/api/index.php"
#         logging.info("Pobieranie danych z URL: %s", POOL_URL)
        
#         response = requests.get(POOL_URL)
#         # Użycie 'html.parser' jest wystarczające
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # --- ZMODYFIKOWANA LOGIKA PARSOWANIA ---
#         # Znajdź pierwszy (i jedyny) tag <h3>
#         counter_element = soup.find('h3')
        
#         if counter_element:
#             # 1. Pobierz tekst np. "8 osób"
#             raw_text = counter_element.text.strip()
            
#             # 2. Wyodrębnij tylko cyfry z tekstu
#             # Użycie list comprehension/join pozwala na usunięcie wszystkich niecyfrowych znaków
#             people_count_str = ''.join(filter(str.isdigit, raw_text))
            
#             if people_count_str:
#                 people_count = int(people_count_str)
#             else:
#                 logging.error("Nie znaleziono liczby w tagu <h3>. Surowy tekst: %s", raw_text)
#                 return
#         else:
#             logging.error("Nie znaleziono tagu <h3> na stronie.")
#             return

#         # 2. Zapis do Azure Table Storage
#         # Zmienna środowiskowa powinna być ustawiona w konfiguracji Function App
#         connection_string = os.environ.get("POOL_STORAGE_CONNECTION") 
        
#         if not connection_string:
#             logging.error("Brak zmiennej środowiskowej POOL_STORAGE_CONNECTION.")
#             return

#         table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
#         # Używamy nazwy tabeli 'poolpeektable'
#         table_client = table_service_client.get_table_client(table_name="poolpeektable")

#         # Używamy datetime.now() bez utc, ponieważ RowKey jest oparty o timestamp
#         now = datetime.datetime.now()
#         current_date = now.strftime("%Y-%m-%d")
#         current_time = now.strftime("%H:%M:%S")

#         entity = {
#             # PartitionKey: Data (dla łatwego filtrowania dziennego)
#             "PartitionKey": current_date, 
#             # RowKey: Timestamp (dla unikalności i naturalnego porządku)
#             "RowKey": str(now.timestamp()).replace('.', ''), # Usuwamy kropkę z timestampu, by był poprawnym RowKey
#             "PeopleCount": people_count,
#             "Timestamp": current_time
#         }

#         # Tworzymy nową encję w Table Storage
#         table_client.create_entity(entity=entity)
#         logging.info("Sukces! Zapisano dane: Liczba osób: %d", people_count)

#     except Exception as e:
#         logging.error("Krytyczny błąd podczas scrapowania/zapisu: %s", str(e))



import logging
import datetime
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    try:
        utc = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        logging.info("Timer trigger fired at %s", utc)

        if mytimer.past_due:
            logging.warning("Timer is past due!")

        # TODO: przenieś ciężkie importy (requests, bs4, azure.data.tables) tutaj
        # import requests
        # from bs4 import BeautifulSoup
        # from azure.data.tables import TableServiceClient

        # ...tutaj twoja logika scrapowania i zapisu...
    except Exception:
        logging.exception("Unhandled exception in PoolScraperFunction")