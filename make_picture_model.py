import cv2
import numpy as np
import os, tkinter, tkinter.filedialog, tkinter.messagebox


root = tkinter.Tk()
root.withdraw()

fTyp = [("", "*")]

iDir = os.path.abspath(os.path.dirname(__file__))
file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

if file == "":
    print("No picture source found")
    sys.exit(1)

picture_path = file

work_frame = cv2.imread(picture_path)

work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
work_frame = cv2.threshold(work_frame, 200, 255, cv2.THRESH_BINARY)[1]
work_frame = cv2.bitwise_not(work_frame)

print("\n保存file名を入力してください")
input_name = input(">> ")

np.save("model/" + input_name + ".npy", work_frame)