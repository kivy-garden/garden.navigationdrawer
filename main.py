'''
Example program demonstrating NavigationDrawer.
'''

from kivy.app import App
from kivy.base import runTouchApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp

from navigationdrawer import NavigationDrawer


class ExampleApp(App):
    def build(self):
    
        navigationdrawer = NavigationDrawer()

        side_panel = BoxLayout(orientation='vertical')
        side_panel.add_widget(Label(text='Panel label'))
        side_panel.add_widget(Button(text='A button'))
        side_panel.add_widget(Button(text='Another button'))
        navigationdrawer.add_widget(side_panel)

        label_head = '''[b]Example label filling main panel[/b]\n\n[color=ff0000](pull from left to right!)[/color]\n\nIn this example, the left panel is a simple boxlayout menu, and this main panel is a BoxLayout with a label and example image.\n\nSeveral preset layouts are available (see buttons below), but users may edit every parameter for much more customisation.'''
        main_panel = BoxLayout(orientation='vertical')
        label_bl = BoxLayout(orientation='horizontal')
        label = Label(text=label_head, font_size='15sp',
                           markup=True, valign='top')
        label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
        label_bl.add_widget(label)
        label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
        main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
        main_panel.add_widget(label_bl)
        main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
        main_panel.add_widget(Image(source='red_pixel.png', allow_stretch=True,
                                    keep_ratio=False, size_hint_y=0.2))
        navigationdrawer.add_widget(main_panel)
        label.bind(size=label.setter('text_size'))

        def set_anim_type(name):
            navigationdrawer.anim_type = name
        modes_layout = BoxLayout(orientation='horizontal')
        modes_layout.add_widget(Label(text='preset\nanims:'))
        slide_in_button = Button(text='slide_in')
        slide_in_button.bind(on_press=lambda j: set_anim_type('slide_in'))
        fade_in_button = Button(text='fade_in')
        fade_in_button.bind(on_press=lambda j: set_anim_type('fade_in'))
        reveal_button = Button(text='reveal_\nfrom_\nbelow')
        reveal_button.bind(on_press=lambda j: set_anim_type('reveal_from_below'))
        modes_layout.add_widget(slide_in_button)
        modes_layout.add_widget(fade_in_button)
        modes_layout.add_widget(reveal_button)
        main_panel.add_widget(modes_layout)


        button = Button(text='toggle NavigationDrawer state (animate)', size_hint_y=0.2)
        button.bind(on_press=lambda j: navigationdrawer.toggle_state())
        button2 = Button(text='toggle NavigationDrawer state (jump)', size_hint_y=0.2)
        button2.bind(on_press=lambda j: navigationdrawer.toggle_state(False))
        button3 = Button(text='toggle _main_above', size_hint_y=0.2)
        button3.bind(on_press=navigationdrawer.toggle_main_above)
        main_panel.add_widget(button)
        main_panel.add_widget(button2)
        main_panel.add_widget(button3)

        return navigationdrawer

    def on_pause(self):
        return True


if __name__ == '__main__':
    ExampleApp().run()


    
