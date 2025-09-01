from plugins.base import OrganPlugin


class RespiratoryPlugin(OrganPlugin):
    name = "respiratory"

    def __init__(self, engine):
        super().__init__(engine)
        self.breathing_rate = 16.0
        self.oxygen_saturation = 98.0

    def update(self, tick_duration: float):
        # Dependency on another plugin
        circulatory = self.engine.get_plugin("circulatory")
        if circulatory:
            self.breathing_rate = (
                16 + (circulatory.heart_rate - circulatory.base_heart_rate) / 5
            )

    def get_sensations(self) -> list[str]:
        s = []
        if self.breathing_rate > 25:
            s.append("[体感: 呼吸急促, 喘息]")
        if self.oxygen_saturation < 92:
            s.append("[体感: 缺氧, 头晕]")
        return s

    def get_state(self) -> dict[str, str]:
        return {
            "Breathing Rate": f"{self.breathing_rate:.1f} / min",
            "Oxygen Saturation": f"{self.oxygen_saturation:.1f} %",
        }
