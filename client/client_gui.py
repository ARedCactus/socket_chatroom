import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, messagebox
from tkinter import END, RIGHT, LEFT
from tkinter import font
import threading, time, queue
import json

import client_core
import client_style

class RootWindow:
    def __init__(self, root=None, width:int=800, height:int=600, windows_name:str="root gui", resizable:bool=True):
        self.root = tk.Tk() if not root else root
        self.root.withdraw()
        self.root.title(windows_name)
        self.root.resizable(resizable, resizable)
        self.root.geometry("{}x{}".format(width, height))
        self.root.update_idletasks()

        # 为了确保grid布局正确，需要配置行和列的权重
        self.root.grid_rowconfigure(0, weight=1)  # 第0行（left_canvas所在行）可以扩展
        self.root.grid_rowconfigure(1, weight=0)  # 第1行（new_frame所在行）不扩展，保持固定高度
        self.root.grid_columnconfigure(0, weight=1)  # 第0列可以扩展
        self.root.grid_columnconfigure(1, weight=0)

    def setTitle(self, name:str):
        self.root.title(name)

    def loop(self):
        self.root.mainloop()

    def quit(self):
        self.root.quit()
        self.root = None

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.deiconify()

class LoginGUI:
    def __init__(self, root:RootWindow):
        self.__root = root
        
        self.__canvas = tk.Canvas(self.__root.root, bg='lightgray', width=300, height=50)  # 增加高度以容纳更多行
        self.__canvas.pack(pady=0)  # 添加一些垂直间距

        self.__entry1_frame = ttk.Frame(self.__root.root)
        self.__entry1_frame.pack(padx=5, pady=10)

        self.label1 = tk.Label(self.__entry1_frame, text="账号: ")
        self.label1.pack(side=tk.LEFT, padx=1, pady=10)

        self.__entry1 = tk.Entry(self.__entry1_frame, width=30)
        self.__entry1.pack(pady=10)

        self.__entry2_frame = ttk.Frame(self.__root.root)
        self.__entry2_frame.pack(padx=5, pady=10)

        self.label2 = tk.Label(self.__entry2_frame, text="密码: ")
        self.label2.pack(side=tk.LEFT, padx=1, pady=10)

        self.__entry2 = tk.Entry(self.__entry2_frame, width=30, show='*')
        self.__entry2.pack(pady=10)

        # 创建按钮框架，用于平行排列两个按钮
        self.__button_frame = ttk.Frame(self.__root.root)
        self.__button_frame.pack(pady=10)

        self.__button1 = ttk.Button(self.__button_frame, text="登录", command=self.__onButtonClick_1)
        self.__button1.pack(side=tk.LEFT, padx=10)  # 左侧对齐，并添加一些水平间距

        self.__button2 = ttk.Button(self.__button_frame, text="注册", command=self.__onButtonClick_2)
        self.__button2.pack(side=tk.LEFT)  # 左侧对齐

        self.__flush_log = client_style.FlushText(self.__root.root, self.__canvas, 3, 300//2, 50//2)
        self.__is_show = True

        self.__root.root.protocol("WM_DELETE_WINDOW", lambda: (self.__root.quit()))

    def __checkFormat(self, account:str, password:str):
        def allDigtalAndNoSapce(s:str):
            stripped_s = s.strip()
            if not stripped_s:
                return False  # 如果字符串为空（只有空格），则返回False
            return stripped_s.isdigit()
        def isAscllNoSpaces(s):
            if ' ' in s: return False
            # 检查字符串中的每个字符是否是ASCII码字符
            for char in s:
                # ord()函数返回字符的Unicode码点
                # 如果码点大于127，则不是ASCII码字符
                if ord(char) > 127: return False
            return True
        if not allDigtalAndNoSapce(account):
            self.__flush_log.drawLog("账号格式错误,仅为数字且不包含空格\n")
            return False
        if not isAscllNoSpaces(password):
            self.__flush_log.drawLog("密码不应包含非ascll码及空格\n")
            return False
        return True
    
    def setClient(self, client: client_core.ClientCore):
        self.__client = client

    def initBuffer(self):
        self.__is_show = True
        self.account_login = "system"
        self.__entry1.delete(0, tk.END)
        self.__entry2.delete(0, tk.END)
    
    def __onButtonClick_1(self):
        account = self.__entry1.get()
        password = self.__entry2.get()
        if not self.__checkFormat(account=account, password=password): return

        try_login_result = self.__client.tryLogin(account=account, password=password)
        if try_login_result == -1:   self.__flush_log.drawLog("unable to receive data\n")
        elif try_login_result == -2: self.__flush_log.drawLog("无法连接到服务器\n")
        elif try_login_result == 0:  self.__flush_log.drawLog("账号不存在, 请先注册\n")
        elif try_login_result == 1:  self.__flush_log.drawLog("密码错误\n")
        elif try_login_result == 2:  self.__flush_log.drawLog("账号已在其他地方登录\n")
        elif try_login_result == 3:  self.__is_show, self.account_login = False, account #登录成功
        else:                        self.__flush_log.drawLog("登录时发生未知错误\n")

    def __onButtonClick_2(self):
        account = self.__entry1.get()
        password = self.__entry2.get()
        if not self.__checkFormat(account=account, password=password): return
        
        try_register_result = self.__client.tryRegister(account=account, password=password)
        if try_register_result == 0:    self.__flush_log.drawLog("账号已存在\n")
        elif try_register_result == 1:  self.__flush_log.drawLog("注册成功\n")
        elif try_register_result == -1: self.__flush_log.drawLog("unable to receive data\n")
        elif try_register_result == -2: self.__flush_log.drawLog("无法连接到服务器\n")
        else:                           self.__flush_log.drawLog("注册时发生未知错误\n")

    def loop(self):
        self.__root.show()
        while self.__is_show: time.sleep(0.5) #休眠，否则占用大量CPU
        self.__root.hide()

class MainGUI:
    def __init__(self, root=RootWindow):
        self.__root = root
        # 创建左边的Canvas
        self.left_canvas = tk.Canvas(self.__root.root, bg='lightgray', width=670, height=570)
        self.left_canvas.grid(row=0, column=0, sticky="nsew")
        self.left_canvas.bind("<Configure>", lambda event: self.__onCanvasConfigure(self.left_canvas)(event))
        self.left_canvas.bind("<MouseWheel>", lambda event: self.__onMouseWheel(self.left_canvas)(event))
        self.left_canvas.config(scrollregion=self.left_canvas.bbox("all")) # 设置Canvas的滚动区域（这里设置为与Frame相同的大小）

        # 将重叠界面元素放置在主框架中，但初始时隐藏
        self.__overlay_frame = tk.Frame(self.left_canvas, bg='red')
        self.__overlay_frame.pack(fill=tk.BOTH, expand=True)
        self.overlay_cansvas = tk.Canvas(self.__overlay_frame, bg="lightgray")
        self.overlay_cansvas.pack(fill=tk.BOTH, expand=True)  # 让Canvas根据Frame的大小自动调整并填充
        self.overlay_cansvas.bind("<Configure>", lambda event: self.__onCanvasConfigure(self.overlay_cansvas)(event))
        self.overlay_cansvas.bind("<MouseWheel>", lambda event: self.__onMouseWheel(self.overlay_cansvas)(event))
        self.__overlay_frame.pack_forget()

        # 创建一个新的Frame并放置在left_canvas下方, 用于装入输入框 
        self.__entry_frame = tk.Frame(self.__root.root)
        self.__entry_frame.grid(row=1, column=0, sticky='nsew')  # 占据第1行第0列，并沿南北方向拉伸
        self.__entry_frame.grid_propagate(False)  # 禁止Frame自动调整其大小以适应其内容

        self.__entry = tk.Entry(self.__entry_frame, width=30)  # Adjusted width to make space for buttons
        self.__entry.pack(side=LEFT, fill=tk.X, expand=True, padx=5, pady=5)  # Added padding for better spacing
        self.__entry.bind("<Return>", lambda event: self.__sendAction())

        self.__send_button = tk.Button(self.__entry_frame, text="Send", command=self.__sendAction)
        self.__send_button.pack(side=LEFT, padx=5)  # Packed to the left with some padding

        self.__logout_button = tk.Button(self.__entry_frame, text="Logout", command=self.__logoutAction)
        self.__logout_button.pack(side=LEFT)

        # 创建右边的Canvas
        self.__right_canvas = tk.Canvas(self.__root.root, bg='#8D8F8F', width=120, height=200)
        self.__right_canvas.grid(row=0, column=1, rowspan=2, sticky="nsew") #  sticky="nsew" 表示自适应大小自动填充
        self.__right_canvas.bind("<Configure>", lambda event: self.__onCanvasConfigure(self.__right_canvas)(event))
        self.__right_canvas.bind("<MouseWheel>", lambda event: self.__onMouseWheel(self.__right_canvas)(event))
        self.__right_canvas.config(scrollregion=self.__right_canvas.bbox("all"))

        # 按钮栏的frame
        self.__button_frame = tk.Frame(self.__right_canvas, bg='#8D8F8F')
        self.__right_canvas.create_window((0, 0), window=self.__button_frame, anchor='nw')

        self.canvas_text = client_style.CanvasText()
        
        def onQuit_():
            if not self.client_.is_server_disconnect: self.client_.send(request="offline")
            self.__window_state = 2
            self.__root.quit()
        self.__root.root.protocol("WM_DELETE_WINDOW", onQuit_)

        style = ttk.Style()  
        style.configure('Green.TButton', background='green', foreground='black')  
        style.configure('Red.TButton', background='red', foreground='black')  
        style.configure('White.TButton', background='yellow', foreground='black')

        self.texts = {}
        self.buttons = []
        self.msg_for_exchange = queue.Queue()
        self.is_print_server_disconnect = False
        self.__account_clicked = None
        self.__last_account_clicked = None
        self.now_account_click = "group"

    def updateCanvas(self, canvas:tk.Canvas, account:str, msgs:list, line:int=None):
        if account in self.texts: canvas.create_text(10, (len(self.texts[account])-1) * 20, text=f"...{msgs}...", anchor=tk.NW)

    def __onCanvasConfigure(self, canvas):
        def canvasConfigure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        return canvasConfigure
    
    def __onMouseWheel(self, canvas):
        def onMouseWheel(event):
            if event.delta > 0: canvas.yview_scroll(1, "units")  # 向上滚动一小段
            else:               canvas.yview_scroll(-1, "units")  # 向下滚动一小段
        return onMouseWheel
    
    def addAccountsButton(self, account_list_online, account_list_text):
        if not account_list_online and not account_list_text: return

        def updateButtonsColor(now_click):
            for button in self.buttons:
                if button["account"] == now_click:              button["value"].configure(style='Red.TButton')  # 设置红色样式
                elif button["account"] in account_list_online:  button["value"].configure(style='Green.TButton')  # 设置绿色样式
                else:                                           button["value"].configure(style='White.TButton')

        def onButtonClick_(account_name:str):
            self.now_account_click = account_name
            if account_name == "group" and self.__account_clicked: self.__overlay_frame.pack_forget(); self.__account_clicked = None
            elif account_name != "group": 
                self.__overlay_frame.pack(fill=tk.BOTH, expand=True); self.__account_clicked = account_name
                if not self.__last_account_clicked or self.__last_account_clicked != account_name:
                    self.overlay_cansvas.delete("all")
                    for i in range(0, len(self.texts[account_name])):
                        self.canvas_text.updateTextWithLine(canvas=self.overlay_cansvas, msgs=self.texts[account_name][i], line=i)
                    self.__last_account_clicked = account_name

            updateButtonsColor(self.now_account_click)

        for account in (account_list_online | account_list_text):
            new_button = ttk.Button(self.__button_frame, text=account, command=lambda obj=account: onButtonClick_(obj))
            new_button.state(['!pressed'])  # 取消按下状态
            new_button.pack(padx=10, pady=3)
            self.buttons.append({"account":account, "value":new_button})
            self.__button_frame.update_idletasks()
            self.__right_canvas.configure(scrollregion=self.__right_canvas.bbox("all"))

        updateButtonsColor(self.now_account_click)

    def __sendAction(self):
        msg_to_send = self.__entry.get(); self.__entry.delete(0, tk.END)
        subscriber = None if self.now_account_click == "group" else self.now_account_click
        msgs_to_show = [[0, 'you', msg_to_send]] if self.client_.send(request="send", subscriber=subscriber, msg=msg_to_send) else [[2, "system", "发送失败, 无法连接到服务器"], [3, "you", msg_to_send]]

        for msg_to_show in msgs_to_show:
            if self.now_account_click == "group":
                if "group" in self.texts: self.texts["group"].append(msg_to_show)
                self.canvas_text.updateText(canvas=self.left_canvas, account="group", msgs=msg_to_show, texts=self.texts)
            elif self.now_account_click in self.texts:
                if self.now_account_click in self.texts: self.texts[self.now_account_click].append(msg_to_show)
                self.canvas_text.updateText(canvas=self.overlay_cansvas, account=self.now_account_click, msgs=msg_to_show, texts=self.texts)

    def __logoutAction(self):
        if not self.client_.is_server_disconnect: self.client_.send(request="logout")
        self.__window_state = 1
        self.texts.clear()
        self.left_canvas.delete("all")
        self.overlay_cansvas.delete("all")
        for button in self.buttons: 
            if button["value"]: button["value"].destroy(); button["value"] = None 
            del button

    def initBuffer(self):
        self.__window_state:int = 0
        self.texts.clear()
        self.left_canvas.delete("all")
        self.overlay_cansvas.delete("all")
        for button in self.buttons:
            if button["value"]: button["value"].destroy(); button["value"] = None
            del button

    def setClient(self, client: client_core.ClientCore):
        self.client_ = client

    def loop(self):
        def subsrciberCallBack_():
            while self.__window_state == 0: 
                buffers = self.client_.subscriberCallBack()
                if buffers: [self.msg_for_exchange.put(item) for item in buffers]

        threading.Thread(target=subsrciberCallBack_, daemon=True).start()

        self.__root.show()
        while self.__window_state == 0: time.sleep(0.5) #休眠，否则占用大量CPU
        self.__root.hide()
        return self.__window_state

if __name__ == "__main__":
    log_root = RootWindow(width=300, height=250, windows_name="Login", resizable=False)
    log_gui = LoginGUI(root=log_root)

    main_root = RootWindow(root=tk.Toplevel(log_root.root), resizable=False)
    main_gui = MainGUI(root=main_root)
    
    stop_event_listener = threading.Event()

    def updateMainGui():
        try:
            while not stop_event_listener.is_set():
                if main_gui.client_.is_server_disconnect and not main_gui.is_print_server_disconnect:
                    print("Server is disconnected...")
                    main_gui.is_print_server_disconnect = True

                obj = main_gui.msg_for_exchange.get_nowait()
                # print("[updateMainGui] ", obj)
                if not obj: continue
                if "accounts" in obj:
                    main_gui.texts.update({account: [] for account in obj["accounts"] if account not in main_gui.texts})
                    while main_gui.buttons:
                        button_to_remove = main_gui.buttons.pop()
                        if button_to_remove["value"]: button_to_remove["value"].destroy(); button_to_remove["value"] = None
                        del button_to_remove
                    main_gui.addAccountsButton(set([item for item in obj["accounts"] if item != log_gui.account_login]), set([item for item in main_gui.texts if len(main_gui.texts[item])>0]))
                elif all(key in obj for key in ["message", "publisher", "subscriber"]):
                    msg_to_show = [2, obj["publisher"], obj["message"]] if obj["publisher"] == "system" else [1, obj["publisher"], obj["message"]]
                    if not obj["subscriber"] and "group" in main_gui.texts: 
                        main_gui.texts["group"].append(msg_to_show)
                        main_gui.canvas_text.updateText(canvas=main_gui.left_canvas, account="group", msgs=msg_to_show, texts=main_gui.texts)
                    elif obj["subscriber"] in main_gui.texts:
                        main_gui.texts[obj["publisher"]].append(msg_to_show)
                        main_gui.canvas_text.updateText(canvas=main_gui.overlay_cansvas, account=obj["publisher"], msgs=msg_to_show, texts=main_gui.texts)

        except queue.Empty as e:
            pass
        main_root.root.after(100, updateMainGui)

    def begin_():
        while not stop_event_listener.is_set():
            try:
                client = client_core.ClientCore()
                log_gui.setClient(client=client)
                log_gui.initBuffer()
                log_gui.loop()
                
                main_root.setTitle(log_gui.account_login)
                main_gui.setClient(client=client)
                main_gui.initBuffer()
                main_root.root.after(100, updateMainGui)
                if main_gui.loop() == 2: break
                
                client.close()
            except Exception as e:  
                print(f"[client] run error: {e}")
            finally: pass
        main_root.quit()
        log_root.quit()

    threading.Thread(target=begin_, daemon=True).start()
    try:
        log_root.loop()
    except KeyboardInterrupt:
        print("[client] received ctrl+c, stoping client ...")
        stop_event_listener.set()
