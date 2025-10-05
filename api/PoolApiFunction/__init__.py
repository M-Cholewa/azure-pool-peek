import logging
import json
import datetime
import os
import azure.functions as func
from azure.functions import HttpResponse
from azure.data.tables import TableServiceClient
from zoneinfo import ZoneInfo

def main(req: func.HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Pobranie opcjonalnej daty z parametru (domyślnie: dziś)
        target_date = req.params.get('date') or datetime.datetime.now().strftime("%Y-%m-%d")

        # 1. Odczyt z Azure Table Storage
        connection_string = os.environ["POOL_STORAGE_CONNECTION"] 
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service_client.get_table_client(table_name="poolpeektable")

        # Zapytanie filtrujące po PartitionKey (dacie)
        filter_query = f"PartitionKey eq '{target_date}'"
        
        entities = table_client.query_entities(query_filter=filter_query)

        data = []
        for entity in entities:
            rowkey_str = entity.get("RowKey", "")
            timestamp_float = 0.0
            try:
                # Konwersja RowKey -> timestamp float
                timestamp_float = float(rowkey_str[:10] + "." + rowkey_str[10:]) if len(rowkey_str) > 10 else float(rowkey_str)
                dt = datetime.datetime.fromtimestamp(timestamp_float, tz=datetime.timezone.utc).astimezone(ZoneInfo("Europe/Warsaw"))
                formatted_time = dt.strftime("%d-%m-%Y %H:%M:%S")
            except Exception as e:
                logging.error(f"Błąd konwersji RowKey na timestamp: {e}")
                formatted_time = rowkey_str  # fallback gdyby coś poszło nie tak

            data.append({
                "timestamp_float": timestamp_float,
                "time": formatted_time,
                "count": entity.get("PeopleCount", 0),
                "rowkey": rowkey_str
            })

        # Sortowanie po RowKey numerycznie
        data.sort(key=lambda x: x["timestamp_float"])

        # Do responsa tylko czas i liczba osób
        response_data = [{"time": d["time"], "count": d["count"]} for d in data]

        # 2. Zwrócenie danych jako JSON
        return HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error("Błąd podczas serwowania API: %s", str(e))
        return HttpResponse(
             "Wystąpił błąd serwera podczas pobierania danych.",
             status_code=500
        )