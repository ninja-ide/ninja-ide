
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPainter

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QPropertyAnimation

_widget = None


class FadingIndicator(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(.999)

        self._label = QLabel()
        font = self._label.font()
        font.setPixelSize(18)
        self._label.setFont(font)
        palette = self.palette()
        palette.setColor(QPalette.WindowText, palette.color(QPalette.Window))
        # self._label.setPalette(palette)

        self._layout = QHBoxLayout(self)
        self._layout.addWidget(self._label)

    def set_text(self, text):
        self._label.setText(text)
        self._layout.setSizeConstraint(self._layout.SetFixedSize)
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            x = parent.width() - self.rect().width() - 15
            self.move(x, 15)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.palette().color(QPalette.Window))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 3, 3)

    def start(self, ms):
        self.show()
        QTimer.singleShot(ms, self._start)

    def _start(self):
        animation = QPropertyAnimation(self._effect, b"opacity", self)
        animation.setDuration(200)
        animation.setEndValue(0.)
        animation.finished.connect(self.deleteLater)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    @staticmethod
    def show_text(parent, text, ms=2500):
        global _widget
        if _widget is not None:
            _widget = None
            del _widget
        _widget = FadingIndicator(parent)
        _widget.set_text(text)
        _widget.start(ms=ms)
