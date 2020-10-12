from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

from PyQt5.QtWidgets import QShortcut, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, QEventLoop, QObject, QPointF, QUrl
from PyQt5.QtGui import QPainter

import os
import sys
import json
import requests
from urllib.request import urlopen
import time
import logging
import datetime

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

'''
from PyQt5.QtCore import pyqtSlot, QEventLoop, QObject, QPointF, QUrl
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
'''

now = datetime.datetime.now()
global date_log
date_log = str(now.strftime("%d-%m-%Y %H:%M:%S"))

with open('settings.json') as f:
    file_content = f.read()
    data = json.loads(file_content)

server = data['server']
res_dir = data['res_dir']
app_ver = data['version']
update_server = data['update_server']
log_dir = data['log_dir']
debug_file = data['debug_file']

term_app_name = data['apps'][0]['name']
term_app_viewname = data['apps'][0]['view_name']
term_app_icon = data['apps'][0]['icon']
term_app_path = data['apps'][0]['path']

wms_app_name = data['apps'][1]['name']
wms_app_viewname = data['apps'][1]['view_name']
wms_app_icon = data['apps'][1]['icon']
wms_app_path = data['apps'][1]['path']

update_data = json.loads(urlopen(update_server).read().decode("utf-8"))
update_ver = update_data['version']

def logger():
    logging.basicConfig(
        format='|%(levelname)s|%(name)s|%(process)d:%(processName)s| %(lineno)d:%(funcName)s:%(filename)s %(message)s|%(pathname)s|',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_dir+"/"+debug_file, 'a', 'utf-8'),
            logging.StreamHandler()
        ])
    return logging

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("WMS Assistant")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(res_dir, 'ma-icon-128.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Версия " + app_ver))
        layout.addWidget(QLabel("Created by Alex Borsch, Copyright 2020"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

class UpdateDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(UpdateDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("WMS Assistant - Проверка обновления программы")
        font = title.font()
        font.setPointSize(15)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(res_dir, 'ma-icon-update.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("У вас последняя версия программы: " + app_ver))
        
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

class PrintHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_page = None
        self.m_inPrintPreview = False

    @property
    def page(self):
        return self.m_page

    @page.setter
    def page(self, page):
        if isinstance(page, QWebEnginePage):
            self.m_page = page
            self.page.printRequested.connect(self.printPreview)
        else:
            raise TypeError("page must be a QWebEnginePage")
            
    @pyqtSlot()
    def print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self.page.view())
        if dialog.exec_() != QDialog.Accepted:
            return
        self.printDocument(printer)

    @pyqtSlot()
    def printPreview(self):
        if self.page is None:
            return
        if self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.page.view())
        preview.paintRequested.connect(self.printDocument)
        preview.exec_()
        self.m_inPrintPreview = False

    @pyqtSlot(QPrinter)
    def printDocument(self, printer):
        result = False
        loop = QEventLoop()

        def printPreview(sucess):
            nonlocal result
            result = sucess
            loop.quit()

        self.page.print(printer, printPreview)
        loop.exec_()
        if not result:
            painter = QPainter()
            if painter.begin(printer):
                font = painter.font()
                font.setPixelSize(100)
                painter.setFont(font)
                painter.drawText(QPointF(10, 30), "Could not generate print preview.")
                painter.end()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        '''Shortcuts'''
        '''
        self.shortcut_open = QShortcut(QKeySequence('F2'), self)
        self.shortcut_open.activated.connect(self.shortcut_f2)
        '''

        '''
        back_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-180.png')), "Назад", self)
        back_btn.setStatusTip("Назад")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-000.png')), "Вперёд", self)
        next_btn.setStatusTip("Вперёд")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)
        '''
        reload_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-circle-315.png')), "Обновить", self)
        reload_btn.setStatusTip("Обновить страницу")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        newtab_btn = QAction(QIcon(os.path.join(res_dir, 'ui-tab--plus.png')), "Новая вкладка", self)
        newtab_btn.setStatusTip("Новая вкладка")
        newtab_btn.triggered.connect(lambda _: self.add_new_tab())
        navtb.addAction(newtab_btn)

        term_btn = QAction(QIcon(os.path.join(res_dir, term_app_icon)), term_app_viewname, self)
        term_btn.setStatusTip(term_app_name)
        term_btn.triggered.connect(self.navigate_terminal)
        navtb.addAction(term_btn)

        wms_btn = QAction(QIcon(os.path.join(res_dir, wms_app_icon)), wms_app_viewname, self)
        wms_btn.setStatusTip(wms_app_name)
        wms_btn.triggered.connect(self.navigate_wms)
        navtb.addAction(wms_btn)
        '''
        print_action = QAction(QIcon(os.path.join(res_dir, 'printer.png')), "Print...", self)
        self.view = self.tabs.currentWidget()
        handler = PrintHandler(self)
        handler.page = self.view
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(handler.printPreview)
        navtb.addAction(print_action)
        '''

        navtb.addSeparator()

        update_btn = QAction(QIcon(os.path.join(res_dir, 'update.png')), "Проверить обновление", self)
        update_btn.setStatusTip("Проверить обновление")
        update_btn.triggered.connect(self.update_terminal)
        navtb.addAction(update_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()  # Yes, really!
        self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))
        navtb.addWidget(self.httpsicon)


        debugger_btn = QAction(QIcon(os.path.join(res_dir, 'debug.png')), "Debugger", self)
        debugger_btn.setStatusTip("CDL Debugger")
        debugger_btn.triggered.connect(self.debugger)
        navtb.addAction(debugger_btn)

        about_btn = QAction(QIcon(os.path.join(res_dir, 'question.png')), "Справка", self)
        about_btn.setStatusTip("Узнайте больше об ассистенте WMS")
        about_btn.triggered.connect(self.about)
        navtb.addAction(about_btn)

        self.add_new_tab(QUrl(""), 'Blank')
        self.show()
        self.setWindowTitle("WMS Assistant")
        self.setWindowIcon(QIcon(os.path.join(res_dir, 'ma-icon-64.png')))

    def test(self):
        handler = self.tabs.currentWidget().page()
        print (type(handler))

    def print_page(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        screen = self.tabs.currentWidget()
        if dialog.exec_() == QPrintDialog.Accepted:
            self.tabs.currentWidget().print_(printer)
            

    def navigate_terminal(self):
        self.tabs.currentWidget().setUrl(QUrl("http://"+server+"/"+term_app_path+"/"))
        logger().info(" | "+date_log+" | reload terminal | Username: "+os.getlogin())
    
    def navigate_wms(self):
        self.tabs.currentWidget().setUrl(QUrl("http://"+server+"/"+wms_app_path+"/"))
        logger().info(" | "+date_log+" | reload wms | Username: "+os.getlogin())
        
    def update_terminal(self):
        update_terminal_data = json.loads(urlopen(update_server).read().decode("utf-8"))
        update_app_ver = update_terminal_data['version']
        
        if app_ver == update_app_ver:
            logger().info(" | "+date_log+" | User update check: The latest version is in use: "+app_ver+" | Username: "+os.getlogin())
            dlg = UpdateDialog()
            dlg.exec_()
        else:
            logger().info(" | "+date_log+" | User update check: a new version has been released: "+update_app_ver+" | Username: "+os.getlogin())
            logger().info(" | "+date_log+" | User update check: start update | Username: "+os.getlogin())
            os.system('updater.exe')

    def debugger(self):
        if os.path.exists('debugger.exe'):
            os.system('debugger.exe')
        else:
            pass

    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl('')
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)
        
        # More difficult! We only want to update the url when it's from the
        # correct tab
        #browser.urlChanged.connect(lambda qurl, browser=browser:
        #                           self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))
        logger().info(" | "+date_log+" | Open new empty tab | Username: "+os.getlogin())

        self.shortcut_open = QShortcut(QKeySequence('Ctrl+p'), self)
        self.view = browser.page()
        handler = PrintHandler(self)
        handler.page = self.view
        self.shortcut_open.activated.connect(handler.printPreview)

    
    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return
        self.shortcut_open = QShortcut(QKeySequence('Ctrl+p'), self)
        self.view = browser.page()
        handler = PrintHandler(self)
        handler.page = self.view
        self.shortcut_open.activated.connect(handler.printPreview)
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - WMS Assistant" % title)

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join(res_dir, 'lock-ssl.png')))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join(res_dir, 'lock-nossl.png')))
        self.shortcut_open = QShortcut(QKeySequence('Ctrl+p'), self)
        self.view = browser.page()
        handler = PrintHandler(self)
        handler.page = self.view
        self.shortcut_open.activated.connect(handler.printPreview)
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
    
    

app = QApplication(sys.argv)
app.setApplicationName("WMS Assistant")
app.setOrganizationName("WMS Assistant")
app.setOrganizationDomain("WMS Assistant")

window = MainWindow()

if app_ver == update_ver:
    logger().info(" | "+date_log+" | Auto update check: The latest version is in use: "+app_ver+" | Username: "+os.getlogin())
    logger().info(" | "+date_log+" | Start session | Username: "+os.getlogin())
    
    app.exec_()
else:
    logger().info(" | "+date_log+" | Auto update check: a new version has been released: "+update_ver+" | Username: "+os.getlogin())
    logger().info(" | "+date_log+" | Auto update check: start update | Username: "+os.getlogin())
    if os.path.exists('updater.exe'):
        os.system('updater.exe')
    else:
        logger().error(" | "+date_log+" | No update utility, old version launch | Username: "+os.getlogin())
        app.exec_()