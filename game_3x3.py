from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from components import CardWidget, Sidebar, MainSection, SidebarRow
from kivy.uix.button import Button
from kivy.app import App


class Game3x3(BoxLayout):
    def __init__(self, **kwargs):
        super(Game3x3, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, 1)

        # 🎯 سکشن اصلی 3x3
        self.main_section = MainSection(size_hint=(1, 1), grid_size=[3, 3])

        # 🎨 9 رنگ مختلف برای پشت کارت‌ها
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

        # 📌 ساخت سایدبار با عرض 350 (کمی کوچکتر از 6x6)
        self.sidebar = Sidebar(
            show_logo=False, add_back_button=False, size_hint=(None, 1), width=350
        )
        self.add_widget(self.main_section)
        self.add_widget(self.sidebar)

        # پاک کردن محتوای قبلی سایدبار
        self.sidebar.clear_widgets()
        self.sidebar.rows = []
        self.sidebar.row_colors = row_colors

        # ✅ ایجاد 9 ردیف (هر ردیف 1 کارت دارد)
        for color in row_colors:
            row = SidebarRow(row_color=color, size_hint_y=None, height=55, cols=1)
            row.cols = 1
            self.sidebar.add_widget(row)
            self.sidebar.rows.append(row)

        # ✅ ایجاد دکمه‌های کنترلی
        button_panel = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=80,
            spacing=10,
            padding=[10, 5, 10, 5],
        )
        flip_button = Button(
            background_normal="assets/flip.png",
            background_down="assets/flip_down.png",
            size_hint=(None, None),
            size=(70, 70),
        )
        rotate_button = Button(
            background_normal="assets/rotate.png",
            background_down="assets/rotate_down.png",
            size_hint=(None, None),
            size=(70, 70),
        )
        return_button = Button(
            background_normal="assets/return.png",
            background_down="assets/return_down.png",
            size_hint=(None, None),
            size=(70, 70),
        )
        reset_button = Button(
            background_normal="assets/reset.png",
            background_down="assets/reset_down.png",
            size_hint=(None, None),
            size=(70, 70),
        )
        button_panel.add_widget(flip_button)
        button_panel.add_widget(rotate_button)
        button_panel.add_widget(return_button)
        button_panel.add_widget(reset_button)
        self.sidebar.add_widget(button_panel)

        # تنظیم دکمه‌های سایدبار
        self.sidebar.flip_button = flip_button
        self.sidebar.return_button = return_button
        self.sidebar.reset_button = reset_button
        self.sidebar.rotate_button = rotate_button

        # ✅ دکمه برگشت
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

        # ✅ ایجاد 9 کارت و افزودن به سایدبار
        self.all_cards = []
        for color in row_colors:
            card = CardWidget()
            card.card_color = color
            card.face_up = True
            card.in_sidebar = True
            card.size_hint = (None, None)
            card.size = (65, 65)  # اندازه کارت‌ها
            self.all_cards.append(card)
            self.sidebar.add_card(card)

        # 📌 تنظیم اندازه ردیف‌ها و کارت‌ها برای 3×3
        for row in self.sidebar.rows:
            row.height = 80  # ارتفاع هر ردیف کمتر از 6x6 است

        for card in self.all_cards:
            card.size = (65, 65)

        self.selected_card = None

        # اتصال دکمه‌ها به توابع کنترلی
        self.sidebar.flip_button.bind(on_press=self.flip_selected)
        self.sidebar.return_button.bind(on_press=self.return_selected)
        self.sidebar.rotate_button.bind(on_press=self.rotate_selected)
        self.sidebar.reset_button.bind(on_press=self.reset_main_section)

    # 🔄 توابع کنترلی بازی
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
                child.size = (65, 65)  # اندازه کارت‌ها
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
                child.size = (65, 65)
                self.sidebar.add_card(child)
                break


# **🔹 صفحه `Game3x3Screen` برای ScreenManager**
class Game3x3Screen(Screen):
    def __init__(self, **kwargs):
        super(Game3x3Screen, self).__init__(**kwargs)
        self.game = Game3x3()
        self.add_widget(self.game)
