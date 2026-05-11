from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label

class ConfirmDialog(ModalScreen[bool]):
    """确认对话框。"""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    #message {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    #confirm {
        width: 1fr;
    }

    #cancel {
        width: 1fr;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label(self.message, id="message")
            yield Button("确认", variant="error", id="confirm")
            yield Button("取消", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
