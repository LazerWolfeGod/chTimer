import pygame,math,random,sys,os,time,json,datetime
import PyUI as pyui
pygame.init()
screenw = 1800
screenh = 1024
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()

ui.styleset(wallpapercol=(207,215,220),font='arialrounded',col=(100,117,147),textcol=(30,30,30),roundedcorners=2,textsize=30)
#'ocraextended'
ui.addinbuiltimage('bg',pygame.image.load('background.png'))

def sectostr(sec):
    if sec == '-': return '-'
    h = int(sec//3600)
    m = int(sec%3600//60)
    s = str(int(sec%60))
    rounded = 2
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
            self.timertext.settext(sectostr(time.perf_counter()-self.start_time))
        elif self.spacepressed and not self.leftwindow.enabled and not self.readytostart:
            self.readytostart = True
            self.timertext.settextcol((0,225,0))
            self.timertext.settext(sectostr(0))

## GUI   
    def makegui(self):
        self.timertext = ui.maketext(0,0,sectostr(0),120,center=True,anchor=('w/2','h/2'),pregenerated=False,font='ocraextended')

        ui.maketext(0,0,'{bg}',screenh,center=True,anchor=('w/2','h/2'),layer=-10)

        self.leftwindow = ui.makewindow(0,0,400,'h',enabled=True,col=(27,215,220),animationtype='moveleft',bounditems=[

            ui.makedropdown(3,3,[a for a in self.alldata]+['Add Session'],30,command=self.change_session,width=400-6,startoptionindex=1,ID='session select'),

            ui.makescrollertable(3,47,[],['Solve','Time','AO5'],ID='timestable',pageheight='h-83',width=394,boxwidth=[108,-1,-1],font='arialrounded')
            ])

        self.session = ui.IDs['session select'].active
        self.refresh_times_table()

        ui.makewindowedmenu(50,0,300,200,'time_edit_menu','main',isolated=True)

    def refresh_times_table(self):
        data = []
        for i,a in enumerate(self.alldata[self.session]):
            func = pyui.funcer(self.time_edit_menu,num=i+1)
            row = [ui.makebutton(0,0,i+1,command=func.func),sectostr(a[0]),sectostr(self.AOX([b[0] for b in self.alldata[self.session][i-5:i]],5))]
            data.insert(0,row)
        ui.IDs['timestable'].data = data
        ui.IDs['timestable'].refresh()
    def time_edit_menu(self,num):
        ui.movemenu('time_edit_menu','right')
        print(num)
        
#### Manage timer
    def press_start(self):
        if not self.timing:
            self.shut_menus()
            self.timertext.settextcol((255,0,0))
            self.readytostart = False
        else:
            info = (time.perf_counter()-self.start_time,timetodate(time.time()))
            self.alldata[self.session].append(info)
            self.save_json()
            self.juststopped = True
            self.timing = False
            self.open_menus()

            func = pyui.funcer(self.time_edit_menu,num=len(ui.IDs['timestable'].table))
            
            ui.IDs['timestable'].row_insert([ui.makebutton(0,0,len(ui.IDs['timestable'].table),command=func.func),sectostr(info[0]),sectostr(self.AOX([b[0] for b in self.alldata[self.session][-5:]],5))],0)

            
    def shut_menus(self):
        self.leftwindow.shut()
    def open_menus(self):
        self.leftwindow.open(toggleopen=False)
    def release_start(self):
        if not self.timing:
            if self.readytostart:
                if not self.juststopped:
                    self.timing = True
                    self.start_time = time.perf_counter()
                else:
                    self.juststopped = False
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
    timer.gameloop()
    screen.fill(pyui.Style.wallpapercol)
    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
