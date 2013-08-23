NavigationDrawer
============

(Formerly called ActionPanel until I bothered to look up the normal name...)

NavigationDrawer is a kivy widget to duplicate the popular android
behaviour of having a panel hidden on the left of the screen, which
can be made visible by sliding from the left. It supports many
different animations and behaviours (movement, opacity, transparency,
stacking order), including several preset options.

The panel usually would contain (e.g.) a list of menu items, but
NavigationDrawer lets the user add any kivy widget for the role of side
panel and main panel. A normal usage might be to have a GridLayout
containing a list of menu items to navigate the app.

The file example.mp4 is a short video of this behaviour. It can also
be viewed at www.youtube.com/watch?v=VnXgn5L5r28&feature=youtu.be

Todo
----

Improve touch management
