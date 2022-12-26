from tkinter import Canvas
from typing import Optional


class RoundLabel(Canvas):

    def __init__(self, parent, width, height, radius: Optional[int] = None, fill: str = "black", outline: Optional[str] = None, bg: str = "white"):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=bg)

        if outline is None:
            outline = fill

        if radius is None:
            radius = int(0.5 * min(width, height))

        if radius > 0.5 * width:
            raise ValueError("Error: radius is greater than width.")

        if radius > 0.5 * height:
            raise ValueError("Error: radius is greater than height.")

        diameter = 2 * radius

        # Create fill
        self.create_polygon(0,height-radius,0,radius,radius,0,width-radius,0,width,radius,width,height-radius,width-radius,height,radius,height, fill=fill, outline=fill)
        self.create_arc(0,diameter,diameter,0, start=90, extent=90, fill=fill, outline=fill)
        self.create_arc(width-diameter,0,width,diameter, start=0, extent=90, fill=fill, outline=fill)
        self.create_arc(width,height-diameter,width-diameter,height, start=270, extent=90, fill=fill, outline=fill)
        self.create_arc(0,height-diameter,diameter,height, start=180, extent=90, fill=fill, outline=fill)

        # Create outline
        if outline != fill:
            # Create rectangle border
            self.create_line(radius-1, 0, 1+width-radius, 0, fill=outline)
            self.create_line(radius-1, height, 1+width-radius, height, fill=outline)
            self.create_line(0, radius-1, 0, 1+height-radius, fill=outline)
            self.create_line(width, radius-1, width, 1+height-radius, fill=outline)
            # Create arc border
            self.create_arc(0,diameter,diameter,0,                       start= 90, extent=90, outline=outline, style="arc")
            self.create_arc(width-diameter,0,width,diameter,             start=  0, extent=90, outline=outline, style="arc")
            self.create_arc(width,height-diameter,width-diameter,height, start=270, extent=90, outline=outline, style="arc")
            self.create_arc(0,height-diameter,diameter,height,           start=180, extent=90, outline=outline, style="arc")

        x0, y0, x1, y1 = self.bbox("all")
        self.configure(width=x1-x0-3, height=y1-y0-3)