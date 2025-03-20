# game_6x6.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from components import CardWidget, Sidebar, MainSection, SidebarRow
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App


class Game6x6(BoxLayout):
    def __init__(self, **kwargs):
        super(Game6x6, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, 1)

        # سکشن اصلی 6x6
        self.main_section = MainSection(size_hint=(1, 1), grid_size=[6, 6])

        # 9 رنگ مختلف برای پشت کارت
        row_colors = [
            [0, 0, 1, 1],  # Blue
            [1, 0, 0, 1],  # Red
            [1, 1, 0, 1],  # Yellow
            [0, 1, 0, 1],  # Green
            [0.59, 0.29, 0, 1],  # Brown
            [0.5, 0.5, 0.5, 1],  # Gray
            [1, 0.5, 0, 1],  # Orange
            [1, 0.75, 0.8, 1],  # Pink
            [0.5, 0, 0.5, 1],  # Purple
        ]

        # ساخت سایدبار
        # دکمه‌ها و اندازه سایدبار را دست‌نخورده می‌گذاریم
        self.sidebar = Sidebar(
            show_logo=False, add_back_button=False, size_hint=(None, 1), width=420
        )
        self.add_widget(self.main_section)
        self.add_widget(self.sidebar)

        # پاک‌کردن ویجت‌های پیشین
        self.sidebar.clear_widgets()
        self.sidebar.rows = []
        self.sidebar.row_colors = row_colors

        # ایجاد 9 ردیف با ارتفاع کوچکتر (height=55)
        # بدون تغییر در دکمه‌ها
        for color in row_colors:
            row = SidebarRow(row_color=color, size_hint_y=None, height=50)
            row.cols = 4
            self.sidebar.add_widget(row)
            self.sidebar.rows.append(row)

        # ایجاد پنل دکمه‌ها (Flip, Rotate, Return, Reset) با اندازه پیشین دکمه‌ها (80×80)
        button_panel = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=100,
            spacing=10,
            padding=[10, 5, 10, 5],
        )
        flip_button = Button(
            background_normal="assets/flip.png",
            background_down="assets/flip_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        rotate_button = Button(
            background_normal="assets/rotate.png",
            background_down="assets/rotate_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        return_button = Button(
            background_normal="assets/return.png",
            background_down="assets/return_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        reset_button = Button(
            background_normal="assets/reset.png",
            background_down="assets/reset_down.png",
            size_hint=(None, None),
            size=(80, 80),
        )
        button_panel.add_widget(flip_button)
        button_panel.add_widget(rotate_button)
        button_panel.add_widget(return_button)
        button_panel.add_widget(reset_button)
        self.sidebar.add_widget(button_panel)
        self.sidebar.flip_button = flip_button
        self.sidebar.return_button = return_button
        self.sidebar.reset_button = reset_button
        self.sidebar.rotate_button = rotate_button

        # دکمه برگشت در انتهای سایدبار
        back_button = Button(
            text="",
            size_hint=(1, None),
            height=50,
            background_normal="assets/back.png",
            background_down="assets/back_down.png",
        )
        back_button.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "launcher"
            )
        )
        self.sidebar.add_widget(back_button)

        # ایجاد 36 کارت با اندازه پیش‌فرض (مثلاً 50×50)
        self.all_cards = []
        for color in row_colors:
            for i in range(4):
                card = CardWidget()
                card.card_color = color
                card.face_up = True
                card.in_sidebar = True
                card.size = (60, 60)  # اندازه پیش‌فرض در فایل اصلی
                self.all_cards.append(card)
                self.sidebar.add_card(card)

        # شرط: اگر بازی 9 ردیف است (مثلاً بازی 6x6)
        if len(row_colors) == 9:
            # Override اندازه ردیف‌ها و کارت‌ها
            for row in self.sidebar.rows:
                row.height = 80  # ارتفاع جدید برای هر ردیف
                # تنظیم padding (مثلاً: فاصله بین کارت‌ها محاسبه شود)
                available = (
                    self.sidebar.width - 20
                )  # اگر padding داخلی کلی 20 در هر طرف است
                spacing = (available - 4 * 70) / 3.0
                row.spacing = spacing
            for card in self.all_cards:
                card.size = (60, 60)  # اندازه جدید کارت‌ها

        self.selected_card = None

        # اتصال دکمه‌های سایدبار
        self.sidebar.flip_button.bind(on_press=self.flip_selected)
        self.sidebar.return_button.bind(on_press=self.return_selected)
        self.sidebar.rotate_button.bind(on_press=self.rotate_selected)
        self.sidebar.reset_button.bind(on_press=self.reset_main_section)

    def flip_selected(self, instance):
        for child in self.main_section.children:
            if isinstance(child, CardWidget) and child.selected:
                child.animate_flip()
                break

    def rotate_selected(self, instance):
        if not self.selected_card:
            for child in self.main_section.children:
                if isinstance(child, CardWidget) and child.selected:
                    self.selected_card = child
                    break
        if not self.selected_card:
            return
        old_angle = self.selected_card.angle
        new_angle = (old_angle + 90) % 360
        new_angle = round(new_angle / 90) * 90
        self.selected_card.angle = new_angle

    def reset_main_section(self, instance):
        for child in list(self.main_section.children):
            if isinstance(child, CardWidget):
                self.main_section.remove_widget(child)
                child.in_sidebar = True
                child.selected = False
                card.size = (50, 50)  # type: ignore
            self.sidebar.add_card(child)
        self.main_section.reset()

    def return_selected(self, instance):
        for child in list(self.main_section.children):
            if isinstance(child, CardWidget) and child.selected:
                cell = self.main_section.get_cell_for_card(child)
                if cell:
                    cell["occupied"] = False
                    cell["card"] = None
                self.main_section.remove_widget(child)
                child.in_sidebar = True
                child.selected = False
                child.size = (50, 50)
                self.sidebar.add_card(child)
                break


class Game6x6Screen(Screen):
    def __init__(self, **kwargs):
        super(Game6x6Screen, self).__init__(**kwargs)
        self.game = Game6x6()
        self.add_widget(self.game)
