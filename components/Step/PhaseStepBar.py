
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal


class PhaseStepBar(QWidget):
    stepClicked = Signal(int)

    def __init__(self, phase_title: str, num_questions: int, parent=None):
        super().__init__(parent)
        self.phase_title = phase_title
        self.num_questions = num_questions
        self.buttons = []
        self.checkmarks = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Titre de la phase
        self.title_label = QLabel(f"Phase : {self.phase_title}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937 ;border: none;")
        layout.addWidget(self.title_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Container pour boutons + checkmarks
        btn_column = QVBoxLayout()
        btn_row = QHBoxLayout()
        chk_row = QHBoxLayout()
        btn_row.setSpacing(20)
        chk_row.setSpacing(20)

        for i in range(self.num_questions):
            btn = QToolButton()
            btn.setText(str(i + 1))
            btn.setCheckable(True)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: #F2F2F2;
                    border-radius: 16px;
                    font-size: 14px;
                    color: black;
                    border: 2px solid #D1D5DB;
                    padding: 0px;
                }
                QToolButton:checked {
                    background-color: #24f416;
                    color: black;
                    border: 2px solid #10b981;
                }
            """)
            btn.clicked.connect(lambda _, idx=i: self.stepClicked.emit(idx))
            self.buttons.append(btn)
            btn_row.addWidget(btn)

            """ chk = QLabel(f"{i}")
            chk.setAlignment(Qt.AlignCenter)
            chk.setStyleSheet("font-size: 12px; color: black;")  # Corrected color value
             """
            #self.checkmarks.append(chk)  # Uncommented to append checkmarks
            #chk_row.addWidget(chk)  # Uncommented to add checkmarks to the layout

        btn_column.addLayout(btn_row)
        #btn_column.addLayout(chk_row)

        layout.addLayout(btn_column)

    def update_active(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

    def set_answered(self, answered_list: list[bool]):
        pass
        #for i, state in enumerate(answered_list):
        #    self.checkmarks[i].setText("✓" if state else "")

    def set_phase_title(self, title: str):
        self.phase_title = title
        self.title_label.setText(f"Phase : {title}")
