# -*- coding: utf-8 -*-
import subprocess
import time
import ntpath
import tkMessageBox
import tkFileDialog
import os
import matplotlib.pyplot as plt
import networkx as nx
import operator
from Tkinter import Tk, Button, DISABLED, NORMAL
from shutil import copyfile
from xml.etree import ElementTree


# Constants
selected_img_path = None

current_dir = os.path.abspath(os.path.dirname(__file__))
current_dir = current_dir.decode('cp1251').encode("utf-8")
# Directory where we store files while process them
temp_dir = os.path.join(current_dir, "tmp")


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


src_img_path = 'C:\\Users\\Leo\\Desktop\\project\\image.png'
src_file_name = ntpath.basename(src_img_path)

# Check existence for given file
if os.path.isfile(src_img_path) and False:
    # Make a copy of selected file + rename it to png
    tgt_img = os.path.join(temp_dir, "input_img.png")
    copyfile(src_img_path, tgt_img)

    # Start processing image in another program to get svg_file
    svg_file = os.path.join(temp_dir, "output.svg")
    command = "%s %s %s" % (os.path.join(current_dir, "voronoi.exe"), tgt_img, svg_file)

    # Create a new process to fetch points from given image
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    process_output = "".join([line for line in process.stdout])

    if "Completed" in process_output:
        print "Image successfully processed"
    # Show error
    else:
        print process_output
else:
    print "File doesn't exist"
    # return


svg_file = "C:\\Users\\Leo\\Desktop\\project\\tmp\\output.svg"

# Create undirected graph
g = nx.Graph()

################################
# Parse all points
tree = ElementTree.parse(svg_file)
points, id = [], 1

# Iterate over all attributes to fetch needed info
for el in tree.getroot():
    if "circle" in el.tag:
        attr = el.attrib
        x, y, radius = attr['cx'], attr['cy'], attr['r']
        points.append((id, x, y))  # save points as tuple

        # Add new node to the graph
        g.add_node(id, pos=(x, y), radius=radius)

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
    info = "\n".join(["%s %s %s" % (id, x, y) for (id, x, y) in points])
    f.write(info)

    # Footer
    f.write("\nEOF")
print "TSP target task (with points from image) was successfully saved"

################################
print "Run Lin-Kernighan heuristic"

# Create a new process to run Lin-Kernighan heuristic
lkh_exe = os.path.join(current_dir, "lkh.exe")
lkh_params_file = os.path.join(current_dir, "lkh_params.txt")


# status = subprocess.check_output(["cmd", cmd], shell=use_shell)
# s = subprocess.check_output(
#      ["cmd", "ls non_existent_file; exit 0"],
#      stderr=subprocess.STDOUT,
#      shell=True)
# print s

if False:
    process = subprocess.Popen([lkh_exe, lkh_params_file], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

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

################################
print "Read the tour from solved.tsp file"

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
            g.add_edge(previous_id, current_id)

print "Points were read successfully"

################################
print "Prepare to draw the tour..."
# Define the radius for nodes
node_sizes, node_list = [], []
for node_id, radius in nx.get_node_attributes(g, 'radius').items():
    node_list.append(node_id)
    node_sizes.append(radius * 30000)

# Plot the graph (coords are fixed)
fixed_positions = {node_id: (float(x), float(y)) for (node_id, (x, y)) in nx.get_node_attributes(g, 'pos').items()}
fixed_nodes = fixed_positions.keys()

pos = nx.spring_layout(g, pos=fixed_positions, fixed=fixed_nodes)
# nx.draw_networkx_labels(g, pos)

nx.draw(g, pos, with_labels=True, nodelist=node_list, node_size=node_sizes)
print "Drawing the tour..."
plt.show()
