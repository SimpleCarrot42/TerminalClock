import psutil
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits, Label
from textual.containers import Container
from textual.reactive import reactive


BYTES_IN_GB = 1024 ** 3


def color_for_percent(percent: float) -> str:
    if 0 <= percent < 15:
        return "white"
    elif 15 <= percent < 45:
        return "green"
    elif 45 <= percent < 85:
        return "orange"
    elif 85 <= percent <= 100:
        return "red"
    else:
        return "white"


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
        self.ram_percent = float(mem.percent)
        self.ram_used_gb = mem.used / BYTES_IN_GB
        self.ram_total_gb = mem.total / BYTES_IN_GB

    def render(self) -> str:
        cpu_color = color_for_percent(self.cpu_percent)
        ram_color = color_for_percent(self.ram_percent)

        return (
            f"CPU: [{cpu_color}]{self.cpu_percent:4.1f}%[/] "
            f"| RAM: [{ram_color}]{self.ram_percent:4.1f}%[/]"
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
