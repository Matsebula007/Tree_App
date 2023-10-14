from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager ,FadeTransition,Screen
from kivy.properties import StringProperty,ListProperty,NumericProperty
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.pickers import MDTimePicker
from kivy.clock import Clock
#from dateutil import tz 

from datetime import date ,datetime
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.behaviors import HoverBehavior
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
import random
import sqlite3


class database():
    con = sqlite3.connect('User_Database.db')
    cursor = con.cursor()

class HoverButton(Button,HoverBehavior):
    background =ListProperty((30/255,47/255,151/255,.4))
    def on_enter(self):
        self.background = ((26/255,167/255,236/255,1))
        Animation(size_hint =(.28,.05),d=0.3).start(self)
    def on_leave(self):
        self.background = ((30/255,47/255,151/255,.4))
        Animation(size_hint =(.2,.046),d=0.1).start(self)

    pass

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


class TaskCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, cardpk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.cardpk = cardpk

    weekday = StringProperty()
    daydate = StringProperty()
    title = StringProperty()
    frmtime = StringProperty()
    totime = StringProperty()
    

class TodoCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark_task_as_complete(self, taskid):
        database.cursor.execute("UPDATE TASK SET completed=1 WHERE id=?", (taskid,)) # type: ignore
        database.con.commit()

    def mark_task_as_incomplete(self, taskid):
        database.cursor.execute("UPDATE TASK SET completed=0 WHERE id=?", (taskid,))
        database.con.commit()
        task_text = database.cursor.execute("SELECT Description FROM TASK WHERE Id=?", (taskid,)).fetchall()
        return task_text[0][0]
    
    def delete_task(self, taskid):
        database.cursor.execute("DELETE FROM TASK WHERE Id=?", (taskid,))
        database.con.commit()

    tittle = StringProperty()
    description = StringProperty()
    task_date= StringProperty()
    task_time = StringProperty()
    task_time2 = StringProperty()

class OverviewCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, categ_key=None, **kwargs):
        super().__init__(**kwargs)
        # state a categ_key which we shall use link the list items with the database primary keys
        self.course_key = categ_key

    Category=StringProperty()
    Letter_grade=StringProperty()
    TUG_count=StringProperty()
    Contribution=StringProperty()
    def Navigate(self):
        screen_manager.transition = FadeTransition()
        screen_manager.current = "AssessmentSummary"

    def add_categmary(self,catName,catContr):
        screen_manager.get_screen("AssessmentSummary").categName.text =f"{catName}"
        screen_manager.get_screen("AssessmentSummary").categContrib.text =f"{catContr}"
        pass


class CourseCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self, course_key=None, **kwargs):
        super().__init__(**kwargs)
        # state a course_key which we shall use link the list items with the database primary keys
        self.course_key = course_key
    def navigate(self):
        self.add_Overview()
        screen_manager.transition = FadeTransition()
        screen_manager.current = "overviewscreen"
        #screen_manager.current = "addAssesment"
        pass

    def add_Overview(self):
        tugcount = str(5)+" TUG"
        contrib= str(40)
        add_categ =(OverviewCard(categ_key=0,Category="ASSIGNMENT",Letter_grade="B+",TUG_count=tugcount,Contribution=contrib))
        screen_manager.get_screen("overviewscreen").category_list.add_widget(add_categ)

    crsaverage = NumericProperty(78)
    CourseID = StringProperty()
    C_Credit = StringProperty()
    C_CA=StringProperty()
    C_Basis=StringProperty()
    CA_ratio=StringProperty()
    Ex_ratio=StringProperty()


class OverviewScreen(MDScreen,MDFloatLayout):
    #Category to overview
    def on_enter(self):
        pass
    def on_leave(self,*args):
        pass
        

class AssesSummary(MDScreen,MDFloatLayout):
    #Assessment  overview
    def on_enter(self):
        pass
    def on_leave(self,*args):
        pass


class Account(MDScreen):
    name = StringProperty()
    Department = StringProperty()


class MainApp(MDApp):  
    
#Screen manager build
    def build(self):
        global screen_manager
        self.tiTtle ="myUNESWA Tree"
        screen_manager = ScreenManager()
        """ screen_manager.add_widget(Builder.load_file("Screens/Main.kv"))
        screen_manager.add_widget(Builder.load_file("Screens/Login.kv"))  
        screen_manager.add_widget(Builder.load_file("Screens/SignUp.kv")) """ 
        screen_manager.add_widget(Builder.load_file('Screens/HomeScreen.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/TaskView.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/AddTask.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/CoursesView.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/Addcourse.kv'))
        Builder.load_file('Screens/OverviewScr.kv')
        Builder.load_file('Screens/AssesSummary.kv')
        screen_manager.add_widget(AssesSummary(name="AssessmentSummary"))
        screen_manager.add_widget(OverviewScreen(name='overviewscreen'))
        screen_manager.add_widget(Builder.load_file('Screens/AddAssessment.kv'))
        screen_manager.add_widget(Builder.load_file('Screens/AccountScreen.kv'))

        Window.size = [300, 600]
        return screen_manager
    

    def get_tasks(self):
        uncomplete_tasks = database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 0").fetchall()
        completed_tasks = database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 1").fetchall()
        return completed_tasks, uncomplete_tasks
    def get_courses(self):
        taken_courses = database.cursor.execute("SELECT ID, COURSE_ID,CREDIT,CA_R,EX_R FROM COURSES").fetchall()
        return taken_courses
    def get_schedule(self):
        schedule = database.cursor.execute("SELECT Id,Date,Tittle,FromTime,ToTime FROM TASK  WHERE completed = 0").fetchall()
        return schedule
    def on_start(self):
        today = date.today()
        wd = date.weekday(today)
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
        year = str(datetime.now().year)
        month = str(datetime.now().strftime("%b"))
        day = str(datetime.now().strftime("%d"))
        screen_manager.get_screen("todoScreen").date_text.text = f"{days[wd]}, {day} {month}"
       
        try:
            completed_tasks, uncomplete_tasks = self.get_tasks()
            taken_courses =self.get_courses()
            toschedule = self.get_schedule()
            if completed_tasks != []:
                for i in completed_tasks: 
                    add_task =(TodoCard(pk=i[0],tittle=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],task_time2=i[5]))
                    add_task.ids.check.active = True 
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            if uncomplete_tasks != []:
                for i in uncomplete_tasks:
                    add_task = TodoCard(pk=i[0],tittle=i[1], description=i[2],task_date=i[3],task_time=i[4],task_time2=i[5])
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            if toschedule !=[]:
                for scl in toschedule:
                    ddname =f"{year} "+scl[1]
                    my_date = datetime.strptime(ddname,"%Y %A %d %B")
                    weekd=my_date.strftime("%A")
                    daydt = my_date.strftime("%d")

                    frtime = datetime.strptime(scl[3],"%H:%M")
                    asd= frtime.time().strftime("%I:%M %p") 
                    totime = datetime.strptime(scl[4],"%H:%M")
                    bsd= totime.time().strftime("%I:%M %p")

                    add_taskHom = TaskCard(cardpk=scl[0],weekday=weekd, daydate=daydt,title=scl[2],frmtime=asd,totime=bsd)
                    screen_manager.get_screen("Home").tasks_home.add_widget(add_taskHom)
            
            if taken_courses !=[]:
                for c in taken_courses:
                    cr= str (c[2])
                    ca = str (c[3])
                    ex = str (c[4])
                    add_course = CourseCard(course_key = c[0],CourseID=c[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)
        except Exception:
            Snackbar(text="Murky Start",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            pass

#calculates total credit taken 
    def creditscal(self):
        database.cursor.execute("SELECT CREDIT FROM COURSES")
        creds = database.cursor.fetchall()
        total_cre =0.0
        for cre in creds:
            for i in cre:
                i =float(i)
                total_cre =total_cre + i
        cred_format ="{:.1f}".format(total_cre)
        return str(cred_format)
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
                bar.md_bg_color =30/255,47/255,151/255,.8 
                TodoCard.mark_task_as_incomplete(task_card,task_card.pk)
#Category selection in add course
    def cat_select(self,value,catW,percentbar):

        if value.active == True:
            percentbar.md_bg_color =0/255,255/255,125/255,1
       
        elif value.active == False:
            catW.text = ""
            percentbar.md_bg_color =0/255,255/255,125/255,.2

#delete widget from view and info from database
    def delete_item(self, task_card):
        screen_manager.get_screen("todoScreen").todo_list.remove_widget(task_card)
        TodoCard.delete_task(task_card,task_card.pk)

#delete widget from HOME view 
    def delete_card(self, task_cardID):
        
        screen_manager.get_screen("Home").tasks_home.remove_widget(task_cardID)
        

#update TASK view 
    def update_task(self,tittle):
        database.cursor.execute("SELECT Id,Description,Date,FromTime,ToTime,completed FROM TASK WHERE Tittle=?",(tittle,))
        arr =database.cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],tittle=tittle, description=i[1],
                                                                                  task_date=i[2],task_time=i[3],task_time2=i[4]))
    def update_taskHome(self,tittle):
        year = str(datetime.now().year)
        database.cursor.execute("SELECT Id,Date,FromTime,ToTime FROM TASK  WHERE Tittle=?",(tittle,))
        tohome = database.cursor.fetchall()
        if tohome !=[]:
            for scl in tohome:
                ddname =f"{year} "+scl[1]
                my_date = datetime.strptime(ddname,"%Y %A %d %B")
                weekd=my_date.strftime("%A")
                daydt = my_date.strftime("%d")

                frtime = datetime.strptime(scl[2],"%H:%M")
                asd= frtime.time().strftime("%I:%M %p") 
                totime = datetime.strptime(scl[3],"%H:%M")
                bsd= totime.time().strftime("%I:%M %p")

                """ day1 =f"{year} "+scl[1]+f" {scl[3]}"
                dday1 = datetime.strptime(day1,"%Y %A %d %B %H:%M" )

                day2 =f"{year} "+scl[1]+f" {scl[4]}"
                dday2 = datetime.strptime(day2,"%Y %A %d %B %H:%M" )
                
                duration = dday2 - dday1
                secsD = duration.total_seconds()
                houRs = divmod(secsD,3600)[0]
                minTs = divmod(secsD,60)[0]

                timeNow=datetime.now()

                print(f"{minTs}" +" Hrs " )
                print(timeNow)
                #print(dday2)

                print(type(my_date.weekday()))
                teks =my_date.weekday()-1 """
                
                add_taskHom = TaskCard(cardpk=scl[0],weekday=weekd, daydate=daydt,title=tittle,frmtime=asd,totime=bsd)
                screen_manager.get_screen("Home").tasks_home.add_widget(add_taskHom)


# add task settings
    def add_todo(self,tittle,description,date_time,task_time,task_time2):
        
        try:
            if tittle !="" and description !="" and len(tittle)<21 and len(description)<61 and date_time!=""and task_time!="" and task_time2!="" :
                # adding task to database
                data= tittle,description,date_time,task_time,task_time2,0
                database.cursor.execute("INSERT INTO TASK(Tittle,Description,Date,FromTime,ToTime,completed) VALUES(?,?,?,?,?,?)",data)
                database.con.commit()
                screen_manager.transition = FadeTransition()
                screen_manager.current = "todoScreen"
                #screen_manager.get_screen("Home").tasks_home.add_widget(TaskCard(tittle=tittle, description=description))

            elif tittle =="":
                Snackbar(text="Tittle is missing",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif description =="":
                Snackbar(text="Description is missing!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore 
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                
            elif len(tittle)>21:
                Snackbar(text="Tittle must be < 21 char",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                screen_manager.get_screen("add_todo").tittle.text=""
            elif len(description)>61:
                Snackbar(text="Description must be < 60 char",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                screen_manager.get_screen("add_todo").description.text=""
            
            elif date_time=="":
                Snackbar(text="Specify date",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                        #add action mybe highlight empty area   
            elif task_time=="":
                Snackbar(text="Specify start time",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
            
            elif task_time2=="":
                Snackbar(text="Specify completion time",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="Task Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            pass
            
#adding new course to course view
    def update_Course(self,Course_ID):
        courID = str(Course_ID)
        CourseID =courID.replace(" ","")
        CourseID = CourseID.upper()
        try:
            database.cursor.execute("SELECT ID,CREDIT,CA_R,EX_R FROM COURSES WHERE COURSE_ID=?",(CourseID,))
            arr =database.cursor.fetchall()
            for c in arr:
                cre=float(c[1])
                cr= str (cre)
                ca = str (c[2])
                ex = str (c[3])
                crse= CourseCard(course_key = c[0],CourseID=CourseID, C_Credit=cr,CA_ratio=ca,Ex_ratio=ex) #type: ignore
                screen_manager.get_screen("CoursesScreen").course_list.add_widget(crse)
                screen_manager.get_screen("CoursesScreen").crtot.text= self.creditscal()
        except Exception:
            Snackbar(text="Course Update Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            pass
     
# add course settings
    def add_course(self,tcheck,testW,acheck,assW,pcheck,preseW,qcheck,quizW,lcheck,labW,gcheck,groupW,ccheck,clswrkW,ocheck,otherW,Course_ID,C_Credit,CA_ratio,Ex_ratio):
        try: 
            if Course_ID!="":
                courID = str(Course_ID)
                CourseID =courID.replace(" ","")
                CourseID = CourseID.upper()
                database.cursor.execute("SELECT COURSE_ID FROM COURSES")
                arr =database.cursor.fetchall()
                takenC=[]
                for crse in arr:
                    for i in crse:
                        takenC.append(i)    

                if CourseID in takenC:
                    Snackbar(text="Course Alredy exist",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
                    
                elif CourseID not in takenC: 
                      
                    if  C_Credit !=""and CA_ratio !=""  and Ex_ratio !="":
                            
                        try:
                            #create databse for course and initialize tables of categories
                            con = sqlite3.connect(f'{CourseID}.db')
                            cursor = con.cursor() # type: ignore
                            CA_ratio=float(CA_ratio)
                            Ex_ratio=float(Ex_ratio)
                            totalRatio=(CA_ratio+Ex_ratio)
                            
                            if totalRatio ==100.0:
                                try:
                                    cursor.execute("CREATE TABLE CATEGORY(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0)")
                                    con.commit()
                                    cursor.execute("CREATE TABLE SUMMARY(ID INTEGER PRIMARY KEY AUTOINCREMENT,CATEGORY TEXT NOT NULL,MARK DECIMAL NOT NULL  DEFAULT 100.0,CAT_CONTRIB DECIMAL,LETGRADE TEXT,TUG_COUNT DECIMAL)")
                                    con.commit()

                                    if tcheck.active == True and testW !="":     
                                        cursor.execute("CREATE TABLE TEST(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        tdata ="TEST",testW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",tdata)
                                        con.commit()
                                    else:pass

                                    if acheck.active ==True and assW !="":     
                                        cursor.execute("CREATE TABLE ASSIGNMENT(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        adata = "ASSIGNMENT",assW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",adata)
                                        con.commit()
                                    else:pass

                                    if pcheck.active ==True and preseW !="":     
                                        cursor.execute("CREATE TABLE PRESENTATION(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        pdata = "PRESENTATION",preseW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",pdata)
                                        con.commit()
                                    else:pass

                                    if qcheck.active ==True and quizW !="":    
                                        cursor.execute("CREATE TABLE QUIZ(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        qdata = "QUIZ",quizW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",qdata)
                                        con.commit()
                                    else:pass

                                    if lcheck.active ==True and labW !="":     
                                        cursor.execute("CREATE TABLE LAB(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        ldata = "LAB",labW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",ldata)
                                        con.commit()                                 
                                    else:pass
                                    
                                    if  gcheck.active ==True and groupW !="":     
                                        cursor.execute("CREATE TABLE GROUPWORK(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        gdata = "GROUPWORK",groupW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",gdata)
                                        con.commit()
                                    else:pass
                                    
                                    if ccheck.active ==True and clswrkW !="":     
                                        cursor.execute("CREATE TABLE CLASSWORK(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        cdata = "CLASSWORK",clswrkW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",cdata)
                                        con.commit()
                                    else:pass

                                    if ocheck.active ==True and otherW !="":     
                                        cursor.execute("CREATE TABLE OTHER(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        odata = "OTHER",otherW
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",odata) 
                                        con.commit()
                                    else:pass
                        
                                    try:   
                                    # adding COURSE to database
                                        data= CourseID,C_Credit,CA_ratio,Ex_ratio
                                        database.cursor.execute("INSERT INTO COURSES(COURSE_ID,CREDIT,CA_R,EX_R) VALUES(?,?,?,?)",data)
                                        database.con.commit()
                                        screen_manager.transition = FadeTransition()
                                        screen_manager.current = "CoursesScreen"       
                                    except Exception:
                                        Snackbar(text="INDE:4:Faulty category weights",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                                font_size ="15dp").open() # type: ignore
                                        pass
                                except Exception:
                                    Snackbar(text="INDE:3: Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                            font_size ="15dp").open() # type: ignore
                                    pass
                            elif totalRatio!=100.0:
                                Snackbar(text="Faulty Course ratio",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                        font_size ="15dp").open() # type: ignore
                        except Exception:
                            Snackbar(text="INDE:2: Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                    font_size ="15dp").open() # type: ignore
                            pass

                    elif C_Credit =="":
                        Snackbar(text="Credit hours empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
                    elif CA_ratio =="":
                        Snackbar(text="CA Weight  empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
                    elif Ex_ratio =="":
                        Snackbar(text="Exam Weight empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
        
            elif Course_ID =="":
                    Snackbar(text="Course ID empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="INDE:1:Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            pass


#clear overview screen
    def clearOverview(self):
        screen_manager.get_screen("overviewscreen").category_list.clear_widgets()
#course summary calculations
    def summariseCourse(self):
        print("Calculations")
        pass
# add course ID to next screen
    def get_id(self,CID,CidCR):
        screen_manager.get_screen("overviewscreen").crseid.text=f"{CID}"
        screen_manager.get_screen("overviewscreen").crsecr.text=f"{CidCR} Cr"
        screen_manager.get_screen("addAssesment").ass_courseid.text=f"{CID}"
        screen_manager.get_screen("AssessmentSummary").crseid.text=f"{CID}"
        screen_manager.get_screen("AssessmentSummary").crsecr.text=f"{CidCR} Cr"
        pass

#get Category from assessment summary to add assessment
    def getCateg(self,categName):
        screen_manager.get_screen("addAssesment").ass_category.text=f"{categName}"

    
#clear input fields
    def clear_screenTask(self):
        screen_manager.get_screen("add_todo").description.text=""
        screen_manager.get_screen("add_todo").tittle.text=""
        screen_manager.get_screen("add_todo").task_date.text=""
        screen_manager.get_screen("add_todo").task_time.text=""
        screen_manager.get_screen("add_todo").task_time2.text=""
        pass
#add assessment
    def add_assessment(self, ass_courseid,ass_mark,ass_contr,ass_category,ass_name):

        try: 
            if  ass_name !=""and ass_category!="" and ass_mark!="" and ass_contr!="":
                assNm = str(ass_name)
                ass_name =assNm.replace(" ","")
                con = sqlite3.connect(f'{ass_courseid}.db')
                cursor = con.cursor() # type: ignore
                cursor.execute(f"SELECT TITTLE FROM {ass_category}")
                arr =cursor.fetchall()
                takenAss=[]
                for asnm in arr:
                    for i in asnm:
                        takenAss.append(i)    

                if ass_name in takenAss:
                    Snackbar(text="Assessment already Exists",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
                    
                elif ass_name not in takenAss:
                    
                    try: 
                        ass_mark =float(ass_mark)
                        ass_contr=float(ass_contr)
                        if  ass_mark<100.01 and ass_contr<100.01:
                            # adding COURSE to database
                            con = sqlite3.connect(f'{ass_courseid}.db')
                            cursor = con.cursor()
                        
                            ass_weight = ass_mark*(ass_contr/100.0)
                            data=ass_name,ass_contr,ass_mark,ass_weight
                                
                            try:
                                cursor.execute(f"INSERT INTO {ass_category}(TITTLE,WEIGHT,MARK,CONTRIB) VALUES(?,?,?,?)",data)
                                con.commit()
                                screen_manager.transition = FadeTransition()
                                screen_manager.current = "CoursesScreen"
                            except Exception:
                                Snackbar(text="Category not in Course!",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                        font_size ="15dp").open()# type: ignore
                                pass
                                
                        if ass_mark >=101.01:
                            Snackbar(text="Mark greater than 100",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore                    
                        elif ass_contr >=100.01:
                            Snackbar(text="Contribution empty default-100",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore
                    except Exception:
                        Snackbar(text="INDE:2:Add Assessment Indigenous error",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open() # type: ignore
                        pass
            elif ass_name =="":
                            Snackbar(text="Assessment name empty",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore
            elif ass_category=="":
                Snackbar(text="Long press to select category",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore   
            elif ass_mark =="":
                Snackbar(text="Mark empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif ass_contr =="":
                Snackbar(text="Contribution empty default-100",snackbar_x ="10dp",snackbar_y ="17dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore   
                
        except Exception:
            Snackbar(text="INDE:1:Course has no Categories",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
        pass

#display from databse
    def display_task_complete(self):
        database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=1")
        arr =database.cursor.fetchall()
        for i in arr:
            add_task =(TodoCard(pk=i[0],tittle=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3],task_time=i[4],
                                task_time2=i[5]))                                                             
            add_task.ids.check.active = True
            if add_task.ids.pk !=i[0]:
                screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
           
            #prevent double display of items on list    
            # move reading database from button trigger to read to display when app starts                                                     
    def display_task_incomplete(self):
        database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed=0")
        arr =database.cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],tittle=i[1], description=i[2],
                                                                                  task_date=i[3],task_time=i[4],task_time2=i[5]))
        

# User sign up settings
    def userSignUp(self,user_name,user_email,user_password):
        user_name = screen_manager.get_screen("SignUp").usr_name.text
        user_email = screen_manager.get_screen("SignUp").usr_email.text
        user_password = screen_manager.get_screen("SignUp").usr_pass.text

        try:
            if user_name !="" and user_email !="" and user_password !="" and len(user_name)<21 and len(user_password)<60:
                data = (user_name,user_email,user_password)
                #prevent more user sign up if one user alredy signed up
                database.cursor.execute("SELECT UserName,Password FROM LOGIN")
                arr =database.cursor.fetchall()
                for i in arr:
                    if i[0] =="" and i[1] =="":

                        database.cursor.execute("INSERT INTO LOGIN VALUES(?,?,?)",data)
                        database.con.commit()
                        screen_manager.transition = FadeTransition()
                        screen_manager.current = "Home"
                    
                    elif i[0] !="" and i[1] !="":
                        Snackbar(text="Illegal Sign UP !",snackbar_x ="10dp",snackbar_y ="10dp",
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open()
            elif user_name =="":
                Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open()
            elif user_email =="":
                Snackbar(text="Email  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open()
            elif user_password =="":
                Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
            elif len(user_name)>21:
                Snackbar(text="Username must<21",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open()
            elif len(user_password)>61 :
                Snackbar(text="Password must<61",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="Sign Up Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            pass

# user login settings
    def userlogin(self,user_name,user_password):
            
        user_name = screen_manager.get_screen("Login").usr_Username.text
        user_password = screen_manager.get_screen("Login").usr_password.text
        try:
            database.cursor.execute("SELECT UserName,Password FROM LOGIN")
            arr =database.cursor.fetchall()
            for i in arr:
                usname = i[0]
                uspassword = i[1]
            
                if user_name !="" and user_password !="" and user_name == usname and user_password == uspassword:
                    screen_manager.transition = FadeTransition()
                    screen_manager.current = "Home"

                elif user_name =="":
                    Snackbar(text="Username  missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                            font_size ="15dp").open() # type: ignore
                elif user_password =="":
                    Snackbar(text="Password missing!",snackbar_x ="10dp",snackbar_y ="10dp",
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                            font_size ="15dp").open()
                elif user_name != usname:
                    Snackbar(text="Invalid username",snackbar_x ="10dp",snackbar_y ="10dp",
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                            font_size ="15dp").open()
                elif user_password != uspassword:
                    Snackbar(text="Invalid password",snackbar_x ="10dp",snackbar_y ="10dp",
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                            font_size ="15dp").open()
        except Exception:
            Snackbar(text="Login Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            pass

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
        
        previous_time = datetime.strptime("16:20:00",'%H:%M:%S').time()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)
        time_dialog.bind(time=self.get_time) #type: ignore
        time_dialog.open() # type: ignore

    def get_time2(self,instance,time):
        Time= time.strftime('%H:%M')
        screen_manager.get_screen("add_todo").task_time2.text = str(Time)

    def show_time_picker2(self):
        '''Open time picker dialog.'''
        previous_time = datetime.strptime("16:20:00",'%H:%M:%S').time()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)
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
    
     
    """ database.cursor.execute("DROP TABLE TASK") 
    for it in range(37,56,1):
        database.cursor.execute(f"DELETE FROM COURSES WHERE ID ={it}")
        database.con.commit()
        
    database.con.commit() 
    database.cursor.execute("DELETE FROM COURSES WHERE ID =29")
    database.con.commit() 
                                                                 
    database.cursor.execute("CREATE TABLE TASK(Id INTEGER PRIMARY KEY AUTOINCREMENT,Tittle VARCHAR(20) NOT NULL,Description VARCHAR(20) NOT NULL,Date TEXT,FromTime TEXT,ToTime TEXT, completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))) ")
    database.con.commit() """ 
    """ database.cursor.execute("DELETE FROM COURSES WHERE ID =15")
    database.con.commit()
    database.cursor.execute("DELETE FROM COURSES WHERE ID =16")
    database.con.commit() """

    """ sr ="ENG 221"
    database.cursor.execute("DELETE FROM ALLASSESSMENT WHERE TUG_ID =1")
    database.cursor.execute("DELETE FROM ALLASSESSMENT WHERE TUG_ID =4")
    database.cursor.execute("DELETE FROM ALLASSESSMENT WHERE TUG_ID =5")
    database.cursor.execute("DELETE FROM ALLASSESSMENT WHERE COURSE_ID =?",(sr,))
    database.cursor.execute("DROP TABLE ALLASSESSMENT")
    database.con.commit()
    database.cursor.execute("CREATE TABLE ALLASSESSMENT(COURSE_ID TEXT NOT NULL,TUG_ID INTEGER PRIMARY KEY AUTOINCREMENT,CATEGORY TEXT SECONDARY KEY,MARK DECIMAL NOT NULL  DEFAULT 100.0,CONTRIB DECIMAL NOT NULL DEFAULT 100.0,TUG_WEIGHT DECIMAL,TUG_NAME TEXT NOT NULL,FOREIGN KEY(COURSE_ID) REFERENCES COURSES(COURSE_ID)) ")
    database.con.commit() """