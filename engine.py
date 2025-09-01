import time

# --- Sub-systems for the Body Engine ---

class DigestiveSystem:
    def __init__(self):
        self.fullness = 80.0  # 饱腹度
        self.digest_rate = 0.5  # 每秒消化率
        self.nutrient_buffer = 50.0  # 营养缓冲

    def update(self, tick_duration):
        # 消化
        digested_amount = self.digest_rate * tick_duration
        if self.fullness > 0:
            self.fullness = max(0, self.fullness - digested_amount)
            self.nutrient_buffer = min(100, self.nutrient_buffer + digested_amount * 0.5)
        
        # 消耗营养
        self.nutrient_buffer = max(0, self.nutrient_buffer - 0.2 * tick_duration)

    def get_sensations(self):
        sensations = []
        if self.fullness < 20: sensations.append("[体感: 胃部空虚, 轻微饥饿感]")
        if self.fullness < 5: sensations.append("[体感: 强烈的饥饿感, 胃部痉挛]")
        if self.fullness > 95: sensations.append("[体感: 腹胀, 轻微不适]")
        if self.nutrient_buffer < 10: sensations.append("[体感: 全身无力, 头晕]")
        return sensations

class CirculatorySystem:
    def __init__(self):
        self.base_heart_rate = 70.0
        self.heart_rate = self.base_heart_rate
        self.blood_pressure = "normal"

    def update(self, tick_duration):
        # 缓慢恢复心率
        if self.heart_rate > self.base_heart_rate:
            self.heart_rate = max(self.base_heart_rate, self.heart_rate - 1.0 * tick_duration)
        else:
            self.heart_rate = min(self.base_heart_rate, self.heart_rate + 1.0 * tick_duration)

    def get_sensations(self):
        sensations = []
        if self.heart_rate > 100: sensations.append("[体感: 心跳加速, 紧张]")
        if self.heart_rate > 140: sensations.append("[体感: 心悸, 胸闷]")
        return sensations

class RespiratorySystem:
    def __init__(self, circulatory_system):
        self.circulatory = circulatory_system
        self.breathing_rate = 16.0
        self.oxygen_saturation = 98.0

    def update(self, tick_duration):
        # 呼吸频率与心率关联
        self.breathing_rate = 16 + (self.circulatory.heart_rate - self.circulatory.base_heart_rate) / 5

    def get_sensations(self):
        sensations = []
        if self.breathing_rate > 25: sensations.append("[体感: 呼吸急促, 喘息]")
        if self.oxygen_saturation < 92: sensations.append("[体感: 缺氧, 头晕]")
        return sensations

class EndocrineSystem:
    def __init__(self):
        self.adrenaline = 0.0  # 肾上腺素
        self.cortisol = 10.0  # 皮质醇 (长期压力)
        self.endorphins = 20.0 # 内啡肽 (愉悦)

    def update(self, tick_duration):
        # 激素随时间衰减
        self.adrenaline = max(0, self.adrenaline - 5.0 * tick_duration)
        self.cortisol = max(0, self.cortisol - 0.1 * tick_duration)
        self.endorphins = max(0, self.endorphins - 0.5 * tick_duration)

    def get_sensations(self):
        sensations = []
        if self.adrenaline > 50: sensations.append("[体感: 警觉, 思维锐化]")
        if self.cortisol > 60: sensations.append("[体感: 持续的背景压力, 烦躁]")
        if self.endorphins > 40: sensations.append("[体感: 舒适, 平静, 心情愉悦]")
        return sensations

# --- Main Body Engine ---

class BodyEngine:
    def __init__(self):
        self.digestive = DigestiveSystem()
        self.circulatory = CirculatorySystem()
        self.respiratory = RespiratorySystem(self.circulatory)
        self.endocrine = EndocrineSystem()
        
        self.sub_systems = [self.digestive, self.circulatory, self.respiratory, self.endocrine]
        self.last_update_time = time.time()

    def update(self):
        """
        Updates all sub-systems based on the time elapsed since the last update.
        """
        current_time = time.time()
        tick_duration = current_time - self.last_update_time
        self.last_update_time = current_time

        if tick_duration > 0:
            for system in self.sub_systems:
                system.update(tick_duration)

    def get_all_sensations(self):
        """
        Aggregates sensations from all sub-systems.
        """
        all_sensations = []
        for system in self.sub_systems:
            all_sensations.extend(system.get_sensations())
        return all_sensations

    def get_full_state(self):
        """
        Returns a dictionary with the full state of the body for display.
        """
        return {
            "Digestive": {
                "Fullness": f"{self.digestive.fullness:.1f} / 100",
                "Nutrient Buffer": f"{self.digestive.nutrient_buffer:.1f} / 100",
            },
            "Circulatory": {
                "Heart Rate": f"{self.circulatory.heart_rate:.1f} BPM",
                "Blood Pressure": self.circulatory.blood_pressure,
            },
            "Respiratory": {
                "Breathing Rate": f"{self.respiratory.breathing_rate:.1f} / min",
                "Oxygen Saturation": f"{self.respiratory.oxygen_saturation:.1f} %",
            },
            "Endocrine": {
                "Adrenaline": f"{self.endocrine.adrenaline:.1f}",
                "Cortisol": f"{self.endocrine.cortisol:.1f}",
                "Endorphins": f"{self.endocrine.endorphins:.1f}",
            }
        }

    def apply_impact(self, impact: dict):
        """
        Applies a dictionary of changes from the Reflex LLM to the body state.
        """
        for key, value in impact.items():
            try:
                # Ensure value is a number
                change = float(value)
                
                # Normalize the key to lower case for robust matching
                lower_key = key.lower()

                if 'heart_rate' in lower_key:
                    self.circulatory.heart_rate += change
                elif 'adrenaline' in lower_key:
                    self.endocrine.adrenaline += change
                elif 'cortisol' in lower_key:
                    self.endocrine.cortisol += change
                elif 'endorphins' in lower_key:
                    self.endocrine.endorphins += change
                elif 'fullness' in lower_key:
                    self.digestive.fullness = min(100, self.digestive.fullness + change)
                elif 'nutrient_buffer' in lower_key:
                    self.digestive.nutrient_buffer = min(100, self.digestive.nutrient_buffer + change)
                elif 'breathing_rate' in lower_key:
                    self.respiratory.breathing_rate += change
                # Add other mappings here as needed

            except (ValueError, TypeError):
                # Handle non-numeric values or other errors gracefully
                print(f"[ENGINE WARNING] Could not apply impact: {key}: {value}")

if __name__ == '__main__':
    # Simple test loop to see the engine running
    engine = BodyEngine()
    try:
        while True:
            engine.update()
            state = engine.get_full_state()
            sensations = engine.get_all_sensations()
            
            # Clear screen for better display
            print("\033[H\033[J", end="")
            
            for system, values in state.items():
                print(f"--- {system} ---")
                for key, value in values.items():
                    print(f"{key}: {value}")
            
            print("\n--- Sensations ---")
            if sensations:
                for s in sensations:
                    print(s)
            else:
                print("None")

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEngine test stopped.")