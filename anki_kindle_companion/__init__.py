from aqt import mw
from aqt.qt import *

from .gui.window import KindleBrowserWindow


def on_browse_kindle():
    KindleBrowserWindow.show_modal(mw)


action = QAction("Browse Kindle", mw)
action.setShortcut("Ctrl+B")
action.triggered.connect(on_browse_kindle)
mw.form.menuTools.addAction(action)
