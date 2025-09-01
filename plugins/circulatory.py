from plugins.base import OrganPlugin, OrganProperty


class CirculatoryPlugin(OrganPlugin):
    name = "circulatory"
    display_name = "循环系统"

    heart_rate = OrganProperty(default=70.0, min_val=0, description="The current heart rate in beats per minute.")

    def __init__(self, engine):
        super().__init__(engine)
        self.base_heart_rate = 70.0
        # self.heart_rate is now managed by the OrganProperty descriptor
        self.blood_pressure = "normal"

    def update(self, tick_duration: float):
        # Gradually return to base heart rate
        if self.heart_rate > self.base_heart_rate:
            self.heart_rate -= 0.5 * tick_duration
        else:
            self.heart_rate += 0.5 * tick_duration

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
