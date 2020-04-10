#!/usr/bin/venv python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 13:43:12 2020

@author: Y.H. Cheng
"""

import os
import pandas as pd
import secrets
import hashlib

from PyQt5 import QtWidgets, QtCore


class ChooseFile(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(ChooseFile, self).__init__(parent)
        #self.setCommitPage(True)
        
        body = QtWidgets.QVBoxLayout(self)
        body.addWidget(QtWidgets.QLabel('Welcome to Pseudonymiser!'))
        body.addWidget(QtWidgets.QLabel('This app pseudonymises by hashing.\n'))
        body.addWidget(QtWidgets.QLabel('Path of the CSV file to pseudonymise:'))

        self.filePathShow = QtWidgets.QLineEdit(self)
        self.filePathShow.setReadOnly(True)  # not editable
        self.registerField("filePathShow*", self.filePathShow)  # mandatory
        body.addWidget(self.filePathShow)

        browseButton = QtWidgets.QPushButton("Browse...", self)
        browseButton.clicked.connect(self.browseDialog)
        browseBox = QtWidgets.QHBoxLayout()
        browseBox.addStretch(1)
        browseBox.addWidget(browseButton)
        
        body.addLayout(browseBox)

    def browseDialog(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open CSV", "/home", "(*.csv)")
        if filePath:  # only changes if valid file, stays same if user cancels dialog
            self.setField("filePathShow", filePath)


class ChooseColumns(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(ChooseColumns, self).__init__(parent)

        self.comboboxes = []
        self.printFileName = QtWidgets.QLabel()
        self.form = QtWidgets.QFormLayout()
        
        box = QtWidgets.QGroupBox()
        box.setLayout(self.form)
        
        body = QtWidgets.QVBoxLayout(self)
        body.addWidget(self.printFileName)
        body.addWidget(QtWidgets.QLabel(
            'Pseudonymiser has detected the following columns.'))
        body.addWidget(QtWidgets.QLabel(
            'Which column(s) would you like to copy or pseudonymise?'))
        body.addWidget(box)
        body.addWidget(QtWidgets.QLabel(
            'The number of columns to be pseudonymised must be at least 1.'))
        body.addWidget(QtWidgets.QLabel(
            'Options will be reset if you click Back.'))

    def initializePage(self):
        '''
        makes comboboxes according to the selected file's columns'
        '''
        for combo in self.comboboxes:
            self.form.removeRow(combo)
        self.comboboxes = []
        self.wizard().setProperty("indexes_selected", [])
        self.wizard().setProperty("options_selected", [])

        filePath2 = self.field("filePathShow")
        
        fileName = os.path.split(str(filePath2))[-1]
        self.printFileName.setText(f'Chosen file:   {fileName}')  # prints file name
        
        df = pd.read_csv(filePath2)
        options = (  # if modified, need to edit is_completed (here) & choiceIdx (Finish)
            "", 
            #"Do not use", 
            "Copy only", 
            #"Pseudonymise with token", 
            "Pseudonymise"  # with hash
        )
        for i, colName in enumerate(df.columns):
            combo = QtWidgets.QComboBox()
            combo.addItems(options)
            combo.currentIndexChanged.connect(self.completeChanged)
            self.form.addRow(colName, combo)
            self.comboboxes.append(combo)

    def isComplete(self):
        '''
        at least 1 column must be chosen to be pseudonymised and the others chosen to be copied
        '''
        indexes = [combo.currentIndex() for combo in self.comboboxes]
        is_completed = all(index >= 1 for index in indexes) and any(index >= 2 for index in indexes)
        self.wizard().setProperty("indexes_selected", indexes)
        self.wizard().setProperty(
            "options_selected", [combo.currentText() for combo in self.comboboxes]
        )
        return is_completed


class SaltAndKeyfile(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def initializePage(self):
        filePath2 = self.field("filePathShow")
        fileDirectory = os.path.split(str(filePath2))[0]  # file directory
        fileName_noExt = os.path.split(str(filePath2))[-1][:-4]  # file name without extension
        
        body = QtWidgets.QVBoxLayout(self)
        
        body.addWidget(QtWidgets.QLabel('Do you want to use a specific salt?'))        
        
        saltBox = QtWidgets.QHBoxLayout()
        saltBox.addWidget(QtWidgets.QLabel('Enter your salt or leave it blank:'))
        salt = QtWidgets.QLineEdit()
        self.registerField("salt", salt)  # NOT mandatory
        saltBox.addWidget(salt)
        body.addLayout(saltBox)
        body.addWidget(QtWidgets.QLabel('If not provided, the salt will be randomly generated.\n'))
        
        keyFile = QtWidgets.QHBoxLayout()
        keyFile.addWidget(QtWidgets.QLabel('Do you want to keep a key file?   '))

        keyFileChoice = QtWidgets.QComboBox()
        keyFileChoice.addItem("")
        keyFileChoice.addItem("Yes")
        keyFileChoice.addItem("No")
        keyFileChoice.setMinimumWidth(50)
        self.registerField("keyFileChoice*", keyFileChoice)  # mandatory      
        
        keyFile.addWidget(keyFileChoice)
        keyFile.addStretch(1)
        
        body.addLayout(keyFile)
        body.addWidget(QtWidgets.QLabel(
            'A key file is recommended if you do not provide salt, since the random salt will not be saved.'))

        body.addWidget(QtWidgets.QLabel(
            f'The key file will be stored as: {fileName_noExt}_key.csv'))
        body.addWidget(QtWidgets.QLabel(
            f'\n\nThe pseudonymised file will be stored as: {fileName_noExt}_pseudo.csv'))
        body.addWidget(QtWidgets.QLabel(
            f'\n\nFiles will be stored in the same folder as {fileName_noExt}.csv :'))
        body.addWidget(QtWidgets.QLabel(fileDirectory + '/'))
        
        self.setLayout(body)


class Finish(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        body = QtWidgets.QVBoxLayout(self)
        body.addWidget(QtWidgets.QLabel('All done! Thank you for using Pseudonymiser.'))
        self.setLayout(body)
        
    def initializePage(self):
        '''
        columns are pseudonymised, key file created (if "Yes" selected in prev page)
        '''
        filePath2 = self.field("filePathShow")
        fileDirectory = os.path.split(str(filePath2))[0]
        fileName_noExt = os.path.split(str(filePath2))[-1][:-4]
        df = pd.read_csv(filePath2)
        
        choiceIdx = self.wizard().property("indexes_selected")
        key = []
        keyColNames = []
        saltLengthMax = 32  # bytes
        for i, colName in enumerate(df.columns):
            #colName = str(colName)
            if choiceIdx[i] == 2:  # hash
                key.append(df[colName].tolist())
                keyColNames.append(colName)
                
                if self.field("salt") == '':
                    # random salt of random length
                    saltLength = secrets.randbelow(saltLengthMax + 1) + 1
                    salt = secrets.token_hex(saltLength)
                else:
                    # user-provided salt
                    salt = self.field("salt")
                    
                df[colName] = df[colName].astype(str) + str(salt)
                df[colName] = [hashlib.sha256(str.encode(j)).hexdigest() for j in df[colName]]  # SHA256
                
                key.append(df[colName].tolist())
                keyColNames.append(colName + 'key')
                
        if self.field("keyFileChoice") == 1:
            # make key file
            df_key = pd.DataFrame(data = key).transpose()
            df_key.columns = keyColNames
            # save files
            df_key.to_csv(fileDirectory + f'/{fileName_noExt}_key.csv', index = False, header = True)
        df.to_csv(fileDirectory + f'/{fileName_noExt}_pseudo.csv', index = False, header = True)
        

class Manager(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        
        self.resize(500, 300)  # window size
        self.setWindowTitle("Pseudonymiser")
        #self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.setWizardStyle(1)  # 1 = ModernStyle
        self.setWindowFlags(  # for the title bar
            QtCore.Qt.CustomizeWindowHint | 
            QtCore.Qt.WindowSystemMenuHint | 
            QtCore.Qt.WindowTitleHint | 
            QtCore.Qt.WindowCloseButtonHint | 
            QtCore.Qt.WindowMinMaxButtonsHint
        )
        self.setOption(self.HaveHelpButton, False)  # delete Help button on all pages

        self.addPage(ChooseFile())
        self.addPage(ChooseColumns())
        self.addPage(SaltAndKeyfile())
        self.addPage(Finish())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')
    w = Manager()
    w.show()
    sys.exit(app.exec_())