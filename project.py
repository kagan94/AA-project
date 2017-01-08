import tkMessageBox
import tkFileDialog
from Tkinter import Tk, Button, DISABLED, NORMAL

# Constants
selected_img_path = None


def show_error(msg):
    tkMessageBox.showerror("Error", msg)


################################
# Handlers for buttons
def on_file_selected():
    global selected_img_path
    # Ask user where is image located
    img_path = tkFileDialog.askopenfilename()
    selected_img_path = img_path if img_path else None


def on_start_processing():
    if not selected_img_path:
        show_error("You didn't select image")
        return

    # Block "select img" and "start" buttons until process will be finished
    select_img_b.config(state=DISABLED)
    start_b.config(state=DISABLED)

    # TODO: Put user image in "tmp" folder
    # TODO: Save *.svg result in "tmp" folder

    print "Processing has been started"


################################
# Main program window
root = Tk()
root.geometry("250x150")

# Buttons
select_img_b = Button(root, text='Select image', command=on_file_selected)
start_b = Button(root, text='Start processing', command=on_start_processing)
exit_b = Button(root, text='Exit Program', command=root.destroy)

select_img_b.pack(pady=(20, 0))
start_b.pack(pady=10)
exit_b.pack()

# TODO: uncomment in final version
# root.mainloop()


img_path
