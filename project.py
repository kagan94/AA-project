# -*- coding: utf-8 -*-
import subprocess
import time
import ntpath
import tkMessageBox
import tkFileDialog
import os
from Tkinter import Tk, Button, DISABLED, NORMAL, Frame, Label, END
from ScrolledText import *
from shutil import copyfile
from xml.etree import ElementTree
from threading import Thread

# Constants
selected_img_path = None

current_dir = os.path.abspath(os.path.dirname(__file__))
current_dir = current_dir.decode('cp1251').encode("utf-8")
# Directory where we store files while process them
temp_dir = os.path.join(current_dir, "tmp")


################################
# Additional methods
def show_error(msg):
    tkMessageBox.showerror("Error", msg)


def add_notif(msg):
    ''' Add new notification to notification area '''
    notif_area.insert(1.0, ">> %s \n" % msg)


def clean_notifications():
    ''' Clean all notifications which are currently in notification area'''
    notif_area.delete(1.0, "end")


################################
# MAIN METHOD TO PROCESS SELECTED IMAGE
def start_processing(img_path):
    '''
    :param img_path: full path to the image
    '''
    def run_processing(img_path):
        # src_img_path = 'C:\\Users\\Leo\\Desktop\\project\\image.png'
        src_file_name = ntpath.basename(img_path)

        # TODO: Converting any image to *.PNG image
        # TODO: Show initial image, and processed image

        # Check existence for given file
        if os.path.isfile(img_path):
            # Make a copy of selected file + rename it to png
            tgt_img = os.path.join(temp_dir, "input_img.png")
            copyfile(img_path, tgt_img)

            # Start processing image in another program to get svg_file (stippled image)
            svg_file = os.path.join(temp_dir, "output.svg")
            command = "%s %s %s" % (os.path.join(current_dir, "voronoi.exe"), tgt_img, svg_file)

            add_notif("Running \"Weighted Voronoi Stippling\" algorithm to get points from image")

            # Create a new process to fetch points from given image
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()
            process_output = "".join([line for line in process.stdout])

            if "Completed" in process_output:
                add_notif("Image successfully processed through \"Weighted Voronoi Stippling\"")
            # Show error
            else:
                print process_output
                show_error(process_output)
                return
        else:
            show_error("File doesn't exist")
            return

        ################################
        # Parse all points
        tree = ElementTree.parse(svg_file)
        root_tree = tree.getroot()

        # Points is dict where key is node_id, value - tuple with coordinates (x, y)
        points, id = {}, 1

        # Iterate over all attributes to fetch needed info
        for el in root_tree:
            if "circle" in el.tag:
                attr = el.attrib
                x, y, radius = attr['cx'], attr['cy'], attr['r']
                points[id] = (x, y)  # save points as tuple

                id += 1

        ################################
        # Save points in temporary file
        file_points = os.path.join(temp_dir, "target_tsp_task.tsp")
        with open(file_points, "w") as f:
            # Header
            f.write("NAME:TSP_TASK"
                    "\nTYPE:TSP"
                    "\nDIMENSION:%s"
                    "\nEDGE_WEIGHT_TYPE:EUC_2D"
                    "\nNODE_COORD_TYPE:TWOD_COORDS"
                    "\nNODE_COORD_SECTION:\n" % len(points))

            # Main info - about points
            info = "\n".join(["%s %s %s" % (id, x, y) for id, (x, y) in points.items()])
            f.write(info)

            # Footer
            f.write("\nEOF")

        add_notif("TSP target task (with points from image) was successfully saved")

        ################################
        add_notif("Run Lin-Kernighan heuristic in separate process")

        # Create a new process to run Lin-Kernighan heuristic
        lkh_exe = os.path.join(current_dir, "lkh.exe")
        lkh_params_file = os.path.join(current_dir, "lkh_params.txt")

        process = subprocess.Popen([lkh_exe, lkh_params_file], shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)

        try:
            while True:
                from_program = process.stdout.readline()  # Read custom amount of output
                print from_program.strip()

                # If we found "Time.max" in the line, then the app finished its work, exit
                if "Time.max" in from_program:
                    to_program = "terminate"
                    process.stdin.write(to_program)
                    break

                # Do timeout of 0.1 second on each iteration
                time.sleep(0.1)
            process.wait()
        except IOError as e:
            print "error: %s" % e

        add_notif("Lin-Kernighan heuristic completed processing")

        ################################
        add_notif("Read the tour from solved.tsp file")

        solved_tsp_file = os.path.join(temp_dir, "solved.tsp")
        with open(solved_tsp_file, "r") as f:
            # skip unnecessary lines
            lines = f.readlines()
            previous_id = None

            # Read all points except header and "EOF" i the footer
            for line in lines[6:-1]:
                # Current node id
                current_id = abs(int(line))

                if previous_id:
                    # Connect previous node to current node
                    (x1, y1), (x2, y2) = points[previous_id], points[current_id]
                    line = '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:black; stroke-width:2px"/>' % (
                    x1, y1, x2, y2)

                    # Add new connection (line) in the SVG file
                    el = ElementTree.fromstring(line)
                    root_tree.append(el)

                previous_id = current_id

        add_notif("Points were read successfully")

        ################################
        add_notif("Prepare to save a new tour as final SVG file...")

        # Represent root tree to string to clean namespaces
        tree_str = ElementTree.tostring(root_tree)
        # Clean namespaces to avoid problems with drawing lines && points
        tree_str = tree_str.replace("ns0:", "").replace(":ns0", "")

        # Update existing tree with fixed markup
        root_tree = ElementTree.fromstring(tree_str)
        tree = ElementTree.ElementTree(root_tree)

        ################################
        # Save final svg file with a tour
        final_tour_svg = os.path.join(temp_dir, "final_tour.svg")
        tree.write(final_tour_svg)

        add_notif("New tour was saved successfully as SVG file (final_tour.svg)")
        return True

    # Capture the result of processing image
    result = run_processing(img_path)

    if result:
        add_notif("Image processing finished successfully")
    else:
        add_notif("Error occurred while program tried to process image")

    # Unblock "select image" and "start processing" buttons
    select_img_b.config(state=NORMAL)
    start_b.config(state=NORMAL)


################################
# Handlers for buttons
def on_file_selected():
    global selected_img_path

    # Ask user where is image located
    img_path = tkFileDialog.askopenfilename()
    if img_path:
        selected_img_path = img_path

        clean_notifications()
        add_notif("Selected path to image: \n  %s" % selected_img_path)
    else:
        selected_img_path = None


def on_start_processing():
    if not selected_img_path:
        show_error("You didn't select image")
        return

    # Clean previous notifications before running the image processing
    clean_notifications()

    add_notif("Selected path to image: \n  %s" % selected_img_path)

    # Block "select img" and "start" buttons until process will be finished
    select_img_b.config(state=DISABLED)
    start_b.config(state=DISABLED)

    # RUN MAIN PART OF APP TO PROCESS IMAGE
    add_notif("Processing has been started")

    # Run processing in separate Thread
    Thread(target=start_processing, args=(selected_img_path,)).start()


################################
# Main program window
root = Tk()
root.geometry("650x300")

leftFrame = Frame(root)
centerFrame = Frame(root)
# rightFrame = Frame(root)

# Buttons
select_img_b = Button(leftFrame, text='Select image', command=on_file_selected)
start_b = Button(leftFrame, text='Start processing', command=on_start_processing)
exit_b = Button(leftFrame, text='Exit Program', command=root.destroy)

select_img_b.pack(pady=(20, 0))
start_b.pack(pady=10)
exit_b.pack()

# Center area
Label(centerFrame, text="Notification area").pack(pady=5)
notif_area = ScrolledText(centerFrame, width=60, height=15)
notif_area.pack()

# Fix left and right sides
leftFrame.grid(row=0, column=0, padx=10)
centerFrame.grid(row=0, column=1, pady=(10, 0))

root.mainloop()
