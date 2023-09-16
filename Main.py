from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.pickers import MDTimePicker
import datetime
from datetime import date
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
import json
import sqlite3



class HomePage(MDScreen):
    pass
class TodoCard(FakeRectangularElevationBehavior,MDFloatLayout):
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark_task_as_complete(self, taskid):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE TASK SET completed=1 WHERE id=?", (taskid,))
        con.commit()
    def mark_task_as_incomplete(self, taskid):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE TASK SET completed=0 WHERE id=?", (taskid,))
        con.commit()
        task_text = cursor.execute("SELECT Description FROM TASK WHERE Id=?", (taskid,)).fetchall()
        return task_text[0][0]
    def delete_task(self, taskid):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM TASK WHERE Id=?", (taskid,))
        con.commit()

    title = StringProperty()
    description = StringProperty()
    task_date= StringProperty()
    task_time = StringProperty()
    task_time2 = StringProperty()
class TaskCard(FakeRectangularElevationBehavior,MDFloatLayout):
    title = StringProperty()
    description = StringProperty()
    date_time= StringProperty()
class CourseCard(FakeRectangularElevationBehavior,MDFloatLayout):
    title = StringProperty()
    description = StringProperty()



class MainApp(MDApp):
      
#Screen manager build
    def build(self):
        global screen_manager
        #self.title ="Ä Goals"
        screen_manager = ScreenManager()
        """ screen_manager.add_widget(Builder.load_file("Screens/Main.kv"))
        screen_manager.add_widget(Builder.load_file("Screens/Login.kv")) 
        screen_manager.add_widget(Builder.load_file("Screens/SignUp.kv")) """
        screen_manager.add_widget(Builder.load_file('Screens/homeScreen.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/Addtodo.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/todo.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/Courses.kv'))

        Window.size = [300, 600]
        return screen_manager

    def get_tasks(self):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        uncomplete_tasks = cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 0").fetchall()
        completed_tasks = cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 1").fetchall()

        return completed_tasks, uncomplete_tasks
    
    def on_start(self):
        today = date.today()
        wd = date.weekday(today)
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().strftime("%b"))
        day = str(datetime.datetime.now().strftime("%d"))
        screen_manager.get_screen("todoScreen").date_text.text = f"{days[wd]}, {day} {month}"

        try:
            completed_tasks, uncomplete_tasks = self.get_tasks()

            if uncomplete_tasks != []:
                for i in uncomplete_tasks:
                    add_task = (TodoCard(pk=i[0],title=i[1], description=i[2],task_date=i[3],task_time=i[4],task_time2=i[5]))
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)

            if completed_tasks != []:
                for i in completed_tasks:
                    add_task =(TodoCard(pk=i[0],title=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],task_time2=i[5]))
                    add_task.ids.check.active = True
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
        except Exception as e:
            print(e)
            pass

#checkbox seetings
    def on_complete(self,task_card,value,description,bar):

        if value.active == True:
            description.text = f"[s]{description.text}[/s]"
            bar.md_bg_color =0,179/255,0,1
            TodoCard.mark_task_as_complete(task_card,task_card.pk)
       
        else:
            remove = ["[s]", "[/s]"]
            for i in remove:
                description.text = description.text.replace(i,"")
                bar.md_bg_color =1,170/255,23/255,1
                TodoCard.mark_task_as_incomplete(task_card,task_card.pk)

    def delete_item(self, task_card):
        screen_manager.get_screen("todoScreen").todo_list.remove_widget(task_card)
        TodoCard.delete_task(task_card,task_card.pk)

#update table
    def update_task(self,title):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("SELECT Id,Description,Date,FromTime,ToTime,completed FROM TASK WHERE Title=?",(title,))
        arr =cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],title=title, description=i[1],task_date=i[2],task_time=i[3],task_time2=i[4]))

# add task settings
    def add_todo(self,title,description,date_time,task_time,task_time2):
        con= sqlite3.connect('User_Database.db')
        cursor=con.cursor()
       
        if title !="" and description !="" and len(title)<21 and len(description)<61:
            # adding task to database
            data= title,description,date_time,task_time,task_time2,0
            cursor.execute("INSERT INTO TASK(Title,Description,Date,FromTime,ToTime,completed) VALUES(?,?,?,?,?,?)",data)
            con.commit()
            screen_manager.transition.direction = "right"
            screen_manager.current = "todoScreen"

        elif title =="":
            Snackbar(text="Title is missing!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1), # type: ignore
                    font_size ="19dp").open() # type: ignore
        elif description =="":
            Snackbar(text="Description is missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()
        elif len(title)>21:
            Snackbar(text="Title too long!must<20",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()
        elif len(description)>61:
            Snackbar(text="Description too long! must<60",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()

#display fromdatabse
    def display_task_complete(self):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=1")
        arr =cursor.fetchall()
        for i in arr:
            add_task =(TodoCard(pk=i[0],title=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],task_time2=i[5]))                                                             
            add_task.ids.check.active = True
            if add_task.ids.pk !=i[0]:
                screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
           
            #prevent double display of items on list    
            # move reading database from button trigger to read to display when app starts                                                     
    def display_task_incomplete(self):
        con= sqlite3.connect('User_Database.db')
        cursor = con.cursor()
        cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=0")
        arr =cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],title=i[1], description=i[2],task_date=i[3],task_time=i[4],task_time2=i[5]))
        

# User sign up settings
    def userSignUp(self,user_name,user_email,user_password):
        user_name = screen_manager.get_screen("SignUp").usr_name.text
        user_email = screen_manager.get_screen("SignUp").usr_email.text
        user_password = screen_manager.get_screen("SignUp").usr_pass.text

        #connecting to database
        con= sqlite3.connect('User_Database.db')
        cursor=con.cursor()
        """ with con:
            cursor=con.cursor()
        cursor.execute('CREATE TABLE LOGIN(Name TEXT,Email TEXT,Password TEXT)') """
    
        if user_name !="" and user_email !="" and user_password !="" and len(user_name)<21 and len(user_password)<60:
            data = (user_name,user_email,user_password)
            cursor.execute("INSERT INTO LOGIN VALUES(?,?,?)",data)
            con.commit()
            screen_manager.transition.direction = "right"
            screen_manager.current = "Home"

        elif user_name =="":
            Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()
        elif user_email =="":
            Snackbar(text="Email  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()
        elif user_password =="":
            Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open() # type: ignore
        elif len(user_name)>21:
            Snackbar(text="Username must<21",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open()
        elif len(user_password)>61 :
            Snackbar(text="Password must<61",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                    font_size ="19dp").open() # type: ignore

# user login settings
    def userlogin(self,user_name,user_password):
        con= sqlite3.connect('User_Database.db')
        cursor=con.cursor()
            
        user_name = screen_manager.get_screen("Login").usr_Username.text
        user_password = screen_manager.get_screen("Login").usr_password.text
        
        cursor.execute("SELECT Name,Password FROM LOGIN")
        arr =cursor.fetchall()
        for i in arr:
            usname = i[0]
            uspassword = i[1]
           
            if user_name !="" and user_password !="" and user_name == usname and user_password == uspassword:
                screen_manager.transition.direction = "right"
                screen_manager.current = "Home"

            elif user_name =="":
                Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                        font_size ="19dp").open() # type: ignore
            elif user_password =="":
                Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                        font_size ="19dp").open()
            elif user_name != usname:
                Snackbar(text="Invalid username",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                        font_size ="19dp").open()
            elif user_password != uspassword:
                Snackbar(text="Invalid password",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(1,170/255,23/255,1),
                        font_size ="19dp").open()

# date picker
    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B')
        screen_manager.get_screen("add_todo").task_date.text = str(date)

    def on_cancel(self):
        MDDatePicker.close() # type: ignore

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save) #type: ignore
        date_dialog.open()#type: ignore

#time picker
    def get_time(self,instance,time):
        Time= time.strftime('%H:%M')
        screen_manager.get_screen("add_todo").task_time.text = str(Time)
        
    def show_time_picker(self):
        '''Open time picker dialog.'''
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time) #type: ignore
        time_dialog.open() # type: ignore

    def get_time2(self,instance,time):
        Time= time.strftime('%H:%M')
        screen_manager.get_screen("add_todo").task_time2.text = str(Time)

    def show_time_picker2(self):
        '''Open time picker dialog.'''
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time2)#type: ignore
        time_dialog.open()#type: ignore





if __name__ == "__main__":
    MainApp().run()
    
   
""" 
    con= sqlite3.connect('User_Database.db')
    cursor = con.cursor()

    cursor.execute("DELETE FROM LOGIN WHERE Name =='mukrlo'") 
    con.commit()
 """
#screen_manager.get_screen("Home").tasks_home.add_widget(TaskCard(title=title, description=description))
            #screen_manager.get_screen("Home").course_home.add_widget(CourseCard(title=title, description=description))
    


