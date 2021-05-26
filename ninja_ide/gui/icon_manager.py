from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import (
    QIconEngine,
    QPixmap,
    QPainter,
    QIcon,
    QFont,
    QFontDatabase,
    QColor,
)

from PyQt5.QtCore import (
    Qt,
    QRect,
    QPoint,
    QByteArray,
    QFile,
)

from ninja_ide.tools.logger import NinjaLogger

# TODO: support more fonts
# TODO: complete CHARMAP

CHARMAP = {
    'bookmark': 0xf02e,
    'bug': 0xf188,
    'cube': 0xf1b2,
    'exclamation-triangle': 0xf071,
    'file': 0xf15b,
    'file-code': 0xf1c9,
    'folder': 0xf07b,
    'folder-open': 0xf07c,
    'play': 0xf04b,
    'square-full': 0xf45c,
    'stop': 0xf04d,
}
DEFAULT_ESCALE_FACTOR = 1.0
DEFAULT_ICON_COLOR = 'black'
DEFAULT_OPTIONS = {
    'color': DEFAULT_ICON_COLOR,
    'scale_factor': DEFAULT_ESCALE_FACTOR
}

logger = NinjaLogger(__name__)


class IconManager:

    def __init__(self):
        self.painter = Painter()
        self.font_name = ''
        self.cache = {}
        self.load_font()

    def icon(self, name: str, **kwargs) -> QIcon:
        key = f'{name}-{kwargs}'
        if key not in self.cache:
            options = DEFAULT_OPTIONS.copy()
            options['name'] = name
            options.update(kwargs)

            engine = IconEngine(self, self.painter, options)
            self.cache[key] = QIcon(engine)
        return self.cache[key]

    def load_font(self):
        if QApplication.instance() is None:
            logger.warning('No QApplication instance found')
            return

        font_file = QFile(':font/awesome')
        if font_file.open(QFile.ReadOnly):
            idf = QFontDatabase.addApplicationFontFromData(
                QByteArray(font_file.readAll()))
            font_file.close()

            self.font_name = QFontDatabase.applicationFontFamilies(idf)[0]

    def font(self, size) -> QFont:
        fnt = QFont(self.font_name)
        fnt.setPixelSize(size)
        fnt.setStyleName('Solid')
        return fnt


class Painter:

    def paint(
        self,
        awesome: IconManager,
        painter: QPainter,
        rect: QRect,
        mode: QIcon.Mode,
        state: QIcon.State,
        options: dict

    ):
        painter.save()

        icon_name = options.get('name')
        color_str = options.get('color')
        scale_factor = options.get('scale_factor')

        icon_code = chr(CHARMAP.get(icon_name))
        icon_color = QColor(color_str)

        assert icon_name
        assert icon_color.isValid(), f'Color "{color_str}" is not valid'

        painter.setPen(icon_color)
        size = rect.height() * scale_factor
        painter.setFont(awesome.font(size))
        painter.drawText(rect, Qt.AlignCenter, icon_code)

        painter.restore()


class IconEngine(QIconEngine):

    def __init__(self, awesome, painter, options):
        super().__init__()
        self.awesome = awesome
        self.painter = painter
        self.options = options

    def paint(self, painter, rect, mode, state):
        self.painter.paint(self.awesome, painter, rect, mode, state, self.options)

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        self.paint(QPainter(pm), QRect(QPoint(0, 0), size), mode, state)
        return pm


_IconManagerInstance = IconManager()
icon = _IconManagerInstance.icon
