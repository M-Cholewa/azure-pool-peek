import logging
import json
import datetime
import os
from azure.functions import HttpResponse
from azure.data.tables import TableServiceClient, QueryDelimiter

def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Pobranie opcjonalnej daty z parametru (domyślnie: dziś)
        target_date = req.params.get('date') or datetime.datetime.now().strftime("%Y-%m-%d")

        # 1. Odczyt z Azure Table Storage
        connection_string = os.environ["AzureWebJobsStorage"] 
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service_client.get_table_client(table_name="PoolCounterData")

        # Zapytanie filtrujące po PartitionKey (dacie)
        filter_query = f"PartitionKey eq '{target_date}'"
        
        entities = table_client.query_entities(filter=filter_query)

        data = []
        for entity in entities:
            # Tworzenie obiektu przyjaznego dla JSON i wykresu
            data.append({
                "time": entity.get("Timestamp", ""),
                "count": entity.get("PeopleCount", 0)
            })

        # Sortowanie danych po RowKey, aby były chronologiczne
        data.sort(key=lambda x: datetime.datetime.strptime(x["time"], "%H:%M:%S"))

        # 2. Zwrócenie danych jako JSON
        return HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error("Błąd podczas serwowania API: %s", str(e))
        return HttpResponse(
             "Wystąpił błąd serwera podczas pobierania danych.",
             status_code=500
        )