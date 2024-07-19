### 使用方法
- 克隆仓库到本地
- 运行`pip install -r requirements.txt`下载依赖
- 运行`python continus_recognize.py`生成`config.json`并下载需要的模型
- 编写合适的`config.json`, 它应该在`./data/`目录下
- 运行`python continus_recognize.py`
### 任务编写
任务的编写在`config.json`中, `config.json`应是这样:
``` c++
[
    // task 1
    {
        "id":"id", // 任务id(唯一)
        "name":"name", // 任务名称
        "data_type":["right_hand","left_hand","body","face"]/"time", // 所需数据类型
        "match_data":"path-to-json"/"contain"/time(ms), // 匹配数据路径/匹配数据
        "command":"", // 运行的命令(可为空字符串)
        "sensetive":100, // 检测敏感度(仅对形态匹配生效)
        "start":true/false, // 任务是否初始启动
        "next_tasks":[ // 运行指令之后对任务激活进行修改
            {
                "operator":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
            ...
        ]
    },
    // task 2
    ...
]
```
你可以查看`data_example`, 那里提供了一个示例

### 任务类型
允许三种任务:
- 身体形态识别
- 延时
- 身体形态检测

#### 身体形态识别
身体形态识别可以识别身体特点位点的形态, 在与对应数据相似时执行
身体形态识别任务应如下编写:
``` c++
{
    "id":"id", // 任务id(唯一)
    "name":"name", // 任务名称
    "data_type":["right_hand","left_hand","body","face"], // 所需数据类型(应为该列表的子集, 无视顺序)
    "match_data":"path-to-json", // 匹配数据路径
    "command":"", // 运行的命令(可为空字符串)
    "sensetive":100, // 检测敏感度
    "start":true/false, // 任务是否初始启动
    "next_tasks":[ // 运行指令之后对任务激活进行修改
        {
            "operator":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```
匹配数据可由`python get_hand_config.py`获取, 启动后会捕捉人体, 按空格后会退出并将姿态保存在`./data/output.json`中

#### 延时任务
延时任务可以在被激活后延时一段时间执行, 可以被其他任务的`next_tasks`打断
延时任务应如下编写:
``` c++
{
    "id":"id", // 任务id(唯一)
    "name":"name", // 任务名称
    "data_type":"time", // 所需数据类型(应为该列表的子集, 无视顺序)
    "match_data":time, // 时间(整数, 毫秒)
    "command":"", // 运行的命令(可为空字符串)
    "sensetive":0, // 需保留该字段
    "start":true/false, // 任务是否初始启动
    "next_tasks":[ // 运行指令之后对任务激活进行修改
        {
            "operator":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```
时间从任务被启动时开始计时, 默认会在执行后重新计时, 如需停止应在`next_tasks`中关闭自身

#### 检测任务
检测任务可以在检测到对应的身体部位时执行
检测任务应如下编写:

``` c++
{
    "id":"id", // 任务id(唯一)
    "name":"name", // 任务名称
    "data_type":["right_hand","left_hand","body","face"], // 所需数据类型(应为该列表的子集, 无视顺序)
    "match_data":"contain", // 匹配数据路径
    "command":"", // 运行的命令(可为空字符串)
    "sensetive":100, // 需保留该字段
    "start":true/false, // 任务是否初始启动
    "next_tasks":[ // 运行指令之后对任务激活进行修改
        {
            "operator":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```