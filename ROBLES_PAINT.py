# ============================================================
# Creative Paint Studio - Python Tkinter + Pillow Paint App
# ============================================================

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

# ------------------------------------------------------------
# Application settings
# ------------------------------------------------------------
APP_TITLE = "Creative Paint Studio"
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 600
MAX_HISTORY = 50

BG = "#F3F4F6"
TOOLBAR = "#FFFFFF"
PRIMARY = "#4F46E5"
SECONDARY = "#E0E7FF"
TEXT = "#1F2937"
ACCENT = "#10B981"
CANVAS_BG = "#FFFFFF"
BORDER = "#D1D5DB"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SECTION = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")
FONT_STATUS = ("Segoe UI", 10)

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.LANCZOS

# ------------------------------------------------------------
# Main window
# ------------------------------------------------------------
root = tk.Tk()
root.title(APP_TITLE)
root.configure(bg=BG)
root.geometry("1220x760")
root.minsize(1100, 700)
try:
    root.eval("tk::PlaceWindow . center")
except Exception:
    pass

# ------------------------------------------------------------
# Drawing state
# ------------------------------------------------------------
image = None
photo_image = None
history = []

current_tool = "brush"
current_color = "#000000"
brush_size = 5
fill_shapes = False

last_point = None
shape_start = None

tool_buttons = {}

# ------------------------------------------------------------
# Widget references
# ------------------------------------------------------------
canvas = None
color_indicator = None
size_var = None
status_var = None
fill_var = None
brush_scale = None


# ============================================================
# CORE FUNCTIONS
# ============================================================

def clamp_point(x, y):
    return max(0, min(CANVAS_WIDTH - 1, x)), max(0, min(CANVAS_HEIGHT - 1, y))


def paint_color():
    return CANVAS_BG if current_tool == "eraser" else current_color


def push_history():
    global history
    history.append(image.copy())
    if len(history) > MAX_HISTORY:
        history.pop(0)


def refresh_canvas():
    global photo_image
    photo_image = ImageTk.PhotoImage(image)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=photo_image)


def update_status():
    status_var.set(
        "Tool: {}    |    Color: {}    |    Size: {} px    |    Fill: {}".format(
            current_tool.title(), current_color, brush_size,
            "On" if fill_shapes else "Off"
        )
    )


def make_button(parent, text, command, bg=PRIMARY, fg="white"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=FONT_BTN,
        bg=bg,
        fg=fg,
        activebackground=ACCENT if bg == PRIMARY else BORDER,
        activeforeground="white" if bg == PRIMARY else TEXT,
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=7,
        cursor="hand2",
        highlightthickness=0,
    )


# ------------------------------------------------------------
# Color and tool controls
# ------------------------------------------------------------
def choose_color():
    chosen = colorchooser.askcolor(initialcolor=current_color,
                                   title="Choose Drawing Color")
    if chosen and chosen[1]:
        set_color(chosen[1])


def set_color(color):
    global current_color
    current_color = color
    color_indicator.config(bg=color)
    update_status()


def set_tool(tool):
    global current_tool, last_point, shape_start
    current_tool = tool
    last_point = None
    shape_start = None
    canvas.delete("preview")

    for name, button in tool_buttons.items():
        if name == tool:
            button.config(bg=PRIMARY, fg="white",
                          activebackground=ACCENT, activeforeground="white")
        else:
            button.config(bg=SECONDARY, fg=TEXT,
                          activebackground=BORDER, activeforeground=TEXT)
    update_status()


def change_brush_size(value):
    global brush_size
    brush_size = int(value)
    size_var.set("Brush Size: {} px".format(brush_size))
    update_status()


def toggle_fill():
    global fill_shapes
    fill_shapes = fill_var.get()
    update_status()


# ------------------------------------------------------------
# Mouse drawing events
# ------------------------------------------------------------
def start_drawing(event):
    global last_point, shape_start
    x, y = clamp_point(event.x, event.y)
    push_history()

    if current_tool in ("brush", "eraser"):
        last_point = (x, y)
        draw = ImageDraw.Draw(image)
        radius = max(1, brush_size // 2)
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=paint_color()
        )
        refresh_canvas()
    else:
        shape_start = (x, y)


def draw_motion(event):
    global last_point
    x, y = clamp_point(event.x, event.y)

    if current_tool in ("brush", "eraser") and last_point is not None:
        draw = ImageDraw.Draw(image)
        draw.line([last_point, (x, y)], fill=paint_color(), width=brush_size)
        last_point = (x, y)
        refresh_canvas()
    elif shape_start is not None:
        preview_shape_drawing((x, y))


def finish_drawing(event):
    global last_point, shape_start
    x, y = clamp_point(event.x, event.y)

    if current_tool in ("brush", "eraser"):
        last_point = None
    elif shape_start is not None:
        canvas.delete("preview")
        draw_final_shape(shape_start, (x, y))
        shape_start = None
        refresh_canvas()


def triangle_points(start, end):
    x0, y0 = start
    x1, y1 = end
    middle_x = (x0 + x1) // 2
    return [(middle_x, y0), (x0, y1), (x1, y1)]


def preview_shape_drawing(end):
    canvas.delete("preview")
    if shape_start is None:
        return

    x0, y0 = shape_start
    x1, y1 = end
    color = current_color
    width = max(1, brush_size)

    if current_tool == "line":
        canvas.create_line(x0, y0, x1, y1, fill=color, width=width,
                           tags="preview")

    elif current_tool == "rectangle":
        if fill_shapes:
            canvas.create_rectangle(x0, y0, x1, y1, fill=color,
                                    outline=color, tags="preview")
        else:
            canvas.create_rectangle(x0, y0, x1, y1, outline=color,
                                    width=width, tags="preview")

    elif current_tool == "oval":
        if fill_shapes:
            canvas.create_oval(x0, y0, x1, y1, fill=color,
                               outline=color, tags="preview")
        else:
            canvas.create_oval(x0, y0, x1, y1, outline=color,
                               width=width, tags="preview")

    elif current_tool == "triangle":
        points = triangle_points(shape_start, end)
        if fill_shapes:
            canvas.create_polygon(points, fill=color, outline=color,
                                  tags="preview")
        else:
            flat = points + [points[0]]
            canvas.create_line(flat, fill=color, width=width,
                               tags="preview", smooth=False)


def draw_final_shape(start, end):
    draw = ImageDraw.Draw(image)
    color = current_color
    width = max(1, brush_size)

    if current_tool == "line":
        draw.line([start, end], fill=color, width=width)

    elif current_tool == "rectangle":
        box = [min(start[0], end[0]), min(start[1], end[1]),
               max(start[0], end[0]), max(start[1], end[1])]
        if fill_shapes:
            draw.rectangle(box, fill=color)
        else:
            draw.rectangle(box, outline=color, width=width)

    elif current_tool == "oval":
        box = [min(start[0], end[0]), min(start[1], end[1]),
               max(start[0], end[0]), max(start[1], end[1])]
        if fill_shapes:
            draw.ellipse(box, fill=color)
        else:
            draw.ellipse(box, outline=color, width=width)

    elif current_tool == "triangle":
        points = triangle_points(start, end)
        if fill_shapes:
            draw.polygon(points, fill=color)
        else:
            draw.line(points + [points[0]], fill=color, width=width,
                      joint="curve")


# ------------------------------------------------------------
# Canvas controls
# ------------------------------------------------------------
def undo():
    global image
    if not history:
        messagebox.showinfo("Undo", "There is nothing to undo.")
        return
    image = history.pop()
    refresh_canvas()


def clear_canvas():
    answer = messagebox.askyesno(
        "Clear Canvas",
        "Are you sure you want to clear the entire canvas?"
    )
    if answer:
        push_history()
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, CANVAS_WIDTH, CANVAS_HEIGHT], fill=CANVAS_BG)
        refresh_canvas()


def open_image():
    global image
    path = filedialog.askopenfilename(
        title="Open Image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
        ]
    )
    if not path:
        return

    try:
        loaded = Image.open(path).convert("RGB")
        loaded.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT), RESAMPLE_FILTER)

        fitted = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), CANVAS_BG)
        offset_x = (CANVAS_WIDTH - loaded.width) // 2
        offset_y = (CANVAS_HEIGHT - loaded.height) // 2
        fitted.paste(loaded, (offset_x, offset_y))

        push_history()
        image = fitted
        refresh_canvas()
    except Exception as error:
        messagebox.showerror("Open Failed", "Could not open image:\n{}".format(error))


def save_image():
    path = filedialog.asksaveasfilename(
        title="Save Image",
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
        ]
    )
    if not path:
        return

    try:
        extension = path.lower().rsplit(".", 1)[-1]
        if extension in ("jpg", "jpeg"):
            image.convert("RGB").save(path, format="JPEG", quality=95)
        elif extension == "bmp":
            image.save(path, format="BMP")
        else:
            image.save(path, format="PNG")
        messagebox.showinfo("Saved", "Image saved successfully!")
    except Exception as error:
        messagebox.showerror("Save Failed", "Could not save image:\n{}".format(error))


# ============================================================
# BUILD THE INTERFACE
# ============================================================

header = tk.Frame(root, bg=PRIMARY, height=70)
header.pack(fill=tk.X)
header.pack_propagate(False)
tk.Label(header, text=APP_TITLE, font=FONT_TITLE, bg=PRIMARY, fg="white").pack(
    side=tk.LEFT, padx=24
)
tk.Label(header, text="Draw • Shape • Create", font=FONT_BODY,
         bg=PRIMARY, fg=SECONDARY).pack(side=tk.LEFT)

main_area = tk.Frame(root, bg=BG)
main_area.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

# ---------- Left toolbar ----------
toolbar = tk.Frame(main_area, bg=TOOLBAR, width=250,
                   highlightbackground=BORDER, highlightthickness=1)
toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
toolbar.pack_propagate(False)


def section(parent, title):
    frame = tk.LabelFrame(parent, text=title, font=FONT_SECTION,
                          bg=TOOLBAR, fg=PRIMARY, padx=10, pady=8,
                          highlightbackground=BORDER, highlightthickness=1)
    frame.pack(fill=tk.X, padx=12, pady=8)
    return frame


tools_frame = section(toolbar, "Drawing Tools")
tool_specs = [
    ("brush", "Brush"),
    ("eraser", "Eraser"),
    ("line", "Line"),
    ("rectangle", "Rectangle"),
    ("oval", "Oval"),
    ("triangle", "Triangle"),
]
for name, label in tool_specs:
    button = make_button(tools_frame, label, lambda t=name: set_tool(t),
                         bg=SECONDARY, fg=TEXT)
    button.config(activebackground=BORDER, activeforeground=TEXT)
    button.pack(fill=tk.X, pady=3)
    tool_buttons[name] = button

color_frame = section(toolbar, "Color Controls")
color_indicator = tk.Label(color_frame, text="Current Color", bg=current_color,
                           fg="white", font=FONT_BODY, width=18,
                           relief=tk.SUNKEN, bd=2, pady=5)
color_indicator.pack(fill=tk.X, pady=(0, 8))

make_button(color_frame, "Choose Color", choose_color).pack(fill=tk.X, pady=3)

quick_colors = [
    ("Black", "#000000", "white"),
    ("Red", "#EF4444", "white"),
    ("Blue", "#3B82F6", "white"),
    ("Green", "#10B981", "white"),
    ("Yellow", "#FACC15", TEXT),
    ("Purple", "#8B5CF6", "white"),
]
for name, hex_color, text_color in quick_colors:
    make_button(color_frame, name, lambda c=hex_color: set_color(c),
                bg=hex_color, fg=text_color).pack(fill=tk.X, pady=2)

brush_frame = section(toolbar, "Brush Controls")
size_var = tk.StringVar(value="Brush Size: 5 px")
tk.Label(brush_frame, textvariable=size_var, font=FONT_BODY,
         bg=TOOLBAR, fg=TEXT).pack(anchor="w")
brush_scale = tk.Scale(
    brush_frame, from_=1, to=100, orient=tk.HORIZONTAL,
    command=change_brush_size, bg=TOOLBAR, fg=TEXT,
    troughcolor=SECONDARY, highlightbackground=TOOLBAR,
    length=200, showvalue=True
)
brush_scale.set(5)
brush_scale.pack(fill=tk.X, pady=(4, 8))

fill_var = tk.BooleanVar(value=False)
tk.Checkbutton(
    brush_frame, text="Fill Shapes", variable=fill_var,
    command=toggle_fill, font=FONT_BODY, bg=TOOLBAR, fg=TEXT,
    activebackground=TOOLBAR, selectcolor=SECONDARY
).pack(anchor="w")

control_frame = section(toolbar, "Canvas Controls")
make_button(control_frame, "Undo", undo, bg=ACCENT).pack(fill=tk.X, pady=3)
make_button(control_frame, "Clear", clear_canvas, bg="#EF4444").pack(fill=tk.X, pady=3)
make_button(control_frame, "Open", open_image, bg=PRIMARY).pack(fill=tk.X, pady=3)
make_button(control_frame, "Save", save_image, bg=PRIMARY).pack(fill=tk.X, pady=3)

# ---------- Right canvas area ----------
canvas_area = tk.Frame(main_area, bg=BG)
canvas_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

canvas_holder = tk.Frame(canvas_area, bg=BORDER, padx=2, pady=2)
canvas_holder.pack(padx=4, pady=4)

canvas = tk.Canvas(
    canvas_holder,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    bg=CANVAS_BG,
    highlightthickness=0,
    cursor="crosshair"
)
canvas.pack()

canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_motion)
canvas.bind("<ButtonRelease-1>", finish_drawing)

status_var = tk.StringVar()
status_bar = tk.Label(canvas_area, textvariable=status_var, font=FONT_STATUS,
                      bg=TOOLBAR, fg=TEXT, anchor="w", padx=12, pady=6,
                      highlightbackground=BORDER, highlightthickness=1)
status_bar.pack(fill=tk.X, padx=4, pady=(4, 0))

# ------------------------------------------------------------
# Start
# ------------------------------------------------------------
image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), CANVAS_BG)
set_tool("brush")
change_brush_size(5)
refresh_canvas()
update_status()

root.mainloop()