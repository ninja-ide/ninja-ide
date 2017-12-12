# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.

# Based on manhattanstyle

from PyQt5.QtWidgets import (
    QProxyStyle,
    QLabel,
    QCommonStyle,
    QStyleFactory,
    QStyle,
    QApplication,
    QComboBox,
    QToolBar,
    QMenuBar,
    QStyleOptionComboBox,
    QLineEdit,
    QToolButton
)
from PyQt5.QtGui import (
    QColor,
    QLinearGradient,
    QIcon,
    QPalette
)
from PyQt5.QtCore import (
    Qt,
    QRect,
    QPoint,
    QRectF,
    QPointF
)
from ninja_ide.gui import theme

_PALETTE = theme.PALETTE
_COLORS = theme.NTheme.get_colors()

# States
STATE_SUNKEN = QStyle.State_Sunken
STATE_ENABLED = QStyle.State_Enabled
STATE_ON = QStyle.State_On
STATE_MOUSEOVER = QStyle.State_MouseOver
STATE_HASFOCUS = QStyle.State_HasFocus
STATE_KEYBOARDFOCUS = QStyle.State_KeyboardFocusChange
# FIXME: set colors from theme
# FIXME: refactor


class NinjaStyle(QProxyStyle):

    def __init__(self, style=QStyleFactory.create("window")):
        super().__init__(style)

    def drawControl(self, element, opt, painter, widget):
        """elif element == QStyle.CE_PushButtonBevel:
            # States
            is_down = (opt.state & STATE_SUNKEN) | (opt.state & STATE_ON)
            hovered = opt.state & STATE_ENABLED and opt.state & STATE_MOUSEOVER
            has_focus = opt.state & STATE_HASFOCUS

            rect = opt.rect
            btn_color = opt.palette.button().color()
            painter.setPen(btn_color)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), 3, 3)
            if is_down:
                painter.setBrush(btn_color.darker(115))
            elif has_focus:
                painter.setBrush(btn_color.lighter(130))
            elif hovered:
                grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                grad.setColorAt(0.6, btn_color)
                grad.setColorAt(1, btn_color.lighter(120))
                painter.setBrush(grad)
            else:
                painter.setBrush(btn_color)
            painter.drawPath(path)"""
        if element == QStyle.CE_ComboBoxLabel:
            cb = opt
            painter.save()
            edit_rect = self.subControlRect(QStyle.CC_ComboBox, cb,
                                            QStyle.SC_ComboBoxEditField,
                                            widget)
            # Draw icon
            if not cb.currentIcon.isNull():
                if cb.state & STATE_ENABLED:
                    mode = QIcon.Normal
                else:
                    mode = QIcon.Disabled
                pixmap = cb.currentIcon.pixmap(cb.iconSize, mode)
                icon_rect = QRect(cb.rect)
                icon_rect.setWidth(cb.iconSize.width() + 4)
                # icon_rect = self.alignedRect(opt.direction,
                #                             Qt.AlignLeft | Qt.AlignVCenter,
                #                             icon_rect.size(), edit_rect)
                self.drawItemPixmap(painter, icon_rect,
                                    Qt.AlignCenter, pixmap)
                # Space between text
                if cb.direction == Qt.RightToLeft:
                    edit_rect.translate(-4, - cb.iconSize.width(), 0)
                else:
                    edit_rect.translate(cb.iconSize.width() + 4, 0)

            edit_rect.adjusted(0, 0, -13, 0)
            # Draw text
            elide_width = edit_rect.width() - opt.fontMetrics.width('**')
            text = opt.fontMetrics.elidedText(cb.currentText,
                                              Qt.ElideRight, elide_width)
            # FIXME: states
            painter.setPen(_COLORS['ComboBoxTextColor'])
            painter.drawText(edit_rect.adjusted(1, 0, -1, 0),
                             Qt.AlignLeft | Qt.AlignVCenter, text)
            painter.restore()
        # TODO: tab with flat style
        # elif element == QStyle.CE_TabBarTabShape:
        #    pass
        elif element == QStyle.CE_ToolBar:
            rect = opt.rect
            color = _COLORS['ToolButtonColor']
            if widget.property('gradient'):
                base = QColor(_PALETTE['Window'])
                color = QLinearGradient(
                    opt.rect.topRight(), opt.rect.bottomRight())
                color.setColorAt(0.2, base.lighter(150))
                color.setColorAt(0.9, base.darker(135))
            # print(widget.property("border"), widget)
            painter.fillRect(rect, color)
            if widget.property("border"):
                # painter.setPen(opt.palette.light().color().lighter(150))
                painter.setPen(_COLORS['Border'])
                painter.drawLine(rect.topRight(), rect.bottomRight())
            # painter.setPen(_COLORS['Border'])
            # painter.drawLine(opt.rect.topRight(), opt.rect.bottomRight())

        elif element == QStyle.CE_MenuItem:
            painter.save()
            enabled = opt.state & STATE_ENABLED
            item = opt
            item.rect = opt.rect
            pal = opt.palette
            if enabled:
                color = _COLORS['MenuItemEnabled']
            else:
                color = _COLORS['MenuItemDisabled']
            item.palette = pal
            pal.setBrush(QPalette.Text, color)
            QProxyStyle.drawControl(self, element, opt, painter, widget)
            painter.restore()
        elif element == QStyle.CE_MenuBarEmptyArea:
            painter.fillRect(opt.rect, _COLORS['MenuBar'])
            # Draw border
            painter.save()
            # FIXME: color from theme
            painter.setPen(_COLORS['MenuBarBorderColor'])
            painter.drawLine(opt.rect.bottomLeft() + QPointF(.5, .5),
                             opt.rect.bottomRight() + QPointF(.5, .5))
            painter.restore()
        # elif element == QStyle.CE_PushButtonBevel:
        #    painter.setPen(Qt.red)
        #    painter.fillRect(opt.rect, QColor("red"))
        elif element == QStyle.CE_MenuBarItem:
            painter.save()
            act = opt.state & (STATE_SUNKEN | QStyle.State_Selected)
            dis = not (opt.state & STATE_ENABLED)
            painter.fillRect(opt.rect, _COLORS['MenuBar'])
            pal = opt.palette
            item = opt
            item.rect = opt.rect
            if dis:
                color = _COLORS['MenuBarItemDisabled']
            else:
                color = _COLORS['MenuBarItemEnabled']
            pal.setBrush(QPalette.ButtonText, color)
            item.palette = pal
            QCommonStyle.drawControl(self, element, item, painter, widget)
            if act:
                pal = opt.palette
                color = _COLORS['MenuBarHover']
                painter.fillRect(opt.rect, color)
                align = (Qt.AlignCenter | Qt.TextShowMnemonic |
                         Qt.TextDontClip | Qt.TextSingleLine)
                if not self.styleHint(QStyle.SH_UnderlineShortcut,
                                      opt, widget):
                    align |= Qt.TextHideMnemonic
                # FIXME:
                if dis:
                    co = _COLORS['IconDisabledColor']
                else:
                    co = _COLORS['MenuBarTextHover']
                painter.setPen(Qt.NoPen)
                pal.setBrush(QPalette.Text, co)
                self.drawItemText(painter, item.rect, align, pal, not dis,
                                  opt.text, QPalette.Text)
            painter.restore()
        else:
            QProxyStyle.drawControl(self, element, opt, painter, widget)

    def drawComplexControl(self, element, opt, painter, widget):
        if not self.__panel_widget(widget):
            QProxyStyle.drawComplexControl(self, element, opt, painter, widget)
            return
        if element == QStyle.CC_ComboBox:
            empty = False
            if not opt.currentText and opt.currentIcon.isNull():
                empty = True

            tool_btn = opt
            if empty:
                tool_btn.state &= ~(STATE_ENABLED | STATE_SUNKEN)
            self.drawPrimitive(QStyle.PE_PanelButtonTool, tool_btn,
                               painter, widget)
            # Draw border
            if widget.property("border"):
                painter.setPen(_COLORS["MenuBarBorderColor"])
                painter.drawLine(opt.rect.topRight() + QPoint(0, 6),
                                 opt.rect.bottomRight() - QPoint(0, 6))

            if widget.property("border_bottom"):
                painter.setPen(_COLORS['Border'])
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
            arrow_rect = QRect((opt.rect.left() + opt.rect.right()) / 2 + 6,
                               opt.rect.center().y(), 9, 9)

            arrow_rect.moveRight(opt.rect.width() - 10)
            # FIXME:
            arrow_opt = QStyleOptionComboBox()
            arrow_opt.state = opt.state
            arrow_opt.rect = arrow_rect
            if empty:
                arrow_opt.state &= ~(STATE_ENABLED | STATE_SUNKEN)
            if self.styleHint(QStyle.SH_ComboBox_Popup, opt, widget):
                arrow_opt.rect.translate(0, -6)
                arrow_opt.palette.setColor(
                    QPalette.ButtonText, _COLORS['IconBaseColor'])
                QCommonStyle.drawPrimitive(
                    self, QStyle.PE_IndicatorArrowUp, arrow_opt,
                    painter, widget)
                arrow_opt.rect.translate(0, 6)
                QCommonStyle.drawPrimitive(
                    self, QStyle.PE_IndicatorArrowDown, arrow_opt,
                    painter, widget)
        elif element == QStyle.CC_ToolButton:
            button = self.subControlRect(element, opt, QStyle.SC_ToolButton,
                                         widget)
            flags = opt.state
            if flags & QStyle.State_AutoRaise:
                if not flags & STATE_MOUSEOVER:
                    flags &= ~QStyle.State_Raised

            tool = opt
            tool.palette = self.panel_palette(opt.palette)
            if opt.subControls & QStyle.SC_ToolButton:
                tool.rect = button
                tool.state = flags
                self.drawPrimitive(QStyle.PE_PanelButtonTool, tool, painter,
                                   widget)

            label = opt
            label.palette.setColor(QPalette.ButtonText,
                                   label.palette.buttonText().color())
            fw = self.pixelMetric(QStyle.PM_DefaultFrameWidth, opt, widget)
            label.rect = opt.rect.adjusted(fw, fw, -fw, -fw)
            self.drawControl(QStyle.CE_ToolButtonLabel, label, painter, widget)
        else:
            QProxyStyle.drawComplexControl(self, element, opt, painter, widget)

    def polish(self, args):
        if isinstance(args, QLabel):
            pal = args.palette()
            args.setPalette(self.panel_palette(pal, self.light_colored(args)))
        elif isinstance(args, QComboBox) or \
                isinstance(args, QToolButton):
            args.setMaximumHeight(24)
        elif isinstance(args, QLineEdit):
            args.setMaximumHeight(24)
        return QProxyStyle.polish(self, args)

    @staticmethod
    def light_colored(widget):
        if widget is None:
            return False
        if ((widget.window().windowFlags() & Qt.WindowType_Mask) == Qt.Dialog):
            return True
        p = widget
        while p:
            if p.property("lightcolored"):
                return True
            p = p.parentWidget()
        return False

    @staticmethod
    def panel_palette(old_palette, light_colored=False):
        if light_colored:
            color = _COLORS['PanelTextColorDark']
        else:
            color = _COLORS['PanelTextColorLight']
        pal = old_palette
        pal.setBrush(QPalette.All, QPalette.WindowText, color)
        pal.setBrush(QPalette.All, QPalette.ButtonText, color)
        return pal

    def drawPrimitive(self, element, opt, painter, widget):
        if not self.__panel_widget(widget):
            return QProxyStyle.drawPrimitive(
                self, element, opt, painter, widget)
        if element == QStyle.PE_PanelButtonTool:
            flat = False
            pressed = (opt.state & STATE_SUNKEN or opt.state & STATE_ON)
            hovered = opt.state & STATE_ENABLED and opt.state & STATE_MOUSEOVER
            button_color = _COLORS['ToolButtonColor']
            if not flat and widget.property("gradient"):
                base = QColor(_PALETTE['Window'])

                button_color = QLinearGradient(
                    opt.rect.topRight(), opt.rect.bottomRight())
                button_color.setColorAt(
                    0.2, base.lighter(150))
                button_color.setColorAt(
                    0.9, base.darker(135))
            if pressed:
                button_color = _COLORS['ToolButtonSelected']
            elif hovered:
                if not flat and widget.property("gradient"):
                    button_color.setColorAt(0.2, base.lighter(160))
                    button_color.setColorAt(0.9, base.darker(100))
                else:
                    button_color = _COLORS['ToolButtonHover']
            if widget.property("border_bottom"):
                painter.setPen(_COLORS['Border'])
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
            painter.fillRect(opt.rect.adjusted(1, 1, -1, -1), button_color)
            # elif not opt.state & STATE_ENABLED:
            #    color = _PALETTE['ButtonDisabled']
            #    painter.fillRect(opt.rect, color)
            # TODO: keyboard focus change state
        # elif element == QStyle.PE_PanelButtonCommand:
            # Draw a flat push button
        #    is_down = opt.state & STATE_SUNKEN or opt.state & STATE_ON
        #    is_enabled = opt.state & STATE_ENABLED
        #    is_hover = is_enabled and opt.state & STATE_MOUSEOVER
            # FIXME: has_focus state
            # FIXME: from theme
        #    color = QColor("#444a58")
        #    if is_down:
        #        color = color.darker(130)
        #    elif is_hover:
        #        color = color.lighter(110)
        #    painter.fillRect(opt.rect, color)

        elif element == QStyle.PE_PanelLineEdit:
            painter.save()
            # Fill background
            rect = opt.rect
            enabled = False
            if opt.state & STATE_ENABLED:
                enabled = True
            if not enabled:
                painter.setOpacity(0.55)
            painter.fillRect(rect, _COLORS['LineEditBackground'])
            has_focus = False
            if opt.state & QStyle.State_HasFocus:
                has_focus = True
            if enabled and (has_focus or opt.state & STATE_MOUSEOVER):
                # FIXME: color from theme
                # hover = QColor("#6a6ea9")
                # if has_focus:
                #    alpha = 200
                # else:
                #    alpha = 55
                # hover.setAlpha(alpha)
                # painter.setPen(QPen(hover, 2, Qt.SolidLine,
                #               Qt.SquareCap, Qt.RoundJoin))
                # painter.drawRect(rect.adjusted(0, 0, 0, 0))
                pass
            painter.restore()
        elif element == QStyle.PE_IndicatorToolBarSeparator:
            rect = opt.rect
            painter.setPen(_COLORS['SeparatorColor'])
            border_rect = QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)
            if opt.state & QStyle.State_Horizontal:
                border_rect.setWidth(1)
                painter.drawLine(border_rect.topRight() + QPointF(0, 3),
                                 border_rect.bottomRight() - QPointF(0, 3))
            else:
                border_rect.setHeight(1)
                painter.drawLine(border_rect.topLeft() + QPointF(3, 0),
                                 border_rect.topRight() - QPointF(3, 0))
        elif element == QStyle.PE_IndicatorToolBarHandle:
            # FIXME: draw a fancy handler
            QProxyStyle.drawPrimitive(self, element, opt, painter, widget)
        else:
            QProxyStyle.drawPrimitive(self, element, opt, painter, widget)

    def pixelMetric(self, metric, opt=None, widget=None):

        if metric in (QStyle.PM_ButtonShiftVertical,
                      QStyle.PM_ButtonShiftHorizontal,
                      QStyle.PM_MenuBarPanelWidth,
                      QStyle.PM_ToolBarItemMargin,
                      QStyle.PM_ToolBarItemSpacing):
            return 0
        elif metric in (QStyle.PM_MenuPanelWidth,
                        QStyle.PM_MenuBarHMargin,
                        QStyle.PM_MenuBarVMargin,
                        QStyle.PM_ToolBarFrameWidth,
                        QStyle.PM_SplitterWidth):
            return 1

        return QProxyStyle.pixelMetric(self, metric, opt, widget)

    def __panel_widget(self, widget):
        if widget is None:
            return False
        window = widget.window()
        window_flags = window.windowFlags()

        if window_flags & Qt.WindowType_Mask == Qt.Dialog:
            return False
        w = widget
        while w:
            if w.property("panelwidget") or \
                    isinstance(w, QToolBar) or \
                    isinstance(w, QMenuBar):
                return True
            w = w.parentWidget()
        return False

    def standardPixmap(self, standard, opt=None, widget=None):
        return super().standardPixmap(standard, opt, widget)
