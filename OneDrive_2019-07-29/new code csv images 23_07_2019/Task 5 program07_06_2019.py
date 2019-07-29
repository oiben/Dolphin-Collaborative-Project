import csv
from tkinter import *
from tkinter import messagebox

import os

data_csv = []

with open('data.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        data_csv.append(row)
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        line_count += 1
    print(f'Processed {line_count} lines.')

def types_for_column(column, data):
    types = []
    for row in data:
        if row[column] not in types:
            types.append(row[column])
    return types
    #returns a list of every unique value in the given column (e.g. every common name, or every year that has atleast 1 sighting)

def from_id(id):
    text = ""
    for column in data_csv[id]:
        text += (column + ": " + data_csv[id][column] + "\n")
    return text        
    #return data from one row of the csv (ID: 2, Common name: "Bottlenose Dolphin - common", etc)

def how_many_year_species(year, species, data):
    sightings = 0
    individuals = 0
    dolphins_list = []
    #this list will have all of the filtered entries
    for row in data:
        if year != "" and year != "All years":
            #if there is a year input
            if row["Year observed"] == year:
                if species != "" and species!= "All species":
                    #if there is also a species input
                    if row["Common name"] == species:
                        sightings += 1
                        individuals += int(row["Total individuals"])
                        dolphins_list.append(row)
                else:
                    #if there is a year inpput but no species input
                    sightings += 1
                    individuals += int(row["Total individuals"])
                    dolphins_list.append(row)
        elif species != "" and species != "All species":
            #if there is no year input but there is a species input
            if row["Common name"] == species:
                sightings += 1
                individuals += int(row["Total individuals"])
                dolphins_list.append(row)
        else:
            sightings += 1
            individuals += int(row["Total individuals"])
            dolphins_list = data_csv
    return [sightings, individuals, dolphins_list]
#returns number of individuals sighted of a specific species from a specific year. year or species can be left blank so only one is used
#prints out values but also returns a list of [sightings, individuals] for use in other functions
#e.g. 8 "Common dolphin - Short-beaked" sighted in 1999
#e.g. 1997 total "Common dolphin - Short-beaked" (for all years)
#e.g. 335 total dolphins sighted in 1999 (all species)

def sort_by_individuals(column, data):
    types_dict = {}
    # column : [number of individuals, number of sightings]
    types_list = []
    #[number of individuals, number of sightings, column]
    names = types_for_column(column, data)
    #names is a list of all common names in the csv
    for name in names:
        types_dict[name] = [0, 0]
    #setting up the dictionary with the keys as common names
    for row in data:
        types_dict[row[column]] = [int(types_dict[row[column]][0]) + int(row["Total individuals"]), int(types_dict[row[column]][1]) + 1]
#going through every line in the csv and updating the dictionary values with [total individuals, number of sightings] as a list
    for key in types_dict:
        types_list.append([types_dict[key][0], types_dict[key][1], key])
        #filling a list that can be sorted
    types_list.sort(reverse = True)
    text = ""
    for i in types_list:
        text += (i[2] + ": " + str(i[0]) + " individuals, " + str(i[1]) + " entries\n")
    return text
#print all unique values from (column) sorted by total individuals
#e.g. for every species in the csv print "(species) has (number) total individuals"

def dist(x1, y1, x2, y2):
    distance = (abs(float(x1) - float(x2))**2 + abs(float(y1) - float(y2))**2)**0.5
    return distance
#distance function: find the distance between two coordiante points (latitude and longitude)

def dist_two_ids(id1, id2):
    x1 = data_csv[id1]["Latitude"]
    y1 = data_csv[id1]["Longitude"]
    x2 = data_csv[id2]["Latitude"]
    y2 = data_csv[id2]["Longitude"]
    return dist(x1, y1, x2, y2)
#returns the distance between two sightings

def circle(centrex, centrey, radius):
    individuals = 0
    sightings = 0
    dolphins_list = []
    for row in data_csv:
        x1 = row["Longitude"]
        y1 = row["Latitude"]
        if dist(x1, y1, centrey, centrex) <= radius:
            individuals += int(row["Total individuals"])
            sightings += 1
            dolphins_list.append(row)
    return [dolphins_list, individuals, sightings]
#return the number of dolphins sighted with coordinates within a circle of centre(centrex, centrey) and radius
#if the distance between a sighitng and the centre of the circle is less than the radius then that sighting is within the circle

def rectangle(x1, y1, length, width):
    individuals = 0
    sightings = 0
    for i in data_csv:
        y2 = float(i["Longitude"])
        x2 = float(i["Latitude"])
        if (x2 >= x1 and x2 <= (x1 + width)) and (y2 <= y1 and y2 >= (y1 + length)):
            individuals += int(i["Total individuals"])
            sightings += 1
    print(str(individuals) + " individuals, " + str(sightings) + " sightings")

def circle_filter(centrex, centrey, radius, year, species):
    if radius != "" and centrex != "" and centrey != "":
        dolphin_list = circle(centrex, centrey, radius)
    else:
        dolphin_list = data_csv
    #the circle function is used to fill this list with all the sightings within a specified circle
    filtered_list = how_many_year_species(year, species, dolphin_list)[2]
    #the how_many_year_species function is used to filter the first list into this one
    individuals = 0
    for row in filtered_list:
        individuals += int(row["Total individuals"])
    sightings = len(filtered_list)

    return [sightings, individuals, filtered_list]


def submit_main():
    output_list_box.delete(0, END)
    output_list_box.insert(END, "Totals")
    output_filtered_list = circle_filter(tkvar_circlex.get(), tkvar_circley.get(), tkvar_radius.get(), tkvar_year.get(), tkvar_name.get())[2]
    for i in output_filtered_list:
        output_list_box.insert(END, i["ID"])

def submit_circle(x, y, radius):
    variables_text = "X: " + x + ", Y: " + y + ", Radius: " + radius
    lbl_variables = Label(window, text=variables_text)
    lbl_variables.grid(row=2, column=0, sticky=W)

def btn_output_go():
    output.delete('0.0', END)
    if output_list_box.get(ACTIVE) == "Totals":
        output_totals = [circle_filter(tkvar_circlex.get(), tkvar_circley.get(), tkvar_radius.get(), tkvar_year.get(), tkvar_name.get())[0], circle_filter(tkvar_circlex.get(), tkvar_circley.get(), tkvar_radius.get(), tkvar_year.get(), tkvar_name.get())[1]]
        output_filtered_list = circle_filter(tkvar_circlex.get(), tkvar_circley.get(), tkvar_radius.get(), tkvar_year.get(), tkvar_name.get())[2]
        output.insert(END, "In " + str(output_totals[0]) + " sightings there where " + str(output_totals[1]) + " individuals sighted\n")
        text = sort_by_individuals(tkvar_sort.get(), output_filtered_list)
        output.insert(END, text)
    else:
        text = (from_id(int(output_list_box.get(ACTIVE))))
        output.insert(END, text)

####Main:
window = Tk()
window.title("Dolphins")
window.configure(bg="black")

#Frames
mapframe = Frame(window)
mapframe.grid(rowspan = 2, row=0, column=0)
optionsframe = Frame(window)
optionsframe.grid(row=0, column=1)
thumbsframe = Frame(window)
thumbsframe.grid(column=1, row=1, sticky=E)

#circle and rectangle tkvars
tkvar_circlex = StringVar(window)
tkvar_circley = StringVar(window)
tkvar_radius = StringVar(window)

# Create a Tkinter variable
tkvar_name = StringVar(window)
tkvar_data = StringVar(window)
tkvar_year1 = StringVar(window)
tkvar_year2 = StringVar(window)

#options for menus
names_menu_list = types_for_column("Common name", data_csv)
names_menu_list.append("All species")
tkvar_name.set('All species') # set the default option

data_menu_list = { 'All sightings':data_csv, 'Circle':circle_filter}
tkvar_data.set('All sightings')

#show sightings after and from this year
year_menu_list1 = types_for_column("Year observed", data_csv)
year_menu_list1.append("All years")
year_menu_list1.sort()
tkvar_year1.set("All years")

#show sighitngs before
year_menu_list2 = types_for_column("Year observed", data_csv)
year_menu_list2.append("All years")
year_menu_list2.sort()
tkvar_year2.set("All years")

#create dropdown menus
#name_menu = OptionMenu(optionsframe, tkvar_name, *names_menu_list)

#data_menu = OptionMenu(optionsframe, tkvar_data, *data_menu_list)

#year_menu1 = OptionMenu(optionsframe, tkvar_year1, *year_menu_list1)

#year_menu2 = OptionMenu(optionsframe, tkvar_year2, *year_menu_list2)

#place dropdown menus and text in the window
#Label(optionsframe, text="Show species: ").grid(row=1, column=0, sticky=W)
#name_menu.grid(row=1, column=1, sticky=W)
#Label(optionsframe, text="between years: ").grid(row=2, column=0, sticky=W)
#year_menu1.grid(row=2, column=1, sticky=W)
#Label(optionsframe, text="and ").grid(row=2, column=2, sticky=W)
#year_menu2.grid(row=2, column=3, sticky=W)

# on change name dropdown value
def change_name_dropdown(*args):
    print( tkvar_name.get() )

#change data dropdown value
def change_data_dropdown(*args):
    selection = tkvar_data.get()
    if selection == "Circle":
        #create window with title "Circle Parameters"
        circle_window = Toplevel(window)
        circle_window.title("Circle Parameters")
        #create subtitle label
        Label(circle_window, text="Center Coordinates and Radius of Circle: ").pack()
        #entry box for centre x coord
        entry_xcoord = Entry(circle_window)
        entry_xcoord.insert(END, 'Centre X coordinate')
        entry_xcoord.pack()
        #entry box for centre y coord
        entry_ycoord = Entry(circle_window)
        entry_ycoord.insert(END, 'Centre Y coordinate')
        entry_ycoord.pack()
        #entry box for radius
        entry_radius = Entry(circle_window)
        entry_radius.insert(END, 'Radius')
        entry_radius.pack()
        #tkars for x, y, and radius
        tkvar_circlex.set("")
        tkvar_circley.set("")
        tkvar_radius.set("")
        #submit button
        Button(circle_window, text="SUBMIT", width=6,
               command= lambda: submit_circle(entry_xcoord.get(), entry_ycoord.get(), entry_radius.get())) .pack()
    elif selection == "Rectangle":
        rectangle_window = Toplevel(window)
        rectangle_window.title(window)

# link function to change dropdown
tkvar_name.trace('w', change_name_dropdown)
tkvar_data.trace('w', change_data_dropdown)

####submit button:
#Button(optionsframe, text="SUBMIT", width=6, command=submit_main) .grid(row=1, column=6, sticky=W)

folder = "thumbnails"
#folder two use for thumbnails

row_length = 2
#how many thumbnails in each row (four images with row length two is two rows of 2 images)

#dolphin thumbnails
thumbs = os.listdir(folder)
photoimages = []
#pics is a dictionary of the names of image_name.gif: PhotoImage_name

for i in thumbs:
    image = PhotoImage(file= folder + "/" + i)
    photoimages.append(image)

#map images
maps = os.listdir("map_images")
mapimages = {}

for i in maps:
    i = i.lower()
    image = PhotoImage(file= "map_images/" + i)
    mapimages[i] = image
print(mapimages)
    

lbl_selection = Label(optionsframe, text = "empty")
lbl_selection.grid(row=3)

def dolphin_func(dolphin):
    print(dolphin)
    lbl_selection.config(text=dolphin)
    lbl_map.config(image=mapimages[dolphin])

def create_dolphin_btn(dolphin, v, column):
    row = v% row_length + 1
    print(dolphin + "  " + str(column) + "  " + str(row))
    Button(thumbsframe, image = photoimages[v],
                     command = lambda: dolphin_func(dolphin)).grid(row=column, column=row)
    Label(thumbsframe, text=dolphin[:-4]).grid(row=column, column=row, sticky=S)

v = 0
column=0
for image in thumbs:
    if v % row_length == 0 and v != 0:
        column += 1
    
    create_dolphin_btn(image, v, column)
    v +=1

#Button code
selectedspecies = 0

def dolphin_func(dolphin):
    global selectedspecies
    selectedspecies = dolphin[:-4]
    print(selectedspecies)
    lbl_selection.config(text=dolphin)
    lbl_map.config(image=mapimages[dolphin])

def openWindow():
    top = Toplevel()
    top.title("More Info")
    top.geometry("500x500")
    print(selectedspecies)
    if selectedspecies == "bottlenose":
        Label(top, text = "Bottlenose Facts:").grid(sticky = "w")
        Label(top, text = "They don't user their teeth to chew food but instead swallow thier meal whole.").grid(sticky = "w")
        Label(top, text = "They have estimated lifespan of up to 40 years.").grid(sticky = "w")
        Label(top, text = "They use a echolocation to find food and navigate. ").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Bottlenose Stats:").grid(sticky = "w")
        Label(top, text = "They typically weigh between 150-600kg.").grid(sticky = "w")
        Label(top, text = "They have a length of 2-4m.").grid(sticky = "w")
        Label(top, text = "They have a speed of up to 30km/hr.").grid(sticky = "w")
        Label(top, text = "Can dive 300m below the waters surface.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of typical fish such as squid or crustaceans.").grid(sticky = "w")
    elif selectedspecies == "striped":
        Label(top, text = "Striped Facts:").grid(sticky = "w")
        Label(top, text = "They have an estimated lifespan of up 58 years.").grid(sticky = "w")
        Label(top, text = "They can be found in cohesive groups of about 25 - 100 dolphins that can leap up to 20 feet above the water surface.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Striped Stats:").grid(sticky = "w")
        Label(top, text = "They have a length of 2-3m.").grid(sticky = "w")
        Label(top, text = "They typically weigh between 160kg.").grid(sticky = "w")
        Label(top, text = "They have a speed of up to 60km/hr.").grid(sticky = "w")
        Label(top, text = "Can dive 400-700m below the waters surface.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of herring, pilchard, anchovies, hake, sardines, bonito, squid, octopus and sauries.").grid(sticky = "w")
    elif selectedspecies == "dusky":
        Label(top, text = "Dusky Facts:").grid(sticky = "w")
        Label(top, text = "They have an estimated lifespan of up to 20 to 25 years.").grid(sticky = "w")
        Label(top, text = "They can be found mainly in coastal waters in the Southern Hemisphere.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Dusky Stats:").grid(sticky = "w")
        Label(top, text = "They have a length of 2-2.5m.").grid(sticky = "w")
        Label(top, text = "They typically weigh around 100kg.").grid(sticky = "w")
        Label(top, text = "They have a speed of 37km/hr.").grid(sticky = "w")
        Label(top, text = "Can dive 150m below the waters surface.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of anchovies, lantern fish, pilchards, sculpins, hakes, horse mackerel, hoki and red cod.").grid(sticky = "w")
    elif selectedspecies == "hourglass":
        Label(top, text = "Hourglass Facts:").grid(sticky = "w")
        Label(top, text = "They have an estimated life span of up to 27 years old.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Hourglass Stats:").grid(sticky = "w")
        Label(top, text = "Length of 1.8m (5-6 feet).").grid(sticky = "w")
        Label(top, text = "They weigh up to 110kg.").grid(sticky = "w")
        Label(top, text = "They have swimming speeds of up to 22 km/h. ").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of fish, squid, crustacean and other surface-dwelling fish.").grid(sticky = "w")
    elif selectedspecies == "rissos":
        Label(top, text = "Rissos Facts:").grid(sticky = "w")
        Label(top, text = "They have estimated lifespan of up to 20 – 30 years.").grid(sticky = "w")
        Label(top, text = "They have circular shaped body with no beak and a blunt head.").grid(sticky = "w")
        Label(top, text = "Identifiable by their unique fins.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Rissos Stats:").grid(sticky = "w")
        Label(top, text = "They weight on average 390kg.").grid(sticky = "w")
        Label(top, text = "Length of average 3m but some individuals reach up to 4.3m (13.12 feet).").grid(sticky = "w")
        Label(top, text = "Swim slowly but they are very active in travelling.").grid(sticky = "w")
        Label(top, text = "Able to dive to depths of up to 1000m.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of fish, crustaceans (such as krill) and cephalopods (such as squid, octopus, and cuttlefish).").grid(sticky = "w")
    elif selectedspecies == "shortbeaked":
        Label(top, text = "Shortbeaked Facts:").grid(sticky = "w")
        Label(top, text = "They have estimated lifespan of up to 35 year.").grid(sticky = "w")
        Label(top, text = "Can be found along the continental slope in waters 650 to 6,500 feet deep.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Shortbeaked Stats:").grid(sticky = "w")
        Label(top, text = "An average of 1.5 - 2.4m length.").grid(sticky = "w")
        Label(top, text = "An average of 100 – 140kg mass ").grid(sticky = "w")
        Label(top, text = "Swim in warm waters at up to 60 km.").grid(sticky = "w")
        Label(top, text = "Can dive up to depths of 400–700 meters.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of small fish such as herring, pilchard, anchovies, hake, sardines, bonito, sauries, squid and octopus.").grid(sticky = "w")
    elif selectedspecies == "southern":
        Label(top, text = "Southern Facts:").grid(sticky = "w")
        Label(top, text = "Have estimated lifespan of up to 42 years.").grid(sticky = "w")
        Label(top, text = "Can be found in cool waters of the Southern Hemisphere.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Southern Stats:").grid(sticky = "w")
        Label(top, text = "Average of 1.8 - 2.9m in length.").grid(sticky = "w")
        Label(top, text = "Average of 60 – 100kg").grid(sticky = "w")
        Label(top, text = "Can swim up to 25 km/hr.").grid(sticky = "w")
        Label(top, text = "Can Dive up to 200m in depth.").grid(sticky = "w")
        Label(top, text = "").grid(sticky = "w")
        Label(top, text = "Their diet consists of crustaceans, squid and species of myctophids.").grid(sticky = "w")
    else:
        messagebox.showerror("Error", "No dolphin selected")
        top.destroy()

#Button for the 'Extra Info' window
windowButton = Button(optionsframe, text = "Extra Info", command = openWindow)
windowButton.grid(row = 2, column = 6, sticky = W)

mapimage = PhotoImage(file="map_images/TasAll.PNG")
lbl_map = Label(mapframe, image=mapimage)
lbl_map.grid(row=0, column=0)

####Loop window:
window.mainloop()


