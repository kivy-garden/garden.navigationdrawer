'''
Example program demonstrating NavigationDrawer.
'''

from kivy.app import App
from kivy.base import runTouchApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window

from navigationdrawer import NavigationDrawer


class ExampleApp(App):
    def build(self):
    
        navigationdrawer = NavigationDrawer()

        side_panel = BoxLayout(orientation='vertical')
        side_panel.add_widget(Label(text='Panel label'))
        side_panel.add_widget(Button(text='A button'))
        side_panel.add_widget(Button(text='Another button'))
        navigationdrawer.add_widget(side_panel)

        label_head = '[b]Example label filling main panel[/b]\n\n[color=ff0000](pull from left to right!)[/color]\n\nIn this example, the left panel is a simple boxlayout menu, and this main panel is a BoxLayout with a label and example image.\n\n'
        riker = "Some days you get the bear, and some days the bear gets you. I am your worst nightmare! You enjoyed that. When has justice ever been as simple as a rule book? For an android with no feelings, he sure managed to evoke them in others. Flair is what marks the difference between artistry and mere competence. Worf, It's better than music. It's jazz. The game's not big enough unless it scares you a little. We finished our first sensor sweep of the neutral zone. Your head is not an artifact! What? We're not at all alike!"
        main_panel = BoxLayout(orientation='vertical')
        label = Label(text=label_head+riker, font_size='15sp',
                           markup=True, valign='top', padding=(-30,-30))
        main_panel.add_widget(label)
        main_panel.add_widget(Image(source='red_pixel.png', allow_stretch=True,
                                    keep_ratio=False))
        navigationdrawer.add_widget(main_panel)
        label.bind(size=label.setter('text_size'))
        button = Button(text='toggle NavigationDrawer state (animate)', size_hint_y=0.2)
        button.bind(on_press=lambda j: navigationdrawer.toggle_state())
        button2 = Button(text='toggle NavigationDrawer state (jump)', size_hint_y=0.2)
        button2.bind(on_press=lambda j: navigationdrawer.toggle_state(False))
        main_panel.add_widget(button)
        main_panel.add_widget(button2)

        return navigationdrawer


if __name__ == '__main__':
    ExampleApp().run()


    
