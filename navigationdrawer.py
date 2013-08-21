'''
NavigationDrawer
'''

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty, BoundedNumericProperty

from kivy.lang import Builder

Builder.load_string('''
<NavigationDrawer>:
    size_hint: (1,1)
    _side_panel: sidepanel
    _main_panel: mainpanel
    _join_image: joinimage
    side_panel_width: min(dp(250), 0.5*self.width)
    BoxLayout:
        id: sidepanel
        pos: root.pos
        height: root.height
        width: root.side_panel_width
    BoxLayout:
        id: mainpanel
        x: root.x + root.anim_progress*root.side_panel_width
        y: root.y
        size: root.size
        canvas:
            Color:
                rgba: (0,0,0,1)
            Rectangle:
                pos: self.pos
                size: self.size
    Image:
        id: joinimage
        source: 'navigationdrawer_gradient.png'
        mipmap: False
        width: dp(7)
        height: mainpanel.height
        x: mainpanel.x - self.width + 1
        y: mainpanel.y
        allow_stretch: True
        keep_ratio: False
''')

class NavigationDrawerException(Exception):
    '''Raised when add_widget or remove_widget called incorrectly on an NavigationDrawer.

    '''


class NavigationDrawer(StencilView):
    '''Widget taking two children, a side panel and a main panel,
    displaying them in a way that replicates the popular Android
    functionality (e.g. from ActionBarSherlock?).

    '''

    # Automatically bound to the first and second child widgets respectively.
    # Side panel may be shown by sliding out the main panel.
    _side_panel = ObjectProperty()
    _main_panel = ObjectProperty()
    _join_image = ObjectProperty()
    side_panel = ObjectProperty(None, allownone=True)
    main_panel = ObjectProperty(None, allownone=True)

    side_panel_width = NumericProperty()
    # Defaults (see kv) to minimum of 300dp or half navigationdrawer width

    # Touch properties
    touch_accept_width = NumericProperty('20dp')

    # Animation properties
    _touch = ObjectProperty(None, allownone=True)
    state = OptionProperty('closed',options=('open','closed'))
    anim_progress = NumericProperty(0)
    anim_time = NumericProperty(0.3) # Animation open/close time
    min_dist_to_open = NumericProperty(0.7)
    panel_init_x = NumericProperty(0)

    def add_widget(self, widget):
        if len(self.children) == 0:
            super(NavigationDrawer, self).add_widget(widget)
            self._side_panel = widget
        elif len(self.children) == 1:
            super(NavigationDrawer, self).add_widget(widget)
            self._main_panel = widget
        elif len(self.children) == 2:
            super(NavigationDrawer, self).add_widget(widget)
            self._join_image = widget
        elif self.side_panel is None:
            self._side_panel.add_widget(widget)
            self.side_panel = widget
        elif self.main_panel is None:
            self._main_panel.add_widget(widget)
            self.main_panel = widget
        else:
            raise NavigationDrawerException(
                'Can\'t add widgets directly to NavigationDrawer')

    def remove_widget(self, widget):
        if widget is self.side_panel:
            self._side_panel.remove_widget(widget)
            self.side_panel = None
        elif widget is self.main_panel:
            self._main_panel.remove_widget(widget)
            self.main_panel = None
        else:
            raise NavigationDrawerException(
                'Widget is neither the side or main panel, can\'t remove it.')

    def set_side_panel(self, widget):
        # Clear existing side panel entries
        if len(self._side_panel.children) > 0:
            for child in self._side_panel.children:
                self._side_panel.remove(child)
        # Set new side panel
        self._side_panel.add_widget(widget)
        self.side_panel = widget
    def set_main_panel(self, widget):
        # Clear existing side panel entries
        if len(self._main_panel.children) > 0:
            for child in self._main_panel.children:
                self._main_panel.remove(child)
        # Set new side panel
        self._main_panel.add_widget(widget)
        self.main_panel = widget

    def on_anim_progress(self, *args):
        if self.anim_progress > 1:
            self.anim_progress = 1
        elif self.anim_progress < 0:
            self.anim_progress = 0
        if self.anim_progress >= 1:
            self.state = 'open'
        elif self.anim_progress <= 0:
            self.state = 'closed'

    def on_state(self, *args):
        Animation.cancel_all(self)
        if self.state == 'open':
            self.anim_progress = 1
        else:
            self.anim_progress = 0

    def anim_to_state(self, state):
        if state == 'open':
            anim = Animation(anim_progress=1,
                             duration=self.anim_time,
                             t='out_cubic')
            anim.start(self)
        elif state == 'closed':
            anim = Animation(anim_progress=0,
                             duration=self.anim_time,
                             t='out_cubic')
            anim.start(self)
        else:
            raise NavigationDrawerException(
                'Invalid state received, should be one of `open` or `closed`')

    def toggle_state(self, animate=True):
        '''Toggles from open to closed or vice versa, optionally animating or
simply jumping.'''
        if self.state == 'open':
            if animate:
                self.anim_to_state('closed')
            else:
                self.state = 'closed'
        elif self.state == 'closed':
            if animate:
                self.anim_to_state('open')
            else:
                self.state = 'open'

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or self._touch is not None:
            super(NavigationDrawer, self).on_touch_down(touch)
            return 
        if self.anim_progress > 0.001:
            valid_region = self._main_panel.x <= touch.x <= (self._main_panel.x + self._main_panel.width)
        else:
            valid_region = self.x <= touch.x <= (self.x + self.touch_accept_width)
        if not valid_region:
            super(NavigationDrawer, self).on_touch_down(touch)
            return False
        Animation.cancel_all(self)
        self._panel_init_x = self._main_panel.x
        self._touch = touch
        touch.ud['type'] = self.state
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch is self._touch:
            dx = touch.x - touch.ox
            
            self.anim_progress = max(0,min((self._panel_init_x + dx) / self.side_panel_width,1))
        else:
            super(NavigationDrawer, self).on_touch_move(touch)
            return

    def on_touch_up(self, touch):
        if touch is self._touch:
            self._touch = None
            init_state = touch.ud['type']
            touch.ungrab(self)
            if init_state == 'open':
                if self.anim_progress >= 0.975:
                        self.anim_to_state('closed')
                else:
                    self._anim_relax()
            else:
                self._anim_relax()
        else:
            super(NavigationDrawer, self).on_touch_up(touch)
            return

    def _anim_relax(self):
        '''Animates to the open or closed position, depending on whether the
        current position is past self.min_dist_to_open.

        '''
        if self.anim_progress > self.min_dist_to_open:
            self.anim_to_state('open')
        else:
            self.anim_to_state('closed')

    
if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.image import Image
    from kivy.core.window import Window
    
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
    
    Window.add_widget(navigationdrawer)

    runTouchApp()
        

    
