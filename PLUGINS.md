# ChatRPG 插件开发指南

本文档将指导您如何为本项目创建新的器官或生理系统插件。

## 基本概念

本项目的核心是一个插件化的生理引擎。每个独立的生理功能（如消化、循环）都是一个独立的“插件”。引擎在启动时会自动发现并加载 `plugins/` 目录下的所有插件。

要创建一个新的插件，您只需要创建一个新的 Python 文件，并实现一个继承自 `OrganPlugin` 基类的类。

## 插件接口 (`OrganPlugin`)

您的插件类必须继承位于 `plugins/base.py` 的 `OrganPlugin` 类，并实现其定义的所有抽象方法和属性。

### `name` (属性)

必须提供一个字符串类型的类属性，作为插件的唯一标识符。它应该是小写的。

```python
class MyNewPlugin(OrganPlugin):
    name = "my_new_plugin"
```

### `__init__(self, engine)`

插件的构造函数。它会接收一个 `BodyEngine` 的实例作为参数。您应该保存这个 `engine` 实例，以便将来用于获取其他插件（依赖注入）。

```python
def __init__(self, engine):
    super().__init__(engine)
    # Your initialization logic here
```

### `update(self, tick_duration: float)`

此方法由主引擎在每个时间节拍（大约每秒）调用一次。您应该在这里实现所有随时间自主变化的状态逻辑。

### `get_sensations(self) -> list[str]`

此方法应返回一个字符串列表，每个字符串描述一种由该插件产生的“体感”。当状态正常时，应返回一个空列表。

### `get_state(self) -> dict[str, str]`

此方法应返回一个字典，用于在 TUI 上显示插件的当前状态。键是显示的标签，值是显示的字符串内容。

## 依赖管理

如果您的插件需要依赖另一个插件（例如，呼吸插件需要心率数据），您可以在需要时通过 `self.engine` 来获取它。

```python
def update(self, tick_duration: float):
    circulatory_plugin = self.engine.get_plugin("circulatory")
    if circulatory_plugin:
        # Now you can access its properties
        current_heart_rate = circulatory_plugin.heart_rate
        # ...
```

## 完整范例：创建一个体温插件

以下是一个完整的 `temperature.py` 插件范例。您只需将这样的文件放入 `plugins/` 目录，它就会被自动加载和运行。

```python
# file: plugins/temperature.py
from plugins.base import OrganPlugin

class TemperaturePlugin(OrganPlugin):
    name = "temperature"

    def __init__(self, engine):
        super().__init__(engine)
        self.current_temp = 37.0
        self.ambient_temp = 25.0 # 环境温度

    def update(self, tick_duration: float):
        # 身体会缓慢地向环境温度靠拢
        if self.current_temp > self.ambient_temp:
            self.current_temp -= 0.1 * tick_duration
        else:
            self.current_temp += 0.1 * tick_duration

    def get_sensations(self) -> list[str]:
        sensations = []
        if self.current_temp < 36.0:
            sensations.append("[体感: 感觉寒冷, 皮肤冰凉]")
        elif self.current_temp > 38.0:
            sensations.append("[体感: 感觉发热, 微微出汗]")
        return sensations

    def get_state(self) -> dict[str, str]:
        return {
            "身体温度": f"{self.current_temp:.1f}°C",
            "环境温度": f"{self.ambient_temp:.1f}°C",
        }
```
