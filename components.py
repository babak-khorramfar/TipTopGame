# components.py
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate, Rectangle
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.animation import Animation
from kivy.app import App

CARD_MARGIN = 5


class CardWidget(Widget):
    face_up = BooleanProperty(True)
    angle = NumericProperty(0)
    card_color = ListProperty([1, 1, 1, 1])
    in_sidebar = BooleanProperty(True)
    selected = BooleanProperty(False)
    dragging = BooleanProperty(False)
    old_cell = ObjectProperty(None, allownone=True)

    touch_offset_x = NumericProperty(0)
    touch_offset_y = NumericProperty(0)

    scale_x = NumericProperty(1)
    selection_border_opacity = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CardWidget, self).__init__(**kwargs)
        self.size_hint = (4, 4)
        self.size = (80, 80)
        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            face_up=self.update_canvas,
            angle=self.update_canvas,
            selected=self.update_canvas,
            in_sidebar=self.update_canvas,
            scale_x=self.update_canvas,
            selection_border_opacity=self.update_canvas,
        )
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        center_point = (self.x + self.width / 2.0, self.y + self.height / 2.0)
        with self.canvas:
            PushMatrix()
            Rotate(angle=self.angle, origin=center_point)
            from kivy.graphics.context_instructions import Scale

            Scale(self.scale_x, 1, 1, origin=center_point)
            if self.in_sidebar:
                Color(0.2, 0.2, 0.2, 1)
            else:
                Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            if self.face_up:
                margin = CARD_MARGIN
                inner_w = self.width - 2 * margin
                inner_h = self.height - 2 * margin
                spacing = 2
                sq_w = (inner_w - spacing) / 2.0
                sq_h = (inner_h - spacing) / 2.0
                colors = [
                    [1, 0, 0, 1],
                    [0, 1, 0, 1],
                    [1, 1, 0, 1],
                    [0, 0, 1, 1],
                ]
                positions = [
                    (self.x + margin, self.y + margin + sq_h + spacing),
                    (
                        self.x + margin + sq_w + spacing,
                        self.y + margin + sq_h + spacing,
                    ),
                    (self.x + margin, self.y + margin),
                    (self.x + margin + sq_w + spacing, self.y + margin),
                ]
                for i in range(4):
                    Color(*colors[i])
                    RoundedRectangle(pos=positions[i], size=(sq_w, sq_h), radius=[5])
            else:
                Color(*self.card_color)
                d = self.width - 2 * CARD_MARGIN
                Ellipse(pos=(self.center_x - d / 2, self.center_y - d / 2), size=(d, d))
            if self.selected and not self.in_sidebar:
                Color(0.8, 0.8, 0.8, self.selection_border_opacity)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
            PopMatrix()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_offset_x = self.center_x - touch.x
            self.touch_offset_y = self.center_y - touch.y
            self.dragging = True
            if not self.in_sidebar:
                app = App.get_running_app()
                current_screen = app.root.get_screen(app.root.current)
                game_widget = current_screen.children[0]
                for child in game_widget.main_section.children:
                    if isinstance(child, CardWidget):
                        child.selected = False
                self.selected = True
                game_widget.selected_card = self
                self.selection_border_opacity = 1
                Animation(selection_border_opacity=0, duration=3).start(self)
                cell = game_widget.main_section.get_cell_for_card(self)
                if cell:
                    cell["occupied"] = False
                    cell["card"] = None
                self.old_cell = cell
            return True
        return super(CardWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.dragging:
            self.center_x = touch.x + self.touch_offset_x
            self.center_y = touch.y + self.touch_offset_y
            return True
        return super(CardWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            app = App.get_running_app()
            current_screen = app.root.get_screen(app.root.current)
            game_widget = current_screen.children[0]
            if self.in_sidebar and game_widget.main_section.collide_point(*touch.pos):
                if self.parent:
                    self.parent.remove_widget(self)
                snapped = game_widget.main_section.drop_card(self, touch.pos)
                if not snapped:
                    game_widget.sidebar.add_card(self)
                else:
                    self.in_sidebar = False
            else:
                if game_widget.main_section.collide_point(*touch.pos):
                    snapped = game_widget.main_section.drop_card(self, touch.pos)
                    if not snapped and self.old_cell:
                        self.pos = self.old_cell["pos"]
                        self.size = self.old_cell["size"]
                        self.old_cell["occupied"] = True
                        self.old_cell["card"] = self
                else:
                    if self.old_cell:
                        self.pos = self.old_cell["pos"]
                        self.size = self.old_cell["size"]
                        self.old_cell["occupied"] = True
                        self.old_cell["card"] = self
            self.old_cell = None
            if not self.in_sidebar:
                self.selected = True
                game_widget.selected_card = self
            return True
        return super(CardWidget, self).on_touch_up(touch)


class SidebarRow(GridLayout):
    def __init__(self, row_color, **kwargs):
        super(SidebarRow, self).__init__(**kwargs)
        self.row_color = row_color
        self.cols = kwargs.get("cols", 4)  # اگر مشخص نشود، مقدار پیش‌فرض 4 می‌گیرد.
        self.size_hint_y = None
        self.height = 110
        self.padding = [10, 10, 10, 10]
        self.spacing = 10
        with self.canvas.before:
            Color(*self.row_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Sidebar(BoxLayout):
    def __init__(self, show_logo=True, add_back_button=False, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, 1)
        self.width = 420
        self.padding = [20, 20, 20, 20]
        self.spacing = 15
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        if show_logo:
            self.logo = Image(
                source="assets/Logo.png",
                size_hint=(1, None),
                height=100,
                keep_ratio=True,
                allow_stretch=True,
            )
            self.add_widget(self.logo)

        # row_colors for sidebar will be set externally in game_6x6
        self.row_colors = (
            []
        )  # default empty; should be set in game-specific implementations
        self.rows = []

        # Button panel
        self.button_panel = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=100,
            spacing=15,
            padding=[10, 5, 10, 5],
        )
        self.flip_button = Button(
            background_normal="assets/flip.png",
            background_down="assets/flip_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        self.return_button = Button(
            background_normal="assets/return.png",
            background_down="assets/return_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        self.reset_button = Button(
            background_normal="assets/reset.png",
            background_down="assets/reset_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        self.rotate_button = Button(
            background_normal="assets/rotate.png",
            background_down="assets/rotate_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        self.button_panel.add_widget(self.flip_button)
        self.button_panel.add_widget(self.rotate_button)
        self.button_panel.add_widget(self.return_button)
        self.button_panel.add_widget(self.reset_button)
        self.add_widget(self.button_panel)

        if add_back_button:
            self.back_button = Button(
                text="",
                size_hint=(1, None),
                height=50,
                background_normal="assets/back.png",
                background_down="assets/back_down.png",
            )
            self.back_button.bind(
                on_release=lambda x: setattr(
                    App.get_running_app().root, "current", "launcher"
                )
            )
            self.add_widget(self.back_button)

    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)

    def add_card(self, card):
        # Add card to the row that matches its card_color
        row_index = None
        for i, color in enumerate(self.row_colors):
            if card.card_color[:3] == color[:3]:
                row_index = i
                break
        if row_index is not None and row_index < len(self.rows):
            card.size = (80, 80)
            self.rows[row_index].add_widget(card)
            card.in_sidebar = True
            card.face_up = True


class MainSection(FloatLayout):
    grid_size = ListProperty([None, None])

    def __init__(self, **kwargs):
        grid_size = kwargs.pop("grid_size", [None, None])
        super(MainSection, self).__init__(**kwargs)
        self.grid_size = grid_size
        self.cells = []
        self.bind(size=self.setup_cells, pos=self.setup_cells)

    def setup_cells(self, *args):
        self.canvas.before.clear()
        self.cells = []
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=self.pos, size=self.size)
            cell_size = min(
                self.width / self.grid_size[0], self.height / self.grid_size[1]
            )
            grid_width = cell_size * self.grid_size[0]
            grid_height = cell_size * self.grid_size[1]
            start_x = self.x + (self.width - grid_width) / 2
            start_y = self.y + (self.height - grid_height) / 2
            Color(0.7, 0.7, 0.7, 1)
            Line(rectangle=(start_x, start_y, grid_width, grid_height), width=2)
        cell_size = min(self.width / self.grid_size[0], self.height / self.grid_size[1])
        grid_width = cell_size * self.grid_size[0]
        grid_height = cell_size * self.grid_size[1]
        start_x = self.x + (self.width - grid_width) / 2
        start_y = self.y + (self.height - grid_height) / 2
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                cell_pos = (start_x + col * cell_size, start_y + row * cell_size)
                cell_dict = {
                    "pos": cell_pos,
                    "size": (cell_size, cell_size),
                    "occupied": False,
                    "card": None,
                }
                self.cells.append(cell_dict)

    def get_cell_for_card(self, card):
        for cell in self.cells:
            if cell["card"] == card:
                return cell
        return None

    def drop_card(self, card, drop_pos):
        best_cell = None
        best_dist = None
        for cell in self.cells:
            if not cell["occupied"]:
                cx = cell["pos"][0] + cell["size"][0] / 2.0
                cy = cell["pos"][1] + cell["size"][1] / 2.0
                dist = ((drop_pos[0] - cx) ** 2 + (drop_pos[1] - cy) ** 2) ** 0.5
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_cell = cell
        if best_cell:
            best_cell["occupied"] = True
            best_cell["card"] = card
            if card.parent != self:
                self.add_widget(card)
            card.size = best_cell["size"]
            card.pos = best_cell["pos"]
            from kivy.app import App

            app = App.get_running_app()
            for child in self.children:
                if isinstance(child, CardWidget):
                    child.selected = False
            card.selected = True
            app.root.selected_card = card
            return True
        return False

    def reset(self):
        for cell in self.cells:
            cell["occupied"] = False
            cell["card"] = None
