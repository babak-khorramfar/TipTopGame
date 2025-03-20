# main.py
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
from game_2x2 import Game2x2Screen
from game_3x3 import Game3x3Screen
from game_4x4 import Game4x4Screen
from game_6x6 import Game6x6Screen


def get_contrast_text_color(bg_color):
    """اگر پس‌زمینه روشن بود متن سیاه، در غیر این صورت سفید."""
    r, g, b, _ = bg_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return [0, 0, 0, 1] if lum > 0.5 else [1, 1, 1, 1]


class RoundedButton(Button):
    """
    دکمه لبه‌گرد با رنگ پس‌زمینه خالص.
    - پس‌زمینه پیش‌فرض کیوی را کاملاً حذف می‌کنیم (background_normal="" و background_color=(0,0,0,0))
    - رنگ bg_color را در canvas رسم می‌کنیم
    - رنگ متن را بر اساس روشن/تیره بودن bg_color تعیین می‌کنیم
    """

    bg_color = ListProperty([1, 1, 1, 1])
    corner_radius = NumericProperty(15)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # غیرفعال کردن پس‌زمینه پیش‌فرض
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)  # شفاف تا سفید دیده نشود
        # هر بار تغییر pos، size یا bg_color، دوباره رسم می‌کنیم
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            bg_color=self._on_bg_color,
        )
        # برای تعیین رنگ متن
        self._on_bg_color(self, self.bg_color)

    def _on_bg_color(self, instance, value):
        # رنگ متن را بر اساس روشن/تیره بودن رنگ پس‌زمینه تعیین می‌کنیم
        self.color = get_contrast_text_color(value)

    def _update_canvas(self, *args):
        # پس‌زمینه دلخواه را در canvas قبل از بافت دکمه می‌کشیم
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])


class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super(LauncherScreen, self).__init__(**kwargs)
        # پس‌زمینه خاکستری تیره
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=Window.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation="vertical", spacing=20, padding=20)

        # دکمه خروج (100×100)
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

        # لوگو
        logo = Image(
            source="assets/Logo.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 0.2),
        )
        main_layout.add_widget(logo)

        # گرید 2×2
        grid_anchor = AnchorLayout(size_hint=(1, 0.5))
        grid = GridLayout(cols=2, spacing=20, size_hint=(None, None), size=(550, 550))
        grid_anchor.add_widget(grid)

        # دکمه اول: 2×2 - قرمز
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

        # دکمه دوم: 4×4 - سبز
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

        # دکمه سوم: 3×3 (Coming Soon) - زرد
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

        # دکمه چهارم: 6×6 - آبی
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

        # فوتر
        footer = Label(
            text="Contact: info@hiphoptiptop.com    |    Website: www.HipHopTipTop.com",
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(footer)

        self.add_widget(main_layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class TipTopApp(App):
    def build(self):
        Window.fullscreen = "auto"
        sm = ScreenManager(transition=FadeTransition())
        # صفحه لانچر
        sm.add_widget(LauncherScreen(name="launcher"))
        # بازی‌های موجود
        sm.add_widget(Game2x2Screen(name="game_2x2"))
        sm.add_widget(Game3x3Screen(name="game_3x3"))
        sm.add_widget(Game4x4Screen(name="game_4x4"))
        sm.add_widget(Game6x6Screen(name="game_6x6"))
        sm.current = "launcher"
        return sm


if __name__ == "__main__":
    TipTopApp().run()
