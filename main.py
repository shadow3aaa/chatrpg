from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Grid, Vertical
from textual.timer import Timer

from engine import BodyEngine
from llm_services import get_reflex_impact, get_persona_dialogue


class OrganWidget(Static):
    """A widget to display the state of a single organ system."""

    def __init__(self, system_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.system_name = system_name
        self.border_title = system_name

    def update_content(self, data: dict):
        content = ""
        for key, value in data.items():
            content += f"{key}: {value}\n"
        self.update(content)


class TuiApp(App):
    """A Textual app to display the body engine status."""

    CSS_PATH = "style.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    engine = BodyEngine()
    update_timer: Timer

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        # Dynamically create OrganWidgets based on loaded plugins
        plugin_widgets = [
            OrganWidget(system_name=name.capitalize(), id=name)
            for name in self.engine.plugins.keys()
        ]

        yield Grid(
            *plugin_widgets,
            Static("Sensations", id="sensations"),
            Vertical(
                RichLog(id="log", wrap=True),
                Input(placeholder="Enter event or dialogue..."),
                id="interaction-pane",
            ),
        )
        yield Footer()

    def _refresh_ui_widgets(self) -> None:
        """Refreshes all UI widgets with the current engine state."""
        full_state = self.engine.get_full_state()
        sensations = self.engine.get_all_sensations()

        # Dynamically update widgets
        for system_id, data in full_state.items():
            try:
                widget = self.query_one(f"#{system_id.lower()}", OrganWidget)
                widget.update_content(data)
            except Exception as e:
                self.log_widget.write(f"UI Error: {e}")

        sensation_widget = self.query_one("#sensations", Static)
        sensation_text = "Sensations:\n" + (
            "\n".join(sensations) if sensations else "None"
        )
        sensation_widget.update(sensation_text)

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.update_timer = self.set_interval(1.0, self.update_body_state)
        self.log_widget = self.query_one(RichLog)
        self.log_widget.write(
            "Body engine started. Enter an event (e.g., *a cold wind blows*) or dialogue."
        )
        self.call_later(self.query_one(Input).focus)

    def update_body_state(self) -> None:
        """Update the body state and refresh widgets."""
        self.engine.update()
        self._refresh_ui_widgets()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle user input."""
        user_input = message.value
        if not user_input:
            return

        # Pause the autonomous engine during interaction
        self.update_timer.pause()
        self.log_widget.write("[INFO] Autonomous engine paused.")

        try:
            self.query_one(Input).value = ""
            self.log_widget.write(f"> {user_input}")

            # 1. Call Reflex LLM
            reflex_impact = await get_reflex_impact(
                user_input, self.engine.get_full_state()
            )

            # 2. Apply the impact to the engine
            if reflex_impact:
                self.engine.apply_impact(reflex_impact)
                self.log_widget.write(
                    f"[Body state updated based on reflex: {reflex_impact}]"
                )
                # Manually refresh the UI to show the change immediately
                self._refresh_ui_widgets()

            # 3. Call Persona LLM with the new state
            persona_response = await get_persona_dialogue(
                user_input,
                reflex_impact,
                self.engine.get_full_state(),
                self.engine.get_all_sensations(),
            )

            self.log_widget.write(f"AI: {persona_response}")
        finally:
            # Always resume the autonomous engine
            self.update_timer.resume()
            self.log_widget.write("[INFO] Autonomous engine resumed.")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = TuiApp()
    app.run()
