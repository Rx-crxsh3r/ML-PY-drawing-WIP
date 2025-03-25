import pickle
import os.path
import numpy as np
import PIL.Image, PIL.ImageDraw
import cv2 as cv
from tkinter import *
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

class DrawingClassifier:
    def __init__(self):
        #just for degining attributes
        #we're going to allow the model to guess from three classes defined, so this is how
        self.class1, self.class2, self.class3 = None, None, None

        #the counters are used for tracking how many examples we're feeling the model for each class
        #we should initialize them as none appropriately
        self.class1_counter, self.class2_counter, self.class3_counter = None, None, None

        #
        self.classifier = None

        #name of directory we're storing the items in
        self.projectName = None
        self.root = None
        self.image1 = None
        self.statusLabel = None
        self.canvas = None
        self.draw = None

        #default brush size
        self.brushWidth = 15
        self.classesPrompt()
        self.initGUI()

    def classesPrompt(self):
        message = Tk()
        message.withdraw()

        self.projectName = simpledialog.askstring("Project Name", "Enter the name of the project", parent - message)

        #this is just incase project name already exists, then we can just load it instead of creating a new project 
        if os.path.exists(self.projectName):
            with open(f"{self.projectName}/model.pkl", "rb") as file:
                data = pickle.load(file)
            self.class1 = data["c1"]
            self.class2 = data["c2"]
            self.class3 = data["c3"]
            self.class1_counter = data["c1c"]
            self.class2_counter = data["c2c"]
            self.class3_counter = data["c3c"]
            self.classifier = data["clf"]
            
        else:
            self.class1 = simpledialog.askstring("Class 1", "Enter the name of the first class", parent = message)
            self.class2 = simpledialog.askstring("Class 2", "Enter the name of the second class", parent = message)
            self.class3 = simpledialog.askstring("Class 3", "Enter the name of the third class", parent = message)

            self.class1_counter = 1
            self.class2_counter = 1
            self.class3_counter = 1

            self.classifier = LinearSVC()

            os.mdkir(self.projectName)
            os.chdir(self.projectName)
            os.mkdir(self.class1)
            os.mkdir(self.class2)
            os.mkdir(self.class3)
            os.chdir("..")

    def initGUI(self):
        #gui

        WIDTH = 500
        HEIGHT = 500
        WHITE(255, 255, 255)
        self.root = Tk()
        self.root.title(f"Drawing app thing {self.projectName}")
        
        self.canvas = Canvas(self.root, width = WIDTH-10, height = HEIGHT-10, bg = "white")
        self.canvas.pack(expand = YES, fill = BOTH)

        #binding the motion of clicking a button with a function
        self.canvas.bind("<B1-Motion>", self.paint)

        self.image1 = PIL.Image.new("RGB", (WIDTH, HEIGHT), WHITE)
        self.draw = PIL.ImageDraw.Draw(self.image1)

        #buttons
        buttonFrame = tkinter.Frame(self.root)
        buttonFrame.pack(fill=X, side = BOTTOM)
        buttonFrame.columnconfigure(0, weight = 1)
        buttonFrame.columnconfigure(1, weight = 1)
        buttonFrame.columnconfigure(2, weight = 1)

        class1Button = Button(buttonFrame, text = self.class1, command = lambda: self.saveImage(self.save(1)))
        class1Button.grid(row = 0, column = 0, sticky = W + E)

        class2Button = Button(buttonFrame, text = self.class2, command = lambda: self.saveImage(self.save(2)))
        class2Button.grid(row = 0, column = 1, sticky = W+E)

        class3Button = Button(buttonFrame, text = self.class3, command = lambda: self.saveImage(self.save(3)))
        class3Button.grid(row = 0, column = 2, sticky = W+E)

        brushSizeMinusButton = Button(buttonFrame, text = "-Brush size", command = self.brushminus)
        brushSizeMinusButton.grid(row = 1, column = 0, sticky = W+E)

        clearButton = Button(buttonFrame, text = "Clear", command = self.clear)
        clearButton.grid(row = 1, column = 1, sticky = W+E)

        brushSizePlusButton = Button(buttonFrame, text = "+Brush size", command = self.brushplus)
        brushSizePlusButton.grid(row = 1, column = 2, sticky = W+E)

        trainButton = Button(buttonFrame, text = "Train Model", command = self.trainModel)
        trainButton.grid(row = 2, column = 0, sticky = W+E)

        saveModelButton = Button(buttonFrame, text = "Save Model", command = self.saveModel)
        saveModelButton.grid(row = 2, column = 1, sticky = W+E)

        loadModelButton = Button(buttonFrame, text = "Load Model", command = self.loadModel)
        loadModelButton.grid(row = 2, column = 2, sticky = W+E)

        changeModelButton = Button(buttonFrame, text = "Change Model", command = self.changeModel)
        changeModelButton.grid(row = 3, column = 0, sticky = W+E)

        predictButton = Button(buttonFrame, text = "Predict Class", command = self.predictClass)
        predictButton.grid(row = 3, column = 1, sticky = W+E)

        saveEverythingButton = Button(buttonFrame, text = "Save Everything", command = self.saveEverything)
        saveEverythingButton.grid(row = 3, column = 2, sticky = W+E)

        self.statusLabel = Label(buttonFrame, text = f"Current Model: {type(self.classifier).__name__}")
        self.statusLabel.config(font=("Courier", 12))
        self.statusLabel.grid(row = 4, column = 1, sticky = W+E)

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.attributes("-topmost", True)
        self.root.mainloop()



