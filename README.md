### How to use
- create a `data` folder
- run `python get_data.py` to generate pose file
- create custom `config.json` in `data`
- run `python continus_recognize.py`

### config
The config file should be like this

``` json
[
    {
        "id":"id",// task id(unique)
        "name":"name",// task name
        "data_type":["right_hand","left_hand","body","face"]/"time", // data type
        "match_data":"path-to-json"/"contain"/time(ms), // match pose file/match type
        "command":"", // command to run
        "sensetive":100, // sensetivity(only for match)
        "start":true/false, // is the task activate for default
        "next_tasks":[
            {
                "operator":"start"/"stop", // operation type
                "id":"id" // target task id
            }
        ]
    }
    ...
]
```