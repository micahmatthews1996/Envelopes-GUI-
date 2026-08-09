from math import isclose

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPaintEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget

from models.donut_chart_segment import (
    DonutChartSegment,
)


class DonutChartWidget(QWidget):
    """Draws a reusable donut chart."""

    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("donutChart")

        self.setMinimumSize(
            240,
            240,
        )

        self._segments: list[
            DonutChartSegment
        ] = []

        self._track_color = QColor(
            "#E7ECF2"
        )

        self._center_value = "$0.00"
        self._center_caption = (
            "Spent this month"
        )

    def set_segments(
        self,
        segments: list[
            DonutChartSegment
        ],
    ) -> None:
        """Replace the chart segments."""

        self._segments = segments

        self.update()

    def set_center_text(
        self,
        value: str,
        caption: str,
    ) -> None:
        """Update the center text."""

        self._center_value = value
        self._center_caption = caption

        self.update()

    def paintEvent(
        self,
        event: QPaintEvent,
    ) -> None:
        """Paint the donut chart."""

        del event

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        chart_size = min(
            self.width(),
            self.height(),
        )

        margin = 28

        chart_rect = QRectF(
            (
                self.width()
                - chart_size
            )
            / 2
            + margin,
            (
                self.height()
                - chart_size
            )
            / 2
            + margin,
            chart_size
            - margin * 2,
            chart_size
            - margin * 2,
        )

        stroke_width = max(
            18,
            int(chart_size * 0.09),
        )

        self._draw_track(
            painter,
            chart_rect,
            stroke_width,
        )

        self._draw_segments(
            painter,
            chart_rect,
            stroke_width,
        )

        self._draw_center_text(
            painter,
            chart_rect,
        )

        painter.end()

    def _draw_track(
        self,
        painter: QPainter,
        chart_rect: QRectF,
        stroke_width: int,
    ) -> None:
        """Draw the gray background ring."""

        pen = QPen(
            self._track_color,
            stroke_width,
        )

        pen.setCapStyle(
            Qt.PenCapStyle.FlatCap
        )

        painter.setPen(pen)
        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.drawArc(
            chart_rect,
            0,
            360 * 16,
        )

    def _draw_segments(
        self,
        painter: QPainter,
        chart_rect: QRectF,
        stroke_width: int,
    ) -> None:
        """Draw all donut segments."""

        if not self._segments:
            return

        total = sum(
            segment.value
            for segment in self._segments
        )

        if total <= 0:
            return

        gap = 1.0
        current_angle = 90.0

        for segment in self._segments:
            percentage = (
                segment.value / total
            )

            sweep = (
                percentage * 360.0
            )

            if not isclose(
                sweep,
                360.0,
            ):
                sweep -= gap

            pen = QPen(
                QColor(segment.color),
                stroke_width,
            )

            pen.setCapStyle(
                Qt.PenCapStyle.FlatCap
            )

            painter.setPen(pen)

            painter.drawArc(
                chart_rect,
                int(current_angle * 16),
                int(-sweep * 16),
            )

            current_angle -= (
                sweep + gap
            )

    def _draw_center_text(
        self,
        painter: QPainter,
        chart_rect: QRectF,
    ) -> None:
        """Draw the center labels."""

        center_y = (
            chart_rect.center().y()
        )

        value_rect = QRectF(
            chart_rect.left(),
            center_y - 34,
            chart_rect.width(),
            34,
        )

        caption_rect = QRectF(
            chart_rect.left() + 20,
            center_y + 3,
            chart_rect.width() - 40,
            40,
        )

        value_font = QFont(
            "Segoe UI"
        )
        value_font.setPixelSize(25)
        value_font.setWeight(
            QFont.Weight.Bold
        )

        painter.setFont(
            value_font
        )

        painter.setPen(
            QColor("#1F2937")
        )

        painter.drawText(
            value_rect,
            Qt.AlignmentFlag.AlignCenter,
            self._center_value,
        )

        caption_font = QFont(
            "Segoe UI"
        )
        caption_font.setPixelSize(
            12
        )

        painter.setFont(
            caption_font
        )

        painter.setPen(
            QColor("#6B7280")
        )

        painter.drawText(
            caption_rect,
            Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop
            | Qt.TextFlag.TextWordWrap,
            self._center_caption,
        )