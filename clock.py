#Made by SimpleCarrot42 - Simple Terminal Clock and Perfomance monitor
import psutil
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits, Label
from textual.containers import Container
from textual.reactive import reactive

BYTES_IN_GB = 1024 ** 3


class PerformanceMonitor(Label):

    cpu_percent = reactive(0.0)
    ram_percent = reactive(0.0)
    ram_used_gb = reactive(0.0)
    ram_total_gb = reactive(0.0)

    def on_mount(self) -> None:
        # Prime CPU measurement so the first real sample isn't 0.0
        psutil.cpu_percent(interval=None)
        # Do an immediate update so we render real values on first paint
        self.update_metrics()
        self.set_interval(1, self.update_metrics)

    def update_metrics(self) -> None:
        self.cpu_percent = psutil.cpu_percent(interval=None)

        mem = psutil.virtual_memory()
        # Use psutil's computed percent so it's consistent across OSes
        self.ram_percent = float(mem.percent)
        self.ram_used_gb = mem.used / BYTES_IN_GB
        self.ram_total_gb = mem.total / BYTES_IN_GB

    def render(self) -> str:
        return (
            f"CPU: {self.cpu_percent:4.1f}% "
            f"| RAM: {self.ram_percent:4.1f}% "
        )


class SimpleTuiApp(App):
    BINDINGS = [("q", "quit", "Quit the app")]

    CSS = """
    Screen {
        align: center middle;
    }
    #main-container {
        width: auto;
        align: center middle;
    }
    #clock-digits {
        width: auto;
        text-style: bold;
    }
    #monitor-label {
        width: auto;
        margin-top: 1;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        self.clock = Digits("", id="clock-digits")
        self.monitor = PerformanceMonitor(id="monitor-label")
        with Container(id="main-container"):
            yield self.clock
            yield self.monitor

    def on_ready(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.clock.update(f"{clock:%H:%M:%S}")

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = SimpleTuiApp()
    app.run()
