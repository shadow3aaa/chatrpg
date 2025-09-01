from plugins.base import OrganPlugin, OrganProperty


class DigestivePlugin(OrganPlugin):
    name = "digestive"
    display_name = "消化系统"

    fullness = OrganProperty(
        default=80.0, min_val=0, max_val=100, description="How full the stomach is."
    )
    nutrient_buffer = OrganProperty(
        default=50.0, min_val=0, max_val=100, description="Short-term energy reserves."
    )

    def __init__(self, engine):
        super().__init__(engine)
        self.digest_rate = 0.1

    def update(self, tick_duration: float):
        digested_amount = self.digest_rate * tick_duration
        if self.fullness > 0:
            self.fullness -= digested_amount
            self.nutrient_buffer += digested_amount * 0.5

        # Passive nutrient drain
        self.nutrient_buffer -= 0.01 * tick_duration

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
