from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Grid, Vertical
from textual.timer import Timer

from engine import BodyEngine
from llm_services import get_reflex_impact, get_persona_dialogue
from tui_widgets import OrganWidget # Import the default widget

class ChatRPG(App):
    """A Textual app to display the body engine status."""

    CSS_PATH = "style.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    engine = BodyEngine()
    update_timer: Timer

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        plugin_widgets = []
        for name, plugin in self.engine.plugins.items():
            WidgetClass = plugin.get_widget_class()
            if WidgetClass:
                # Use the custom widget provided by the plugin
                plugin_widgets.append(WidgetClass(id=name))
            else:
                # Use the default widget. The display_name is now guaranteed by the base class.
                plugin_widgets.append(OrganWidget(system_name=plugin.display_name, id=name))

        yield Grid(
            *plugin_widgets,
            Static("Sensations", id="sensations"),
            Vertical(
                RichLog(id="log", wrap=True, markup=True),
                Input(placeholder="Enter event or dialogue..."),
                id="interaction-pane"
            )
        )
        yield Footer()

    def _refresh_ui_widgets(self) -> None:
        """Refreshes all UI widgets with the current engine state."""
        sensations = self.engine.get_all_sensations()

        for name, plugin in self.engine.plugins.items():
            try:
                widget = self.query_one(f"#{name}", Static)
                state_data = plugin.get_state()
                # All widgets (default or custom) must have an `update_state` method
                widget.update_state(state_data)
            except Exception as e:
                self.log_widget.write(f"[bold white on red]CRITICAL UI ERROR: {e}[/bold white on red]")
        
        sensation_widget = self.query_one("#sensations", Static)
        sensation_text = "Sensations:\n" + ("\n".join(sensations) if sensations else "None")
        sensation_widget.update(sensation_text)

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.update_timer = self.set_interval(1.0, self.update_body_state)
        self.log_widget = self.query_one(RichLog)
        self.log_widget.write("[bold green]Body engine started.[/bold green] Enter an event (e.g., *a cold wind blows*) or dialogue.")
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
        
        self.update_timer.pause()
        self.log_widget.write("[silver][INFO] Autonomous engine paused.[/silver]")

        try:
            self.query_one(Input).value = ""
            self.log_widget.write(f"You: {user_input}")

            # Generate schema for precise LLM reflection
            organs_schema = self.engine.get_organs_schema()
            reflex_impact = await get_reflex_impact(user_input, self.engine.get_full_state(), organs_schema)

            if reflex_impact:
                self.engine.apply_impact(reflex_impact)
                formatted_impact_messages = []
                for system_name, attributes in reflex_impact.items():
                    for attribute, operator_value in attributes.items():
                        formatted_impact_messages.append(f"{attribute} {operator_value}")
                
                if formatted_impact_messages:
                    impact_text = "\n".join(formatted_impact_messages)
                    self.log_widget.write(f"[yellow]{impact_text}[/yellow]")
                else:
                    self.log_widget.write("[yellow]Body state updated based on reflex.[/yellow]") # Fallback if no specific changes
                
                self._refresh_ui_widgets()
            
            persona_response = await get_persona_dialogue(
                user_input, 
                reflex_impact,
                self.engine.get_full_state(), 
                self.engine.get_all_sensations()
            )
            
            self.log_widget.write(f"[bold green]AI:[/bold green] {persona_response}")
        except Exception as e:
            self.log_widget.write(f"[bold white on red]CRITICAL APPLICATION ERROR: {e}[/bold white on red]")
        finally:
            self.update_timer.resume()
            self.log_widget.write("[silver][INFO] Autonomous engine resumed.[/silver]")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = ChatRPG()
    app.run()

