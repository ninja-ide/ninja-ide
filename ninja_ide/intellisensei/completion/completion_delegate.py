from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QStyle
)
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtCore import (
    Qt,
    QSize
)


class CompletionDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, opt, index):
        rect = opt.rect
        painter.setPen(opt.palette.color(QPalette.Text))
        if opt.state & QStyle.State_Selected:
            painter.fillRect(rect, opt.palette.color(QPalette.Highlight))

        previous_font = painter.font()

        icon = QIcon(index.data(Qt.DecorationRole))

        icon.paint(painter, rect, Qt.AlignLeft | Qt.AlignVCenter)

        proposal = index.data(Qt.DisplayRole)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(rect.left() + 25, rect.top(), rect.width(), rect.height(),
                         Qt.AlignLeft, proposal)

        desc = index.data(Qt.UserRole + 1)
        width = rect.width() - opt.fontMetrics.width(proposal) - 30
        text_elided = opt.fontMetrics.elidedText(
            desc, Qt.ElideRight, width)
        painter.setFont(previous_font)
        painter.setPen(opt.palette.color(QPalette.Mid))
        painter.drawText(rect.left(), rect.top(), rect.width() - 10,
                         rect.height(), Qt.AlignRight, text_elided)

    def sizeHint(self, opt, index):
        # TODO: bad
        return QSize(18, 18)
