from tkinter import Tk


class MyTk(Tk):


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Make the window borderless
        self.overrideredirect(True)

        # Bind the move commands
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        # Set gray as the transparent color
        self.transparentcolor = "#123456"
        self.attributes("-transparentcolor", self.transparentcolor)
        self.configure(background=self.transparentcolor)

        # Make the window stay on top
        self.attributes("-topmost", True)

        # Bind END to close the window
        self.bind("<End>", lambda x: self.destroy())

    def start_move(self, event) -> None:
        """
        Save the position where the button was pressed.
        Used when dragging the window.
        """
        self.x = event.x
        self.y = event.y

    def stop_move(self, event) -> None:
        """
        Clear the saved starting position.
        Used when finished dragging the window.
        """
        self.x = None
        self.y = None

    def do_move(self, event) -> None:
        """
        Move the window by how much the mouse was moved.
        """
        x = self.winfo_x() + event.x - self.x
        y = self.winfo_y() + event.y - self.y
        self.geometry(f"+{x}+{y}")