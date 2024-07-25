# Запрос данных для получения списка отчетных периодов (тело запроса)
request_get_all_periods = {
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
request_get_all_components_period = {
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
        "reportPeriodId": "",
        "page": 1,
        "start": 0,
        "limit": 25
    }],
    "type": "rpc",
    "tid": 34
}

# Получение компонента отчетного периода
requests_data_get_kop = [{"action": "ReportPeriodComponent", "method": "Load",
                          "data": ["",
                                   {"profiles": ["00000000-0000-0000-0000-000000000000"], "DbKey": "",
                                    "dicActualityDate": "2024-06-13T17:06:08",
                                    "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
                                    "isReadOnly": False,
                                    "currentNode": {"additionalData": {"StoredObjectId": None}}}],
                          "type": "rpc", "tid": 43},
                         {"action": "ReportPeriodComponent", "method": "GetEqualityGroups", "data": None,
                          "type": "rpc", "tid": 44}]

requests_save_period = {
  "action": "ReportPeriod",
  "method": "SaveOneModifiedAsync",
  "data": ["{body}",
    {
      "profiles": [
        "00000000-0000-0000-0000-000000000000"
      ],
      "DbKey": "",
      "dicActualityDate": "2024-07-25T11:59:50",
      "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
      "isReadOnly": False
    }
  ],
  "type": "rpc",
  "tid": 37
}


request_get_period = [
  {
    "action": "ReportPeriod",
    "method": "Load",
    "data": [
      "{idPeriod}",
      {
        "profiles": [
          "00000000-0000-0000-0000-000000000000"
        ],
        "DbKey": "",
        "dicActualityDate": "2024-07-25T11:59:50",
        "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
        "isReadOnly": False
      }
    ],
    "type": "rpc",
    "tid": 30
  },
  {
    "action": "UserAccount",
    "method": "GetSettingProfiles",
    "data": None,
    "type": "rpc",
    "tid": 31
  }
]