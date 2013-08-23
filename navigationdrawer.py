'''NavigationDrawer
================

The NavigationDrawer widget provides a hidden panel view designed to
duplicate the popular Android layout.  The user views one main widget
but can slide from the left of the screen to view a second, previously
hidden widget. The transition between open/closed is smoothly
animated, with the parameters (anim time, panel width, touch
detection) all user configurable. If the panel is released without
being fully open or closed, it animates to an appropriate
configuration.

NavigationDrawer supports many different animation properties,
including moving one or both of the side/main panels, darkening
either/both widgets, changing side panel opacity, and changing which
widget is on top. The user can edit these individually to taste (this
is enough rope to hang oneself, it's easy to make a useless or silly
configuration!), or use one of a few preset animations.

The hidden panel might normally a set of navigation buttons, but the
implementation lets the user use any widget(s).

The first widget added to the NavigationDrawer is automatically used
as the side panel, and the second widget as the main panel. No further
widgets can be added, further changes are left to the user via editing
the panel widgets.

Example::

    class ExampleApp(App):
        def build(self):
            navigationdrawer = NavigationDrawer()

            side_panel = BoxLayout(orientation='vertical')
            side_panel.add_widget(Label(text='Panel label'))
            side_panel.add_widget(Button(text='A button'))
            side_panel.add_widget(Button(text='Another button'))
            navigationdrawer.add_widget(side_panel)

            label_head = '[b]Example label filling main panel[/b]\n\n[color=ff0000](pull from left to right!)[/color]\n\nIn this example, the left panel is a simple boxlayout menu, and this main panel is a BoxLayout with a label and example image.\n\n'
            main_panel = BoxLayout(orientation='vertical')
            label = Label(text=label_head+riker, font_size='15sp',
                               markup=True, valign='top', padding=(-30,-30))
            main_panel.add_widget(label)
            navigationdrawer.add_widget(main_panel)
            label.bind(size=label.setter('text_size'))
            button = Button(text='toggle NavigationDrawer state (animate)', size_hint_y=0.2)
            button.bind(on_press=lambda j: navigationdrawer.toggle_state())
            button2 = Button(text='toggle NavigationDrawer state (jump)', size_hint_y=0.2)
            button2.bind(on_press=lambda j: navigationdrawer.toggle_state(False))
            main_panel.add_widget(button)
            main_panel.add_widget(button2)

            return navigationdrawer

    ExampleApp().run()

'''

__all__ = ('NavigationDrawer', )

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, OptionProperty, BooleanProperty

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
        y: root.y
        x: root.x - (1-root._anim_progress)*root._side_panel_init_offset*root.side_panel_width
        height: root.height
        width: root.side_panel_width
        opacity: root._side_panel_opacity + (1-root._side_panel_opacity)*root._anim_progress
        canvas:
            Color:
                rgba: (0,0,0,1)
            Rectangle:
                pos: self.pos
                size: self.size
        canvas.after:
            Color:
                rgba: (0,0,0,(1-root._anim_progress)*root._main_panel_darkness)
            Rectangle:
                size: self.size
                pos: self.pos
    BoxLayout:
        id: mainpanel
        x: root.x + root._anim_progress*root.side_panel_width*root._main_panel_final_offset
        y: root.y
        size: root.size
        canvas:
            Color:
                rgba: (0,0,0,1)
            Rectangle:
                pos: self.pos
                size: self.size
        canvas.after:
            Color:
                rgba: (0,0,0,root._anim_progress*root._main_panel_darkness)
            Rectangle:
                size: self.size
                pos: self.pos
    Image:
        id: joinimage
        opacity: min(sidepanel.opacity, 0 if root._anim_progress < 0.00001 else min(root._anim_progress*40,1))
        source: 'navigationdrawer_gradient_rtol.png' if root._main_above else 'navigationdrawer_gradient_ltor.png'
        mipmap: False
        width: dp(7)
        height: root._side_panel.height
        x: (mainpanel.x - self.width + 1) if root._main_above else (sidepanel.x + sidepanel.width - 1)
        y: root.y
        allow_stretch: True
        keep_ratio: False
''')

class NavigationDrawerException(Exception):
    '''Raised when add_widget or remove_widget called incorrectly on a NavigationDrawer.

    '''


class NavigationDrawer(StencilView):
    '''Widget taking two children, a side panel and a main panel,
    displaying them in a way that replicates the popular Android
    functionality. See module documentation for more info.

    '''

    # Internal references for side, main and image widgets
    _side_panel = ObjectProperty()
    _main_panel = ObjectProperty()
    _join_image = ObjectProperty()

    side_panel = ObjectProperty(None, allownone=True)
    '''Automatically bound to whatever widget is added as the hidden panel.'''
    main_panel = ObjectProperty(None, allownone=True)
    '''Automatically bound to whatever widget is added as the main panel.'''

    side_panel_width = NumericProperty()
    '''The width of the hidden side panel. Defaults to the minimum of
250dp or half the NavigationDrawer width.'''

    # Touch properties
    touch_accept_width = NumericProperty('9dp')
    '''Distance from the left of the NavigationDrawer in which to grab the
touch and allow revealing of the hidden panel.'''
    _touch = ObjectProperty(None, allownone=True) # The currently active touch

    # Animation properties
    state = OptionProperty('closed',options=('open','closed'))
    '''Specifies the state of the widget. Must be one of 'open' or
'closed'. Setting its value automatically jumps to the relevant state,
or users may use the anim_to_state() method to animate the
transition.'''
    anim_time = NumericProperty(0.3)
    '''The time taken for the panel to slide to the open/closed state when
released or manually animated with anim_to_state.'''
    min_dist_to_open = NumericProperty(0.7)
    '''Must be between 0 and 1. Specifies the fraction of the hidden panel width beyond which the NavigationDrawer will relax to open state when released. Defaults to 0.7.'''
    _anim_progress = NumericProperty(0) # Internal state controlling
                                        # widget positions
    _panel_init_x = NumericProperty(0) # Keeps track of where the main
                                       # panel was on touch down

    # Animation internal controls
    _main_above = BooleanProperty(True)
    _side_panel_init_offset = NumericProperty(1) # Initial offset for
                                                 # side panel as a
                                                 # fraction of its
                                                 # width
    _side_panel_darkness = NumericProperty(0)
    # Fade out darkness for side panel in hidden state

    _side_panel_opacity = NumericProperty(0.2)
    # Fade out opacity for side panel in hidden state

    _main_panel_final_offset = NumericProperty(0)
    # Final offset for main panel as a fraction of root.side_panel_width

    _main_panel_darkness = NumericProperty(0)
    # Fade out darkness as main panel slides to offset state

    anim_type = OptionProperty('hidden_underneath',
                               options=['hidden_underneath',
                                        'slide_from_above'])

    def on__main_above(self,*args):
        print 'on__main_above'
        if self.main_panel is not None or self.side_panel is not None:
            newval = self._main_above
            print 'main above toggled', newval, self._join_image.source, self._join_image.pos, self._join_image.size
            main_panel = self._main_panel
            side_panel = self._side_panel
            self.canvas.remove(main_panel.canvas)
            self.canvas.remove(side_panel.canvas)
            if newval:
                self.canvas.insert(0,main_panel.canvas)
                self.canvas.insert(0,side_panel.canvas)
            else:
                self.canvas.insert(0,side_panel.canvas)
                self.canvas.insert(0,main_panel.canvas)

    def toggle_main_above(self,*args):
        if self._main_above:
            self._main_above = False
        else:
            self._main_above = True


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
        '''Removes any existing side panel widgets, and replaces them with the
        argument `widget`.
        '''
        # Clear existing side panel entries
        if len(self._side_panel.children) > 0:
            for child in self._side_panel.children:
                self._side_panel.remove(child)
        # Set new side panel
        self._side_panel.add_widget(widget)
        self.side_panel = widget
    def set_main_panel(self, widget):
        '''Removes any existing main panel widgets, and replaces them with the
        argument `widget`.
        '''
        # Clear existing side panel entries
        if len(self._main_panel.children) > 0:
            for child in self._main_panel.children:
                self._main_panel.remove(child)
        # Set new side panel
        self._main_panel.add_widget(widget)
        self.main_panel = widget

    def on__anim_progress(self, *args):
        if self._anim_progress > 1:
            self._anim_progress = 1
        elif self._anim_progress < 0:
            self._anim_progress = 0
        if self._anim_progress >= 1:
            self.state = 'open'
        elif self._anim_progress <= 0:
            self.state = 'closed'

    def on_state(self, *args):
        Animation.cancel_all(self)
        if self.state == 'open':
            self._anim_progress = 1
        else:
            self._anim_progress = 0

    def anim_to_state(self, state):
        '''If not already in state `state`, animates smoothly to it, taking
        the time given by self.anim_time. State may be either 'open'
        or 'closed'.

        '''
        if state == 'open':
            anim = Animation(_anim_progress=1,
                             duration=self.anim_time,
                             t='out_cubic')
            anim.start(self)
        elif state == 'closed':
            anim = Animation(_anim_progress=0,
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
        if self._anim_progress > 0.001:
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
            
            self._anim_progress = max(0,min((self._panel_init_x + dx) / self.side_panel_width,1))
        else:
            super(NavigationDrawer, self).on_touch_move(touch)
            return

    def on_touch_up(self, touch):
        if touch is self._touch:
            self._touch = None
            init_state = touch.ud['type']
            touch.ungrab(self)
            if init_state == 'open':
                if self._anim_progress >= 0.975:
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
        if self._anim_progress > self.min_dist_to_open:
            self.anim_to_state('open')
        else:
            self.anim_to_state('closed')

    def _choose_image(self,*args):
        '''Chooses which image to display as the main/side separator, based on
        _main_above.'''
        if self._main_above:
            return 'navigationdrawer_gradient_rtol.png'
        else:
            return 'navigationdrawer_gradient_ltor.png'

    
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
    button3 = Button(text='toggle _main_above', size_hint_y=0.2)
    button3.bind(on_press=navigationdrawer.toggle_main_above)
    main_panel.add_widget(button)
    main_panel.add_widget(button2)
    main_panel.add_widget(button3)
    
    Window.add_widget(navigationdrawer)

    runTouchApp()
        

    
