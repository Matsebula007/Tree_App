import random
import sqlite3
from datetime import date, datetime, timedelta

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.behaviors import CommonElevationBehavior, HoverBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar

Window.softinput_mode ="below_target"

class Database(): 
    """_summary_
    """    
    con = sqlite3.connect('db/user_database.db')
    cursor = con.cursor()
    
class HoverButton(Button,HoverBehavior):
    """_summary_

    Args:
        Button (_type_): _description_
        HoverBehavior (_type_): _description_
    """    
    background =ListProperty((30/255,47/255,151/255,.4))
    def on_enter(self):
        
        self.background = ((26/255,167/255,236/255,1))
        Animation(size_hint =(.24,.05),d=0.3).start(self)
    def on_leave(self):
        self.background = ((30/255,47/255,151/255,.4))
        Animation(size_hint =(.2,.046),d=0.1).start(self)

class CircularProgressBar(AnchorLayout):
    """_summary_

    Args:
        AnchorLayout (_type_): _description_
    """    
    set_value = NumericProperty(0)
    bar_color = ListProperty([244/255,249/255,253/255])
    text =StringProperty("0%")
    counter =1
    value =NumericProperty(1)
    duration=NumericProperty(1.5)
    
    def __init__(self,**kwargs):
        super(CircularProgressBar,self).__init__(**kwargs)
        Clock.schedule_once(self.animate,0)
    def animate(self,*args):
        """_summary_
        """        
        Clock.schedule_interval(self.percent_counter,self.duration/self.value)
    def percent_counter(self,*args):
        """_summary_
        """        
        if self.counter < self.value:
            self.counter += 1
            self.text =f"{self.counter}%"
            self.set_value =self.counter
        else:
            Clock.unschedule(self.percent_counter)

class TaskCard(CommonElevationBehavior,MDFloatLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    #HOME SCHEDULE
    def __init__(self, cardpk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the Database primary keys
        self.cardpk = cardpk

    weekday = StringProperty()
    venue = StringProperty()
    title = StringProperty()
    frmtime = StringProperty()
    totime = StringProperty()

class AssessmentCard(CommonElevationBehavior,MDFloatLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    def __init__(self, testpk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the card  with the Database item primary keys
        self.testpk = testpk
    testName=StringProperty()
    testWeight= StringProperty()
    testMark =StringProperty()
    testContrib =StringProperty()

    def Navigate(self):
        ass_courseid =screen_manager.get_screen("AssessmentSummary").crseid.text
        ass_category =screen_manager.get_screen("AssessmentSummary").categName.text
        MainApp.update_assessment(MainApp,ass_courseid,ass_category)
        MainApp.summariseCourse(MainApp)

        
class TodoCard(CommonElevationBehavior,MDFloatLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the card with the Database item primary keys
        self.pk = pk

    def mark_task_as_complete(self, taskid):
        """_summary_

        Args:
            taskid (_type_): _description_
        """        
        Database.cursor.execute("UPDATE TASK SET completed=1 WHERE id=?", (taskid,)) # type: ignore
        Database.con.commit()

    def mark_task_as_incomplete(self, taskid):
        """_summary_

        Args:
            taskid (_type_): _description_

        Returns:
            _type_: _description_
        """        
        try:

            Database.cursor.execute("UPDATE TASK SET completed=0 WHERE id=?", (taskid,))
            Database.con.commit()
            task_text = Database.cursor.execute("SELECT Description FROM TASK WHERE Id=?", (taskid,)).fetchall()
            return task_text[0][0]
        except Exception:
            pass
    
    def delete_task(self, taskid):
        """_summary_

        Args:
            taskid (_type_): _description_
        """        
        Database.cursor.execute("DELETE FROM TASK WHERE Id=?", (taskid,))
        Database.con.commit()

    tittle = StringProperty()
    description = StringProperty()
    task_date= StringProperty()

class OverviewCard(CommonElevationBehavior,MDFloatLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    # state a categ_key which we shall use link the card with the Database item primary keys
    def __init__(self, categ_key=None, **kwargs):
        super().__init__(**kwargs)
        self.course_key = categ_key

    Category=StringProperty()
    Grade=StringProperty()
    TUG_count=StringProperty()
    Contribution=StringProperty()

    def Navigate(self):
        """_summary_
        """        
        screen_manager.transition = FadeTransition()
        screen_manager.current = "AssessmentSummary"

    def add_categmary(self,categ_name,cat_contrb,grade):
        """_summary_

        Args:
            catName (_type_): _description_
            catContr (_type_): _description_
            Grade (_type_): _description_
        """        
        screen_manager.get_screen("AssessmentSummary").categName.text =f"{categ_name}"
        screen_manager.get_screen("AssessmentSummary").categContrib.text =f"{cat_contrb}"
        screen_manager.get_screen("AssessmentSummary").categavar.text =f"{grade}"
        course_id =screen_manager.get_screen("overviewscreen").crseid.text

        try:
            con = sqlite3.connect(f"{course_id}.db")
            cursor = con.cursor()
            cursor.execute(f"SELECT ID,TITTLE,WEIGHT,MARK,CONTRIB FROM {categ_name}")
            arr = cursor.fetchall()
            for i in arr:
                weght =str(i[2])
                mark=str(i[3])
                contrib=str(i[4])
                add_test =(AssessmentCard(testpk=i[0],testName=i[1],testWeight= weght,testMark = mark,testContrib=contrib))
                screen_manager.get_screen("AssessmentSummary").assessmnt_list.add_widget(add_test)

            cursor.execute("SELECT WEIGHT FROM CATEGORY WHERE TITTLE=?",(categ_name,))
            categ = cursor.fetchone()
            for c in categ:
                screen_manager.get_screen("AssessmentSummary").categWeight.text=str(c)

            screen_manager.transition = FadeTransition()
            screen_manager.current = "AssessmentSummary"
        except Exception:
            Snackbar(text="INDE:1:Assessment summary error",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore

class CourseCard(CommonElevationBehavior,MDFloatLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    # state a course_key which we shall use link the card with the Database item primary keys
    def __init__(self, course_key=None, **kwargs):
        super().__init__(**kwargs)
        self.course_key = course_key
    def navigate(self):
        """_summary_
        """        
        screen_manager.transition = FadeTransition()
        screen_manager.current = "overviewscreen"

    def add_Overview(self,course_id):
        """_summary_

        Args:
            course_id (_type_): _description_
        """        
        con = sqlite3.connect(f"{course_id}.db")
        cursor = con.cursor()
        try:
            cursor.execute("SELECT ID,CATEGORY,MARK,CAT_CONTRIB,TUG_COUNT FROM SUMMARY")
            live_categ = cursor.fetchall()
            for cat in live_categ:
                grade = str(cat[2])
                contrib= str(cat[3])
                tugcount = str(cat[4])+" Tug"
                add_categ =(OverviewCard(categ_key=cat[0],Category=cat[1],Grade=grade,Contribution=contrib,TUG_count=tugcount))
                screen_manager.get_screen("overviewscreen").category_list.add_widget(add_categ)
        except Exception:
            Snackbar(text="IDE:Ovev:1:Hot Overview ",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore
        #add categories with zero assessments
        try:
            cursor.execute("SELECT CATEGORY FROM SUMMARY")
            live_categ = cursor.fetchall()
            live_cat=[]
            for categ in live_categ:
                for cat in categ:
                    live_cat.append(cat)    
            cursor.execute("SELECT TITTLE FROM CATEGORY")
            dead_cat = cursor.fetchall()
            for dcateg in dead_cat:
                for deadcat in dcateg:
                    if deadcat not in live_cat:
                        grade = str(0)
                        contrib= str(0)
                        tugcount = str(0)+" Tug"
                        add_categ =(OverviewCard(categ_key=0,Category=deadcat,Grade=grade,Contribution=contrib,TUG_count=tugcount))
                        screen_manager.get_screen("overviewscreen").category_list.add_widget(add_categ)
        except Exception:
            Snackbar(text="IDE:Ovev:2:Hot Overview ",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore
    crsavg = NumericProperty(1)
    CourseID = StringProperty()
    C_Credit = StringProperty()
    C_CA=StringProperty()
    Basis=StringProperty()
    CA_ratio=StringProperty()
    Ex_ratio=StringProperty()

class CourseDisplayCard(CommonElevationBehavior,MDFloatLayout):
    def navigate(self):
        """_summary_
        """        
        screen_manager.transition = FadeTransition()
        screen_manager.current = "CoursesScreen"

    Courseid=StringProperty("PHY312")
    average=StringProperty("0")

class OverviewScreen(MDScreen,MDFloatLayout):
    """_summary_

    Args:
        MDScreen (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    pass

class AssesSummary(MDScreen,MDFloatLayout):
    """_summary_

    Args:
        MDScreen (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    pass

class TableCard(CommonElevationBehavior,MDFloatLayout,MDGridLayout):
    """_summary_

    Args:
        CommonElevationBehavior (_type_): _description_
        MDFloatLayout (_type_): _description_
    """    
    def __init__(self,key=None, **kwargs):
        super().__init__(**kwargs)
        # state a tablecard_key which we shall use link the card with the Database item primary keys
        self.key=key
    event_Name =StringProperty("PHY312")
    start_time =StringProperty("08:30 AM")
    end_time =StringProperty("02:30 PM")
    event_venue = StringProperty("EMPORIUM")
    evnt_date =StringProperty("21")
    evnt_day =StringProperty("Tue")
    duratn=StringProperty("48.7")

class WeekdayCard(CommonElevationBehavior,MDFloatLayout):
    dayname=StringProperty("")

class DaySelectionCard(CommonElevationBehavior,MDFloatLayout):
    selected_day= StringProperty("Sunday")

class MonthCard(CommonElevationBehavior,MDFloatLayout):
    def __init__(self,key=None, **kwargs):
        super().__init__(**kwargs)
        # state a MonthCard_key which we shall use link the card with the Database item primary keys
        self.key=key
    evnt_day =StringProperty("Tue")
    evnt_date= StringProperty("21")
    task_number=StringProperty("4") 
    evnt_hours=StringProperty("8")


class MainApp(MDApp):
    """_summary_
    Args:
        MDApp (_type_): _description_

    Returns:
        _type_: _description_
    """
    def build(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("screens/home.kv"))
        screen_manager.add_widget(Builder.load_file('screens/homeScreen.kv'))
        screen_manager.add_widget(Builder.load_file('screens/taskView.kv'))
        screen_manager.add_widget(Builder.load_file('screens/addTask.kv'))
        screen_manager.add_widget(Builder.load_file('screens/coursesView.kv'))
        screen_manager.add_widget(Builder.load_file('screens/addcourse.kv'))
        screen_manager.add_widget(Builder.load_file('screens/addAssessment.kv'))
        screen_manager.add_widget(Builder.load_file('screens/calendarscreen.kv'))
        screen_manager.add_widget(Builder.load_file('screens/current_month.kv'))
        screen_manager.add_widget(Builder.load_file('screens/addEvent.kv'))
        Builder.load_file('screens/overviewScreen.kv')
        Builder.load_file('screens/assesSummary.kv')
        screen_manager.add_widget(AssesSummary(name="AssessmentSummary"))
        screen_manager.add_widget(OverviewScreen(name='overviewscreen'))

        Window.size = [350, 650]
        return screen_manager
    
    def get_tasks(self):
        """_summary_
            gets all checked and unchecked tasks from user_database 
        Returns:
            tuple-list: all tasks from user_database
        """        
        uncomplete_tasks = Database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 0").fetchall()
        completed_tasks = Database.cursor.execute("SELECT Id,Tittle,Description,Date,FromTime,ToTime,completed FROM TASK WHERE completed = 1").fetchall()
        return completed_tasks, uncomplete_tasks
    def get_courses(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        taken_courses = Database.cursor.execute("SELECT ID, COURSE_ID,CREDIT,CA_R,EX_R,CA,BASIS FROM COURSES WHERE CA IS NOT NULL").fetchall()
        return taken_courses
    def get_emptycrse(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        taken_courses = Database.cursor.execute("SELECT ID, COURSE_ID,CREDIT,CA_R,EX_R,CA,BASIS FROM COURSES WHERE CA IS NULL").fetchall()
        return taken_courses
    def get_schedule(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        schedule = Database.cursor.execute("SELECT ID,TITTLE,VENUE,DAY,ST_TIME,ED_TIME FROM EVENT  WHERE ID IS NOT NULL").fetchall()
        return schedule
                                                          

    def on_start(self):
        """_summary_
        """        
        today = date.today()
        wd = date.weekday(today)
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
        #year = str(datetime.now().year)
        month = str(datetime.now().strftime("%b"))
        fullmonth = str(datetime.now().strftime("%B"))
        day = str(datetime.now().strftime("%d"))
        dtod=str(datetime.now().strftime("%a"))
        screen_manager.get_screen("todoScreen").date_text.text = f"{days[wd]}, {day} {month}"
        screen_manager.get_screen("Calendarscreen").table_month.text = f"{fullmonth}"
        screen_manager.get_screen("monthscreen").table_month.text = f"{fullmonth}"
        
        #updates course summary   
        self.summariseCourse()
        #create month
        self.create_month()
        self.clear_for_week()
        self.clear_for_month()
       
        try:
            completed_tasks, uncomplete_tasks = self.get_tasks()
            taken_courses =self.get_courses()
            empty_course=self.get_emptycrse()
            toschedule = self.get_schedule()
            if completed_tasks != []:
                for i in completed_tasks: 
                    add_task =TodoCard(pk=i[0],tittle=i[1],description= f"[s]{i[2]}[/s]",task_date=i[3]) # type: ignore
                    add_task.ids.check.active = True 
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            else:pass
            if uncomplete_tasks != []:
                for i in uncomplete_tasks:
                    add_task = TodoCard(pk=i[0],tittle=i[1], description=i[2],task_date=i[3]) 
                    screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
                    
            elif completed_tasks==[] and uncomplete_tasks==[]:
                add_task = TodoCard(pk=0,tittle="Welcome", description="Added notes appear here",task_date=f"{days[wd]}, {day} {month}")
                screen_manager.get_screen("todoScreen").todo_list.add_widget(add_task)
            if toschedule !=[]:
                for scl in toschedule:
                    if scl[3]==dtod:
                        add_taskhome = TaskCard(cardpk=scl[0],weekday=scl[3],title=scl[1],venue=scl[2],frmtime=scl[4],totime=scl[5])
                        screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
                    if scl[3]!=dtod:
                        screen_manager.get_screen("Home").tasks_home.clear_widgets()
                        add_taskhome = TaskCard(cardpk=0,weekday="Tue", venue="S1.2",title="PHY101 lab4",frmtime="01:00PM",totime="03:00PM")
                        screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
                
            elif toschedule==[]:
                add_taskhome = TaskCard(cardpk=0,weekday=dtod, venue="Here",title="No events",frmtime="00:00AM",totime="11:59PM")
                screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
            else:
                add_taskhome = TaskCard(cardpk=0,weekday=dtod, venue="Here",title="No events",frmtime="00:00AM",totime="11:59PM")
                screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
                
            if taken_courses !=[]:
                for c in taken_courses:
                    cred =float(c[2])
                    cr= str (cred)
                    ca = str (c[3])
                    ex = str (c[4])
                    bas = str (c[6])
                    add_course = CourseCard(course_key = c[0],CourseID=c[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex,crsavg=c[5],Basis=bas)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)
                    crse_hom = CourseDisplayCard(Courseid=c[1],average=str(c[5])+" %")
                    screen_manager.get_screen("Home").course_home.add_widget(crse_hom)
                for empty_crs in empty_course:
                    cr= str (empty_crs[2])
                    ca = str (empty_crs[3])
                    ex = str (empty_crs[4])
                    avg =1.0
                    bas = "0"
                    add_course = CourseCard(course_key = empty_crs[0],CourseID=empty_crs[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex,crsavg=avg,Basis=bas)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)
                    crse_hom = CourseDisplayCard(Courseid=empty_crs[1], average="0.0 %")
                    screen_manager.get_screen("Home").course_home.add_widget(crse_hom)

            elif taken_courses ==[] and empty_course ==[]:
                crse_hom = CourseDisplayCard(Courseid="PHY101", average="0.0 %")
                screen_manager.get_screen("Home").course_home.add_widget(crse_hom)
                pass
        except Exception:
            Snackbar(text="Murky Start",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore


#calculates total credit taken 
    def creditscal(self):
        """_summary_

        Returns:
            _type_: _description_
        """         
        Database.cursor.execute("SELECT CREDIT FROM COURSES")
        creds = Database.cursor.fetchall()
        total_cre =0.0
        for cre in creds:
            for i in cre:
                i =float(i)
                total_cre =total_cre + i
        cred_format ="{:.1f}".format(total_cre)
        return str(cred_format)

#checkbox seetings
    def on_complete(self,task_card,value,description):
        if value.active == True:
            description.text = f"[s]{description.text}[/s]"
            TodoCard.mark_task_as_complete(task_card,task_card.pk)
        else:
            remove = ["[s]", "[/s]"]
            for i in remove:
                description.text = description.text.replace(i,"")
                TodoCard.mark_task_as_incomplete(task_card,task_card.pk)

# date pickers
    def on_save(self, instance, value, date_range):
        """_summary_

        Args:
            instance (_type_): _description_
            value (_type_): _description_
            date_range (_type_): _description_
        """        
        value = value.strftime('%A %d %B')
        screen_manager.get_screen("add_todo").task_date.text = str(value)
    
    def on_sdate_save(self, instance, value, date_range):
        """_summary_

        Args:
            instance (_type_): _description_
            value (_type_): _description_
            date_range (_type_): _description_
        """        
        value = value.strftime('%a %d %b %Y')
        screen_manager.get_screen("add_event").start_date.text = str(value)

    def on_edate_save(self, instance, value, date_range):
        """_summary_

        Args:
            instance (_type_): _description_
            value (_type_): _description_
            date_range (_type_): _description_
        """        
        value = value.strftime('%a %d %b %Y')
        screen_manager.get_screen("add_event").end_date.text = str(value)

    def on_cancel(self):
        """_summary_
        """        
        MDDatePicker.close() # type: ignore

    def show_date_picker(self):
        """_summary_
        """        
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save) #type: ignore
        date_dialog.open()#type: ignore

    def event_Sdate_picker(self):
        """_summary_
        """        
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_sdate_save) #type: ignore
        date_dialog.open()#type: ignore

    def event_Edate_picker(self):
        """_summary_
        """        
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_edate_save) #type: ignore
        date_dialog.open()#type: ignore

#time pickers
    def get_time(self,instance,time):
        """_summary_

        Args:
            instance (_type_): _description_
            time (_type_): _description_
        """        
        time= time.strftime('%H:%M')
        screen_manager.get_screen("add_todo").task_time.text = str(time)  

    def get_stime(self,instance,time):
        """_summary_

        Args:
            instance (_type_): _description_
            time (_type_): _description_
        """        
        time= time.strftime('%H:%M')
        screen_manager.get_screen("add_event").start_time.text = str(time)      
    def get_etime(self,instance,time):
        """_summary_

        Args:
            instance (_type_): _description_
            time (_type_): _description_
        """        
        time= time.strftime('%H:%M')
        screen_manager.get_screen("add_event").end_time.text = str(time)      

    def event_Stime_picker(self):
        '''Open time picker dialog.'''       
        previous_time = datetime.strptime("16:20:00",'%H:%M:%S').time()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)#type: ignore
        time_dialog.bind(time=self.get_stime) #type: ignore
        time_dialog.open() # type: ignore
    def event_Etime_picker(self):
        '''Open time picker dialog.'''       
        previous_time = datetime.strptime("16:20:00",'%H:%M:%S').time()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)#type: ignore
        time_dialog.bind(time=self.get_etime) #type: ignore
        time_dialog.open() # type: ignore
    
    

#color choosers
    def noteschooser(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        colors = [(66/255,133/255,244/255,1),(186/255,232/255,172/255,1),(120/255,127/255,246/255,1)]
        d = random.choice(colors)
        return d
    def courseschooser(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        pigments =[(26/255,167/255,236/255,1),(74/255,222/255,222/255,1),(130/255,215/255,255/255,1)]
        p =random.choice(pigments)
        return p
    def calendarchooser(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        pigments =[(123/255,223/255,242/255,.8),(30/255,47/255,151/255,.6),(130/255,215/255,255/255,.8)]
        p =random.choice(pigments)
        return p

#Category selection in add course
    def cat_select(self,value,cat_w,percentbar):
        """_summary_

        Args:
            value (_type_): _description_
            catW (_type_): _description_
            percentbar (_type_): _description_
        """        
        if value.active is True:
            percentbar.md_bg_color =0/255,255/255,125/255,1
            cat_w.text = ""
        elif value.active is False:
            cat_w.text = "0"
            percentbar.md_bg_color =0/255,255/255,125/255,.2
#Category selection in add course
    def avg_color(self,mark):
        """_summary_

        Args:
            mark (_type_): _description_

        Returns:
            _type_: _description_
        """         
        mark=float(mark)
        color=(52/255,168/255,83/255,1)
        if mark<50.0000000000001:
            color =(234/255,67/255,53/255,1)
        if mark>49.9999999999999:
            color =(2/255,44/255,26/255,1)
        if mark<0.0:
            color =(52/255,168/255,83/255,1)
        return color
    
    def dayintensiy(self,month_card):
        hours=float(month_card.evnt_hours)
        shade = (30/255,47/255,151/255,.4)
        if hours<5.0:
           shade =(30/255,47/255,151/255,.4)
        if hours<8.0 and hours>4.0:
            shade =(30/255,47/255,151/255,.6)
        if hours<10.0 and hours>8.0:
            shade =(30/255,47/255,151/255,.8)
        if hours>10.0:
            shade =(30/255,47/255,151/255,.9)
        return shade


    def asmark_color(self,mark,weight):
        """_summary_

        Args:
            mark (_type_): _description_

        Returns:
            _type_: _description_
        """         
        if weight!="":
            weight=float(weight)
            mark=float(mark)
            weight_check =weight/2.0
            color=(52/255,168/255,83/255,1)
            if mark<(weight_check+0.0000000000001):
                color =(234/255,67/255,53/255,1)
            if mark>(weight_check-0.0000000000001):
                color =(2/255,44/255,26/255,1)
            if mark<0.0:
                color =(52/255,168/255,83/255,1)
            return color
        else:
            color=(52/255,168/255,83/255,1)
            return color


# add course ID to next screen
    def get_id(self,crseid,crs_cr):
        """_summary_

        Args:
            CID (_type_): _description_
            CidCR (_type_): _description_
        """        
        screen_manager.get_screen("overviewscreen").crseid.text=f"{crseid}"
        screen_manager.get_screen("overviewscreen").crsecr.text=f"{crs_cr} Cr"
        screen_manager.get_screen("addAssesment").ass_courseid.text=f"{crseid}"
        screen_manager.get_screen("AssessmentSummary").crseid.text=f"{crseid}"
        screen_manager.get_screen("AssessmentSummary").crsecr.text=f"{crs_cr} Cr"
        pass

#get Category from assessment summary to add assessment
    def getCateg(self,categ_name):
        """_summary_

        Args:
            categ_name (_type_): _description_
        """        
        screen_manager.get_screen("addAssesment").ass_category.text=f"{categ_name}"
        categ_name =str(categ_name)
        categ_name =categ_name.lower()
        screen_manager.get_screen("addAssesment").ass_name.hint_text =f"{categ_name} name"

#Delete event from view and from database 
    def delete_event(self,table_card,tittle): 
        screen_manager.get_screen("Calendarscreen").table_list.remove_widget(table_card)
        Database.cursor.execute("DELETE FROM EVENT WHERE TITTLE=?", (tittle,))
        Database.con.commit()
        self.update_home_sche()
        self.update_month()

    def pendingupdate(self):
        Snackbar(text="Calendar functionality pending update",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                font_size ="15dp").open() # type: ignore

#update home view when new event added
    def update_home_sche(self):
        live_date =str(datetime.now())
        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
        dtoday=live_date.strftime("%a")
        toschedule = self.get_schedule()
        screen_manager.get_screen("Home").tasks_home.clear_widgets()
        if toschedule !=[]:
            for scl in toschedule:
                if scl[3]==dtoday:
                    add_taskhome = TaskCard(cardpk=scl[0],weekday=scl[3],title=scl[1],venue=scl[2],frmtime=scl[4],totime=scl[5])
                    screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
                elif  scl[3]!=dtoday:
                    screen_manager.get_screen("Home").tasks_home.clear_widgets()
                    add_taskhome = TaskCard(cardpk=0,weekday=dtoday, venue="Here",title="No events",frmtime="00:00AM",totime="11:59PM")
                    screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)
        elif toschedule==[]:
            add_taskhome = TaskCard(cardpk=0,weekday=dtoday, venue="Here",title="No events",frmtime="00:00AM",totime="11:59PM")
            screen_manager.get_screen("Home").tasks_home.add_widget(add_taskhome)

        


#delete widget from view and info from Database HOME and task
    def delete_item(self, task_card):
        """_summary_

        Args:
            task_card (_type_): _description_
        """        
        screen_manager.get_screen("todoScreen").todo_list.remove_widget(task_card)
        TodoCard.delete_task(task_card,task_card.pk)

#delete assessment form database
    def delete_assmt(self,card,tittle):
        screen_manager.get_screen("AssessmentSummary").assessmnt_list.remove_widget(card)
        courseID=screen_manager.get_screen("AssessmentSummary").crseid.text
        category=screen_manager.get_screen("AssessmentSummary").categName.text
        con = sqlite3.connect(f'{courseID}.db')
        cursor = con.cursor() # type: ignore
        cursor.execute(f"DELETE FROM {category} WHERE TITTLE=?", (tittle,))
        con.commit()
        self.summariseCourse()
        
      

#clear overview screen
    def clear_overview(self):
        """_summary_
        """        
        screen_manager.get_screen("overviewscreen").category_list.clear_widgets()
        pass
    def clear_assessmary(self):
        """_summary_
        """        
        screen_manager.get_screen("AssessmentSummary").assessmnt_list.clear_widgets()
        pass

#clear input fields
    def clear_screenTask(self):
        """_summary_
        """        
        screen_manager.get_screen("add_todo").description.text=""
        screen_manager.get_screen("add_todo").tittle.text=""
        screen_manager.get_screen("add_todo").task_date.text="Date"
        pass

    def clear_add_assesmnt(self):
        """_summary_
        """        
        screen_manager.get_screen("addAssesment").ass_contr.text=""
        screen_manager.get_screen("addAssesment").ass_mark.text=""
        screen_manager.get_screen("addAssesment").ass_name.text=""
        pass
# view month day tasks
    def view_monthtask(self,dayname,evtdate):
        evtdate=float(evtdate)
        screen_manager.transition = FadeTransition()
        screen_manager.current = "Calendarscreen"

        screen_manager.get_screen("Calendarscreen").days_of_week.clear_widgets()
        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
        screen_manager.get_screen("Calendarscreen").days_of_week.size_hint_x=1
    
        Database.cursor.execute("SELECT ID,TITTLE,VENUE,DAY,ST_DATE,ED_DATE,ST_TIME,ED_TIME,DURATION FROM EVENT")
        event_arr=Database.cursor.fetchall()
        if event_arr!=[]:
            try:
                if dayname=="Mon":
                    view_day=DaySelectionCard(selected_day="Monday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day) 
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)  
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3] == "Mon" and evtmonth == live_month and evtdate != day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Tue":
                    view_day=DaySelectionCard(selected_day="Tuesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Tue" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Wed":
                    view_day=DaySelectionCard(selected_day="Wednesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Wed" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Thu":
                    view_day=DaySelectionCard(selected_day="Thursday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Thu" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Fri":
                    view_day=DaySelectionCard(selected_day="Friday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Fri" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Sat":
                    view_day=DaySelectionCard(selected_day="Saturday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Sat" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Sun":
                    view_day=DaySelectionCard(selected_day="Sunday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        live_date =str(datetime.now())
                        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
                        live_month=live_date.strftime("%m")
                        
                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        ed_date=(datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S"))+timedelta(days=1)
                        day_dt=st_date.strftime("%d")
                        day_de=ed_date.strftime("%d")
                        evtmonth=st_date.strftime("%m")
                        day_de=float(day_de)
                        if evt[3]=="Sun" and evtmonth==live_month and evtdate!=day_de:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
            except Exception:
                Snackbar(text="Weekday load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
        elif event_arr==[]:
            try:
                if dayname=="Mon":
                    view_day=DaySelectionCard(selected_day="Monday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    #add card for empty events in month
                elif dayname=="Tue":
                    view_day=DaySelectionCard(selected_day="Tuesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                elif dayname=="Wed":
                    view_day=DaySelectionCard(selected_day="Wednesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                elif dayname=="Thu":
                    view_day=DaySelectionCard(selected_day="Thursday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                elif dayname=="Fri":
                    view_day=DaySelectionCard(selected_day="Friday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                elif dayname=="Sat":
                    view_day=DaySelectionCard(selected_day="Saturday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                elif dayname=="Sun":
                    view_day=DaySelectionCard(selected_day="Sunday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
            except Exception:
                Snackbar(text="INDE:2: Empty week load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore


#view selected day events
    def selected_weekday(self,dayname):
        screen_manager.transition = FadeTransition()
        screen_manager.current = "Calendarscreen"
        live_date =str(datetime.now())
        live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )

        screen_manager.get_screen("Calendarscreen").days_of_week.clear_widgets()
        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
        screen_manager.get_screen("Calendarscreen").days_of_week.size_hint_x=1

        Database.cursor.execute("SELECT ID,TITTLE,VENUE,DAY,ST_DATE,ED_DATE,ST_TIME,ED_TIME,DURATION FROM EVENT")
        event_arr=Database.cursor.fetchall()
        if event_arr!=[]:
            try:
                
                if dayname=="Mon":
                    view_day=DaySelectionCard(selected_day="Monday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day) 
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Mon" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Tue":
                    view_day=DaySelectionCard(selected_day="Tuesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Tue" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Wed":
                    view_day=DaySelectionCard(selected_day="Wednesday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Wed" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Thu":
                    view_day=DaySelectionCard(selected_day="Thursday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Thu" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Fri":
                    view_day=DaySelectionCard(selected_day="Friday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Fri" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Sat":
                    view_day=DaySelectionCard(selected_day="Saturday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Sat" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                if dayname=="Sun":
                    view_day=DaySelectionCard(selected_day="Sunday")
                    screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                    for evt in event_arr:
                        en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                        week_in= live_date+timedelta(days=8)

                        st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                        day_dt=st_date.strftime("%d")
                        if evt[3]=="Sun" and en_date>live_date+timedelta(days=-7) and st_date<week_in:
                            dur=str(evt[8])+" mins"
                            day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                            screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                
                
            except Exception:
                Snackbar(text="Weekday load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
        else:
            try:
                day_dt=live_date.strftime("%a")
                day_dy=live_date.strftime("%d")
                day_wkd=live_date.strftime("%A")
                
                view_day=DaySelectionCard(selected_day=day_wkd)
                screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
                day_sch =TableCard(key=0,event_Name="No events today",start_time="00:00AM",end_time="11:59PM",event_venue="Here",evnt_date=day_dy,evnt_day=day_dt,duratn="1439 mins")
                screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                
            except Exception:
                Snackbar(text="INDE:2: Empty week load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
#days menu tabs
    def select_day(self):
        screen_manager.get_screen("Calendarscreen").days_of_week.clear_widgets()
        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
        screen_manager.get_screen("Calendarscreen").days_of_week.size_hint_x=None
        screen_manager.get_screen("Calendarscreen").timetable_view.size_hint= .99,.7
        screen_manager.get_screen("Calendarscreen").timetable_view.pos_hint={"center_x":.5,"center_y":.45} 
        days =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        for day in days:
            screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(WeekdayCard(dayname=day ))
        Database.cursor.execute("SELECT ID,TITTLE,VENUE,DAY,ST_DATE,ED_DATE,ST_TIME,ED_TIME,DURATION FROM EVENT")
        event_arr=Database.cursor.fetchall()
        try:
            
            live_date =str(datetime.now())
            live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
            dtoday=live_date.strftime("%a")
            dtdy=live_date.strftime("%d")
            if event_arr!=[]:
                for evt in event_arr:
                    en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                    week_in= live_date+timedelta(days=8)
                    st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                    day_dt=st_date.strftime("%d")
                    if evt[3]==dtoday and en_date>live_date+timedelta(days=-1) and st_date<week_in:
                        dur=str(evt[8])+" mins"
                        day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                        screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                        
                    if evt[3]!=dtoday and en_date>live_date+timedelta(days=-1) and st_date<week_in:
                        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
                        day_sch =TableCard(key=evt[0],event_Name="No events today",start_time="00:00AM",end_time="11:59PM",event_venue="Here",evnt_date=dtdy,evnt_day=dtoday,duratn="1439")
                        screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)

        except Exception:
            Snackbar(text="Select day load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
#add days of current month to database
    def create_month(self):

        Database.cursor.execute("SELECT COUNT(*) FROM ( SELECT 0 FROM MONTH LIMIT 1)")
        count = Database.cursor.fetchone()
        for icount in count:
            if icount!=0:
                for it in range(0,32,1):
                    Database.cursor.execute("DELETE FROM MONTH WHERE ID IS NOT NULL")
                    Database.con.commit()
                now_year = datetime.now().year
                now_month = datetime.now().month
                first_day=datetime(year=now_year,month=now_month,day=1) 
                last_day=datetime(year=now_year,month=now_month+1,day=1)+timedelta(days=-1) 
                first_dy=int(first_day.strftime("%d"))
                last_dy=int(last_day.strftime("%d"))
                for dayof_mnth in range(first_dy,last_dy+1,1):
                    full_dt=datetime(year=now_year,month=now_month,day=dayof_mnth)
                    day_name=str(full_dt.strftime("%a"))
                    evnt_date=str(dayof_mnth)
                    task_count=0
                    task_duratn="0"
                    data= day_name,evnt_date,task_count,task_duratn
                    Database.cursor.execute("INSERT INTO MONTH(DAY,DATE,TASK,HOURS) VALUES(?,?,?,?)",data)
                    Database.con.commit()
                else:pass
            elif icount==0:
                now_year = datetime.now().year
                now_month = datetime.now().month
                first_day=datetime(year=now_year,month=now_month,day=1) 
                last_day=datetime(year=now_year,month=now_month+1,day=1)+timedelta(days=-1) 
                first_dy=int(first_day.strftime("%d"))
                last_dy=int(last_day.strftime("%d"))
                for dayof_mnth in range(first_dy,last_dy+1,1):
                    full_dt=datetime(year=now_year,month=now_month,day=dayof_mnth)
                    day_name=str(full_dt.strftime("%a"))
                    evnt_date=str(dayof_mnth)
                    task_count=0
                    task_duratn="0"
                    data= day_name,evnt_date,task_count,task_duratn
                    Database.cursor.execute("INSERT INTO MONTH(DAY,DATE,TASK,HOURS) VALUES(?,?,?,?)",data)
                    Database.con.commit()

        self.update_month()

#calculate total booked hours for esch day of the month
    def update_month(self):
        Database.cursor.execute("SELECT ST_DATE,ED_DATE FROM EVENT WHERE ID IS NOT NULL") 
        sted_date = Database.cursor.fetchall()    

        if sted_date !=[]:
            for evt_date in sted_date:
                ed_day=datetime.strptime(evt_date[1],"%Y-%m-%d %H:%M:%S")
                st_day=datetime.strptime(evt_date[0],"%Y-%m-%d %H:%M:%S")
                dof_evt=st_day.strftime("%a")
                stdof=int(st_day.strftime("%d"))
                dofed_evt=int(ed_day.strftime("%d"))
                
                if ed_day!=st_day:
                    repeat_days= ed_day-st_day
                    rpt_days=repeat_days.days
                    
                    
                    Database.cursor.execute("SELECT SUM(DURATION) FROM EVENT WHERE ST_DATE=?",(st_day,))
                    hourarry=Database.cursor.fetchone()
                    Database.cursor.execute("SELECT COUNT(TITTLE) FROM EVENT WHERE ST_DATE=?",(st_day,))
                    countarry=Database.cursor.fetchone()
                    Database.cursor.execute("SELECT HOURS FROM MONTH WHERE DAY=?",(dof_evt,))
                    occpd_hr=Database.cursor.fetchone()
                    
                    
                    for dur in hourarry:
                        dur=float(dur)/60.0
                        if dur!=0.0:
                            for count in countarry:
                                for oc_hours in occpd_hr:
                                    dur_hours=float(oc_hours)
                                    dur=float(dur)
                                    
                                    if dur_hours==0.0 or dur== dur_hours:
                                        pass
                                    if dur!= dur_hours:
                                        hour_diff = abs(dur - dur_hours)
                                        hours_ = hour_diff+dur_hours
                                        hrfmt="{:.0f}".format(hours_)
                                        for ind in range(stdof,(rpt_days+1),7):
                                            print(rpt_days)
                                            Database.cursor.execute(f"UPDATE MONTH SET HOURS={hrfmt} WHERE DATE={ind}")
                                            Database.con.commit()
                                            Database.cursor.execute(f"UPDATE MONTH SET TASK={count} WHERE DATE={ind}")
                                            Database.con.commit()
                                    if rpt_days==0:
                                        hour_diff = abs( dur - dur_hours)
                                        hours_ = hour_diff+dur_hours
                                        hrfmt = "{:.0f}".format(hours_)
                                        for ind in range(stdof,(rpt_days+1),7):
                                            Database.cursor.execute(f"UPDATE MONTH SET HOURS={hrfmt} WHERE DAY={dof_evt}")
                                            Database.con.commit()
                                            Database.cursor.execute(f"UPDATE MONTH SET TASK={count} WHERE DAY={dof_evt}")
                                            Database.con.commit()
                                                
                        else:
                            pass
                    
                if ed_day==st_day:
                    pass
                
                
                
                                
                                    
               
        elif sted_date ==[]:
            pass
                        
    def clear_for_month(self):
        try:
           
            screen_manager.get_screen("monthscreen").table_list.clear_widgets()
            Database.cursor.execute("SELECT ID,DAY,DATE,TASK,HOURS FROM MONTH WHERE ID IS NOT NULL")
            month_arr=Database.cursor.fetchall()
            for i in month_arr:
                day=str(i[2])
                num=str(i[3])
                hr=str(i[4])
                month_sch =MonthCard(key=i[0],evnt_day=i[1],evnt_date=day,task_number=num,evnt_hours=hr)
                screen_manager.get_screen("monthscreen").table_list.add_widget(month_sch)
        except Exception:
            Snackbar(text="Month load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
             
    def clear_for_week(self):
        """_summary_
        """        
        screen_manager.get_screen("Calendarscreen").timetable_view.size_hint= .99,.7
        screen_manager.get_screen("Calendarscreen").timetable_view.pos_hint={"center_x":.5,"center_y":.45} 
        screen_manager.get_screen("Calendarscreen").days_of_week.clear_widgets()
        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
        screen_manager.get_screen("Calendarscreen").days_of_week.size_hint_x=1
        #day_sch must only be Monday events form databse if end_date not datetime now 

        Database.cursor.execute("SELECT ID,TITTLE,VENUE,DAY,ST_DATE,ED_DATE,ST_TIME,ED_TIME,DURATION FROM EVENT")
        event_arr=Database.cursor.fetchall()
        try:
            
            live_date =str(datetime.now())
            live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )
            dtoday=live_date.strftime("%a")
            today_dy=live_date.strftime("%d")
            dtday=live_date.strftime("%A")
            if event_arr!=[]:
                view_day=DaySelectionCard(selected_day=dtday)
                screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                for evt in event_arr:
                    en_date=datetime.strptime(evt[5],"%Y-%m-%d %H:%M:%S" )
                    week_in= live_date+timedelta(days=8)
                    st_date=datetime.strptime(evt[4],"%Y-%m-%d %H:%M:%S")
                    day_dt=st_date.strftime("%d")
                    if evt[3]==dtoday and en_date>live_date+timedelta(days=-1) and st_date<week_in:
                        dur=str(evt[8])+" mins"
                        day_sch =TableCard(key=evt[0],event_Name=evt[1],start_time=evt[6],end_time=evt[7],event_venue=evt[2],evnt_date=day_dt,evnt_day=evt[3],duratn=dur)
                        screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)
                    elif evt[3]!=dtoday and en_date>live_date+timedelta(days=-1) and st_date<week_in:
                        screen_manager.get_screen("Calendarscreen").table_list.clear_widgets()
                        day_sch = TableCard(key=0, event_Name="No events today", start_time="00:00AM", end_time="11:59PM", event_venue="Here", evnt_date= today_dy, evnt_day=dtoday , duratn="1439 mins")
                        screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)

            elif event_arr==[]:
                screen_manager.get_screen("Calendarscreen").timetable_view.size_hint= .99,.7
                screen_manager.get_screen("Calendarscreen").timetable_view.pos_hint={"center_x":.5,"center_y":.45} 
                view_day=DaySelectionCard(selected_day=dtday)
                screen_manager.get_screen("Calendarscreen").days_of_week.add_widget(view_day)
                day_sch =TableCard(key=0,event_Name="No events",start_time="00:00AM",end_time="11:59PM",event_venue="Here",evnt_date=today_dy,evnt_day=dtoday,duratn="1439 mins")
                screen_manager.get_screen("Calendarscreen").table_list.add_widget(day_sch)

        except Exception:
            Snackbar(text="No events load Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
    

    def clear_add_course(self):
        """_summary_
        """        
        #also add unchecking of categories and remove weghts
        screen_manager.get_screen("addCourse").courseID.text=""
        screen_manager.get_screen("addCourse").ex_ratio.text=""
        screen_manager.get_screen("addCourse").ca_ratio.text=""
        screen_manager.get_screen("addCourse").c_credit.text=""
        pass
    def clear_addevent(self):
        screen_manager.get_screen("add_event").evnt_venue.text=""
        screen_manager.get_screen("add_event").event_name.text=""
        screen_manager.get_screen("add_event").start_date.text=""
        screen_manager.get_screen("add_event").end_date.text=""
        screen_manager.get_screen("add_event").start_time.text=""
        screen_manager.get_screen("add_event").end_time.text=""
        pass

    def update_overviwscreen(self):
        screen_manager.get_screen("overviewscreen").category_list.clear_widgets()
        course_id =screen_manager.get_screen("overviewscreen").crseid.text
        
        """_summary_

        Args:
            course_id (_type_): _description_
        """        
        con = sqlite3.connect(f"{course_id}.db")
        cursor = con.cursor()
        try:
            cursor.execute("SELECT ID,CATEGORY,MARK,CAT_CONTRIB,TUG_COUNT FROM SUMMARY")
            live_categ = cursor.fetchall()
            for cat in live_categ:
                grade = str(cat[2])
                contrib= str(cat[3])
                tugcount = str(cat[4])+" Tug" # type: ignore
                add_categ =(OverviewCard(categ_key=cat[0],Category=cat[1],Grade=grade,Contribution=contrib,TUG_count=tugcount))
                screen_manager.get_screen("overviewscreen").category_list.add_widget(add_categ)
        except Exception:
            Snackbar(text="IDE2:Ovev:1:Hot Overview ",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore
        #add categories with zero assessments
        try:
            cursor.execute("SELECT CATEGORY FROM SUMMARY")
            live_categ = cursor.fetchall()
            live_cat=[]
            for categ in live_categ:
                for cat in categ:
                    live_cat.append(cat)    
            cursor.execute("SELECT TITTLE FROM CATEGORY")
            dead_cat = cursor.fetchall()
            for dcateg in dead_cat:
                for deadcat in dcateg:
                    if deadcat not in live_cat:
                        grade = str(0)
                        contrib= str(0)
                        tugcount = str(0)+" Tug"
                        add_categ =(OverviewCard(categ_key=0,Category=deadcat,Grade=grade,Contribution=contrib,TUG_count=tugcount))
                        screen_manager.get_screen("overviewscreen").category_list.add_widget(add_categ)
        except Exception:
            Snackbar(text="IDE2:Ovev:2:Hot Overview ",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore

    def update_coursescreen(self):
        screen_manager.get_screen("CoursesScreen").course_list.clear_widgets()
        screen_manager.get_screen("Home").course_home.clear_widgets()
        taken_courses =self.get_courses()
        emty_crse =self.get_emptycrse()
        if taken_courses !=[]:
                for c in taken_courses:
                    cred =float(c[2])
                    cr= str (cred)
                    ca = str (c[3])
                    ex = str (c[4])
                    bas = str (c[6])
                    add_course = CourseCard(course_key = c[0],CourseID=c[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex,crsavg=c[5],Basis=bas)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)
                    crse_hom = CourseDisplayCard(Courseid=c[1],average=str(c[5])+" %")
                    screen_manager.get_screen("Home").course_home.add_widget(crse_hom)
        if  emty_crse!=[]:
                for c in emty_crse:
                    cred =float(c[2])
                    cr= str (cred)
                    ca = str (c[3])
                    ex = str (c[4])
                    avg =1.0
                    bas = "0"
                    add_course = CourseCard(course_key = c[0],CourseID=c[1], C_Credit=cr,CA_ratio=ca,Ex_ratio=ex,crsavg=avg,Basis=bas)
                    screen_manager.get_screen("CoursesScreen").course_list.add_widget(add_course)
                    crse_hom = CourseDisplayCard(Courseid=c[1],average="0 %")
                    screen_manager.get_screen("Home").course_home.add_widget(crse_hom)
        if taken_courses==[] and emty_crse==[]:
            crse_hom = CourseDisplayCard(Courseid="PHY101",average="0 %")
            screen_manager.get_screen("Home").course_home.add_widget(crse_hom)


#Add event to user_database table EVENT 
    def add_event(self,tittle,venue,st_date,ed_date,st_time,ed_time):

        try:
            if tittle!="" and len(tittle)<16 and venue!="" and len(venue)<13 and st_date!="" and ed_date!="" and st_time!="" and ed_time!="":

                mystart_date =datetime.strptime(st_date,"%a %d %b %Y")
                day=mystart_date.strftime("%a") 

                myend_date =datetime.strptime(ed_date,"%a %d %b %Y")
                
                strt_time = datetime.strptime(st_time,"%H:%M")
                srt_time= strt_time.time().strftime("%I:%M %p") 
                end_time = datetime.strptime(ed_time,"%H:%M")
                en_time= end_time.time().strftime("%I:%M %p") 
                dur="10"
                if end_time>strt_time or end_time==strt_time:
                    event_dur= end_time- strt_time
                    evnt_min=divmod(event_dur.total_seconds(),60)[0]
                    dur_formt="{:.0f}".format(abs(evnt_min))
                    dur=str(dur_formt)
                if end_time<strt_time:
                    event_dur= end_time- strt_time
                    evnt_hr=event_dur.total_seconds()/3600
                    timediff=(24.0- abs(evnt_hr))*60.0
                    dur_formt="{:.0f}".format(abs(abs(timediff)))
                    dur=str(dur_formt)

                live_date =str(datetime.now())
                live_date=datetime.strptime(live_date,"%Y-%m-%d %H:%M:%S.%f" )

                if mystart_date <= myend_date and myend_date >live_date+timedelta(days=-1):

                    Database.cursor.execute("SELECT TITTLE FROM EVENT")
                    tittle_arr =Database.cursor.fetchall()
                    Database.cursor.execute("SELECT ST_TIME FROM EVENT")
                    st_arr =Database.cursor.fetchall()
                    Database.cursor.execute("SELECT ST_DATE FROM EVENT")
                    sd_arr =Database.cursor.fetchall()

                    existing_event=[]
                    tittle=str(tittle)
                    for exist_tl in tittle_arr:
                        for i in exist_tl:
                            existing_event.append(i)

                    event_startT=[]
                    event_startD=[]
                    for booked_tm  in st_arr :
                        for t in booked_tm :
                            t=str(t) 
                            event_startT.append(t)
                    for booked_dt  in sd_arr :
                        for d in booked_dt :
                            d=str(d) 
                            event_startD.append(d)
    
                    full_startT=[]
                    if event_startD !="" and event_startT!="":
                        for i in range(0,len(event_startD),1):
                            tm=event_startT[i]
                            dt=event_startD[i]
                            tm=str(tm)
                            dt=str(dt)
                            full_startT.append(tm+" "+dt)
                            
                    partsrt_time=str(srt_time)  
                    partsrt_date=str(mystart_date)
                    new_eventst=partsrt_time+" "+partsrt_date
                    
                    if new_eventst in full_startT:
                        Snackbar(text="Time-slot Already Booked",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignore  
                        
                    if tittle in existing_event:
                        Snackbar(text="Event Already exist",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignore  
                    elif tittle not in existing_event and new_eventst not in full_startT:
                        data= tittle,venue,day,mystart_date,myend_date,srt_time,en_time,dur
                        Database.cursor.execute("INSERT INTO EVENT(TITTLE,VENUE,DAY,ST_DATE,ED_DATE,ST_TIME,ED_TIME,DURATION) VALUES(?,?,?,?,?,?,?,?)",data)
                        Database.con.commit()
                        self.selected_weekday(day)
                    
                elif mystart_date>myend_date:
                    Snackbar(text="Invalid Event dates",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignor
                elif myend_date <live_date+timedelta(days=1):
                    Snackbar(text="Event cannot end in the past",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignore
                    
            elif tittle=="":
                Snackbar(text="Event name is missing!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif len(tittle)>16:
                Snackbar(text="Event name must be  <16 char!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif venue=="":
                Snackbar(text=f"Where will {tittle} be ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif len(venue)>13:
                Snackbar(text=f"{tittle} venue must be <11 char ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif st_date=="":
                Snackbar(text=f"What day does {tittle} start ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif ed_date=="":
                Snackbar(text=f"What day does {tittle} end ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif st_time =="":
                Snackbar(text=f"What time does {tittle} start ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif ed_time =="":
                Snackbar(text=f"What time does {tittle} end ?",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="Event Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
        
#update TASK  
    def update_task(self,tittle):
        """_summary_

        Args:
            tittle (_type_): _description_
        """        
        Database.cursor.execute("SELECT Id,Description,Date,completed FROM TASK WHERE Tittle=?",(tittle,))
        arr =Database.cursor.fetchall()
        for i in arr:
            screen_manager.get_screen("todoScreen").todo_list.add_widget(TodoCard(pk=i[0],tittle=tittle, description=i[1],
                                                                                  task_date=i[2]))

# add task settings
    def add_todo(self,tittle,description,date_time):
        """_summary_

        Args:
            tittle (_type_): _description_
            description (_type_): _description_
            date_time (_type_): _description_
            task_time (_type_): _description_
            task_time2 (_type_): _description_
        """        
        try:
            if tittle !="" and description !="" and len(tittle)<21 and len(description)<81 and date_time!="":
                # adding task to Database
                data= tittle,description,date_time,0
                Database.cursor.execute("INSERT INTO TASK(Tittle,Description,Date,completed) VALUES(?,?,?,?)",data)
                Database.con.commit()
                screen_manager.transition = FadeTransition()
                screen_manager.current = "todoScreen"

            elif tittle =="":
                Snackbar(text="Tittle is missing",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
            elif description =="":
                Snackbar(text="Description is missing!",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore 
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                
            elif len(tittle)>20:
                Snackbar(text="Tittle must be < 21 char",snackbar_x ="10dp",snackbar_y ="10dp",
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
            elif len(description)>80:
                Snackbar(text="Description must be < 81 characters",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
            
            elif date_time=="":
                Snackbar(text="Specify date",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                        #add action mybe highlight empty area   
                        # change color to alert empty field
           
        except Exception:
            Snackbar(text="Task Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore
            
#adding new course to course view
    def update_course(self,course_id):
        """_summary_

        Args:
            course_ID (str): grants access to database -updates CoursesScreen
        """        
        cours_id = str(course_id)
        courseid =cours_id.replace(" ","") # type: ignore
        courseid = courseid.upper()
        Database.cursor.execute("SELECT ID,CREDIT,CA_R,EX_R FROM COURSES WHERE COURSE_ID=?",(courseid,))
        arr =Database.cursor.fetchall()
       
        for c in arr:
            cre=float(c[1])
            cr= str (cre)
            ca = str (c[2])
            ex = str (c[3])
            crse= CourseCard(course_key = c[0],CourseID=courseid, C_Credit=cr,CA_ratio=ca,Ex_ratio=ex) #type: ignore
            screen_manager.get_screen("CoursesScreen").course_list.add_widget(crse)
            screen_manager.get_screen("CoursesScreen").crtot.text= self.creditscal()
                 
# add course settings
    def add_course(self,tcheck,test_w,acheck,ass_w,pcheck,prese_w,qcheck,quiz_w,lcheck,lab_w,gcheck,group_w,ccheck,clswrk_w,ocheck,other_w,course_id,credits,ca_rt,ex_rt):
        """_summary_

        Args:
            tcheck (bool): check test selection
            test_w (int): test weight
            acheck (bool): _description_
            ass_w (int): assingment weight
            pcheck (_type_): _description_
            prese_w (_type_): _description_
            qcheck (_type_): _description_
            quiz_w (_type_): _description_
            lcheck (_type_): _description_
            lab_w (_type_): _description_
            gcheck (_type_): _description_
            group_w (_type_): _description_
            ccheck (_type_): _description_
            clswrk_w (_type_): _description_
            ocheck (_type_): _description_
            other_w (_type_): _description_
            course_id (_type_): _description_
            credits (_type_): _description_
            ca_rt (_type_): _description_
            ex_rt (_type_): _description_
        """        
        try:
            if course_id!="":
                course_id = str(course_id)
                course_id =course_id.replace(" ","")
                courseid = course_id.upper()
                Database.cursor.execute("SELECT COURSE_ID FROM COURSES  WHERE ID IS NOT NULL")
                arr =Database.cursor.fetchall()
                taken_crs=[]
                for crse in arr:
                    for i in crse:
                        taken_crs.append(i)
                if courseid in taken_crs:
                    Snackbar(text="Course Already exist",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore  
                elif taken_crs==[] or courseid not in taken_crs:   
                    test_w=float(test_w)
                    ass_w=float(ass_w)
                    prese_w=float(prese_w)
                    quiz_w=float(quiz_w)
                    lab_w=float(lab_w)
                    group_w=float(group_w)
                    clswrk_w=float(clswrk_w)
                    other_w=float(other_w)

                    totl_weight=test_w+ass_w+prese_w+quiz_w+lab_w+group_w+clswrk_w+other_w
                    if  credits !=""and ca_rt !=""  and ex_rt !="":
                        credits=float(credits)                        
                        ca_rt=float(ca_rt)
                        ex_rt=float(ex_rt)
                        total_ratio=(ca_rt+ex_rt)
                        try:
                            if total_ratio ==100.0 and totl_weight==100.0:
                                try:
                                    con = sqlite3.connect(f'{courseid}.db')
                                    cursor = con.cursor() # type: ignore
                                    cursor.execute("CREATE TABLE CATEGORY(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL UNIQUE,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0)")
                                    con.commit()
                                    cursor.execute("CREATE TABLE SUMMARY(ID INTEGER PRIMARY KEY AUTOINCREMENT,CATEGORY TEXT NOT NULL UNIQUE,MARK DECIMAL NOT NULL  DEFAULT 100.0,CAT_CONTRIB DECIMAL,TUG_COUNT DECIMAL, FOREIGN KEY(CATEGORY) REFERENCES CATEGORY(TITTLE))")
                                    con.commit()
                                    if tcheck.active is True and test_w !="":     
                                        cursor.execute("CREATE TABLE TEST(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        tdata ="TEST",test_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",tdata)
                                        con.commit()
                                    else:pass
                                    if acheck.active is True and ass_w !="":     
                                        cursor.execute("CREATE TABLE ASSIGNMENT(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        adata = "ASSIGNMENT",ass_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",adata)
                                        con.commit()
                                    else:pass
                                    if pcheck.active is True and prese_w !="":     
                                        cursor.execute("CREATE TABLE PRESENTATION(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        pdata = "PRESENTATION",prese_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",pdata)
                                        con.commit()
                                    else:pass
                                    if qcheck.active is True and quiz_w !="":    
                                        cursor.execute("CREATE TABLE QUIZ(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        qdata = "QUIZ",quiz_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",qdata)
                                        con.commit()
                                    else:pass
                                    if lcheck.active is True and lab_w !="":     
                                        cursor.execute("CREATE TABLE LAB(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        ldata = "LAB",lab_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",ldata)
                                        con.commit()                                 
                                    else:pass
                                    if  gcheck.active is True and group_w !="":     
                                        cursor.execute("CREATE TABLE GROUPWORK(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        gdata = "GROUPWORK",group_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",gdata)
                                        con.commit()
                                    else:pass
                                    if ccheck.active is True and clswrk_w !="":     
                                        cursor.execute("CREATE TABLE CLASSWORK(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        cdata = "CLASSWORK",clswrk_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",cdata)
                                        con.commit()
                                    else:pass
                                    if ocheck.active is True and other_w !="":     
                                        cursor.execute("CREATE TABLE OTHER(ID INTEGER PRIMARY KEY AUTOINCREMENT,TITTLE TEXT NOT NULL,WEIGHT DECIMAL NOT NULL  DEFAULT 100.0,MARK DECIMAL NOT NULL,CONTRIB DECIMAL)")
                                        con.commit()
                                        odata = "OTHER",other_w
                                        cursor.execute("INSERT INTO CATEGORY(TITTLE,WEIGHT) VALUES(?,?)",odata) 
                                        con.commit()
                                    else:pass
                                     
                                    data= courseid,credits,ca_rt,ex_rt
                                    Database.cursor.execute("INSERT INTO COURSES(COURSE_ID,CREDIT,CA_R,EX_R) VALUES(?,?,?,?)",data)
                                    Database.con.commit()
                                    screen_manager.transition = FadeTransition()
                                    screen_manager.current = "CoursesScreen"       
                                except Exception:
                                    Snackbar(text="INDE:3: Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                            font_size ="15dp").open() # type: ignore
                            elif total_ratio!=100.0:
                                Snackbar(text="Faulty Course ratio",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                        font_size ="15dp").open() # type: ignore
                            elif totl_weight!=100.0:
                                Snackbar(text="Faulty Assessment weights",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                        font_size ="15dp").open() # type: ignore
                        except Exception:
                            Snackbar(text="INDE:2: Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                    font_size ="15dp").open() # type: ignore

                    elif credits =="":
                        Snackbar(text="Credit hours empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
                    elif ca_rt =="":
                        Snackbar(text="CA Weight  empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
                    elif ex_rt =="":
                        Snackbar(text="Exam Weight empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
        
            elif course_id =="":
                    Snackbar(text="Course ID empty",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                            size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                            font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="INDE:1:Add Course Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore

#course summary calculations
    def summariseCourse(self):
        """_summary_
        """            
        try:
            Database.cursor.execute("SELECT COURSE_ID FROM COURSES")
            arr =Database.cursor.fetchall()
            takenC=[]
            for crse in arr:
                for i in crse:
                    takenC.append(i)    
            for CourseID in takenC:
                con = sqlite3.connect(f"{CourseID}.db")
                cursor = con.cursor()
                cursor.execute("SELECT TITTLE FROM CATEGORY")
                array = cursor.fetchall()
                
                for i in array:
                    for categ_name in i:
                        cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                        count = cursor.fetchone()
                        try:
                            for icount in count:
                                if icount>0:
                                    cursor.execute("INSERT OR REPLACE INTO SUMMARY(CATEGORY) VALUES(?)",(categ_name,))
                                    con.commit()
                                    cursor.execute(f"SELECT SUM(WEIGHT) FROM {categ_name} WHERE  CONTRIB>0.0")
                                    sumarray = cursor.fetchone()
                                    cursor.execute(f"SELECT SUM(CONTRIB) FROM {categ_name} WHERE  CONTRIB>0.0")
                                    contrarry = cursor.fetchone()
                                    for sumof_weights in sumarray:
                                        cursor.execute(f"SELECT COUNT(TITTLE) FROM {categ_name} WHERE CONTRIB>0.0")
                                        assarray = cursor.fetchone()
                                        for ass_count in assarray:
                                            ass_count=float(ass_count)
                                            cursor.execute(f"UPDATE SUMMARY SET TUG_COUNT ={ass_count} WHERE CATEGORY =?",(categ_name,))
                                            con.commit()
                                            for sumof_contrib in contrarry:
                                                sumof_weights =float(sumof_weights)
                                                sumof_contrib=float(sumof_contrib)
                                                if sumof_weights>100.0:
                                                    weight_bal=sumof_weights/100.0
                                                    final_mark =sumof_contrib/weight_bal
                                                    mark_formt = "{:.1f}".format(final_mark)
                                                    cursor.execute(f"UPDATE SUMMARY SET MARK ={mark_formt} WHERE CATEGORY =?",(categ_name,))
                                                    con.commit()
                                                if sumof_weights<100.0:
                                                    cursor.execute(f"UPDATE SUMMARY SET MARK ={sumof_contrib} WHERE CATEGORY =?",(categ_name,))
                                                    con.commit()
                                                if sumof_weights==100.0:
                                                    average =sumof_contrib/ass_count
                                                    cursor.execute(f"UPDATE SUMMARY SET MARK ={average} WHERE CATEGORY =?",(categ_name,))
                                                    con.commit()
                                                    

                        except Exception:
                            Snackbar(text="INDE:CAL:1:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open() # type: ignore
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                            count = cursor.fetchone()
                            for icount in count:
                                if icount>0:
                                    cursor.execute("SELECT WEIGHT FROM CATEGORY WHERE TITTLE =?",(categ_name,))
                                    ca_array = cursor.fetchone()
                                    for ctgry_w in ca_array:
                                        ctgry_w=float(ctgry_w)
                                        cursor.execute("SELECT MARK FROM SUMMARY WHERE CATEGORY =?",(categ_name,))
                                        markar = cursor.fetchone()
                                        for mark in markar:
                                            mark=float(mark)
                                            cat_contrib = mark*(ctgry_w/100.0)
                                            contr_fmt = "{:.1f}".format(cat_contrib)
                                            cursor.execute(f"UPDATE SUMMARY SET CAT_CONTRIB ={contr_fmt} WHERE CATEGORY =?",(categ_name,))
                                            con.commit()
                        except Exception:
                            Snackbar(text="INDE:CAL:2:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open() # type: ignore
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                            count = cursor.fetchone()
                            for icount in count:
                                if icount>0:
                                    cursor.execute("SELECT SUM(CAT_CONTRIB) FROM SUMMARY WHERE ID IS NOT NULL")
                                    ca_array = cursor.fetchone()
                                    for ctgry_w in ca_array:
                                        ctgry_w=float(ctgry_w)
                                        Database.cursor.execute(f"UPDATE COURSES SET CA={ctgry_w} WHERE COURSE_ID=?",(CourseID,))
                                        Database.con.commit()
                                        Database.cursor.execute("SELECT CA_R FROM COURSES WHERE COURSE_ID=?",(CourseID,))
                                        ratio_arr =Database.cursor.fetchone()
                                        for ratio in ratio_arr:
                                            ratio =float(ratio)
                                            basis= (ratio*ctgry_w)/100.0
                                            basis_frt = "{:.1f}".format(basis)
                                            Database.cursor.execute(f"UPDATE COURSES SET BASIS={basis_frt} WHERE COURSE_ID=?",(CourseID,))
                                            Database.con.commit()
                                            pass
                        except Exception:
                            Snackbar(text="INDE:CAL:3:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="INDE:CAL: Indigenous error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore

#add assessment
    def add_assessment(self, ass_courseid,ass_mark,ass_contr,ass_category,ass_name):
        """_summary_

        Args:
            ass_courseid (_type_): _description_
            ass_mark (_type_): _description_
            ass_contr (_type_): _description_
            ass_category (_type_): _description_
            ass_name (_type_): _description_
        """        
        try: 
            if  ass_name !=""and ass_mark!="" and ass_contr!="":
                ass_name = str(ass_name)
                ass_name =ass_name.replace(" ","")
                con = sqlite3.connect(f'{ass_courseid}.db')
                cursor = con.cursor() # type: ignore
                cursor.execute(f"SELECT TITTLE FROM {ass_category}")
                arr =cursor.fetchall()
                takenassmt_name=[]
                for asnm in arr:
                    for i in asnm:
                        takenassmt_name.append(i)    
                if ass_name in takenassmt_name:
                    Snackbar(text="Assessment already Exists",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                        font_size ="15dp").open() # type: ignore
                    
                elif ass_name not in takenassmt_name:
                    try: 
                        ass_mark =float(ass_mark)
                        ass_contr=float(ass_contr)
                        if  ass_mark<100.0000000000001 and ass_mark>-0.01 and ass_contr<100.0000000000001 and ass_contr>-0.01:
                            con = sqlite3.connect(f'{ass_courseid}.db')
                            cursor = con.cursor()
                            ass_contrib = ass_mark*(ass_contr/100.0)  
                            contrib_formt = "{:.1f}".format(ass_contrib)
                            data=ass_name,ass_contr,ass_mark,contrib_formt

                            cursor.execute(f"INSERT INTO {ass_category}(TITTLE,WEIGHT,MARK,CONTRIB) VALUES(?,?,?,?)",data)
                            con.commit()         
                        elif ass_mark >100.0:
                            Snackbar(text="Mark greater than 100",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore                    
                        elif ass_contr >100.0:
                            Snackbar(text="Contribution greater than high default-100",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore
                        elif ass_mark <0.0:
                            Snackbar(text="Mark less than Zero",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore                    
                        elif ass_contr <0.0:
                            Snackbar(text="Contribution less than low default-0.0",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore
                        else:
                            Snackbar(text="INDE:3: Unexpected Assessment",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                    font_size ="15dp").open() # type: ignore
                    except Exception:
                        Snackbar(text="INDE:2:Add Assessment Indigenous error",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                                font_size ="15dp").open() # type: ignore
                    try:
                        
                        ass_mark =float(ass_mark)
                        ass_contr=float(ass_contr)
                        ass_contrib = ass_mark*(ass_contr/100.0)
                        ass_contrib ="{:.1f}".format(ass_contrib)
                        ass_contr=str(ass_contr)
                        ass_mark=str(ass_mark)
                        ass_contr=str(ass_contr)
                        ass_contrib=str(ass_contrib)
                        add_test =(AssessmentCard(testpk=0,testName=ass_name,testWeight= ass_contr,testMark = ass_mark,testContrib=ass_contrib))
                        screen_manager.get_screen("AssessmentSummary").assessmnt_list.add_widget(add_test)
                        screen_manager.transition = FadeTransition()
                        screen_manager.current = "AssessmentSummary"

                    except Exception:
                        Snackbar(text="INDE:0:View update error",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                                size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                                font_size ="15dp").open() # type: ignore
            elif ass_name =="":
                Snackbar(text="Assessment name empty",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
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
            Snackbar(text="INDE:1:Add assessment error",snackbar_x ="10dp",snackbar_y ="7dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                    font_size ="15dp").open() # type: ignore

# Update assessment 
    def update_assessment(self,course_id,categ_name):
        """_summary_

        Args:
            course_id (_type_): _description_
        """
        try: 
            if course_id !="":
                con = sqlite3.connect(f"{course_id}.db")
                cursor = con.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                count = cursor.fetchone()
                try:
                    for icount in count:
                        if icount>0:
                            cursor.execute("INSERT OR REPLACE INTO SUMMARY(CATEGORY) VALUES(?)",(categ_name,))
                            con.commit()
                            cursor.execute(f"SELECT SUM(WEIGHT) FROM {categ_name} WHERE ID IS NOT NULL")
                            sumarray = cursor.fetchone()
                            cursor.execute(f"SELECT SUM(CONTRIB) FROM {categ_name} WHERE  CONTRIB>0.0")
                            contrarry = cursor.fetchone()
                            for sumof_weights in sumarray:
                                cursor.execute(f"SELECT COUNT(TITTLE) FROM {categ_name} WHERE CONTRIB>0.0")
                                assarray = cursor.fetchone()
                                for ass_count in assarray:
                                    cursor.execute(f"UPDATE SUMMARY SET TUG_COUNT ={ass_count} WHERE CATEGORY =?",(categ_name,))
                                    con.commit()
                                    for sumof_contrib in contrarry:
                                        sumof_weights =float(sumof_weights)
                                        sumof_contrib=float(sumof_contrib)
                                        if sumof_weights>100.0000000000001:
                                            weight_bal=sumof_weights/100.0
                                            final_mark =sumof_contrib/weight_bal
                                            mark_formt = "{:.1f}".format(final_mark)
                                            cursor.execute(f"UPDATE SUMMARY SET MARK ={mark_formt} WHERE CATEGORY =?",(categ_name,))
                                            con.commit()
                                            screen_manager.get_screen("AssessmentSummary").categavar.text=str(mark_formt)
                                        if sumof_weights<100.0:
                                            cursor.execute(f"UPDATE SUMMARY SET MARK ={sumof_contrib} WHERE CATEGORY =?",(categ_name,))
                                            con.commit()
                                            screen_manager.get_screen("AssessmentSummary").categavar.text=str(sumof_contrib)
                                        if sumof_weights==100.0:
                                            average =sumof_contrib/ass_count
                                            cursor.execute(f"UPDATE SUMMARY SET MARK ={average} WHERE CATEGORY =?",(categ_name,))
                                            con.commit()
                                            screen_manager.get_screen(
                                                "AssessmentSummary").categavar.text = str(average)
                except Exception:
                    Snackbar(text="INDE:CAL:1:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore  
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                    count = cursor.fetchone()
                    for icount in count:
                        if icount>0:
                            cursor.execute("SELECT WEIGHT FROM CATEGORY WHERE TITTLE =?",(categ_name,))
                            cArray = cursor.fetchone()
                            for ca in cArray:
                                ca=float(ca)
                                cursor.execute("SELECT MARK FROM SUMMARY WHERE CATEGORY =?",(categ_name,))
                                markar = cursor.fetchone()
                                for mark in markar:
                                    mark=float(mark)
                                    cat_contrib = (mark*ca)/100.0
                                    contr_fmt = "{:.1f}".format(cat_contrib)
                                    cursor.execute(f"UPDATE SUMMARY SET CAT_CONTRIB ={contr_fmt} WHERE CATEGORY =?",(categ_name,))
                                    con.commit()
                                    screen_manager.get_screen("AssessmentSummary").categContrib.text=contr_fmt
                        
                except Exception :
                    Snackbar(text="INDE:CAL:2:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ_name} LIMIT 1)")
                    count = cursor.fetchone()
                    for icount in count:
                        if icount>0:
                            cursor.execute("SELECT SUM(CAT_CONTRIB) FROM SUMMARY WHERE ID IS NOT NULL")
                            cArray = cursor.fetchone()
                            for ca in cArray:
                                ca=float(ca)
                                Database.cursor.execute(f"UPDATE COURSES SET CA={ca} WHERE COURSE_ID=?",(course_id,))
                                Database.con.commit()
                                Database.cursor.execute("SELECT CA_R FROM COURSES WHERE COURSE_ID=?",(course_id,))
                                ratioArr =Database.cursor.fetchone()
                                for ratio in ratioArr:
                                    ratio =float(ratio)
                                    basis= (ratio*ca)/100.0
                                    basisFmt = "{:.1f}".format(basis)
                                    Database.cursor.execute(f"UPDATE COURSES SET BASIS={basisFmt} WHERE COURSE_ID=?",(course_id,))
                                    Database.con.commit()
                except Exception:
                    Snackbar(text="INDE:CAL:3:error",snackbar_x ="10dp",snackbar_y ="10dp", # type: ignore
                        size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8),
                        font_size ="15dp").open() # type: ignore
        except Exception:
            Snackbar(text="INDE:0:View update error",snackbar_x ="4dp",snackbar_y ="10dp", # type: ignore
                    size_hint_x =(Window.width -(dp(10)*2))/Window.width, bg_color=(30/255,47/255,151/255,.8), # type: ignore
                    font_size ="15dp").open() # type: ignore

    def close_app(self):
        Window.close()  

if __name__ == "__main__":

    MainApp().run()
