import random
from tkinter import messagebox
from cx_Oracle import DatabaseError
import tkinter as tk
import Player
from MyExceptions import *



def __init__(self):
    self.setup_Player()


def setup_player(self):
    try:
        self.my_player = Player.Player()
        if self.my_player.get_db_status():
            messagebox.showinfo("Success!", "Connected successfully to the DB!!!")
        else:
            raise Exception("Sorry! you cannot save or load favourites!!!")
    except Exception as ex:
        print("DB Error:", ex)
    messagebox.showerror("DB Error!", ex)
    self.addFavourite.configure(state="disabled")
    self.loadFavourite.configure(state="disabled")
    self.removeFavourite.configure(state="disabled")
    self.vol_scale.configure(from_=0, to=100, command=self.change_volume)
    self.vol_scale.set(50)
    self.addSongsToPlayListButton.configure(command=self.add_song)
    self.deleteSongsFromPlaylistButton.configure(command=self.remove_song)
    self.playButton.configure(command=self.play_song)
    self.stopButton.configure(command=self.stop_song)
    self.pauseButton.configure(command=self.pause_song)
    self.playList.configure(font="Vivaldi 12")
    self.playList.bind("<Double-1>", self.list_double_click)
    img = tk.PhotoImage(file="./icons/icon_music1.png")
    self.top.iconphoto(self.top, img)
    self.top.title("MOUZIKKA-Dance to the rhythm of your heart!!")
    self.top.protocol("WM_DELETE_WINDOW", self.closewindow)
    self.isPaused = False
    self.isPlaying = False


def change_volume(self, val):
    volume_level = float(val) / 100
    self.my_player.set_volume(volume_level)


def add_song(self):
    song_name = self.my_player.add_song()
    if song_name is None:
        return
    self.playList.insert(tk.END, song_name)
    rcolor = lambda: random.randint(0, 255)
    red = hex(rcolor())
    green = hex(rcolor())
    blue = hex(rcolor())
    red = red[2:]
    green = green[2:]
    blue = blue[2:]
    if len(red) == 1:
        red = "0" + red
    if len(green) == 1:
        green = "0" + green
    if len(blue) == 1:
        blue = "0" + blue

    mycolor = "#" + red + green + blue
    print(red, green, blue)
    print(mycolor)
    self.playList.configure(fg=mycolor)


def show_song_details(self):
    self.song_length = self.my_player.get_song_length(self.song_name)
    min, sec = divmod(self.song_length, 60)
    min = round(min)
    sec = round(sec)
    self.songTotalDuration.configure(text=str(min) + ':' + str(sec))
    self.songTimePassed.configure(text="0:0")
    ext_index = self.song_name.rfind(".")
    song_name_str = self.song_name[0:ext_index]
    if (len(song_name_str) > 14):
        song_name_str = song_name_str[0:14] + ". . ."
        self.songName.configure(text=song_name_str)


def play_song(self):
    self.sel_song_index_tuple = self.playList.curselection()
    try:
        if len(self.sel_song_index_tuple) == 0:
            raise NoSongSelectedError("Please select a song to play")

        self.song_name = self.playList.get(self.sel_song_index_tuple[0])
        self.show_song_details()
        self.my_player.play_song()
        self.change_volume(self.vol_scale.get())
        self.isPlaying = True

    except(NoSongSelectedError)as ex1:
        messagebox.showerror("Error!", ex1)


def list_double_click(self, e):
    self.play_song()


def stop_song(self):
    self.my_player.stop_song()
    self.isPlaying = False


def pause_song(self):
    if self.isPlaying:
        if self.isPaused == False:
            self.my_player.pause_song()
            self.isPaused = True
        else:
            self.my_player.unpause_song()
            self.isPaused = False


def remove_song(self):
    self.sel_index_tuple = self.playList.curselection()
    print(type(self.sel_index_tuple))
    print(self.sel_index_tuple)
    try:
        if len(self.sel_index_tuple) == 0:
            raise NoSongSelectedError("Please select a song to remove")

        song_name = self.playList.get(self.sel_index_tuple[0])
        self.playList.delete(self.sel_index_tuple[0])
        self.my_player.remove_song(song_name)
    except(NoSongSelectedError)as ex1:
        messagebox.showerror("Error!", ex1)


def closewindow(self):
    result = messagebox.askyesno("App Closing!!!", "Do you want to quit?")
    if (result):
        self.my_player.close_player()
        messagebox.showinfo("Have a good day!", "Thank you for using \"MOUZIKKA\" ")
        self.top.destroy()


def load_previous_song(self):
    try:
        if hasattr(self, "sel_song_index_tuple") == False:
            raise NoSongSelectedError("Please select a song first")
        self.prev_song_index = self.sel_song_index_tuple[0] - 1
        if self.prev_song_index == -1:
            self.prev_song_index = self.playList.count() - 1

        self.playList.select_clear(0, tk.END)
        self.playList.selection_set(self.prev_song_index)
        print("Prev Song index:", self.prev_song_index)
        self.play_song()
    except(NoSongSelectedError)as ex1:
        messagebox.showerror("Error!", ex1)


def add_song_to_favourites(self):
    fav_song_index_tuple = self.playList.curselection()
    try:
        if len(fav_song_index_tuple) == 0:
            raise NoSongSelectedError("Please select a song to add to favourites")

        song_name = self.playList.get(fav_song_index_tuple[0])
        result = self.my_player.add_song_to_favourites(song_name)
        messagebox.showinfo("Success!!!", result)

    except(NoSongSelectedError)as ex1:
        messagebox.showerror("Error!", ex1)
        print(ex1)
    except(DatabaseError)as ex2:
        messagebox.showerror("DB Error!", "Song cannot be added!!!")
        print(ex2)


def load_songs_from_favourites(self):
    try:
        load_result = self.my_player.load_songs_from_favourites()
        result = load_result[0]
        if result.find("No songs present") != -1:
            messagebox.showinfo("Favourites Empty!!!", "No songs in your favourites")
            return
        song_dict = load_result[1]
        self.playList.delete(0, tk.END)
        for song_name in song_dict:
            self.playList.insert(tk.END, song_name)
            print("from db:", song_name)
        rcolor = lambda: random.randint(0, 255)
        red = hex(rcolor())
        green = hex(rcolor())
        blue = hex(rcolor())
        mycolor = "#" + red[2:3] + green[2:3] + blue[2:3]
        print(red, green, blue)
        print(mycolor)
        self.playList.configure(fg=mycolor)
        messagebox.showinfo("Success!!!", "List populated from your favourites!!!")

    except(DatabaseError)as ex1:
        messagebox.showerror("DB Error!", "Sorry! songs cannot be loaded from favourites!!!")


def remove_song_from_favourites(self):
    fav_song_index_tuple = self.playList.curselection()
    try:
        if len(fav_song_index_tuple) == 0:
            raise NoSongSelectedError("Please select a song to remove from favourites")

        song_name = self.playList.get(fav_song_index_tuple[0])
        result = self.my_player.remove_song_from_favourites(song_name)
        if (result.find("deleted") != -1):
            self.playList.delete(fav_song_index_tuple[0])
            if fav_song_index_tuple[0] == self.sel_song_index_tuple[0]:
                self.stop_song()
        messagebox.showinfo("Success!!!", result)
    except(NoSongSelectedError)as ex1:
        messagebox.showerror("Error!", ex1)
        print(ex1)
    except(DatabaseError)as ex2:
        messagebox.showerror("DB Error!", "Song cannot be removed!!!")
        print(ex2)
