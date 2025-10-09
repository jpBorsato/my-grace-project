import os
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def query(query_object):
    with connection.cursor() as cursor:
        return cursor.execute(**query_object).fetchall()


def index(request):
    return render(request, "voc/index.html")


def status(request):
    updated_at = datetime.now().isoformat()

    db_version_res = query({"sql": "SHOW server_version;"})
    db_version_val = db_version_res[0][0]

    db_max_conn_res = query({"sql": "SHOW max_connections;"})
    db_max_conn_val = db_max_conn_res[0][0]

    db_name = os.getenv("POSTGRES_DB")
    db_open_conn_res = query(
        {"sql": "SELECT count(*)::int FROM pg_stat_activity WHERE datname = %s", "params": (db_name,)})
    db_open_conn_val = db_open_conn_res[0][0]

    data = {
        "updated_at": updated_at,
        "dependencies": {
            "database": {
                "version": db_version_val,
                "max_connections": db_max_conn_val,
                "opened_connections": db_open_conn_val,
            },
        },
    }

    return JsonResponse(data)
