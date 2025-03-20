# game_2x2.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from components import CardWidget, Sidebar, SidebarRow, MainSection


class Game2x2(BoxLayout):
    def __init__(self, **kwargs):
        super(Game2x2, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, 1)

        # سکشن اصلی با 2×2 خانه
        self.main_section = MainSection(size_hint=(1, 1), grid_size=[2, 2])

        # سایدبار
        self.sidebar = Sidebar(
            show_logo=False, add_back_button=False, size_hint=(None, 1), width=420
        )

        self.add_widget(self.main_section)
        self.add_widget(self.sidebar)

        # 4 رنگ پشت کارت و ردیف سایدبار
        row_colors = [
            [1, 0, 0, 1],  # قرمز
            [1, 1, 0, 1],  # زرد
            [0, 1, 0, 1],  # سبز
            [0, 0, 1, 1],  # آبی
        ]

        # پاک‌کردن و ساخت ردیف‌های جدید
        self.sidebar.clear_widgets()
        self.sidebar.rows = []
        self.sidebar.row_colors = row_colors

        # ایجاد 4 ردیف
        for color in row_colors:
            row = SidebarRow(row_color=color)
            self.sidebar.add_widget(row)
            self.sidebar.rows.append(row)

        # ساخت پنل دکمه‌ها (Flip, Rotate, Return, Reset)
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

        # ارجاع به دکمه‌های سایدبار
        self.sidebar.flip_button = flip_button
        self.sidebar.rotate_button = rotate_button
        self.sidebar.return_button = return_button
        self.sidebar.reset_button = reset_button

        # دکمه برگشت به صفحه اصلی
        back_button = Button(
            text="",
            size_hint=(1, None),
            height=50,
            background_normal="assets/back.png",
            background_down="assets/back_down.png",
        )
        # برگشت به لانچر
        from kivy.app import App

        back_button.bind(
            on_release=lambda x: setattr(
                App.get_running_app().root, "current", "launcher"
            )
        )
        self.sidebar.add_widget(back_button)

        # ایجاد کارت‌ها (4 کارت برای 2x2)
        for i in range(4):
            card = CardWidget()
            card.card_color = row_colors[i]  # کارت iام با رنگ iام
            card.size_hint = (None, None)
            card.face_up = True
            card.in_sidebar = True
            self.sidebar.add_card(card)

        self.selected_card = None

        # اتصال متدها به دکمه‌ها
        self.sidebar.flip_button.bind(on_press=self.flip_selected)
        self.sidebar.return_button.bind(on_press=self.return_selected)
        self.sidebar.rotate_button.bind(on_press=self.rotate_selected)
        self.sidebar.reset_button.bind(on_press=self.reset_main_section)

    def flip_selected(self, instance):
        for child in self.main_section.children:
            if isinstance(child, CardWidget) and child.selected:
                child.face_up = not child.face_up
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
                child.size = (80, 80)
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
                child.size = (80, 80)
                self.sidebar.add_card(child)
                break


class Game2x2Screen(Screen):
    def __init__(self, **kwargs):
        super(Game2x2Screen, self).__init__(**kwargs)
        self.game = Game2x2()
        self.add_widget(self.game)
