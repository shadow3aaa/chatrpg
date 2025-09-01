from plugins.base import OrganPlugin, OrganProperty


class EndocrinePlugin(OrganPlugin):
    name = "endocrine"
    display_name = "内分泌系统"

    adrenaline = OrganProperty(default=0.0, min_val=0, max_val=100, description="Fight-or-flight hormone.")
    cortisol = OrganProperty(default=10.0, min_val=0, max_val=100, description="Stress hormone.")
    endorphins = OrganProperty(default=20.0, min_val=0, max_val=100, description="Pain and stress-reducing hormones.")

    def __init__(self, engine):
        super().__init__(engine)

    def update(self, tick_duration: float):
        # Hormones naturally decay over time
        self.adrenaline -= 5.0 * tick_duration
        self.cortisol -= 0.1 * tick_duration
        self.endorphins -= 0.5 * tick_duration

    def get_sensations(self) -> list[str]:
        s = []
        if self.adrenaline > 50:
            s.append("[体感: 警觉, 思维锐化]")
        if self.cortisol > 60:
            s.append("[体感: 持续的背景压力, 烦躁]")
        if self.endorphins > 40:
            s.append("[体感: 舒适, 平静, 心情愉悦]")
        return s

    def get_state(self) -> dict[str, str]:
        return {
            "Adrenaline": f"{self.adrenaline:.1f}",
            "Cortisol": f"{self.cortisol:.1f}",
            "Endorphins": f"{self.endorphins:.1f}",
        }
