from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import os
import sys
import json
import requests
from urllib.request import urlopen
import time
import logging
import datetime


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


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://"+server+"/"+term_app_path+"/"))
        self.browser.loadFinished.connect(self.update_title)
        self.setCentralWidget(self.browser)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)
        
        back_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-180.png')), "Назад", self)
        back_btn.setStatusTip("Назад")
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-000.png')), "Вперёд", self)
        next_btn.setStatusTip("Вперёд")
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)
        
        reload_btn = QAction(QIcon(os.path.join(res_dir, 'arrow-circle-315.png')), "Обновить", self)
        reload_btn.setStatusTip("Обновить")
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)
        
        term_btn = QAction(QIcon(os.path.join(res_dir, term_app_icon)), term_app_viewname, self)
        term_btn.setStatusTip(term_app_name)
        term_btn.triggered.connect(self.navigate_terminal)
        navtb.addAction(term_btn)

        navtb.addSeparator()

        update_btn = QAction(QIcon(os.path.join(res_dir, 'update.png')), "Проверить обновление", self)
        update_btn.setStatusTip("Проверить обновление")
        update_btn.triggered.connect(self.update_terminal)
        navtb.addAction(update_btn)

        help_menu = self.menuBar().addMenu("&Services")

        about_action = QAction(QIcon(os.path.join(res_dir, 'question.png')), "Справка", self)
        about_action.setStatusTip("Find out more about WMS Assistant") 
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        debugger = QAction(QIcon(os.path.join(res_dir, 'debug.png')), "Debugger", self)
        debugger.setStatusTip("CDL Debugger") 
        debugger.triggered.connect(self.debugger)
        help_menu.addAction(debugger)
        

        self.show()

        self.setWindowIcon(QIcon(os.path.join(res_dir, 'ma-icon-64.png')))


    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle("%s - WMS Assistant" % title)
        logger().info(" | "+date_log+" | "+title+" | Username: "+os.getlogin())

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()
        logger().info(" | "+date_log+" | about dialog | Username: "+os.getlogin())

    def navigate_terminal(self):
        self.browser.setUrl(QUrl("http://"+server+"/"+term_app_path+"/"))
        logger().info(" | "+date_log+" | reload terminal | Username: "+os.getlogin())
        
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
