import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QPushButton, QInputDialog, QLabel
from PyQt6.QtCore import Qt
from PyQt6 import uic, QtCore, QtWidgets, QtGui
import pandas as pd
import prediction_for_input
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])


class AnotherWindow(QWidget):
    def __init__(self, fig):
        super().__init__()
        layout = QVBoxLayout()
        label1 = QLabel('Bar Plot')
        self.setLayout(layout)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        layout.addWidget(label1)

        toolbar = NavigationToolbar2QT(canvas, self)
        layout.addWidget(toolbar)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        canvas = FigureCanvas(fig)  # create canvas
        layout.addWidget(canvas)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('GUI_DKcat.ui', self)
        self.setWindowTitle('DLKcat')
        self.Predict.clicked.connect(self.testinput)
        self.Reset.clicked.connect(self.resetinput)
        self.Example.clicked.connect(self.exampleinput)
        self.To_Excel.hide()
        self.PlotBar.hide()
        self.w = None

    def exampleinput(self):
        seq = 'MVHVRKNHLTMTAEEKRRFVHAVLEIKRRGIYDRFVKLHIQINSTDYLDKETGKRLGHVNPGFLPWHRQYLLKFEQALQKVDPRVTLPYWDWTTDHGENSPLWSDTFMGGNGRPGDRRVMTGPFARRNGWKLNISVIPEGPEDPALNGNYTHDDRDYLVRDFGTLTPDLPTPQELEQTLDLTVYDCPPWNHTSGGTPPYESFRNHLEGYTKFAWEPRLGKLHGAAHVWTGGHMMYIGSPNDPVFFLNHCMIDRCWALWQARHPDVPHYLPTVPTQDVPDLNTPLGPWHTKTPADLLDHTRFYTYDQ'
        self.input_seq.setText(seq)
        self.input_pos.setText('20')
        self.input_sub.setText('Catechol')
        self.input_smiles.setText('C1=CC=C(C(=C1)O)O')

    def resetinput(self):
        self.input_seq.setText('')
        self.input_pos.setText('')
        self.input_sub.setText('')
        self.input_smiles.setText('')
        self.textBrowser.setText('')
        self.To_Excel.hide()
        self.PlotBar.hide()
        os.remove('input.tsv')
        os.remove('output.tsv')
        self.alert(2)

    def testinput(self):
        if self.input_seq.toPlainText() != '' and self.input_pos.text() != '' and self.input_sub.text() != '' and self.input_smiles.text() != '':
            sequence = self.input_seq.toPlainText()
            position = self.input_pos.text()
            substrate = self.input_sub.text()
            SMILES = self.input_smiles.text()
            # self.textBrowser.setText(
            #     f'{sequence}\n{position}\n{substrate}\n{SMILES}\n')
            try:
                position = int(self.input_pos.text())
                if type(position) == int:
                    try:
                        self.saturated_mutagenesis(
                            sequence, substrate, position, SMILES)
                    except:
                        self.alert(4)
                    try:
                        self.new_windows()
                    except:
                        self.alert(5)
            except:
                self.alert(0)
        else:
            self.alert(1)

    def alert(self, num):
        self.mbox = QMessageBox(self)
        if num == 0:
            self.mbox.information(
                self, 'warning', 'The position have to be integer!')
            self.input_pos.setText('')
            self.textBrowser.setText('')
        elif num == 1:
            self.mbox.information(
                self, 'warning', 'Please fill in the information!'
            )
        elif num == 2:
            self.mbox.information(
                self, 'information', 'The form is reset!'
            )
        elif num == 3:
            self.mbox.information(
                self, 'information', 'The output tsv file is generated!'
            )

        elif num == 4:
            self.mbox.information(
                self, 'warning', 'Something went wrong with the prediction...'
            )
        elif num == 5:
            self.mbox.information(
                self, 'warning', 'Something went wrong when generating the new window...'
            )
        elif num == 6:
            self.mbox.information(
                self, 'information', 'The excel file is generated!'
            )

    def saturated_mutagenesis(self, sequence, substrate, position, SMILES):
        AA = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I',
              'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']
        inputdic = {'Substrate Name': [],
                    'Substrate SMILES': [], 'Protein Sequence': []}
        pos = position-1
        for i in AA:
            sub_name = f'{substrate}_{sequence[pos]}{position}{i}'
            inputdic['Substrate Name'].append(sub_name)
            inputdic['Substrate SMILES'].append(SMILES)
            seq = list(sequence)
            seq[pos] = i
            seq = ''.join(seq)
            inputdic['Protein Sequence'].append(seq)
        df = pd.DataFrame(inputdic)
        df.to_csv('input.tsv', sep='\t', index=False)
        prediction_for_input.main()
        df = pd.read_csv('output.tsv', sep='\t')
        df.drop(['Protein Sequence', 'Substrate SMILES'], axis=1, inplace=True)
        self.textBrowser.setText(df.to_string())
        self.alert(3)
        self.To_Excel.show()
        self.PlotBar.show()
        self.To_Excel.clicked.connect(self.toexcel)
        self.PlotBar.clicked.connect(self.toplot)

    def toplot(self):
        if self.w == None:
            df = pd.read_csv('output.tsv', sep='\t')
            fig = Figure()
            ax = fig.add_subplot()
            x = df['Substrate Name'].str.split('_').str[1]
            y = df['Kcat value (1/s)']
            ax.bar(x, y)
            ax.set_title(
                f'Substrate: {df["Substrate Name"].str.split("_")[0][0]}')
            ax.set_ylabel('Predicted Kcat(1/s)')
            ax.set_xlabel('Mutation')
            ax.tick_params(axis='x', labelrotation=90)
            self.w = AnotherWindow(fig)
            self.w.show()
        else:
            self.w = None

    def toexcel(self):
        Form = QtWidgets.QWidget()
        Form.setWindowTitle('To_Excel')
        Form.resize(50, 50)
        name, ok = QInputDialog().getText(Form, '', 'Please name your excel')
        df = pd.read_csv("output.tsv", sep='\t')
        df.to_excel(f'{name}.xlsx')

    def new_windows(self):
        self.table = QtWidgets.QTableView()
        data = pd.read_csv('output.tsv', sep='\t')
        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.table.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
