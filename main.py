# =============================================================================
# IMPORTS
# =============================================================================

import pickle
import os
import os.path
import tkinter
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
import numpy as np
import PIL.Image, PIL.ImageDraw
import cv2 as cv
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

# =============================================================================
# CLASS: DrawingClassifier
# =============================================================================

class DrawingClassifier:
    def __init__(self):
        """
        Initialize the DrawingClassifier object by setting up attributes, 
        prompting for project and class names, and initializing the GUI.
        """
        # Class names (to be defined by the user)
        self.class1 = None
        self.class2 = None
        self.class3 = None

        # Counters for how many examples have been saved for each class
        self.class1_counter = None
        self.class2_counter = None
        self.class3_counter = None

        # Classifier object (will be set to a default classifier)
        self.classifier = None

        # Project directory name for saving images and model
        self.projectName = None

        # GUI components
        self.root = None
        self.canvas = None
        self.statusLabel = None

        # Image and drawing objects (PIL)
        self.image1 = None
        self.draw = None

        # Default brush size for drawing on the canvas
        self.brushWidth = 15

        # Call the method to prompt for project/class names
        self.classesPrompt()

        # Initialize the graphical user interface
        self.initGUI()

    # -------------------------------------------------------------------------
    def classesPrompt(self):
        """
        Prompt the user for the project name and class names. If the project already
        exists, load the previously saved model and counters.
        """
        # Create a temporary hidden root window for dialogs
        message = Tk()
        message.withdraw()

        # Ask for the project name
        self.projectName = simpledialog.askstring("Project Name",
                                                  "Enter the name of the project",
                                                  parent=message)
        if not self.projectName:
            # If the user cancels the dialog, exit the method
            message.destroy()
            return

        # Check if the project directory already exists
        if os.path.exists(self.projectName):
            # Attempt to load previously saved data
            try:
                with open(f"{self.projectName}/model.pkl", "rb") as file:
                    data = pickle.load(file)
                self.class1 = data["c1"]
                self.class2 = data["c2"]
                self.class3 = data["c3"]
                self.class1_counter = data["c1c"]
                self.class2_counter = data["c2c"]
                self.class3_counter = data["c3c"]
                self.classifier = data["clf"]
            except Exception as e:
                # Show an error message and prompt the user for the next action
                response = tkinter.messagebox.askretrycancel(
                    "Error",
                    f"Error loading model: {e}\nWould you like to retry or create a new project?",
                    parent=message
                )
                if response:  # Retry loading the model
                    self.classesPrompt()
                else:  # Create a new project
                    self.createNewProject(message)
        else:
            # If the project doesn't exist, create new project directories
            self.createNewProject(message)

        # Destroy the temporary window after prompting
        message.destroy()

    # -------------------------------------------------------------------------
    def createNewProject(self, parent):
        """
        Create a new project by prompting for class names and initializing counters,
        classifier, and directories.
        """
        # Prompt for each class name
        self.class1 = simpledialog.askstring("Class 1",
                                               "Enter the name of the first class",
                                               parent=parent)
        self.class2 = simpledialog.askstring("Class 2",
                                               "Enter the name of the second class",
                                               parent=parent)
        self.class3 = simpledialog.askstring("Class 3",
                                               "Enter the name of the third class",
                                               parent=parent)
        # Initialize counters to 1 (first image index)
        self.class1_counter = 1
        self.class2_counter = 1
        self.class3_counter = 1

        # Default classifier is LinearSVC
        self.classifier = LinearSVC()

        # Create the project directory and subdirectories for each class
        try:
            os.mkdir(self.projectName)  # Corrected from os.mdkir to os.mkdir
            os.chdir(self.projectName)
            os.mkdir(self.class1)
            os.mkdir(self.class2)
            os.mkdir(self.class3)
            os.chdir("..")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error creating project directories: {e}",
                                           parent=parent)

    # -------------------------------------------------------------------------
    def initGUI(self):
        """
        Initialize the graphical user interface, including the drawing canvas and control buttons.
        """
        # Define canvas dimensions and white color
        WIDTH = 500
        HEIGHT = 500
        WHITE = (255, 255, 255)

        # Create the main root window
        self.root = Tk()
        self.root.title(f"Drawing App - {self.projectName}")

        # Create a drawing canvas with a white background
        self.canvas = Canvas(self.root, width=WIDTH-10, height=HEIGHT-10, bg="white")
        self.canvas.pack(expand=YES, fill=BOTH)

        # Bind the mouse motion (while button is held) to the paint method
        self.canvas.bind("<B1-Motion>", self.paint)

        # Create a new PIL image for drawing, and an ImageDraw object
        self.image1 = PIL.Image.new("RGB", (WIDTH, HEIGHT), WHITE)
        self.draw = PIL.ImageDraw.Draw(self.image1)

        # Create a frame for buttons at the bottom of the window
        buttonFrame = tkinter.Frame(self.root)
        buttonFrame.pack(fill=X, side=BOTTOM)

        # Configure grid columns for even button distribution
        buttonFrame.columnconfigure(0, weight=1)
        buttonFrame.columnconfigure(1, weight=1)
        buttonFrame.columnconfigure(2, weight=1)

        # Create buttons for each class to save the drawn image
        class1Button = Button(buttonFrame, text=self.class1,
                              command=lambda: self.save(1))
        class1Button.grid(row=0, column=0, sticky=W+E)

        class2Button = Button(buttonFrame, text=self.class2,
                              command=lambda: self.save(2))
        class2Button.grid(row=0, column=1, sticky=W+E)

        class3Button = Button(buttonFrame, text=self.class3,
                              command=lambda: self.save(3))
        class3Button.grid(row=0, column=2, sticky=W+E)

        # Buttons for brush control and clearing the canvas
        brushSizeMinusButton = Button(buttonFrame, text="-Brush size", command=self.brushminus)
        brushSizeMinusButton.grid(row=1, column=0, sticky=W+E)

        clearButton = Button(buttonFrame, text="Clear", command=self.clear)
        clearButton.grid(row=1, column=1, sticky=W+E)

        brushSizePlusButton = Button(buttonFrame, text="+Brush size", command=self.brushplus)
        brushSizePlusButton.grid(row=1, column=2, sticky=W+E)

        # Buttons for model operations: train, save, load
        trainButton = Button(buttonFrame, text="Train Model", command=self.trainModel)
        trainButton.grid(row=2, column=0, sticky=W+E)

        saveModelButton = Button(buttonFrame, text="Save Model", command=self.saveModel)
        saveModelButton.grid(row=2, column=1, sticky=W+E)

        loadModelButton = Button(buttonFrame, text="Load Model", command=self.loadModel)
        loadModelButton.grid(row=2, column=2, sticky=W+E)

        # Buttons for changing model type, predicting, and saving everything
        changeModelButton = Button(buttonFrame, text="Change Model", command=self.changeModel)
        changeModelButton.grid(row=3, column=0, sticky=W+E)

        predictButton = Button(buttonFrame, text="Predict Class", command=self.predictClass)
        predictButton.grid(row=3, column=1, sticky=W+E)

        saveEverythingButton = Button(buttonFrame, text="Save Everything", command=self.saveEverything)
        saveEverythingButton.grid(row=3, column=2, sticky=W+E)

        # Label to display the current classifier type
        self.statusLabel = Label(buttonFrame, text=f"Current Model: {type(self.classifier).__name__}")
        self.statusLabel.config(font=("Courier", 12))
        self.statusLabel.grid(row=4, column=1, sticky=W+E)

        # Set window closing protocol to prompt for saving before exit
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.attributes("-topmost", True)
        self.root.mainloop()

    # -------------------------------------------------------------------------
    def paint(self, event):
        """
        Callback method for drawing on the canvas.
        Draws a small rectangle on both the canvas and the PIL image.
        """
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        # Draw on the Tkinter canvas
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", width=self.brushWidth)
        # Draw on the PIL image
        self.draw.rectangle([x1, y1, x2 + self.brushWidth, y2 + self.brushWidth],
                            fill="black", width=self.brushWidth)

    # -------------------------------------------------------------------------
    def save(self, classNum):
        """
        Save the current canvas drawing as a thumbnail image for the specified class.
        :param classNum: An integer (1, 2, or 3) indicating the class to save the image for.
        """
        # Save the current drawing to a temporary file
        self.image1.save("temp.png")
        image = PIL.Image.open("temp.png")
        # Resize the image to a 50x50 thumbnail using LANCZOS filter
        image.thumbnail((50, 50), PIL.Image.LANCZOS)

        # Save the thumbnail into the appropriate class folder with a sequential name
        if classNum == 1:
            image.save(f"{self.projectName}/{self.class1}/{self.class1_counter}.png", "PNG")
            self.class1_counter += 1
        elif classNum == 2:
            image.save(f"{self.projectName}/{self.class2}/{self.class2_counter}.png", "PNG")
            self.class2_counter += 1
        elif classNum == 3:
            image.save(f"{self.projectName}/{self.class3}/{self.class3_counter}.png", "PNG")
            self.class3_counter += 1

        # Clear the canvas after saving the image
        self.clear()

    # -------------------------------------------------------------------------
    def brushminus(self):
        """
        Decrease the brush width, ensuring it does not go below 1.
        """
        if self.brushWidth > 1:
            self.brushWidth -= 1

    # -------------------------------------------------------------------------
    def brushplus(self):
        """
        Increase the brush width, ensuring it does not exceed 100.
        """
        if self.brushWidth < 100:
            self.brushWidth += 1

    # -------------------------------------------------------------------------
    def clear(self):
        """
        Clear the drawing canvas and the underlying PIL image.
        """
        self.canvas.delete("all")
        # Clear the PIL image by drawing a white rectangle over the entire area
        self.draw.rectangle([0, 0, 800, 800], fill="white")

    # -------------------------------------------------------------------------
    def trainModel(self):
        """
        Train the classifier using the images saved for each class.
        The images are loaded, flattened, and labeled accordingly.
        """
        imageList = np.array([])
        classList = np.array([])

        # Loop through each image in class1 directory
        for x in range(1, self.class1_counter):
            img_path = f"{self.projectName}/{self.class1}/{x}.png"
            image = cv.imread(img_path)[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 1)

        # Loop through each image in class2 directory
        for x in range(1, self.class2_counter):
            img_path = f"{self.projectName}/{self.class2}/{x}.png"
            image = cv.imread(img_path)[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 2)

        # Loop through each image in class3 directory
        for x in range(1, self.class3_counter):
            img_path = f"{self.projectName}/{self.class3}/{x}.png"
            image = cv.imread(img_path)[:, :, 0]
            image = image.reshape(2500)
            imageList = np.append(imageList, image)
            classList = np.append(classList, 3)

        # Reshape the image list into a matrix where each row is a flattened image
        total_images = self.class1_counter + self.class2_counter + self.class3_counter - 3
        imageList = imageList.reshape(total_images, 2500)

        # Train the classifier with the image data and corresponding class labels
        self.classifier.fit(imageList, classList)

        tkinter.messagebox.showinfo("Training Progress",
                                    "Model has been trained successfully",
                                    parent=self.root)

    # -------------------------------------------------------------------------
    def saveModel(self):
        """
        Save the trained model to a file selected by the user.
        Alternatively, the model and project information can be saved to the project directory.
        """
        filePath = filedialog.asksaveasfilename(defaultextension="pickle")
        try:
            with open(filePath, "wb") as file:
                pickle.dump(self.classifier, file)
            tkinter.messagebox.showinfo("Model Saving Progress",
                                        "Model has been saved successfully",
                                        parent=self.root)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error saving model: {e}", parent=self.root)

    # -------------------------------------------------------------------------
    def loadModel(self):
        """
        Load a trained model from a file selected by the user.
        """
        filePath = filedialog.askopenfilename()
        try:
            with open(filePath, "rb") as file:
                self.classifier = pickle.load(file)
            tkinter.messagebox.showinfo("Model Loading Progress",
                                        "Model has been loaded successfully",
                                        parent=self.root)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error loading model: {e}", parent=self.root)

    # -------------------------------------------------------------------------
    def changeModel(self):
        """
        Cycle through a set of predefined classifiers.
        The order is: LinearSVC -> KNeighborsClassifier -> LogisticRegression ->
        DecisionTreeClassifier -> GaussianNB -> LinearSVC (and so on).
        """
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
        # Update the status label with the new classifier name
        self.statusLabel.config(text=f"Current Model: {type(self.classifier).__name__}")

    # -------------------------------------------------------------------------
    def predictClass(self):
        """
        Predict the class of the current drawing.
        The drawn image is resized and processed before being passed to the classifier.
        """
        # Save the current drawing to a temporary file
        self.image1.save("temp.png")
        image = PIL.Image.open("temp.png")
        image.thumbnail((50, 50), PIL.Image.LANCZOS)
        image.save("predictClass.png", "PNG")

        # Load the processed image using OpenCV and flatten it for prediction
        image = cv.imread("predictClass.png")[:, :, 0]
        image = image.reshape(2500)
        prediction = self.classifier.predict([image])
        # Display prediction results in a message box
        if prediction[0] == 1:
            tkinter.messagebox.showinfo("Prediction", f"Prediction: {self.class1}", parent=self.root)
        elif prediction[0] == 2:
            tkinter.messagebox.showinfo("Prediction", f"Prediction: {self.class2}", parent=self.root)
        elif prediction[0] == 3:
            tkinter.messagebox.showinfo("Prediction", f"Prediction: {self.class3}", parent=self.root)

    # -------------------------------------------------------------------------
    def saveEverything(self):
        """
        Save all project-related data, including class names, counters, classifier,
        and project name into a single pickle file.
        """
        data = {
            "c1": self.class1,
            "c2": self.class2,
            "c3": self.class3,
            "c1c": self.class1_counter,
            "c2c": self.class2_counter,
            "c3c": self.class3_counter,
            "clf": self.classifier,
            "projectName": self.projectName
        }
        try:
            with open(f"{self.projectName}/{self.projectName}_data.pickle", "wb") as f:
                pickle.dump(data, f)
            tkinter.messagebox.showinfo("Saving Progress..",
                                        "Everything has been saved successfully",
                                        parent=self.root)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error saving data: {e}", parent=self.root)

    # -------------------------------------------------------------------------
    def onClosing(self):
        """
        Prompt the user to save all data before closing the application.
        """
        answer = tkinter.messagebox.askyesnocancel("Exit..?",
                                                   "Do you want to save everything before exiting?",
                                                   parent=self.root)
        if answer is not None:
            if answer:
                self.saveEverything()
            self.root.destroy()
            exit()

# =============================================================================
# MAIN PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Create an instance of the DrawingClassifier application.
    DrawingClassifier()
