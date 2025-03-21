from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
from game_2x2 import Game2x2Screen
from game_3x3 import Game3x3Screen
from game_4x4 import Game4x4Screen
from game_6x6 import Game6x6Screen


class RoundedButton(Button):
    bg_color = ListProperty([1, 1, 1, 1])
    corner_radius = NumericProperty(15)

    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            bg_color=self._on_bg_color,
        )
        self._on_bg_color(self, self.bg_color)

    def _on_bg_color(self, instance, value):
        r, g, b, _ = value
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        self.color = [0, 0, 0, 1] if lum > 0.5 else [1, 1, 1, 1]

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])


class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super(LauncherScreen, self).__init__(**kwargs)
        # استفاده از FloatLayout به عنوان ریشه
        root = FloatLayout()

        # پس‌زمینه: یک رنگ ثابت + تصویر cover
        with root.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg_rect = Rectangle(pos=root.pos, size=Window.size)
        root.bind(
            pos=lambda inst, val: setattr(
                self, "bg_rect", Rectangle(pos=inst.pos, size=inst.size)
            )
        )
        cover = Image(
            source="assets/cover.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos=(0, 0),
            opacity=1,
        )
        root.add_widget(cover)

        # main_layout: BoxLayout عمودی با تمام اجزا
        main_layout = BoxLayout(
            orientation="vertical", spacing=20, padding=20, size_hint=(1, 1)
        )

        # دکمه خروج (بالا سمت راست)
        exit_anchor = AnchorLayout(
            anchor_x="right", anchor_y="top", size_hint=(1, None), height=120
        )
        exit_btn = Button(
            background_normal="assets/exit.png",
            background_down="assets/exit_down.png",
            size_hint=(None, None),
            size=(100, 100),
            text="",
        )
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        exit_anchor.add_widget(exit_btn)
        main_layout.add_widget(exit_anchor)

        # لوگو: یک BoxLayout با ارتفاع ثابت 200 پیکسل
        logo_box = BoxLayout(size_hint=(1, None), height=200)
        # وسط‌چین کردن لوگو
        logo_anchor = AnchorLayout(anchor_x="center", anchor_y="center")
        logo = Image(
            source="assets/Logo.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=(800, 200),
        )
        logo.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        logo_anchor.add_widget(logo)
        logo_box.add_widget(logo_anchor)
        main_layout.add_widget(logo_box)

        # گرید دکمه‌های بازی
        grid_anchor = AnchorLayout(size_hint=(1, 0.5))
        grid = GridLayout(cols=2, spacing=20, size_hint=(None, None), size=(550, 550))
        grid_anchor.add_widget(grid)

        btn_2x2 = RoundedButton(
            text="Beginner's Grid",
            bg_color=[1, 0, 0, 1],
            size_hint=(None, None),
            size=(250, 250),
            corner_radius=20,
        )
        btn_2x2.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "game_2x2"
            )
        )
        grid.add_widget(btn_2x2)

        btn_4x4 = RoundedButton(
            text="Smart Squares",
            bg_color=[0, 1, 0, 1],
            size_hint=(None, None),
            size=(250, 250),
            corner_radius=20,
        )
        btn_4x4.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "game_4x4"
            )
        )
        grid.add_widget(btn_4x4)

        btn_3x3 = RoundedButton(
            text="Simple Challenge",
            bg_color=[1, 1, 0, 1],
            size_hint=(None, None),
            size=(250, 250),
            corner_radius=20,
        )
        btn_3x3.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "game_3x3"
            )
        )
        grid.add_widget(btn_3x3)

        btn_6x6 = RoundedButton(
            text="Ultimate Challenge",
            bg_color=[0, 0, 1, 1],
            size_hint=(None, None),
            size=(250, 250),
            corner_radius=20,
        )
        btn_6x6.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "game_6x6"
            )
        )
        grid.add_widget(btn_6x6)
        main_layout.add_widget(grid_anchor)

        # فوتر (پایین صفحه)
        footer = Label(
            text="Contact: info@hiphoptiptop.com | Website: www.HipHopTipTop.com",
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(footer)

        root.add_widget(main_layout)
        self.add_widget(root)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class TipTopApp(App):
    def build(self):
        Window.fullscreen = "auto"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LauncherScreen(name="launcher"))
        sm.add_widget(Game2x2Screen(name="game_2x2"))
        sm.add_widget(Game3x3Screen(name="game_3x3"))
        sm.add_widget(Game4x4Screen(name="game_4x4"))
        sm.add_widget(Game6x6Screen(name="game_6x6"))
        sm.current = "launcher"
        return sm


if __name__ == "__main__":
    TipTopApp().run()
