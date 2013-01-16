from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
import flood as fl
import pickle
import math

# mode of operation constants
TERRAIN = 1
LANDCOSTS = 2
FLOODING = 3

# default map
t = [[ 0, 0, 0, 0, 0, 0, 0, 0 ,0, 0  ],
                [ 0, 0, 0, 0, 0, 0, 0, 0 ,0,0 ],
                [ 0, 0, 2, 2, 2, 2, 2, 2 ,0,0 ],
                [ 0, 0, 2, 2, 2, 2, 2, 2 ,0,0],
                [ 0, 0, 2, 2, 0, 0, 2, 2 ,0,0 ],
                [ 0, 0, 2, 2, 0, 0, 2, 2 ,0,0 ],
                [ 0, 0, 2, 2, 2, 2, 2, 2 ,0,0 ],
                [ 0, 0, 2, 2, 2, 2, 2, 2 ,0,0 ],
                [ 0, 0, 0, 0, 0, 0, 0, 0 ,0,0 ],
                [ 0, 0, 0, 0, 0, 0, 0, 0 ,0,0 ],]

land=fl.Landmap(t)
edit_mode = TERRAIN
dim=4

# pads the string s with zeros from left to get length l,
# if longer than l returns a string of length l full of 'f'
def _pad_zeros(s,l):
    dif=l-len(s)
    if(dif>0):
        s= ("0"*dif)+s
    if(dif<0):
        return "f"*l
    return s
        
# converts the int i to a TK hexadecimal color string of l characters
# per channel
def _tk_hex_str(i,l=2):
    try:
        len(i)
    except:
        s=_pad_zeros(hex(int(i))[2:],l)
        return "#"+s+s+s
    ret="#"
    for j in range(len(i)):
        ret+=_pad_zeros(hex(int(i[j]))[2:],l)
    return ret

# gets colour of a tile - brighter means higher value, terr_value creates
# a blueish hue to indicate the tarrain underneath
def _get_col(value,max_value,terr_value):
    if(max_value==0):
        k=0
    else:
        k = int(255/max_value)
    return _tk_hex_str([value*k,value*k,int(math.log(terr_value+1)*100)])

# paints map1 to the canvas, using mmap as background terrain
def paintmap(map1,mmap):
    global land
    y=0
    for i in range(0,len(map1)):
        x=0
        for j in range(0,len(map1[0])):
            try:
                v=map1[i][j][0]
            except:
                v=map1[i][j]
            col = _get_col(v,mmap,land.terrain[i][j])
            canvas.create_rectangle((x,y,x+dim-1,y+dim-1), fill=col,outline="#999")
            x+=dim
        y+=dim

# paints the map in terrain (editing) mode
def paint_terr():
    global edit_mode
    a=canvas.find_all()
    for each in a:
        canvas.delete(each)
    paintmap(land.terrain,land.max_terrain)
    edit_mode = TERRAIN
    status_txt.set("Terrain")
    Lterrain["state"]=NORMAL

# paints the map in landcosts mode
def paint_cost():
    a=canvas.find_all()
    for each in a:
        canvas.delete(each)
        
    global edit_mode,status_txt
    if(len(land.landcosts)==0): # landcosts are empty, count them now
        status_txt.set("counting landcosts")
        land.count_landcosts()
    paintmap(land.landcosts,land.max_landcosts)
    edit_mode=LANDCOSTS
    status_txt.set("Land costs")
    Lterrain["state"]=DISABLED

# paints the map in flooding mode
def paint_floo(mode=2):
    global root,land,edit_mode,status_txt
    
    a=canvas.find_all()
    for each in a:
        canvas.delete(each)
        
    if(len(land.landcosts)==0): # landcosts are empty, count them now
        status_txt.set("counting landcosts")
        land.count_landcosts()    
    
    if(len(land.flooding)==0): # landcosts are empty, count them now
        land.count_flooding_init(TRUE,mode)
        st=0
        stack_len=1
        while(stack_len>0):
            stack_len=land.count_flooding_step()
            st+=1
            if(st>=5000):
                st=0
                status_txt.set(repr(stack_len))
                root.update()
    print("flooding counted")                
    paintmap(land.flooding,land.max_flooding)
    edit_mode=FLOODING
    status_txt.set("Flooding")
    Lterrain["state"]=DISABLED

# convert map indices to canvas coordinates
def _apply_dim(coords,dim):
    for coord in coords:
        h=coord[0]*dim+dim/2
        coord[0]=coord[1]*dim+dim/2
        coord[1]=h

# handle mouse input
def xy(event):
    global canvas,land,status_txt
    i=int(canvas.canvasy(event.y)/dim)
    j=int(canvas.canvasx(event.x)/dim)
    print(land.terrain[i][j])

    if(edit_mode==FLOODING): # paint path to selected tile
        start=[i,j]
        coords=[]
        end=[land.flooding[i][j][1],land.flooding[i][j][2]]
        while((start!=end)): # prepare path coordinates
            coords.append(start)
            start=list(end)
            ii,jj=start[0],start[1]
            end=[land.flooding[ii][jj][1],land.flooding[ii][jj][2]]
        coords.append(end)
        _apply_dim(coords,dim)
        canvas.create_line(coords[:],fill="red")
        return

    if(edit_mode==TERRAIN): # edit selected tile
        if(land.terrain[i][j]!=land.base_terrain):
            land.terrain[i][j]=land.base_terrain
        else:
            lv=int(Lterrain.curselection()[0])
            print(lv)
            if(lv>1):
                lv=lv*10
            land.terrain[i][j]=lv
        paint_terr()
        land.reset_landcosts()
        land.reset_flooding()

def xy_right(event):
    global canvas,land,status_txt
    i=int(canvas.canvasy(event.y)/dim)
    j=int(canvas.canvasx(event.x)/dim)
    print(land.terrain[i][j])
    # give info on selected tile
    s="[T: "+repr(land.terrain[i][j])
    if(len(land.landcosts)>0):
        s+=" C: "+repr(land.landcosts[i][j])
    if(len(land.flooding)>0):
        s+=" F: "+repr(land.flooding[i][j][0])
    s+="]"
    status_txt.set(s)
    

# new map dialog window
    
class NewDialog(simpledialog.Dialog):
    def body(self,master):
        self.b_landcost = IntVar()
        self.top = Frame(master)
        self.top.grid()
        
        self.lab = Label(self.top,text="Set dimensions")
        self.lab.grid(row=0,column=0,columnspan=2)

        self.labX = Label(self.top,text="X cells")
        self.labX.grid(row=1,column=0)
        okayCommand = self.top.register(self.is_string_okay)
        self.enX = Entry(self.top,validate="key",validatecommand = (okayCommand,"%P"))
        self.enX.grid(row=1,column=1)
        self.enX.insert(0,"10")
        self.labY = Label(self.top,text="Y cells")
        self.labY.grid(row=2,column=0)
        self.enY = Entry(self.top,validate="key",validatecommand = (okayCommand,"%P"))
        self.enY.grid(row=2,column=1)
        self.enY.insert(0,"10")

        self.chB = Checkbutton(self.top,text="0 base landcost",onvalue=0,offvalue=1,variable=self.b_landcost)
        self.chB.grid(row=3,column=0)
        self.chB.select()
        return self.enX

# check whether string is an whole number    
    def is_string_okay(self,str):
        try:
            int(str)
        except:
            return False
        return True

    def apply(self):
        self.result=[int(self.enX.get()),int(self.enY.get()),self.b_landcost.get()]

# clear terrain and make new one
def new_terr():
    global root,terr,mterr
    r = NewDialog(root).result
    
    if(r==None):
        return
    
    land.new_terrain(r[0],r[1],r[2])
        
    resize_canvas()
    paint_terr()
    edit_mode=TERRAIN

# load terrain from file        
def open_file():
    global root,terr
    file = filedialog.askopenfile(parent=root,mode='rb',title='Choose a file')
    if file != None:
        terr = pickle.load(file)
        file.close()
        paint_terr()
        reset_cost()
        reset_floo()

# save terrain to file
def save_file():
    global root
    fname = filedialog.asksaveasfilename(parent=root,title='Save terrain as')
    file = open(fname,"wb")
    pickle.dump(terr,file)
    file.close()

# change canvas size (only when creating new terrain)        
def resize_canvas():
    global canvas,dim

    ylen=len(land.terrain[1])
    xlen=len(land.terrain[0])
    ydim=int(canvas.cget("height"))/ylen
    xdim=int(canvas.cget("width"))/xlen
    if(xdim>15):
        xdim=25
    if(ydim>15):
        ydim=25
    if(ydim<xdim):
        dim=ydim
    else:
        dim=xdim
    if(dim<15):
        dim=15
    canvas["scrollregion"]=(0,0,xlen*dim,ylen*dim)
    if(ylen*dim > 350):
        canvas["height"]=350
    else:
        canvas["height"]=ylen*dim
    canvas["width"]=xlen*dim
    canvas["bg"]="#999"
    root.minsize(int(canvas["width"])+100,int(canvas["height"])+40)

# prepare application window

root = Tk()
root.title("Flood GUI")
root.columnconfigure(0, weight=4)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

status_txt = StringVar()

# main menu

mb = Menu(root)
root["menu"]=mb
fmenu = Menu(mb,tearoff=0)
mb.add_cascade(label="File",menu=fmenu)
fmenu.add_command(label="New ...",command=new_terr)
fmenu.add_command(label="Open",command=open_file)
fmenu.add_command(label="Save as",command=save_file)

# drawing frame

drawframe = Frame(root)
hscroll = Scrollbar(drawframe,orient=HORIZONTAL)
vscroll = Scrollbar(drawframe,orient=VERTICAL)
canvas = Canvas(drawframe,yscrollcommand=vscroll.set,xscrollcommand=hscroll.set)
canvas.grid(column=0, row=1, columnspan=2,sticky=(N, W, E, S))
canvas.bind("<Button-1>", xy)
canvas.bind("<Button-3>", xy_right)
hscroll["command"]= canvas.xview
vscroll["command"]= canvas.yview
hscroll.grid(column=0, row=0, columnspan=2, sticky=(E,W))
vscroll.grid(column=2, row=1, sticky=(N,S))
status = Message(drawframe,textvariable=status_txt,justify=LEFT,width=100)
status.grid(column=0, row=2, columnspan=2, sticky=(W))
drawframe.grid(column=0, row=2, sticky=(N,E,S,W))

# controls frame

controlframe = Frame(root)
controlframe.grid(column=1,row=2, sticky=(N, W, S))
bterr = Button(controlframe,text="Terrain",command=paint_terr)
bterr.grid(sticky=(N,W,E))
bcost = Button(controlframe,text="Landcosts",command=paint_cost)
bcost.grid(sticky=(N,W,E))
bfloo_heu = Button(controlframe,text="Flooding",command=paint_floo)
bfloo_heu.grid(sticky=(N,W,E))

terrain_list = StringVar()
terrain_list.set("Terrain_0 Terrain_1 Wall_20")
Lterrain = Listbox(controlframe,listvariable=terrain_list)
Lterrain.grid()
print(Lterrain.size())

resize_canvas()
paintmap(land.terrain,land.max_terrain)

root.mainloop()
