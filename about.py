from aboutform import Ui_widget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon


class AboutForm(QWidget, Ui_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon("sus/icon.ico"))
        rgb = '<span style="color:#FF0000">K</span><span style="color:#FF6D00">h</span>' \
              '<span style="color:#FFDB00">r</span><span style="color:#B6FF00">a</span>' \
              '<span style="color:#49FF00">m</span><span style="color:#00FF24">o</span>' \
              '<span style="color:#00FF92">v</span> <span style="color:#00FFFF">E</span>' \
              '<span style="color:#0092FF">v</span><span style="color:#0024FF">g</span>' \
              '<span style="color:#4900FF">e</span><span style="color:#B600FF">n</span>' \
              '<span style="color:#FF00DB">i</span><span style="color:#FF006D">i</span>'
        self.pltxt.setOpenLinks(False)
        self.pltxt.setOpenExternalLinks(True)
        text = f'''This is Conway's Game of Life interpretation in <span style='color: green;'>PyQt</span>.<br><br>
        <span style='color: pink;'>Rules:</span><br>
        Game based on grid, where each cell can be <span style='color: red;'>dead</span> or
        <span style='color: yellow;'>alive</span>.<br>
        Alive cell stay alive if it has 2 or 3 alive neighbours.<br>
        In dead cell appears alive cell if it has 3 alive neighbours.<br>
        <span style='color: magenta;'>Its all.</span><br><br>
        I added some cosmetic features just for make it look nice. <span style='color: coral;'>Check it out now.
        </span><br><br>
        It is free and distributing for free.<br>
        All rights reserved btw.<br><br>
        Maded by me aka {rgb}, 2022.<br>
        ///Links on me:<br>
        Github: <a href='github.com/myatnyi/'>github.com/myatnyi/</a><br>
        Telegram: <a href='t.me/dendiinside' style='color: red;'>t.me/dendiinside</a><br>
        Discord: <span style='color: purple;'>dendi#8585</span><br>
        &#127795; &#127786; &#129412; &#129367; &#128171;'''
        self.pltxt.setHtml(text)
