## Language

-[English](#english)<br/>
-[中文](#中文)<br/>

---

### English

//TO BE TRANSLATED

---

### 中文

### 使用方法
- 克隆仓库到本地
- 运行`pip install -r requirements.txt`下载依赖
- 运行`python Utils.py`与`python TaskController.py`
- 首次运行`python Main.py`会在`./data/`目录下生成一个`config.json`
- 编写合适的`config.json`详情见[任务编写](#任务编写)
- 可以运行`python GetHandConfig.py`帮助你快速生成在`config.json`下可能用到的**存放手部数据的json文件**
- 运行`python Main.py`
### 任务编写
任务的编写在`config.json`中, `config.json`应是这样:
``` c++
[
    // task 1
    {
        "type":"type",// 任务类型
        "id":"id",// 任务id(唯一)
        "bodyPart":[
            "bodyPart1", // 需要识别的部位
            "bodyPart2",
            ...
        ],
        "start":true/false, // 任务是否初始启动
        "command":"", // 运行的命令(可为空字符串)
        "next_tasks":[ // 运行指令之后对任务激活进行修改
            {
                "operate":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
        ...
        ]
    }
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
[
    {
        "type":"type",// 任务类型
        "id":"id",// 任务id(唯一)
        "bodyPart":[
            "bodyPart1", // 需要识别的部位
            "bodyPart2",
            ...
        ],
        "poseFile": [
            "path-to-json1",// 匹配数据路径
            "path-to-json2"
        ],
        "sensetive": [
            1,// 检测敏感度
            1
        ],
        "start":true/false, // 任务是否初始启动
        "command":"", // 运行的命令(可为空字符串)
        "next_tasks":[ // 运行指令之后对任务激活进行修改
            {
                "operate":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
        ...
        ]
    }
]
```
匹配数据可由`python GetHandConfig.py`获取, 启动后会捕捉人体, 按s后会保存当前姿态，按q后会退出并将姿态保存在当前目录下的`output.json`中

#### 延时任务
延时任务可以在被激活后延时一段时间执行, 可以被其他任务的`next_tasks`打断
延时任务应如下编写:
``` c++
[
    // task 1
    {
        "type":"type",// 任务类型
        "id":"id",// 任务id(唯一)
        "timeout":time, // 时间(整数, 毫秒)
        "loop":true/false, // 是否循环
        "start":true/false, // 任务是否初始启动
        "command":"", // 运行的命令
        "next_tasks":[ // 运行指令之后对任务激活进行修改
            {
                "operate":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
        ...
        ]
    }
]
```
时间从任务被启动时开始计时, 默认会在执行后重新计时, 如需停止应在`next_tasks`中关闭自身

#### 检测任务
检测任务可以在检测到对应的身体部位时执行
检测任务应如下编写:
``` c++
[
    {
        "type":"type",// 任务类型
        "id":"id",// 任务id(唯一)
        "bodyPart":[
            "bodyPart1", // 需要识别的部位
            "bodyPart2",
            ...
        ],
        "poseFile": [
            "path-to-json1",// 匹配数据路径
            "path-to-json2"
        ],
        "sensetive": [
            1,// 检测敏感度,需保留该字段
            1
        ],
        "start":true/false, // 任务是否初始启动
        "command":"", // 运行的命令(可为空字符串)
        "next_tasks":[ // 运行指令之后对任务激活进行修改
            {
                "operate":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
        ...
        ]
    }
]
```