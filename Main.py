from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty,ListProperty,NumericProperty
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.pickers import MDTimePicker
from kivy.clock import Clock
import datetime
from datetime import date
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
import random
import sqlite3


class database():
    con = sqlite3.connect('User_Database.db')
    cursor = con.cursor()

class CircularProgressBar(AnchorLayout):
    set_value = NumericProperty(0)
    bar_color = ListProperty([244/255,249/255,253/255])
    text =StringProperty("0%")
    counter =0
    value =NumericProperty(0)
    duration=NumericProperty(1.5)
    
    def __init__(self,**kwargs):
        super(CircularProgressBar,self).__init__(**kwargs)
        Clock.schedule_once(self.animate,0)
    def animate(self,*args):
        Clock.schedule_interval(self.percent_counter,self.duration/self.value)
    def percent_counter(self,*args):
        if self.counter < self.value:
            self.counter += 1
            self.text =f"{self.counter}%"
            self.set_value =self.counter
        else:
            Clock.unschedule(self.percent_counter)


class TodoCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark_task_as_complete(self, taskid):
        database.cursor.execute("UPDATE TASK SET completed=1 WHERE id=?", (taskid,))
        database.con.commit()
    def mark_task_as_incomplete(self, taskid):
    
        database.cursor.execute("UPDATE TASK SET completed=0 WHERE id=?", (taskid,))
        database.con.commit()
        task_text = database.cursor.execute("SELECT Description FROM TASK WHERE Id=?", (taskid,)).fetchall()
        return task_text[0][0]
    def delete_task(self, taskid):
        database.cursor.execute("DELETE FROM TASK WHERE Id=?", (taskid,))
        database.con.commit()

    title = StringProperty()
    description = StringProperty()
    task_date= StringProperty()
    task_time = StringProperty()
    task_time2 = StringProperty()
class CourseCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, course_key=None, **kwargs):
        super().__init__(**kwargs)
        # state a course_key which we shall use link the list items with the database primary keys
        self.course_key = course_key
    
    def navigate(self):
        screen_manager.transition.direction = "left"
        screen_manager.current = "addAssesment"
        pass
    CourseID = StringProperty()
    C_Credit = StringProperty()
    C_CA=StringProperty()
    C_Basis=StringProperty()
    CA_ratio=StringProperty()
    Ex_ratio=StringProperty()
class Account(MDScreen):
    name = StringProperty()
    Department = StringProperty()

class MainApp(MDApp):    
      
#Screen manager build
    def build(self):
        global screen_manager
        #self.title ="Ä Goals"
        screen_manager = ScreenManager()
        """ screen_manager.add_widget(Builder.load_file("Screens/Main.kv"))
        screen_manager.add_widget(Builder.load_file("Screens/Login.kv"))  
        screen_manager.add_widget(Builder.load_file("Screens/SignUp.kv")) """
        screen_manager.add_widget(Builder.load_file('Screens/HomeScreen.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/TaskView.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/AddTask.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/CoursesView.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/Addcourse.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/AddAssessment.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/AccountScreen.kv'))

        Window.size = [300, 600]
        return screen_manager
    

    def get_tasks(self):
        uncomplete_tasks = database.cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 0").fetchall()
        completed_tasks = database.cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 1").fetchall()
        return completed_tasks, uncomplete_tasks
    def get_courses(self):
        taken_courses = database.cursor.execute("SELECT ID, COURSE_ID,CREDIT,CA_R,EX_R FROM COURSES").fetchall()
        return taken_courses
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
            taken_courses =self.get_courses()

            if completed_tasks != []:
                for i in completed_tasks:
                    add_task =(TodoCard(pk=i[0],title=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],task_time2=i[5]))
                    add_task.ids.check.active = True
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            if uncomplete_tasks != []:
                for i in uncomplete_tasks:
                    add_task = TodoCard(pk=i[0],title=i[1], description=i[2],task_date=i[3],task_time=i[4],task_time2=i[5])
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            if taken_courses !=[]:
                for c in taken_courses:
                    cr= str (c[2])
                    ca = str (c[3])
                    ex = str (c[4])
                    add_course = CourseCard(course_key = c[0],CourseID=c[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)

        except Exception as e:
            print(e)
            pass
    def creditscal(self):
        database.cursor.execute("SELECT CREDIT FROM COURSES")
        creds = database.cursor.fetchall()
        total_cre =0
        for cre in creds:
            for i in cre:
                total_cre =total_cre + i
        cred_format ="{:.1f}".format(total_cre)
        return cred_format
#checkbox seetings
    def on_complete(self,task_card,value,description,bar):

        if value.active == True:
            description.text = f"[s]{description.text}[/s]"
            bar.md_bg_color =12/255,12/255,13/255,.5
            TodoCard.mark_task_as_complete(task_card,task_card.pk)
       
        else:
            remove = ["[s]", "[/s]"]
            for i in remove:
                description.text = description.text.replace(i,"")
                bar.md_bg_color =30/255,47/255,151/255,1 
                TodoCard.mark_task_as_incomplete(task_card,task_card.pk)

#delete widget from view and info from database
    def delete_item(self, task_card):
        screen_manager.get_screen("todoScreen").todo_list.remove_widget(task_card)
        TodoCard.delete_task(task_card,task_card.pk)

#update TASK view table
    def update_task(self,title):
        database.cursor.execute("SELECT Id,Description,Date,FromTime,ToTime,completed FROM TASK WHERE Title=?",(title,))
        arr =database.cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],title=title, description=i[1],
                                                                                  task_date=i[2],task_time=i[3],task_time2=i[4]))

# add task settings
    def add_todo(self,title,description,date_time,task_time,task_time2):
       
        if title !="" and description !="" and len(title)<21 and len(description)<61:
            # adding task to database
            data= title,description,date_time,task_time,task_time2,0
            database.cursor.execute("INSERT INTO TASK(Title,Description,Date,FromTime,ToTime,completed) VALUES(?,?,?,?,?,?)",data)
            database.con.commit()
            screen_manager.transition.direction = "right"
            screen_manager.current = "todoScreen"
            #screen_manager.get_screen("Home").tasks_home.add_widget(TaskCard(title=title, description=description))

        elif title =="":
            Snackbar(text="Title is missing!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1), # type: ignore
                    font_size ="19dp").open() # type: ignore
        elif description =="":
            Snackbar(text="Description is missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
            
        elif len(title)>21:
            Snackbar(text="Title too long!must<20",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
            screen_manager.get_screen("add_todo").title.text=""
        elif len(description)>61:
            Snackbar(text="Description too long! must<60",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
            screen_manager.get_screen("add_todo").description.text=""

#adding new course to course view
    def update_Course(self,CourseID):
        #database.cursor.execute("DELETE FROM COURSES WHERE COURSE_ID=?",("MUK",))
        
        database.con.commit()
        database.cursor.execute("SELECT ID,CREDIT,CA_R,EX_R FROM COURSES WHERE COURSE_ID=?",(CourseID,))
        arr =database.cursor.fetchall()
        for c in arr:
            cr= str (c[1])
            ca = str (c[2])
            ex = str (c[3])
            crse= CourseCard(course_key = c[0],CourseID=CourseID, C_Credit=cr,CA_ratio=ca,Ex_ratio=ex)
            screen_manager.get_screen("CoursesScreen").course_list.add_widget(crse)

# add course settings
    def add_course(self,CourseID,C_Credit,CA_ratio,Ex_ratio):
        #database.cursor.execute("DROP TABLE COURSES")
        #database.cursor.execute("CREATE TABLE COURSES(ID INTEGER PRIMARY KEY AUTOINCREMENT,COURSE_ID TEXT NOT NULL UNIQUE,CREDIT DECIMAL,CA_R INTERGER NOT NULL,EX_R INTERGER NOT NULL,CA DECIMAL,BASIS DECIMAL ) ")
        if CourseID !="" and CA_ratio !="" and Ex_ratio !="":
            # adding COURSE to database
            data= CourseID,C_Credit,CA_ratio,Ex_ratio
            database.cursor.execute("INSERT INTO COURSES(COURSE_ID,CREDIT,CA_R,EX_R) VALUES(?,?,?,?)",data)
            database.con.commit()
            screen_manager.transition.direction = "right"
            screen_manager.current = "CoursesScreen"
            #screen_manager.get_screen("CoursesScreen").course_list.add_widget(CourseCard(CourseID=CourseID, C_Credit=C_Credit,CA_ratio=CA_ratio,Ex_ratio=Ex_ratio))
 
        elif CourseID =="":
            Snackbar(text="Course ID cannot be empty!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1), # type: ignore
                    font_size ="19dp").open() # type: ignore
        elif CA_ratio =="":
            Snackbar(text="CA Weight cannot be empty!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1), # type: ignore
                    font_size ="19dp").open() # type: ignore
        elif Ex_ratio =="":
            Snackbar(text="Exam Weight cannot be empty!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1), # type: ignore
                    font_size ="19dp").open() # type: ignore
#display from databse
    def display_task_complete(self):
        database.cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=1")
        arr =database.cursor.fetchall()
        for i in arr:
            add_task =(TodoCard(pk=i[0],title=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],
                                task_time2=i[5]))                                                             
            add_task.ids.check.active = True
            if add_task.ids.pk !=i[0]:
                screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
           
            #prevent double display of items on list    
            # move reading database from button trigger to read to display when app starts                                                     
    def display_task_incomplete(self):
        database.cursor.execute("SELECT Id,Title,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=0")
        arr =database.cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],title=i[1], description=i[2],
                                                                                  task_date=i[3],task_time=i[4],task_time2=i[5]))
        

# User sign up settings
    def userSignUp(self,user_name,user_email,user_password):
        user_name = screen_manager.get_screen("SignUp").usr_name.text
        user_email = screen_manager.get_screen("SignUp").usr_email.text
        user_password = screen_manager.get_screen("SignUp").usr_pass.text

        if user_name !="" and user_email !="" and user_password !="" and len(user_name)<21 and len(user_password)<60:
            data = (user_name,user_email,user_password)
            database.cursor.execute("INSERT INTO LOGIN VALUES(?,?,?)",data)
            database.con.commit()
            screen_manager.transition.direction = "right"
            screen_manager.current = "Home"

        elif user_name =="":
            Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
        elif user_email =="":
            Snackbar(text="Email  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
        elif user_password =="":
            Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open() # type: ignore
        elif len(user_name)>21:
            Snackbar(text="Username must<21",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open()
        elif len(user_password)>61 :
            Snackbar(text="Password must<61",snackbar_x ="10dp",snackbar_y ="10dp",
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                    font_size ="19dp").open() # type: ignore

# user login settings
    def userlogin(self,user_name,user_password):
            
        user_name = screen_manager.get_screen("Login").usr_Username.text
        user_password = screen_manager.get_screen("Login").usr_password.text
        
        database.cursor.execute("SELECT Name,Password FROM LOGIN")
        arr =database.cursor.fetchall()
        for i in arr:
            usname = i[0]
            uspassword = i[1]
           
            if user_name !="" and user_password !="" and user_name == usname and user_password == uspassword:
                screen_manager.transition.direction = "right"
                screen_manager.current = "Home"

            elif user_name =="":
                Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                        font_size ="19dp").open() # type: ignore
            elif user_password =="":
                Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                        font_size ="19dp").open()
            elif user_name != usname:
                Snackbar(text="Invalid username",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
                        font_size ="19dp").open()
            elif user_password != uspassword:
                Snackbar(text="Invalid password",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,1),
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

    def Noteschooser(self):
        colors = [(85/255,204/255,96/255,1),(43/255,175/255,252/255,1),
                  (158/255,245/255,1,1),(186/255,232/255,172/255,1),(120/255,127/255,246/255,1)]
        d = random.choice(colors)
        return d
    def Courseschooser(self):
        pigments =[(121/255,126/255,246/255,1),(74/255,222/255,222/255,1),
                  (26/255,167/255,236/255,1),(130/255,215/255,255/255,1)]
        p =random.choice(pigments)
        return p

if __name__ == "__main__":   
    
    MainApp().run()

