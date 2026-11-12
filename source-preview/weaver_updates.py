"""Check stable Weaver releases without blocking the UI."""
import json
import re
from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QPushButton

REPO = 'Alejandro07873/Weaver'
LATEST = f'https://api.github.com/repos/{REPO}/releases/latest'


def version_tuple(tag):
    match = re.fullmatch(r'(?:Weaver)?v?(\d+)\.(\d+)(?:\.(\d+))?', str(tag), re.I)
    if not match:
        raise ValueError('Unrecognized version')
    return tuple(int(n or 0) for n in match.groups())


class ReleaseChecker(QObject):
    def __init__(self, window, version):
        super().__init__(window)
        self.window = window
        self.version = version_tuple(version)
        self.network = QNetworkAccessManager(self)
        self.reply = None
        self.manual = False
        self.tag = ''
        self.button = QPushButton(window)
        self.button.hide()
        self.button.clicked.connect(self.open_release)
        window.statusBar().addPermanentWidget(self.button)

    def check(self, manual=False):
        self.manual = self.manual or manual
        if self.reply is not None:
            return
        request = QNetworkRequest(QUrl(LATEST))
        request.setRawHeader(b'User-Agent', b'Weaver-Desktop')
        request.setTransferTimeout(10000)
        self.reply = self.network.get(request)
        self.reply.finished.connect(self.finished)

    def open_release(self):
        if self.tag:
            QDesktopServices.openUrl(QUrl(f'https://github.com/{REPO}/releases/tag/{self.tag}'))

    def finished(self):
        reply = self.reply
        self.reply = None
        t = self.window.t
        try:
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if status == 404:
                message = t('Todavía no hay una versión publicada.', 'No release has been published yet.')
            else:
                if reply.error() != QNetworkReply.NoError or status != 200:
                    raise ValueError(reply.errorString())
                release = json.loads(bytes(reply.readAll()))
                tag = release['tag_name']
                if version_tuple(tag) > self.version and not release.get('prerelease') and not release.get('draft'):
                    self.tag = tag
                    self.button.setText(t('Descargar ', 'Download ') + tag)
                    self.button.show()
                    message = t('Actualización disponible.', 'Update available.')
                else:
                    message = t('Ya tienes la versión más reciente.', 'You have the latest version.')
        except (ValueError, KeyError, TypeError):
            message = t('No se pudo consultar la versión en GitHub.', 'Could not check the release on GitHub.')
        if self.manual or self.tag:
            self.window.statusBar().showMessage(message, 10000)
        self.manual = False
        reply.deleteLater()
