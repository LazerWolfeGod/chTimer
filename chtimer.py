import pygame,math,random,sys,os,time,json,datetime
import PyUI as pyui
import CubeMesh as cm
pygame.init()
screenw = 1800
screenh = 1024
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()

ui.styleset(wallpapercol=(207,214,222),font='arialrounded',col=(100,117,147),textcol=(30,30,30),roundedcorners=2,textsize=30,windowedmenu_roundedcorners=10,clickdownsize=2)
#'ocraextended'
ui.addinbuiltimage('bg',pygame.image.load('assets\\background.png'))

def sectostr(sec,rounded=2):
    if type(sec) == str: return sec
    h = int(sec//3600)
    m = int(sec%3600//60)
    s = str(int(sec%60))
    ms = str(round(sec%1,rounded))[2:]
    if h == 0:
        if m == 0:
            return f'{s}.{ms:0>2}'
        return f'{m}:{s:0>2}.{ms:0>2}'
    return f'{h}:{m:0>2}:{s:0>2}.{ms:0>2}'
def timetodate(time,display=False):
    st = str(datetime.datetime.fromtimestamp(time))
    if display:
        st = st.replace('-','/')
        lis = st.split()[0].split('/')
        return f'{lis[2]}/{lis[1]}/{lis[0]}'
    else:
        return st.rsplit(':',1)[0]
        

class Timer:
    def __init__(self):
        timing = False
        displaytime = 0
        self.spacepressed = False
        self.timing = False
        self.juststopped = False
        self.readytostart = False
        self.load_json()
        self.makegui()

        
    def gameloop(self):
        if ui.kprs[pygame.K_SPACE]:
            if not self.spacepressed:
                self.spacepressed = True
                self.press_start()
        elif self.spacepressed:
            self.release_start()
            self.spacepressed = False
        if self.timing:
            self.timertext.timetracker = time.perf_counter()-self.start_time
            self.timertext.settext(sectostr(self.timertext.timetracker))
        elif self.spacepressed and not self.leftwindow.enabled and not self.readytostart:
            self.readytostart = True
            self.timertext.settextcol((0,225,0))
            self.timertext.settext(sectostr(0))
    def drawcubemesh(self):
        if self.cubemesh != -1:
            surf = pygame.Surface((self.cubemeshrect[0],self.cubemeshrect[1]))
            surf.fill((30,30,31))
            self.cubemesh.update(surf)
            surf.set_colorkey((30,30,31))
            ui.IDs['cube surf'].textimage = surf
        else:
            ui.IDs['cube surf'].textimage = pygame.Surface((0,0))

## GUI   
    def makegui(self):
        self.timertext = ui.maketext(0,0,sectostr(0),120,center=True,anchor=('w/2','h/2'),pregenerated=False,font='ocraextended')

        ui.maketext(0,0,'{bg}',screenh,center=True,anchor=('w/2','h/2'),layer=-10,colorkey=(207,214,222))

        self.leftwindow = ui.makewindow(0,0,400,'h',enabled=True,col=(27,215,220),animationtype='moveleft',backingdraw=False,bounditems=[

            ui.makedropdown(3,3,[a for a in self.alldata]+['Add Session'],30,command=self.change_session,width=400-6,startoptionindex=1,ID='session select'),

            ui.makescrollertable(3,47,[],['Solve','Time','AO5'],ID='timestable',pageheight='h-83',width=394,boxwidth=[108,-1,-1],font='arialrounded')
            ])

        self.session = ui.IDs['session select'].active
        self.refresh_times_table()


        ### time edit menu
        ui.makewindowedmenu(410,10,500,300,'time_edit_menu','main',isolated=True,ID='time_edit_menu')
        ui.maketext(10,5,'test',25,'time_edit_menu','time_edit_display',backingcol=ui.IDs['time_edit_menu'].col,maxwidth=480,refreshbind=['time_edit_menu'])
        ui.IDs['time_edit_menu'].setheight('ui.IDs["time_edit_display"].height+45')
        
        ui.makelabeledcheckbox(180,-35,'{+2 scale=0.8}',40,self.edit_time,'time_edit_menu',anchor=(0,'h'),backingcol=ui.IDs['time_edit_menu'].col,toggle=False,ID='time_edit_+2')
        ui.makelabeledcheckbox(320,-35,'{DNF scale=0.75}',40,self.edit_time,'time_edit_menu',anchor=(0,'h'),backingcol=ui.IDs['time_edit_menu'].col,toggle=False,ID='time_edit_DNF')
        ui.makebutton(-5,-5,'Delete',25,self.delete_time,'time_edit_menu',anchor=('w','h'),objanchor=('w','h'),col=(230,50,20),horizontalspacing=4,roundedcorners=7,verticalspacing=0)


        ### Cube Mesh Stuf
        self.cubemeshrect = (300,300)
        self.cubemesh = cm.Cube(self.cubemeshrect[0],self.cubemeshrect[1],ui,3)
        self.rightwindow = ui.makewindow(0,0,300,'h',enabled=True,col=(27,215,220),anchor=('w',0),objanchor=('w',0),animationtype='moveright',backingdraw=False,bounditems=[
            ui.maketext(-150,-310,'',ID='scramble text',anchor=('w','h'),objanchor=('w/2','h'),maxwidth=280,textcenter=True,textsize=40,command=self.cubemesh.replayscramble),
            ui.maketext(-300,-300,'',300,anchor=('w','h'),ID='cube surf')
            ])
        ui.IDs['scramble text'].settext(self.cubemesh.scramble())
        

    def refresh_times_table(self):
        data = []
        for i,a in enumerate(self.alldata[self.session]):
            data.insert(0,self.make_times_table_row(a,i))
        ui.IDs['timestable'].data = data
        ui.IDs['timestable'].refresh()
    def make_times_table_row(self,data,index):
        func = pyui.funcer(self.time_edit_menu,num=index+1)
        if data[4]: tim = 'DNF'
        else: tim = sectostr(data[0]+2*data[3])+'+'*data[3]
        return [ui.makebutton(0,0,index+1,command=func.func),tim,sectostr(self.AOX(self.alldata[self.session][index-4:index+1],5))]
        
        
    def time_edit_menu(self,num):
        ui.movemenu('time_edit_menu','down')
        self.editingtime = num-1
        self.refresh_time_edit_menu()
    def refresh_time_edit_menu(self):
        txt = f'{self.session} Solve\n'
        if self.alldata[self.session][self.editingtime][4]: txt+='Time: DNF'
        else: txt+= f'Time:{sectostr(self.alldata[self.session][self.editingtime][0]+2*self.alldata[self.session][self.editingtime][3],3)}'+'+'*self.alldata[self.session][self.editingtime][3]
        txt+= f'\nDate:{self.alldata[self.session][self.editingtime][1]}'
        st = ''
        for a in self.alldata[self.session][self.editingtime][2]:
            st+=a+' '
        txt+='\nScramble:'+st
        ui.IDs['time_edit_display'].settext(txt)
        ui.IDs['time_edit_menu'].setheight('ui.IDs["time_edit_display"].height+45')
        ui.IDs['time_edit_+2'].toggle = self.alldata[self.session][self.editingtime][3]
        ui.IDs['time_edit_DNF'].toggle = self.alldata[self.session][self.editingtime][4]
        
    def edit_time(self):
        self.alldata[self.session][self.editingtime][3] = ui.IDs['time_edit_+2'].toggle
        self.alldata[self.session][self.editingtime][4] = ui.IDs['time_edit_DNF'].toggle
        self.refresh_time_edit_menu()
        self.save_json()
        for i in range(self.editingtime,min(self.editingtime+5,len(self.alldata[self.session]))):
            ui.IDs['timestable'].row_replace(self.make_times_table_row(self.alldata[self.session][i],i),len(self.alldata[self.session])-i-1)
    def delete_time(self):
        del self.alldata[self.session][self.editingtime]
        self.save_json()
        self.refresh_times_table()
        ui.menuback()
            
#### Manage timer
    def press_start(self):
        if not self.timing:
            self.shut_menus()
            self.juststopped = False
            self.timertext.settextcol((255,0,0))
        else:
            info = [self.timertext.timetracker,timetodate(time.time()),ui.IDs['scramble text'].text.split(),False,False]
            self.alldata[self.session].append(info)
            self.save_json()
            self.readytostart = False
            self.juststopped = True
            self.timing = False
            self.open_menus()
            
            func = pyui.funcer(self.time_edit_menu,num=len(ui.IDs['timestable'].table))
            ui.IDs['timestable'].row_insert([ui.makebutton(0,0,len(ui.IDs['timestable'].table),command=func.func),sectostr(info[0]),sectostr(self.AOX([b[0] for b in self.alldata[self.session][-5:]],5))],0)

            ui.IDs['scramble text'].settext(self.cubemesh.scramble())
             
    def shut_menus(self):
        self.leftwindow.shut()
        self.rightwindow.shut()
    def open_menus(self):
        self.leftwindow.open(toggleopen=False)
        self.rightwindow.open(toggleopen=False)
    def release_start(self):
        if not self.timing:
            if self.readytostart:
                if not self.juststopped:
                    self.timing = True
                    self.start_time = time.perf_counter()
            else:
                self.open_menus()
            self.timertext.settextcol((0,0,0))
            

### Tracking times
    def change_session(self):
        self.session = ui.IDs['session select'].active
        if self.session == 'Add Session':
            self.alldata[f'Session {len(ui.IDs["session select"].options)}'] = []
            self.save_json()
            new = [a for a in self.alldata]+['Add Session']
            ui.IDs['session select'].setoptions(new)
            ui.IDs['session select'].table.table[-2][0].press()
        else:
            self.refresh_times_table()
            try:
                n = int(self.session[0])
            except:
                n = -1
            textsizekey = [40,40,50,40,35,30,30,27,25,25,40]
            ui.IDs['scramble text'].settextsize(textsizekey[n])
            if n!=-1:
                self.cubemesh = cm.Cube(self.cubemeshrect[0],self.cubemeshrect[1],ui,n)
                
                ui.IDs['scramble text'].settext(self.cubemesh.scramble())
                ui.IDs['scramble text'].enabled = True
                ui.IDs['scramble text'].command = self.cubemesh.replayscramble
            else:
                self.cubemesh = -1
                ui.IDs['scramble text'].enabled = False



    def load_json(self):
        path = pyui.resourcepath('assets\\data.json')
        if not os.path.isfile(path):
             with open(path,'w') as f:
                 json.dump({a:[] for a in ['2x2','3x3','4x4','5x5','6x6','7x7','Piraminx','Skewb','Square 1']},f)

        with open(path,'r') as f:
            self.alldata = json.load(f)
    def save_json(self):
        path = pyui.resourcepath('assets\\data.json')
        with open(path,'w') as f:
            json.dump(self.alldata,f)


## Calculations
    def AOX(self,nums,X=-1):
        if len(nums)>0:
            if X==-1 or len(nums) == X:
                if type(nums[0]) == list:
                    new = []
                    for a in nums:
                        if a[4]: new.append('DNF')
                        else: new.append(a[0]+2*a[3])
                    nums = new
                if 'DNF' in nums: nums.remove('DNF')
                else: nums.remove(max(nums))
                if 'DNF' in nums: return 'DNF'
                nums.remove(min(nums))
                return sum(nums)/len(nums)
        return '-'

    def makescramble(self,length=20):
        basics = ['R','L','U','F','D','B']
        moves = [a for a in self.movemap if a[0] in basics]
        scramble = []
        for a in range(length):
            move = random.choice(moves)
            while move[0] in [m[0] for m in scramble[len(scramble)-2:]]:
                move = random.choice(moves)
            scramble.append(move)
        return scramble
    

timer = Timer()

while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            timer.cubemeshrect = (300*ui.scale,300*ui.scale)
            timer.cubemesh.refreshscale(300*ui.scale,300*ui.scale)
    screen.fill(pyui.Style.wallpapercol)
    timer.gameloop()
    ui.rendergui(screen)
    timer.drawcubemesh()
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
