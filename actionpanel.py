'''
ActionPanel
'''

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty, BoundedNumericProperty

from kivy.lang import Builder

Builder.load_string('''
<ActionPanel>:
    size_hint: (1,1)
    _side_panel: sidepanel
    _main_panel: mainpanel
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
        source: 'actionpanel_gradient6.png'
        mipmap: True
        width: dp(10)
        height: mainpanel.height
        x: mainpanel.x - self.width + 1
        y: mainpanel.y
        allow_stretch: True
        keep_ratio: False
        # canvas.before:
        #     Color:
        #         rgba: (1,0,0,1)
        #     Rectangle:
        #         pos: self.pos
        #         size: self.size
    
    
''')

class ActionPanelException(Exception):
    '''Raised when add_widget or remove_widget called incorrectly on an ActionPanel.

    '''


class ActionPanel(StencilView):
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
    # Defaults (see kv) to minimum of 300dp or half actionpanel width

    # Animation properties
    _touch = ObjectProperty(None, allownone=True)
    side_panel_open = BooleanProperty(False)
    anim_progress = NumericProperty(0)
    panel_init_x = NumericProperty(0)

    def add_widget(self, widget):
        if len(self.children) == 0:
            super(ActionPanel, self).add_widget(widget)
            self._side_panel = widget
        elif len(self.children) == 1:
            super(ActionPanel, self).add_widget(widget)
            self._main_panel = widget
        elif len(self.children) == 2:
            super(ActionPanel, self).add_widget(widget)
            self._join_image = widget
        elif self.side_panel is None:
            self._side_panel.add_widget(widget)
            self.side_panel = widget
        elif self.main_panel is None:
            self._main_panel.add_widget(widget)
            self.main_panel = widget
        else:
            raise ActionPanelException(
                'Can\'t add widgets directly to ActionPanel')

    def remove_widget(self, widget):
        if widget is self.side_panel:
            self._side_panel.remove_widget(widget)
            self.side_panel = None
        elif widget is self.main_panel:
            self._main_panel.remove_widget(widget)
            self.main_panel = None
        else:
            raise ActionPanelException(
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
        if self.anim_progress > 0.9999:
            self.side_panel_open = True
        elif self.anim_progress < 0.0001:
            self.side_panel_open = False

    def on_side_panel_open(self, *args):
        Animation.cancel_all(self)
        if self.side_panel_open:
            self.anim_progress = 1
        else:
            self.anim_progress = 0.000001

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            super(ActionPanel, self).on_touch_down(touch)
            return 
        Animation.cancel_all(self)
        self._panel_init_x = self._main_panel.x
        self._touch = touch
    def on_touch_move(self, touch):
        if touch is self._touch:
            dx = touch.x - touch.ox
            
            self.anim_progress = max(0,min((self._panel_init_x + dx) / self.side_panel_width,1))
        else:
            super(ActionPanel, self).on_touch_move(touch)
            return

    def on_touch_up(self, touch):
        if touch is self._touch:
            self._touch = None
            self._anim_to_steady()
        else:
            super(ActionPanel, self).on_touch_up(touch)
            return

    def _anim_to_steady(self):
        if self.anim_progress > 0.7:
            # self.anim_progress = 1
            anim = Animation(anim_progress=1, duration=0.3, t='out_cubic')
        else:
            # self.anim_progress = 0
            anim = Animation(anim_progress=0, duration=0.3, t='out_cubic')
        anim.start(self)
        
        
        
        
            

    
if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.core.window import Window
    
    actionpanel = ActionPanel()

    side_panel = BoxLayout(orientation='vertical')
    side_panel.add_widget(Label(text='Panel label'))
    side_panel.add_widget(Button(text='A button'))
    side_panel.add_widget(Button(text='Another button'))
    actionpanel.add_widget(side_panel)

    label_head = '[b]Example label filling main panel[/b]\n\n(pull from left to right)\n\n'
    riker = "Some days you get the bear, and some days the bear gets you. I am your worst nightmare! You enjoyed that. When has justice ever been as simple as a rule book? For an android with no feelings, he sure managed to evoke them in others. Flair is what marks the difference between artistry and mere competence. Worf, It's better than music. It's jazz. The game's not big enough unless it scares you a little. We finished our first sensor sweep of the neutral zone. Your head is not an artifact! What? We're not at all alike!"
    main_panel = Label(text=label_head+riker+riker, font_size='20sp',
                       markup=True, valign='top', padding=(-30,-30))
    actionpanel.add_widget(main_panel)
    main_panel.bind(size=main_panel.setter('text_size'))
    
    Window.add_widget(actionpanel)

    runTouchApp()
        

    
