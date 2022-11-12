import sys

from main_ui import Ui_MainWindow
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QColorDialog, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt, QTimer, QRect
from re import match
import about
import sqlite3
import numpy as np
import json
import alg


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.COLOR_GRAD = [QColor(255, 0, 0), QColor(255, 127, 0), QColor(255, 255, 0), QColor(0, 255, 0),
                           QColor(0, 0, 255), QColor(75, 0, 130), QColor(148, 0, 211)]
        # иконка
        self.setWindowIcon(QIcon("sus/icon.ico"))
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
        self.cell_color = QColor(255, 255, 255)
        self.heat_color = QColor(255, 255, 255)
        self.menu_box.setMinimumWidth(self.menu_box.width() + self.scrollArea.verticalScrollBar().sizeHint().width())
        # Генерация
        self.le_width.textChanged.connect(self.width_height_input_err)
        self.le_height.textChanged.connect(self.width_height_input_err)
        self.gen_btn.clicked.connect(self.paint)
        # Основная часть
        self.scrollArea.setEnabled(False)
        self.cb_showgrid.setChecked(True)
        self.cb_showgrid.stateChanged.connect(self.repaint)
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
        self.f10_lbl.setProperty('class', 'hotkey')
        self.f11_lbl.setProperty('class', 'hotkey')
        self.home_lbl.setProperty('class', 'hotkey')
        # график
        self.generation = 1
        self.population = np.array([np.count_nonzero(self.grid == self.heatAlive)])
        self.graph.plot(np.arange(1, self.generation + 1), self.population, p='w')
        self.graph.getAxis("left").setStyle(tickFont=QFont("More Perfect DOS VGA", 10))
        self.graph.getAxis("bottom").setStyle(tickFont=QFont("More Perfect DOS VGA", 10))
        # color
        self.color_btn.clicked.connect(self.set_cell_color)
        self.cb_heatc.setChecked(True)
        self.heatc_btn.setEnabled(False)
        self.heatc_lbl.setEnabled(False)
        self.cb_heatc.stateChanged.connect(self.check_heatc)
        self.heatc_btn.clicked.connect(self.set_heat_color)
        self.cb_rgb.stateChanged.connect(self.repaint)
        # aboutform
        self.about_btn.clicked.connect(self.open_aboutform)
        # saveform
        self.con = sqlite3.connect('saves.db')
        self.cur = self.con.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS saves(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, path TEXT)')
        self.file_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save)
        self.load_btn.clicked.connect(self.load)
        self.err_Box = QMessageBox(self)
        self.err_Box.setText("You aren't selected any file in dropbox, please open .json file")
        self.err_Box.setWindowTitle("File isn't selected")
        self.err_Box.setStandardButtons(QMessageBox.Ok)
        self.create_btn.clicked.connect(self.create_save)

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
                and 10 >= int(self.sender().text()) > 1:
            self.err_lbl_heat.setText('')
            self.heat_btn.setEnabled(True)
        elif self.sender().text() == '':
            self.err_lbl_heat.setText('enter max cell heat')
            self.heat_btn.setEnabled(False)
        elif not (self.sender().text().lstrip('-').isdigit()
                  and int(self.sender().text()) == float(self.sender().text())):
            self.err_lbl_heat.setText('heat must be int')
            self.rnd_btn.setEnabled(False)
        elif int(self.sender().text()) > 10 or int(self.sender().text()) <= 1:
            self.err_lbl_heat.setText('heat must be 2-10')
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
                self.grid = self.grid if self.grid.size > 0 else np.zeros((self.height, self.width), dtype=np.ushort)
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
        if self.cb_showgrid.isChecked():
            for i in range(self.width + 1):
                qp.drawLine(i * self.cell_size, 0, i * self.cell_size, self.height * self.cell_size)
            for i in range(self.height + 1):
                qp.drawLine(0, i * self.cell_size, self.width * self.cell_size, i * self.cell_size)
        for j, i in np.ndindex(self.grid.shape):
            if self.grid[j][i]:
                if self.cb_rgb.isChecked():
                    form = 6 - (self.grid[j][i] * 6 // self.heatAlive)
                    qp.fillRect(QRect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size),
                                self.COLOR_GRAD[form])
                elif self.cb_heatc.isChecked():
                    color1 = int(self.cell_color.red() * self.grid[j][i] // self.heatAlive)
                    color2 = int(self.cell_color.green() * self.grid[j][i] // self.heatAlive)
                    color3 = int(self.cell_color.blue() * self.grid[j][i] // self.heatAlive)
                    qp.fillRect(QRect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size),
                                QColor(color1, color2, color3))
                else:
                    if self.grid[j][i] == self.heatAlive:
                        qp.fillRect(QRect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size),
                                    QColor(self.cell_color.red(), self.cell_color.green(), self.cell_color.blue()))
                    else:
                        color1 = int(self.heat_color.red() * self.grid[j][i] // (self.heatAlive - 1))
                        color2 = int(self.heat_color.green() * self.grid[j][i] // (self.heatAlive - 1))
                        color3 = int(self.heat_color.blue() * self.grid[j][i] // (self.heatAlive - 1))
                        qp.fillRect(QRect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size),
                                    QColor(color1, color2, color3))

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
        elif event.button() == Qt.LeftButton and \
                (not event.x() in range(self.menu_box.pos().x(), self.menu_box.pos().x() + self.menu_box.width())
                 and event.y() in range(self.menu_box.pos().y(), self.menu_box.pos().y() + self.menu_box.height())) \
                or self.menu_box.isHidden():
            x = int(((event.x() - self.curr_grid_pos[0]) // (self.cell_size * self.scale)))
            y = int(((event.y() - self.curr_grid_pos[1])) // (self.cell_size * self.scale))
            if self.width > x >= 0 and self.height > y >= 0:
                self.grid[y][x] = self.heatAlive if self.grid[y][x] != self.heatAlive else 0
                self.repaint()
            self.population[-1] = np.count_nonzero(self.grid == self.heatAlive)

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
        elif event.key() == Qt.Key_F1:
            self.open_aboutform()
        elif event.key() == Qt.Key_F5:
            self.save()
        elif event.key() == Qt.Key_F6:
            self.load()
        elif event.key() == Qt.Key_F10:
            if self.menu_box.isHidden():
                self.menu_box.show()
            else:
                self.menu_box.hide()
                print(self.menu_box.pos().x(), self.menu_box.pos().x() + self.menu_box.width())
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

# color
    def set_cell_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.cell_color = color
            sum_color = color.red() + color.green() + color.blue()
            self.color_lbl.setText(color.name())
            self.color_lbl.setStyleSheet(f'background-color: {color.name()}; '
                                         f'color: {"white" if sum_color < 383 else "black"};')
            self.repaint()

    def check_heatc(self):
        if self.cb_heatc.isChecked():
            self.heatc_btn.setEnabled(False)
            self.heatc_lbl.setEnabled(False)
            sum_color = self.heat_color.red() + self.heat_color.green() + self.heat_color.blue()
            half_color = (self.heat_color.red() // 2, self.heat_color.green() // 2, self.heat_color.blue() // 2)
            self.heatc_lbl.setStyleSheet(f'background-color: rgb{half_color}; '
                                         f'color: {"gray" if sum_color < 383 else "black"};')
        else:
            self.heatc_btn.setEnabled(True)
            self.heatc_lbl.setEnabled(True)
            sum_color = self.heat_color.red() + self.heat_color.green() + self.heat_color.blue()
            self.heatc_lbl.setStyleSheet(f'background-color: {self.heat_color.name()}; '
                                         f'color: {"white" if sum_color < 383 else "black"};')
        self.repaint()

    def set_heat_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.heat_color = color
            sum_color = color.red() + color.green() + color.blue()
            self.heatc_lbl.setText(color.name())
            self.heatc_lbl.setStyleSheet(f'background-color: {color.name()}; '
                                         f'color: {"white" if sum_color < 383 else "black"};')
            self.repaint()

# aboutform
    def open_aboutform(self):
        self.aboutform = about.AboutForm()
        self.aboutform.show()

# saveform
    def open_file(self):
        file = QFileDialog.getOpenFileName(self, 'Choose save file', '', 'json file (*.json)')[0]
        if file:
            self.cur.execute(f'INSERT INTO saves(path) VALUES ("{file}")')
            self.file_drop.addItem(file.split('/')[-1])
            self.file_drop.setCurrentText(file.split('/')[-1])

    def save(self):
        try:
            js = {'array': self.grid.tolist(), 'pop': self.population.tolist(), 'gen': self.generation}
            file = self.cur.execute(f'select * from saves where path like "%{self.file_drop.currentText()}"').fetchone()
            with open(file[-1], 'w') as g:
                json.dump(js, g)
        except TypeError:
            self.err_Box.exec()

    def load(self):
        try:
            file = self.cur.execute(f'select * from saves where path like "%{self.file_drop.currentText()}"').fetchone()
            with open(file[-1], 'r') as f:
                js = json.loads(f.read())
                self.grid = np.asarray(js['array'], dtype=np.ushort)
                self.population = np.asarray(js['pop'], dtype=np.ushort)
                self.generation = js['gen']
                self.graph.clear()
                self.graph.plot(np.arange(1, self.generation + 1), self.population, p='w')
            self.scrollArea.setEnabled(True)
            self.width, self.height = self.grid.shape
            self.le_width.setText(str(self.width))
            self.le_height.setText(str(self.height))
            self.repaint()
            if self.gen_btn.text() == 'generate grid':
                self.paint()
        except FileNotFoundError:
            ferr_Box = QMessageBox(self)
            ferr_Box.setText("File somehow got lost, it may deleted, please check out")
            ferr_Box.setWindowTitle("File not found")
            ferr_Box.setStandardButtons(QMessageBox.Ok)
            ferr_Box.exec()
            self.cur.execute(f'delete from saves where path like "%{self.file_drop.currentText()}"')
            self.file_drop.removeItem(self.file_drop.currentText())
        except KeyError and ValueError:
            kerr_Box = QMessageBox(self)
            kerr_Box.setText("File isn's a save file or you saved a blank grid, i think")
            kerr_Box.setWindowTitle("Invalid file")
            kerr_Box.setStandardButtons(QMessageBox.Ok)
            kerr_Box.exec()
        except TypeError:
            self.err_Box.exec()

    def create_save(self):
        in_Box = QInputDialog(self).getText(self, "Enter a name", "Enter name of file WITHOUT extension")
        if match("^[A-Za-z0-9_-]*$", in_Box[0]) and in_Box[0]:
            try:
                js = {'array': self.grid.tolist(), 'pop': self.population.tolist(), 'gen': self.generation}
                self.cur.execute(f'INSERT INTO saves(path) VALUES ("{in_Box[0]}.json")')
                self.file_drop.addItem(f'{in_Box[0]}.json')
                self.file_drop.setCurrentText(f'{in_Box[0]}.json')
                with open(f'{in_Box[0]}.json', 'w') as g:
                    json.dump(js, g)
            except TypeError:
                self.err_Box.exec()
        else:
            ierr_Box = QMessageBox(self)
            ierr_Box.setText("This cannot be a file name")
            ierr_Box.setWindowTitle("Invalid file name")
            ierr_Box.setStandardButtons(QMessageBox.Ok)
            ierr_Box.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
