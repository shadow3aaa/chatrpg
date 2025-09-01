from plugins.base import OrganPlugin


class DigestivePlugin(OrganPlugin):
    name = "digestive"

    @property
    def display_name(self) -> str:
        return "消化系统"

    def __init__(self, engine):
        super().__init__(engine)
        self.fullness = 80.0
        self.digest_rate = 0.1
        self.nutrient_buffer = 50.0

    def update(self, tick_duration: float):
        digested_amount = self.digest_rate * tick_duration
        if self.fullness > 0:
            self.fullness = max(0, self.fullness - digested_amount)
            self.nutrient_buffer = min(
                100, self.nutrient_buffer + digested_amount * 0.5
            )
        self.nutrient_buffer = max(0, self.nutrient_buffer - 0.2 * tick_duration)

    def get_sensations(self) -> list[str]:
        s = []
        if self.fullness < 20:
            s.append("[体感: 胃部空虚, 轻微饥饿感]")
        if self.fullness < 5:
            s.append("[体感: 强烈的饥饿感, 胃部痉挛]")
        if self.fullness > 95:
            s.append("[体感: 腹胀, 轻微不适]")
        if self.nutrient_buffer < 10:
            s.append("[体感: 全身无力, 头晕]")
        return s

    def get_state(self) -> dict[str, str]:
        return {
            "Fullness": f"{self.fullness:.1f} / 100",
            "Nutrient Buffer": f"{self.nutrient_buffer:.1f} / 100",
        }
