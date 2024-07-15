# Запрос данных для получения списка отчетных периодов (тело запроса)
request_data = {
    "action": "ReportPeriod",
    "method": "GetPageAsync",
    "data": [
        {
            "context": {
                "profiles": ["00000000-0000-0000-0000-000000000000"],
                "DbKey": "",
                "dicActualityDate": "2024-06-11T12:23:31",
                "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
                "isReadOnly": False,
                "currentNode": {
                    "additionalData": {
                        "AdditionalProperties": {}
                    }
                }
            },
            "page": 1,
            "start": 0,
            "limit": 100
        }
    ],
    "type": "rpc",
    "tid": 26
}

# Запрос данных для получения списка КОП (тело запроса)
request_period_data = {
    "action": "ReportPeriod",
    "method": "GetReportPeriodComponentsPage",
    "data": [{
        "context": {
            "profiles": ["00000000-0000-0000-0000-000000000000"],
            "DbKey": "",
            "dicActualityDate": "2024-06-13T15:50:16",
            "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
            "isReadOnly": False,
            "currentNode": None
        },
        "reportPeriodId":"",
        "page": 1,
        "start": 0,
        "limit": 25
    }],
    "type": "rpc",
    "tid": 34
}