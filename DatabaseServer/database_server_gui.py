# -*- coding: utf-8 -*-

from tkinter import *
import time
import sys
import psutil

terminal = None
screen = None

CPU_percent_label = None
RAM_usage_percent_label = None
RAM_usage_left_label = None

CPU_percent_string_var = None
RAM_usage_percent_string_var = None
RAM_usage_left_string_var = None

commands = []

def getCommands():
    global commands

    temp = commands
    commands = []
    return temp

def main_screen():
    global terminal
    global screen

    global CPU_percent_label
    global RAM_usage_percent_label
    global RAM_usage_left_label
    
    global CPU_percent_string_var
    global RAM_usage_percent_string_var
    global RAM_usage_left_string_var

    screen = Tk()
    screen.geometry("900x700")
    screen.resizable(False, False)
    screen.title("Wand And Sword Database Manager 1.0")

    left_frame = Frame(screen, bg='white', width=400, height=700)
    right_frame = Frame(screen, bg='white', width=500, height=700)

    screen.grid_rowconfigure(1, weight=1)
    screen.grid_columnconfigure(0, weight=1)

    left_frame.grid(row=1, column=0)
    right_frame.grid(row=1, column=1)

    terminal = Application(left_frame, "text")
    terminal.pack()
    Application(left_frame, "input").pack()

    CPU_percent_string_var = StringVar(right_frame)
    RAM_usage_percent_string_var = StringVar(right_frame)
    RAM_usage_left_string_var = StringVar(right_frame)

    CPU_percent_label = Label(right_frame, textvariable=CPU_percent_string_var)
    RAM_usage_percent_label = Label(right_frame, textvariable=RAM_usage_percent_string_var)
    RAM_usage_left_label = Label(right_frame, textvariable=RAM_usage_left_string_var)

    CPU_percent_label.pack()
    RAM_usage_percent_label.pack()
    RAM_usage_left_label.pack()

def update_computer_info():
    CPU_percent_string_var.set("CPU Usage: {}%".format(psutil.cpu_percent()))
    RAM_usage_percent_string_var.set("RAM Usage: {}%".format(psutil.virtual_memory().percent))
    RAM_usage_left_string_var.set("RAM Left: {}MB/{}MB".format(psutil.virtual_memory().free >> 20, psutil.virtual_memory().total >> 20))

def print_gui(msg):
    terminal.addText(msg)

class Application(Frame):
    def __init__(self, master, typ):
        Frame.__init__(self, master)
        self.text = Text(self, wrap="word", height=20)
        self.vsb = Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.bind("<Return>", self.process_input)
        self.prompt = ">>> "

        if typ == "input":
            self.insert_prompt()

        self.typ = typ

    def insert_prompt(self):
        # make sure the last line ends with a newline; remember that
        # tkinter guarantees a trailing newline, so we get the
        # character before this trailing newline ('end-1c' gets the
        # trailing newline, 'end-2c' gets the char before that)
        c = self.text.get("end-2c")
        if c != "\n":
            self.text.insert("end", "\n")
        self.text.insert("end", self.prompt, ("prompt",))

        # this mark lets us find the end of the prompt, and thus
        # the beggining of the user input
        self.text.mark_set("end-of-prompt", "end-1c")
        self.text.mark_gravity("end-of-prompt", "left")

    def process_input(self, event=None):
        if self.typ == "text":
            return "break"
    
        # if there is an event, it happened before the class binding,
        # thus before the newline actually got inserted; we'll
        # do that here, then skip the class binding.
        self.text.insert("end", "\n")
        command = self.text.get("end-of-prompt", "end-1c")
        command = command.strip()
        
        commands.append(command)
        #self.text.insert("end", "output of the command '%s'...!" % command)
        self.text.see("end")
        self.insert_prompt()

        # this prevents the class binding from firing, since we 
        # inserted the newline in this method
        return "break"

    def addText(self, msg):
        self.text.insert("end", msg + "\n")
        self.text.see("end")

main_screen()