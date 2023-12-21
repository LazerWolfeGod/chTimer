import pygame,math,random,sys,os
import PyUI as pyui
pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.styleload_teal()
ui.styleset(scalesize=False)

def update():
    maintext.settext(textbox.text)
def changefont(font):
    maintext.font = font
    maintext.refresh()

maintext = ui.maketext(0,0,'Text',100,center=True,anchor=('w/3*2','h/2'))

textbox = ui.maketextbox(3,3,'',400,3,command=update,commandifkey=True,enterreturns=True)

data = []
fonts = pygame.font.get_fonts()
for f in fonts:
    func = pyui.funcer(changefont,font=f)
    data.append([ui.makebutton(0,0,'{'+f+' font=calibre} '+f,20,font=f,command=func.func,ID=f,toggleable=True,bindtoggle=fonts,toggle=False,togglecol=20)])



table = ui.makescrollertable(3,78,data,['Font'],textcenter=True)


while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                for a in range(len(table.data)):
                    if table.data[a][0].toggle:
                        table.data[(a+1)%len(table.data)][0].press()
                        break
            elif event.key == pygame.K_UP:
                for a in range(len(table.data)):
                    if table.data[a][0].toggle:
                        table.data[a-1][0].press()
                        break  
    screen.fill(pyui.Style.wallpapercol)
    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
