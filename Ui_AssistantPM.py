# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainhbWbwS.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QSizePolicy, QSplitter, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_AssistantPM(object):
    def setupUi(self, AssistantPM):
        if not AssistantPM.objectName():
            AssistantPM.setObjectName(u"AssistantPM")
        AssistantPM.resize(1100, 480)
        AssistantPM.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.centralwidget = QWidget(AssistantPM)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 40))
        self.widget.setMaximumSize(QSize(16777215, 40))
        self.widget.setStyleSheet(u"background-color: #fff;")
        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 10, 99, 23))
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet(u"color: #3f7d00;")

        self.verticalLayout.addWidget(self.widget)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        font1 = QFont()
        font1.setPointSize(10)
        self.splitter.setFont(font1)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.sidebar = QWidget(self.splitter)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMinimumSize(QSize(200, 0))
        self.sidebar.setMaximumSize(QSize(800, 16777215))
        self.sidebar.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.verticalLayout_2 = QVBoxLayout(self.sidebar)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.splitter.addWidget(self.sidebar)
        self.main = QWidget(self.splitter)
        self.main.setObjectName(u"main")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main.sizePolicy().hasHeightForWidth())
        self.main.setSizePolicy(sizePolicy)
        self.main.setStyleSheet(u"background-color: #F9FAFB;")
        self.splitter.addWidget(self.main)

        self.verticalLayout.addWidget(self.splitter)

        AssistantPM.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(AssistantPM)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 33))
        AssistantPM.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(AssistantPM)
        self.statusbar.setObjectName(u"statusbar")
        AssistantPM.setStatusBar(self.statusbar)

        self.retranslateUi(AssistantPM)

        QMetaObject.connectSlotsByName(AssistantPM)
    # setupUi

    def retranslateUi(self, AssistantPM):
        AssistantPM.setWindowTitle(QCoreApplication.translate("AssistantPM", u"MainWindow", None))
        self.label_6.setText(QCoreApplication.translate("AssistantPM", u"AssistantPM", None))
    # retranslateUi
