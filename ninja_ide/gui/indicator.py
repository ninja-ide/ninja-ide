from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QGraphicsOpacityEffect
)
from PyQt5.QtGui import (
    QPainter,
    QPalette
)
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QTimer
)
from ninja_ide.core import settings

# FIXME: move to ui_tools


class Indicator(QWidget):

    instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(1.)

        box = QHBoxLayout(self)
        self._label = QLabel()
        font = self._label.font()
        font.setPixelSize(18)
        self._label.setFont(font)
        box.addWidget(self._label)

        palette = self.palette()
        palette.setColor(QPalette.Text, palette.color(QPalette.Window))
        self._label.setPalette(palette)

    def run(self, ms):
        self.show()
        self.raise_()
        QTimer.singleShot(ms, self.show_indicator)

    def show_indicator(self):
        animation = QPropertyAnimation(self._effect, b"opacity", self)
        animation.setDuration(200)
        animation.setEndValue(0.)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    def set_text(self, text):
        self._label.setText(text)
        width = self.parent().width()
        x = width - (self._label.sizeHint().width() + 50)
        y = self.parent().rect().y()
        self.move(x, y + 10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.palette().color(QPalette.AlternateBase))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 1, 1)

    @classmethod
    def show_text(cls, parent, text, ms=1500):
        if cls.instance is not None:
            cls.instance.deleteLater()
            cls.instance = None
        cls.instance = Indicator(parent)
        cls.instance.set_text(text)
        cls.instance.run(ms)
