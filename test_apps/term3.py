from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys
import json
import requests

with open('data.json') as f:
    file_content = f.read()
    data = json.loads(file_content)


#print(data['server'])
server = data['server']
res_dir = data['res_dir']
'''
Данные терминала
'''
term_app_name = data['apps'][0]['name']
term_app_viewname = data['apps'][0]['view_name']
term_app_icon = data['apps'][0]['icon']
term_app_status = data['apps'][0]['status']
term_app_path = data['apps'][0]['path']
'''
Данные WEB интерфейса
'''
web_app_name = data['apps'][1]['name']
web_app_viewname = data['apps'][1]['view_name']
web_app_icon = data['apps'][1]['icon']
web_app_status = data['apps'][1]['status']
web_app_path = data['apps'][1]['path']

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

        layout.addWidget(QLabel("Version 0.1"))
        layout.addWidget(QLabel("Copyright 2020"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        server_check = requests.get("http://"+server+"/"+term_app_path+"/")
        if(server_check.status_code == '200'):
            self.browser.setUrl(QUrl("http://"+server+"/"+term_app_path+"/"))
        else:
            self.browser.setHtml(QUrl(str, "/pages/404.html"))
        self.browser.urlChanged.connect(self.update_urlbar)
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

        home_btn = QAction(QIcon(os.path.join(res_dir, web_app_icon)), web_app_viewname, self)
        home_btn.setStatusTip(web_app_name)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        term_btn = QAction(QIcon(os.path.join(res_dir, term_app_icon)), term_app_viewname, self)
        term_btn.setStatusTip(term_app_name)
        term_btn.triggered.connect(self.navigate_terminal)
        navtb.addAction(term_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()  # Yes, really!
        self.httpsicon.setPixmap(QPixmap(os.path.join(res_dir, 'lock-nossl.png')))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        #navtb.addWidget(self.urlbar)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join(res_dir, 'question.png')), "About WMS Assistant", self)
        about_action.setStatusTip("Find out more about WMS Assistant")  # Hungry!
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        self.show()

        self.setWindowIcon(QIcon(os.path.join(res_dir, 'ma-icon-64.png')))

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle("%s - WMS Assistant" % title)

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()


    def navigate_home(self):
        self.browser.setUrl(QUrl("http://"+server+"/"+web_app_path+"/"))

    def navigate_terminal(self):
        self.browser.setUrl(QUrl("http://"+server+"/"+term_app_path+"/"))
        
    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)

    def update_urlbar(self, q):

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join(res_dir, 'lock-ssl.png')))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join(res_dir, 'lock-nossl.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)


app = QApplication(sys.argv)
app.setApplicationName("WMS Assistant")
app.setOrganizationName("WMS Assistant")
app.setOrganizationDomain("WMS Assistant")

window = MainWindow()

app.exec_()
