import sys

from PyQt5 import uic
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect, QSize
import numpy as np
import alg


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_ui.ui', self)
        self.initUI()

    def initUI(self):
        # иконка
        self.setWindowIcon(QIcon("sus/icon.png"))
        # стандартные переменные
        self.do_paint = False
        self.fullScreen = False
        self.isEdit = True
        self.scale = 1.0
        self.width = 0
        self.height = 0
        self.heatAlive = 1
        self.cell_size = 30
        self.curr_grid_pos = [0, 0]
        self.grid = np.zeros((self.height, self.width))
        # Генерация
        self.le_width.textChanged.connect(self.width_height_input_err)
        self.le_height.textChanged.connect(self.width_height_input_err)
        self.gen_btn.clicked.connect(self.paint)
        # Основная часть
        self.scrollArea.setEnabled(False)
        self.cb_showgrid.setChecked(True)
        self.cb_showgrid.stateChanged.connect(lambda: self.repaint())
        self.clear_btn.clicked.connect(self.clear_grid)
        # a n i m a t i o n
        self.next_step_btn.clicked.connect(self.next_step)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.animation)
        self.stop_btn.clicked.connect(self.animation)
        self.speed_slider.valueChanged.connect(self.animation)
        # рандомизация сетки
        self.le_rnd.textChanged.connect(self.rnd_err)
        self.rnd_btn.clicked.connect(self.rnd_grid)
        # heatmap
        self.le_aliveHeat.setEnabled(False)
        self.heat_btn.setEnabled(False)
        self.cb_heat.stateChanged.connect(self.heat_en)
        self.heat_btn.clicked.connect(self.heat)
        self.le_aliveHeat.textChanged.connect(self.heat_err)
        # message box
        self.m_Box = QMessageBox(self)
        self.m_Box.setText("Are you want to regenerate grid?(all progress will be lost)")
        self.m_Box.setWindowTitle("Sure?")
        self.m_Box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # hotkeys
        self.f1_lbl.setProperty('class', 'hotkey')
        self.f5_lbl.setProperty('class', 'hotkey')
        self.f6_lbl.setProperty('class', 'hotkey')
        self.f11_lbl.setProperty('class', 'hotkey')
        self.home_lbl.setProperty('class', 'hotkey')
        # график
        self.generation = 1
        self.population = np.array([np.count_nonzero(self.grid == self.heatAlive)])
        self.graph.plot(np.arange(1, self.generation + 1), self.population, p='w')
        self.graph.getAxis("left").setStyle(tickFont=QFont("More Perfect DOS VGA", 10))
        self.graph.getAxis("bottom").setStyle(tickFont=QFont("More Perfect DOS VGA", 10))

    # Обработка ошибок ввода
    def width_height_input_err(self):
        if self.sender().text().isdigit() and int(self.sender().text()) == float(self.sender().text()) \
                and int(self.sender().text()) > 0:
            self.err_lbl_gen.setText('')
            self.gen_btn.setEnabled(True)
        elif self.sender().text() == '':
            self.err_lbl_gen.setText('enter width and height')
            self.gen_btn.setEnabled(False)
        elif not (self.sender().text().lstrip('-').isdigit()
                  and int(self.sender().text()) == float(self.sender().text())):
            self.err_lbl_gen.setText('width and height must be int')
            self.gen_btn.setEnabled(False)
        else:
            self.err_lbl_gen.setText('width and height must be >0')
            self.gen_btn.setEnabled(False)

    def rnd_err(self):
        if self.sender().text().isdigit() and int(self.sender().text()) == float(self.sender().text()) \
                and 100 >= int(self.sender().text()) > 0:
            self.err_lbl_rnd.setText('')
            self.rnd_btn.setEnabled(True)
        elif self.sender().text() == '':
            self.err_lbl_rnd.setText('enter chance of cell spawning')
            self.rnd_btn.setEnabled(False)
        elif not (self.sender().text().lstrip('-').isdigit()
                  and int(self.sender().text()) == float(self.sender().text())):
            self.err_lbl_rnd.setText('chance must be int')
            self.rnd_btn.setEnabled(False)
        elif int(self.sender().text()) > 100 or int(self.sender().text()) <= 0:
            self.err_lbl_rnd.setText('chance must be 1-100')
            self.rnd_btn.setEnabled(False)

    def heat_err(self):
        if self.sender().text().isdigit() and int(self.sender().text()) == float(self.sender().text()) \
                and 10 >= int(self.sender().text()) > 0:
            self.err_lbl_heat.setText('')
            self.heat_btn.setEnabled(True)
        elif self.sender().text() == '':
            self.err_lbl_heat.setText('enter max cell heat')
            self.heat_btn.setEnabled(False)
        elif not (self.sender().text().lstrip('-').isdigit()
                  and int(self.sender().text()) == float(self.sender().text())):
            self.err_lbl_heat.setText('heat must be int')
            self.rnd_btn.setEnabled(False)
        elif int(self.sender().text()) > 10 or int(self.sender().text()) <= 0:
            self.err_lbl_heat.setText('heat must be 1-10')
            self.heat_btn.setEnabled(False)

# Отрисовка
    def paintEvent(self, event):
        if self.do_paint:
            qp = QPainter(self)
            qp.translate(self.curr_grid_pos[0], self.curr_grid_pos[1])
            qp.scale(self.scale, self.scale)
            qp.begin(self)
            self.draw(qp)
            qp.end()

    def paint(self):
        if self.le_width.text() != '' and self.le_height.text() != '':
            if self.gen_btn.text() != 'regenerate grid' or\
                    np.array_equal(self.grid, np.zeros((self.height, self.width))):
                self.do_paint = True
                self.scrollArea.setEnabled(True)
                self.gen_btn.setText('regenerate grid')
                self.scale = 1.0
                self.width = int(self.le_width.text())
                self.height = int(self.le_height.text())
                self.curr_grid_pos = [(self.size().width() - self.width * self.cell_size - 350) // 2,
                                      (self.size().height() - self.height * self.cell_size) // 2]
                self.grid = np.zeros((self.height, self.width), dtype=np.ushort)
                self.repaint()

                self.graph.getAxis('left').setTextPen('w')
                self.graph.getAxis('bottom').setTextPen('w')
            elif self.m_Box.exec() == QMessageBox.Yes and self.gen_btn.text() == 'regenerate grid':
                if not self.start_btn.isEnabled():
                    self.timer.stop()
                    self.start_btn.setEnabled(True)
                    self.next_step_btn.setEnabled(True)
                    self.stop_btn.setEnabled(False)
                self.curr_grid_pos = [(self.size().width() - self.width * self.cell_size) // 2 - 175,
                                      (self.size().height() - self.height * self.cell_size) // 2]
                self.scale = 1.0
                self.width = int(self.le_width.text())
                self.height = int(self.le_height.text())
                self.grid = np.zeros((self.height, self.width), dtype=np.ushort)
                self.repaint()

                self.graph.clear()
                self.generation = 1
                self.population = np.array([np.count_nonzero(self.grid == self.heatAlive)])
        else:
            self.err_lbl_gen.setText('enter width and height')
            self.gen_btn.setEnabled(False)

    def draw(self, qp):
        qp.setBrush(QColor(255, 255, 255))
        if self.cb_showgrid.isChecked():
            for i in range(self.width + 1):
                qp.drawLine(i * self.cell_size, 0, i * self.cell_size, self.height * self.cell_size)
            for i in range(self.height + 1):
                qp.drawLine(0, i * self.cell_size, self.width * self.cell_size, i * self.cell_size)
        for j, i in np.ndindex(self.grid.shape):
                if self.grid[j][i] != 0:
                    color = int(255 * self.grid[j][i] // self.heatAlive)
                    qp.fillRect(QRect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size),
                                QColor(color, color, color))

# обработка мышклавы
    def wheelEvent(self, event):
        if not event.x() in range(self.menu_box.pos().x(), self.menu_box.pos().x() + self.menu_box.width()) and \
                event.y() in range(self.menu_box.pos().y(), self.menu_box.pos().y() + self.menu_box.height()):
            dif = (event.angleDelta().y()/480 if self.scale + event.angleDelta().y()/480 > 0 else 0)
            self.curr_grid_pos = [self.curr_grid_pos[0] + (dif * (self.curr_grid_pos[0] - event.x()) // self.scale),
                                  self.curr_grid_pos[1] + (dif * (self.curr_grid_pos[1] - event.y()) // self.scale)]
            self.scale += dif
            self.repaint()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rb_x = event.x()
            self.rb_y = event.y()
        elif event.button() == Qt.LeftButton:
            x = int(((event.x() - self.curr_grid_pos[0]) // (self.cell_size * self.scale)))
            y = int(((event.y() - self.curr_grid_pos[1])) // (self.cell_size * self.scale))
            if self.width > x >= 0 and self.height > y >= 0:
                self.grid[y][x] = self.heatAlive if self.grid[y][x] != self.heatAlive else 0
                self.repaint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:
            self.curr_grid_pos[0] += event.x() - self.rb_x
            self.curr_grid_pos[1] += event.y() - self.rb_y
            self.rb_x = event.x()
            self.rb_y = event.y()
            self.repaint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Home:
            self.curr_grid_pos = [(self.size().width() - self.width * self.cell_size) // 2 - 175,
                                  (self.size().height() - self.height * self.cell_size) // 2]
            self.scale = 1.0
            self.repaint()
        elif event.key() == Qt.Key_F11:
            if self.fullScreen:
                self.showNormal()
                self.curr_grid_pos = [(self.size().width() - self.width * self.cell_size) // 2 - 175,
                                      (self.size().height() - self.height * self.cell_size) // 2]
                self.scale = 1.0
            else:
                self.showFullScreen()
            self.repaint()
            self.fullScreen = not self.fullScreen

# просчет следующего поколения
    def next_step(self):
        self.grid = alg.algorithm(self.width, self.height, self.grid, self.heatAlive)
        self.repaint()
        self.generation += 1
        self.population = np.append(self.population, np.count_nonzero(self.grid == self.heatAlive))
        self.graph.clear()
        self.graph.plot(np.arange(1, self.generation + 1), self.population, p='w')

# a n i m a t i o n2
    def animation(self):
        if self.sender() == self.start_btn:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.next_step)
            self.timer.start(1000 // self.speed_slider.value())
            self.start_btn.setEnabled(False)
            self.next_step_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        elif self.sender() == self.speed_slider and not self.start_btn.isEnabled():
            self.timer.start(1000 // self.speed_slider.value())
        elif self.sender() == self.stop_btn:
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.next_step_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

# рандом грид и clear
    def clear_grid(self):
        if np.array_equal(self.grid, np.zeros((self.height, self.width))) or self.m_Box.exec() == QMessageBox.Yes:
            self.grid = np.zeros((self.height, self.width), dtype=np.ushort)
            self.repaint()

    def rnd_grid(self):
        if self.le_rnd.text() != '' and (np.array_equal(self.grid, np.zeros((self.height, self.width))) or
                                         self.m_Box.exec() == QMessageBox.Yes):
            self.grid = self.heatAlive * np.random.binomial(1, float(self.le_rnd.text()) / 100,
                                                            size=(self.height, self.width))
            self.repaint()
        else:
            self.err_lbl_rnd.setText('enter chance of cell spawning')
            self.rnd_btn.setEnabled(False)

# heatmap
    def heat_en(self):
        if self.cb_heat.isChecked():
            self.le_aliveHeat.setEnabled(True)
            self.heat_btn.setEnabled(True)
        else:
            for j, i in np.ndindex(self.grid.shape):
                    self.grid[j][i] = 1 if self.grid[j][i] == self.heatAlive else 0
            self.heatAlive = 1
            self.le_aliveHeat.setEnabled(False)
            self.heat_btn.setEnabled(False)
            self.le_aliveHeat.setText('')
            self.err_lbl_heat.setText('')
            self.repaint()

    def heat(self):
        if self.le_aliveHeat.text() != '':
            for j, i in np.ndindex(self.grid.shape):
                    self.grid[j][i] += int(self.le_aliveHeat.text()) - self.heatAlive if self.grid[j][i] != 0 else 0
            self.heatAlive = int(self.le_aliveHeat.text())
            self.repaint()
        else:
            self.err_lbl_heat.setText('enter max cell heat')
            self.heat_btn.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())