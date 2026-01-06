import threading
from typing import Callable, Any, TypeVar

from matplotlib.figure import Figure
from matplotlib.artist import Artist
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import pathlib
from PyQt5.QtCore import QTimer

from quflow.tasks.base import Task
from quflow.tasks.utils import empty_function, false_function
from quflow.status import Status

# This helper schedules a figure closure on the main thread.


dir_path = pathlib.Path(__file__).parent.absolute()
# Assume these are defined elsewhere based on your paths.
RESOURCES = f'{dir_path}\\resources'  # Replace with your actual resource directory path
STOP_ICON = plt.imread(f'{RESOURCES}\\stop_icon.jpg')
SAVE_ICON = plt.imread(f'{RESOURCES}\\save_icon.png')

T = TypeVar('T')

SetupFuncType = Callable[[], tuple[Figure, list[Artist]]]
CleanupFuncType = Callable[[tuple[Figure, list[Artist]]], None]
UpdateFuncType = Callable[[list[Artist], T], list[Artist]]


class LiveAnimationTask(Task):
    """Runs a Matplotlib animation in the main thread, updating plots in real-time.

    Args:
        setup_func (Callable): Must return (figure, [artist1, artist2, ...]).
        update (Callable): A function (artists, data) -> updated_artists.
        interrupt (threading.Event): If set, stops the animation loop.
        refresh_time_sec (float): Interval between animation frames in seconds.
        cleanup_func (Callable): Optional cleanup routine.

    The animation calls `step()` repeatedly, reading new data from the read channel
    and updating the artists with the provided update function. A 'Stop' button is
    automatically added to the figure.

    Note:
        This should typically be marked `is_main_thread=True` in the Node
        to avoid concurrency issues with matplotlib.
    """

    def __init__(self, *,
                 setup_func: SetupFuncType,
                 update: UpdateFuncType,
                 refresh_time_sec: float = 0.05,
                 cleanup_func: CleanupFuncType | empty_function = empty_function,
                 stop_callable: Callable[[], bool] = false_function,
                 current_avg_callable: Callable[[], int] | None = None,
                 max_avg_callable: Callable[[], int] | None = None
                 ):

        super().__init__()

        self.update = update
        self.cleanup_func = cleanup_func
        self.setup_func = setup_func
        self.exception = None
        self.stop_callable = stop_callable
        # self.interrupt = interrupt

        self.figure: Figure | None = None
        self.artists: list[Artist] | None = None
        self.animation = None
        self.refresh_time_ms: int = int(refresh_time_sec * 1000)
        # self.exception = None  # To store any exception from the update callback
        self.current_avg_callable = current_avg_callable
        self.max_avg_callable = max_avg_callable
        self._stop_button = None
        self._continue_button = None
        self._text_artist_for_avg = None

    def update_average(self) -> tuple:
        if self._text_artist_for_avg is None:
            return ()

        current_avg = self.current_avg_callable()
        max_avg = self.max_avg_callable()

        if current_avg and max_avg:
            text = self._get_averager_text_formatter(current_avg, max_avg)
            self._text_artist_for_avg.set_text(text)

        return (self._text_artist_for_avg, )

    def stop_from_animation(self):
        QTimer.singleShot(0, lambda: plt.close(self.figure))

    @staticmethod
    def _get_averager_text_formatter(curr_avg=None, max_avg=None):
        if curr_avg is None or max_avg is None:
            return f"n=?/?"
        return f"n={curr_avg}/{max_avg:g}"

    def _setup_averager_artist(self) -> Artist:
        text = self._get_averager_text_formatter()
        return self.figure.text(x=1.0, y=1.0,
                                s=text,
                                fontsize='large',
                                horizontalalignment='right',
                                verticalalignment='top')

    def setup(self):
        # Set up the plot and store the figure and axes in the task.
        self.figure, self.artists = self.setup_func()

        if self.current_avg_callable is not None and self.max_avg_callable is not None:
            self._text_artist_for_avg = self._setup_averager_artist()

        # Add a stop button to the figure.
        self.add_stop_button()
        self.add_continue_button()

    def cleanup(self):
        self.cleanup_func()

    def handle_exception(self, e: Exception):
        self.interrupt.set()

    def execute(self):
        # Create the FuncAnimation using the task's figure.
        self.animation = FuncAnimation(
            fig=self.figure,
            func=self.step,
            interval=self.refresh_time_ms,
            blit=False,
            repeat=True,
            frames=200
        )

        # Run the event loop in a try/finally so we can check for exceptions afterwards.
        plt.show()  # This blocks until the figure is closed.

        # raising exception
        if self.exception:
            raise self.exception

        # checking the stop callable
        # if it arrived here without setting the stop callable
        # there are two options: either interrupt is on or user closed window
        # in both cases we say interrupt on
        if not self.stop_callable():
            self.interrupt.set()

    def stop_from_button(self):
        # Stop the animation's event source.
        if self.animation is not None:
            # print('stopping animation')
            self.animation.event_source.stop()

        # Close the task's figure so that plt.show() returns.
        if self.figure is not None:
            # print('closing fig')
            plt.close(self.figure)

    def stop_when_button_pressed(self, event):
        self.report_status(Status.STOPPED)
        self.stop_from_button()
        # self.interrupt.set()

    def continue_when_button_pressed(self, event):
        self.stop_from_button()
        # self.interrupt.set()

    def add_stop_button(self):
        # Create a stop button on the figure.
        ax_stop = self.figure.add_axes([0.1, 0.9, 0.08, 0.08])
        ax_stop.set_axis_off()  # Hide the axis.
        self._stop_button = Button(ax_stop, '', image=STOP_ICON)
        # When clicked, call self.stop().
        self._stop_button.on_clicked(self.stop_when_button_pressed)

    def add_continue_button(self):
        ax_continue = self.figure.add_axes([0.9, 0.9, 0.08, 0.08])
        ax_continue.set_axis_off()

        self._continue_button = Button(ax_continue, '', image=SAVE_ICON)
        # When clicked, call self.stop().
        self._continue_button.on_clicked(self.continue_when_button_pressed)

    def check_stop_status(self):
        return self.interrupt.is_set() or self.stop_callable()

    def step(self, frame):
        text_artist_as_tuple = ()

        try:
            if self.check_stop_status():
                self.stop_from_animation()
            data = self.read_data()

            if data is not None:
                self.artists = self.update(self.artists, data)
                text_artist_as_tuple = self.update_average()
            # Always return the same artist list so blitting remains stable.

        except Exception as e:
            self.exception = e
            self.stop_from_animation()
            self.interrupt.set()

        # Always return the artist tuple expected by blitting.
        artists = (*self.artists, *text_artist_as_tuple)
        return artists
