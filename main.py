import sys
import os
from time import time
from PySide6 import QtCore, QtWidgets, QtGui


class TimeLabel(QtWidgets.QLabel):

    def __init__(self,myclock,colorRef):

        super().__init__()

        self.clk = myclock

        self.color = colorRef

        self.updater = QtCore.QTimer()
        self.updater.timeout.connect(self.updateLabel)
        self.updater.start(100)

        self.setAlignment(QtCore.Qt.AlignCenter)

        if(self.color == Clock.BLACK):
            self.setStyleSheet("background-color : black;")
            self.setBackgroundRole(QtGui.QPalette.Dark)
        else:
            self.setStyleSheet("background-color : orange;")
            self.setBackgroundRole(QtGui.QPalette.Light)


    def updateLabel(self):
        currentTime = self.clk.remainingTime(self.color)
        self.setText(self.clk.labels[self.color] + os.linesep +currentTime)
        if(self.clk.game_end == False):
            self.updater.start(100)


class Clock(QtWidgets.QWidget):

    BLACK = 0
    WHITE = 1

    APP_NAME= "Chess Timer v0.9"

    def __init__(self):
        super().__init__()

        self.game_end = False
        #TIME FOR EACH PLAYER IN SECONDS
        self.TOTAL_TIME_EACH = 10*60
        self.labels = ["A","B"]
        self.labels[Clock.BLACK] = "Black time : "
        self.labels[Clock.WHITE] = "White time : "
        self.paused_time = [0 , 0]
        self.last_pause = [-1 , -1]
        self.startTime = -1
        self.STARTED = False
        self.now_playing = -1

        #QT INIT
        self.mbar = QtWidgets.QMenuBar(self)
        self.helpMenu = QtWidgets.QMenu("Help ?")
        self.help_action = QtGui.QAction("What to do",self)

        #Create Help Message
        self.helpmessage = QtWidgets.QMessageBox()  
        self.helpmessage.setIcon(QtWidgets.QMessageBox.Information)
        self.helpmessage.setText(Clock.APP_NAME)
        self.helpmessage.setInformativeText("Press RETURN to start the opponent timer")
        self.helpmessage.setWindowTitle(Clock.APP_NAME)
        self.helpmessage.setStandardButtons(QtWidgets.QMessageBox.Ok )
        #--------------------------------------------------------------------------------#

        self.help_action.triggered.connect(self.helpmessage.exec_)
        self.helpMenu.addAction(self.help_action)
        self.mbar.addMenu(self.helpMenu)

        #Install keyboard listener
        self.installEventFilter(self)
        
        self.labelUP = TimeLabel(self,Clock.BLACK)

        self.labelDOWN = TimeLabel(self,Clock.WHITE)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.mbar)
        self.layout.addWidget(self.labelUP)
        self.layout.addWidget(self.labelDOWN)
        self.setLayout(self.layout)

        
        
        


    def eventFilter(self,obj,event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return:
                self.click()
                return True
        return False

    @QtCore.Slot()
    def click(self):

        if self.game_end == True :

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("GAME END !")
            msg.setInformativeText("The game ended. Close the window, then restart if you wish")
            msg.setWindowTitle(Clock.APP_NAME)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

            return


        if self.STARTED == False :
            self.STARTED = True
            self.now_playing = Clock.WHITE
            now = time()
            self.last_pause[Clock.BLACK] = now
            self.startTime = now
            return
        
        if self.now_playing == Clock.BLACK :

            self.now_playing = Clock.WHITE
            #COMPUTE TIME WHITE HAS BEEN PAUSED SINCE LAST SWITCH
            now = time()
            toSum = now - self.last_pause[Clock.WHITE]
            self.paused_time[Clock.WHITE] += toSum
            #UPDATE LAST PAUSE FOR BLACK
            self.last_pause[Clock.BLACK] = now
        else :

            self.now_playing = Clock.BLACK
            #COMPUTE TIME BLACK HAS BEEN PAUSED SINCE LAST SWITCH
            now = time()
            toSum = now - self.last_pause[Clock.BLACK]
            self.paused_time[Clock.BLACK] += toSum
            #UPDATE LAST PAUSE FOR WHITE
            self.last_pause[Clock.WHITE] = now

    def remainingTime(self,WHO):
        
        now = time()
        elapsed_from_start = 0
        if(WHO == self.now_playing):
            elapsed_from_start = now - self.startTime
        else : 
            elapsed_from_start = self.last_pause[WHO] - self.startTime
        time_in_pause = self.paused_time[WHO]
        effective_play_time = elapsed_from_start - time_in_pause
        remainingSeconds = self.TOTAL_TIME_EACH - effective_play_time
        if(remainingSeconds <= 0 ):
            self.game_end = True
            return "YOU LOSE"
        else :
            return str(int(remainingSeconds/60))+":"+str(round(remainingSeconds%60,2))

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    

    widget = Clock()
    widget.resize(300, 300)
    widget.setFixedSize(widget.frameSize())
    widget.setWindowTitle(Clock.APP_NAME)
    widget.setStyleSheet("font : bold 30pt; background-color : grey")
    widget.show()

    sys.exit(app.exec_())