from textual.widgets import Static

class OrganWidget(Static):
    """The default widget to display the state of a single organ system."""
    
    def __init__(self, system_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.system_name = system_name
        self.border_title = system_name

    def update_state(self, data: dict):
        """A standardized method to update the widget's content."""
        content = ""
        for key, value in data.items():
            content += f"{key}: {value}\n"
        self.update(content)

