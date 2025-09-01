from plugins.base import OrganPlugin, OrganProperty


class RespiratoryPlugin(OrganPlugin):
    name = "respiratory"
    display_name = "呼吸系统"

    breathing_rate = OrganProperty(default=16.0, min_val=0, description="Breaths per minute.")
    oxygen_saturation = OrganProperty(default=98.0, min_val=0, max_val=100, description="Percentage of oxygen in the blood.")

    def __init__(self, engine):
        super().__init__(engine)

    def update(self, tick_duration: float):
        # Dependency on another plugin
        circulatory = self.engine.get_plugin("circulatory")
        if circulatory:
            # Breathing rate is affected by heart rate
            base_breathing_rate = 16.0
            heart_rate_effect = (circulatory.heart_rate - circulatory.base_heart_rate) / 5.0
            self.breathing_rate = base_breathing_rate + heart_rate_effect

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
