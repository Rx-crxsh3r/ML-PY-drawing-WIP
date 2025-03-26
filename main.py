import pickle
import os.path
import tkinter
import tkinter.messagebox
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

    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill = "black", width = self.brushWidth)
        self.draw.rectangle([x1, y1, x2 + self.brushWidth, y2 + self.brushWidth], fill = "black", width = self.brushWidth)

    def save(self, classNum):
        self.image1.save("temp.png")
        image = PIL.Image.open("temp.png")
        image = thumbnail((50, 50), PIL.Image.LANCZOS)
        
        if classNum == 1:
            image.save(f"{self.projectName}/{self.class1}/{self.class1_counter}.png", "PNG")
            self.class1_counter += 1
        
        elif classNum == 2:
            image.save(f"{self.projectName}/{self.class2}/{self.class2_counter}.png", "PNG")
            self.class2_counter += 1
        
        elif classNum == 3:
            image.save(f"{self.projectName}/{self.class3}/{self.class3_counter}.png", "PNG")
            self.class3_counter += 1
        
        self.clear()

    def brushminus(self):
        if self.brushWidth > 1:
            self.brushWidth -= 1
    
    def brushplus(self):
        if self.brushWidth < 100:
            self.brushWidth += 1

    def clear(self):
        self.canvas.delete("all")

        #not just the canvas needs to be clear, whatever we drew using PIL also needs to be cleared
        self.draw.rectangle([0, 0, 800, 800], fill = "white")

    def trainModel(self):
        imageList = np.array([])
        classList = np.array([])

        for x in range(1, self.class1_counter):
            image = cv.imread(f"{self.projectName}/{self.class1}/{x}.png")[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 1)

        for x in range(1, self.class2_counter):
            image = cv.imread(f"{self.projectName}/{self.class2}/{x}.png")[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 2)

        for x in range(1, self.class3_counter):
            image = cv.imread(f"{self.projectName}/{self.class3}/{x}.png")[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 3)
        
        imageList = imageList.reshape(self.class1_counter + self.class2_counter + self.class3_counter - 1, 2500)
       
        self.classifier.fit(imageList, classList)
        tkinter.messagebox.showinfo("Training Progress", "Model has been trained successfully", parent = self.root)
    
    def saveModel(self):
        filePath = filedialog.asksaveasfilename(defaultextension = "pickle")
        with open(filePath, "wb") as file:
            pickle.dump(self.clf, file)
        tkinter.messagebox.showinfo("Model Saving Progress", "Model has been saved successfully", parent = self.root)
       
        ########or can be done like:
        # with open(f"{self.projectName}/model.pkl", "wb") as file:
        #     pickle.dump({"c1": self.class1, "c2": self.class2, "c3": self.class3, "c1c": self.class1_counter, "c2c": self.class2_counter, "c3c": self.class3_counter, "clf": self.classifier}, file)
        # tkinter.messagebox.showinfo("Model Saving Progress", "Model has been saved successfully", parent = self.root)

    def loadModel(self):
        filePath = filedialog.askopenfilename()
        with open(filePath, "rb") as file:
            self.classifier = pickle.load(file)
        tkinter.messagebox.showinfo("Model Loading Progress", "Model has been loaded successfully", parent = self.root)
    
    def changeModel(self):
        if isinstance(self.classifier, LinearSVC):
            self.classifier = KNeighborsClassifier()
        elif isinstance(self.classifier, KNeighborsClassifier):
            self.classifier = LogisticRegression()
        elif isinstance(self.classifier, LogisticRegression):
            self.classifier = DecisionTreeClassifier()
        elif isinstance(self.classifier, DecisionTreeClassifier):
            self.classifier = GaussianNB()
        elif isinstance(self.classifier, GaussianNB):
            self.classifier = LinearSVC()
        self.statusLabel.config(text = f"Current Model: {type(self.classifier).__name__}")

    def predictClass(self):
        self.image1.save("temp.png")
        image = PIL.Image.open("temp.png")
        image.thumbnail((50, 50), PIL.Image.LANCZOS)
        image.save("predictClass.png"), "PNG")
        
        image = cv.imread("predictClass.png")[:, :, 0]
        image = image.reshape(2500)
        prediction = self.classifier.predict([image])
        if prediction[0] == 1:
            tkinter.messagebox.showinfo("Prediction", f"Prediction: {self.class1}", parent = self.root)
        elif prediction[0] == 2:
            tkinter.messagebox.showinfo("Prediction", f"This is probably a(n) {self.class2}", parent = self.root)
        elif prediction[0] == 3:
            tkinter.messagebox.showinfo("Prediction", f"Prediction: {self.class3}", parent = self.root)
        
    def saveEverything(self):
        data = {
            "c1": self.class1,
            "c2": self.class2,
            "c3": self.class3,
            "c1c": self.class1_counter,
            "c2c": self.class2_counter,
            "c3c": self.class3_counter,
            "clf": self.classifier,
            "classifier": self.classifier,
            "projectName": self.projectName}
        with open(f"{self.projectName}/{self.projectName}_data.pickle", "wb") as f:
            pickle.dump(data, f)
           
            tkinter.messagebox.showinfo("Saving Progress..", "Everything has been saved successfully", parent = self.root)

        def onClosing(self):
            answer = tkinter.messagebox.askyesnocancel("Exit..?", "Do you want to save everything before exiting?", parent = self.root)

            if answer is not None:
                if answer:
                    self.saveEverything()
                self.root.destroy()
                exit()

DrawingClassifier()