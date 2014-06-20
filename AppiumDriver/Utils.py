'''
Created on Jun 19, 2014

@author: pli
'''

def drawRec(filename, cordlist, color=(0,0,0)):
    '''
    draw rectangles to images
    '''
    import Image, ImageDraw
    im = Image.open(filename)
    draw = ImageDraw.Draw(im)
    for cord in cordlist:
        newcord = (cord[0], cord[1], cord[2], cord[3])
        draw.rectangle(newcord, fill=color)
    del draw
    newfile = filename
    im.save(newfile)
    return newfile

def getRec(filename, x1, y1, x2, y2):
    import Image
    im = Image.open(filename)
    box = (x1, y1, x2, y2)
    xim = im .crop(box)
    xim.save(filename)