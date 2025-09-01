from plugins.base import OrganPlugin


class EndocrinePlugin(OrganPlugin):
    name = "endocrine"

    @property
    def display_name(self) -> str:
        return "内分泌系统"

    def __init__(self, engine):
        super().__init__(engine)
        self.adrenaline = 0.0
        self.cortisol = 10.0
        self.endorphins = 20.0

    def update(self, tick_duration: float):
        self.adrenaline = max(0, self.adrenaline - 5.0 * tick_duration)
        self.cortisol = max(0, self.cortisol - 0.1 * tick_duration)
        self.endorphins = max(0, self.endorphins - 0.5 * tick_duration)

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
