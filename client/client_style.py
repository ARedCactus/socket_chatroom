import tkinter as tk

class FlushText:
    def __init__(self, root, canvas, duration:float, text_x:int, text_y:int):
        self.__root = root
        self.__canvas = canvas
        self.__duration = duration
        self.__x = text_x
        self.__y = text_y
        self.__text_id = None

    def __clearText(self):
        if self.__text_id is not None:  
            self.__canvas is not None and self.__canvas.delete(self.__text_id)
            self.__text_id = None

    def drawLog(self, log:str):
        self.__clearText()
        self.__text_id = self.__canvas.create_text(self.__x, self.__y, text=log, font=('Arial', 10,  "bold")) 
        # 重置定时器  
        self.__root.after(self.__duration*1000, self.__clearText)  

class CanvasText:
    def __init__(self):
        self.boundary = (30, 10)  #距离画布边界的距离
        self.text_dis = (5, 50)   #文字上下行的间距
        self.text_size = 14       #文字的尺寸
        self.trct_dis = 5         #矩形扩展距离
        self.system_log_dis = (220, 10)
        self.system_log_size = 12
        self.icon_dis = (35, -25)
        self.icon_size = 10
        self.color_left = ("lightgreen", "black")
        self.color_system = ("red", "white")
        self.color_right = ("#2B5AD9", "white")

    def __drawText(self, canvas, msg, position=(0, 0), size=10, color="red"):
        if not msg: return
        canvas.create_text(position[0], position[1], text=msg, anchor='nw', font=("Arial", size), fill=color)

    def __drawTextInRectangle(self, canvas, msgs, y):
        if len(msgs) != 3: return
        position, corner, color = ((self.boundary[0], y), 'nw', self.color_left) if msgs[0] == 1 else ((canvas.winfo_width()-self.boundary[0], y), 'ne', self.color_right)
        pos_icon = (self.icon_dis[0]-20, y+self.icon_dis[1]) if msgs[0] == 1 else (canvas.winfo_width()-self.icon_dis[0],  y+self.icon_dis[1])
        if msgs[0] == 3: color = self.color_system
        self.__draw_text_in_rectangle(canvas=canvas, text=msgs[2], position=position, corner=corner, color=color)
        self.__drawText(canvas=canvas, msg=msgs[1], position=pos_icon, size=self.icon_size, color="black") #name

    def updateText(self, canvas, account:str, msgs, texts=None):
        if len(msgs) != 3: return
        height = (len(texts[account])-1)*self.text_dis[1] + self.boundary[1]
        if msgs[0] == 2: self.__drawText(canvas=canvas, msg=msgs[2], position=(self.system_log_dis[0], self.system_log_dis[1]+height), size=self.system_log_size, color="black")
        else:            self.__drawTextInRectangle(canvas=canvas, msgs=msgs, y=height)

    def updateTextWithLine(self, canvas, msgs, line):
        if len(msgs) != 3: return
        height = line*self.text_dis[1] + self.boundary[1]
        if msgs[0] == 2: self.__drawText(canvas=canvas, msg=msgs[2], position=(self.system_log_dis[0], self.system_log_dis[1]+height), size=self.system_log_size, color="black")
        else:            self.__drawTextInRectangle(canvas=canvas, msgs=msgs, y=height)

    def __draw_text_in_rectangle(self, canvas, text, position=(10, 10), corner='nw', color=("lightgreen", "black")):
        text_id = canvas.create_text(position, text=text, anchor=corner, font=("Arial", self.text_size))  
        bbox = canvas.bbox(text_id)  # 获取文本边框  
        canvas.delete(text_id)  # 移除文本，只保留边框信息  
        
        if corner == 'nw':  # 左上角  
            x1 = bbox[0] - self.trct_dis
            y1 = bbox[1] - self.trct_dis  
            x2 = bbox[2] + self.trct_dis  
            y2 = bbox[3] + self.trct_dis  
        elif corner == 'ne':  # 右上角  
            x1 = position[0] - (bbox[2] - bbox[0]) - self.trct_dis  
            y1 = bbox[1] - self.trct_dis  
            x2 = position[0] + self.trct_dis  
            y2 = bbox[3] + self.trct_dis  
        else:  
            raise ValueError("无效的角标，应该是 'nw' 或 'ne'。")  
        canvas.create_rectangle(x1, y1, x2, y2, outline="", fill=color[0])
        canvas.create_text(x1 + self.trct_dis, y1 + self.trct_dis, text=text, anchor='nw', font=("Arial", self.text_size), fill=color[1])