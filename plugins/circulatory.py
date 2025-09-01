from plugins.base import OrganPlugin


class CirculatoryPlugin(OrganPlugin):
    name = "circulatory"

    @property
    def display_name(self) -> str:
        return "循环系统"

    def __init__(self, engine):
        super().__init__(engine)
        self.base_heart_rate = 70.0
        self.heart_rate = self.base_heart_rate
        self.blood_pressure = "normal"

    def update(self, tick_duration: float):
        if self.heart_rate > self.base_heart_rate:
            self.heart_rate = max(
                self.base_heart_rate, self.heart_rate - 0.1 * tick_duration
            )
        else:
            self.heart_rate = min(
                self.base_heart_rate, self.heart_rate + 0.5 * tick_duration
            )

    def get_sensations(self) -> list[str]:
        s = []
        if self.heart_rate > 100:
            s.append("[体感: 心跳加速, 紧张]")
        if self.heart_rate > 140:
            s.append("[体感: 心悸, 胸闷]")
        return s

    def get_state(self) -> dict[str, str]:
        return {
            "Heart Rate": f"{self.heart_rate:.1f} BPM",
            "Blood Pressure": self.blood_pressure,
        }
