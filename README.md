### 使用方法

- 克隆仓库到本地
- 运行`pip install -r requirements.txt`下载依赖
- 首次运行`python Main.py`会在`./data/`目录下生成一个`config.json`并下载所需的模型
- 编写合适的`config.json`，详情见[任务编写](#任务编写)
- 可以运行`python GetHandConfig.py`帮助你快速生成在`config.json`下可能用到的**存放姿势数据的 json 文件**
- 运行`python Main.py`

### 任务编写

任务的编写在`config.json`中，`config.json`应是这样:

```c++
[
    // task 1
    {
        "type":"type", // 任务类型
        "id":"id", // 任务id(唯一)
        "start":true/false, // 任务是否初始启动
        "nextTasks":[ // 运行指令之后对任务激活进行修改
            {
                "operate":"start"/"stop", // 启动/停止任务
                "id":"id" // 目标任务id
            },
            ...
        ],
        ...
    },
    // task 2
    ...
]
```

任务在满足条件后会自动停止自己的运作，如需要循环运行请在`nextTasks`中重新启动自身  
~~你可以查看`data_example`，那里提供了一个示例~~  
这个`data_example`还未完成

### 任务类型

允许四种任务：

- 执行命令
- 模拟按键
- 身体形态识别
- 延时
- 检测身体部位

#### 执行命令

命令执行是一个任务，应如下编写：

```c++
{
    "type":"command", // 任务类型
    "id":"id", // 任务id(唯一)
    "command":[ // 满足条件运行的命令(可为空数组)
        "start example.exe", // 按顺序运行的命令(可为空字符串)
        "python ./example.py",
        ...
    ],
    "timeout":[ // 命令运行的最大时间(0表示不限制，单位为秒)
        0.5,
        0,
        ...
    ],
    "start":true/false, // 任务是否初始启动
    "nextTasks":[ // 运行指令之后对任务激活状态进行修改
        {
            "operate":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```

你可以在命令中使用`%s`，他们会被替换成识别到的姿势位置  
替换后为一个无空格`json`，与`python GetHandConfig.py`生成的`output.json`格式相同  
如需原始的`%`，请使用`%%`

#### 模拟按键

模拟按键任务应如下编写：

```c++
{
    "type":"keypress", // 任务类型
    "id":"id", // 任务id(唯一)
    "keys":[ // 满足条件运行的按键(可为空数组)
        ["key1","key2","key3",...], // 快捷键列表
        ...
    ],
    "start":true/false, // 任务是否初始启动
    "nextTasks":[ // 运行指令之后对任务激活状态进行修改
        {
            "operate":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```

此处的`key1`，`key2`……应该在`pyautogui.KEYBOARD_KEYS`里  
`pyautogui.KEYBOARD_KEYS`为以下列表

```python
['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace', 'browserback', 'browserfavorites', 'browserforward', 'browserhome', 'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear', 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete', 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack', 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn', 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn', 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator', 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab', 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen', 'command', 'option', 'optionleft', 'optionright']
```

#### 身体形态识别

身体形态识别可以识别身体特点位点的形态, 在与对应数据相似时执行  
身体形态识别任务应如下编写：

```c++
{
    "type":"match", // 任务类型
    "id":"id", // 任务id(唯一)
    "bodyPart":[
        ["bodyPart1","bodyPart2",...], // 需要识别的部位，与poseFile一一对应
        ["bodyPart1","bodyPart2",...] // bodyPart 为 ["face","leftHand","rightHand","body"] 其一
        ...
    ],
    "poseFile": [
        "path-to-json1", // 匹配数据路径
        "path-to-json2",
        ...
    ],
    "sensetive": [
        0.01, // 检测敏感度，与poseFile一一对应
        0.01,
        ...
    ],
    "frames": [
        30, // 连续多少帧检测到才运行，与poseFile一一对应
        20,
        ...
    ],
    "start":true/false, // 任务是否初始启动
    "nextTasks":[ // 运行指令之后对任务激活状态进行修改
        {
            "operate":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```

匹配数据可由`python GetHandConfig.py`获取，启动后会捕捉人体，按`s`后会保存当前姿态，此时可以查看其他动作的`sensetive`值，按`q`后会退出并将姿态保存在当前目录下的`output.json`中

#### 延时任务

延时任务可以在被激活后延时一段时间执行，可以被其他任务的`nextTasks`打断  
延时任务应如下编写：

```c++
{
    "type":"timeout", // 任务类型
    "id":"id", // 任务id(唯一)
    "timeout":time, // 时间(整数，毫秒)
    "start":true/false, // 任务是否初始启动
    "nextTasks":[ // 运行指令之后对任务激活状态进行修改
        {
            "operate":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```

时间从任务被启动时开始计时

#### 检测任务

检测任务可以在检测到对应的身体部位时执行  
检测任务应如下编写：

```c++
{
    "type":"detect", // 任务类型
    "id":"id", // 任务id(唯一)
    "bodyPart":[
        "bodyPart1", // 需要识别的部位
        "bodyPart2", // bodyPart 为 ["face","leftHand","rightHand","body"] 其一
        ...
    ],
    "frames":frames, // 连续多少帧检测到才运行
    "start":true/false, // 任务是否初始启动
    "nextTasks":[ // 运行指令之后对任务激活状态进行修改
        {
            "operate":"start"/"stop", // 启动/停止任务
            "id":"id" // 目标任务id
        },
        ...
    ]
}
```
