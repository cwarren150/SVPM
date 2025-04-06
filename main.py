import datetime
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
#from kivymd.uix.list import OneLineIconListItem
import psycopg2

class MainApp(MDApp):
    def connectPostgres(self):
        self.conn = psycopg2.connect(database="svpm",
                            host="localhost",
                            user="cori",
                            password="pmpass",
                            port="5432")

        self.cur = self.conn.cursor()
        self.equipItems=[]

#Home Screen   
    def homeOpen(self):
        #populate the pm list
        self.cur.execute(
            'select pmname, equipname, pmfreqqty, pmfrequnit, recurdate, pmid, recurid from recurt right join pmt using (pmid) left join equipt using (equipid)')
        pmItems = self.cur.fetchall()
        self.root.ids.homePmList.clear_widgets()
        for i in pmItems:
            pmname=i[0]
            equipname=i[1]
            pmfreqqty=i[2]
            pmfrequnit=i[3]
            recurdate=i[4]
            pmID= i[5]
            recurID=i[6]
            if recurdate==None:
                alertColor = 1,0,0,0
                dueDate = self.dueDate(datetime.date(2025,1,1), pmfrequnit, pmfreqqty)
            else:
                dueDate = self.dueDate(recurdate, pmfrequnit, pmfreqqty)
            item=OneLineListItem(text=f"{pmname}", id=f"{pmID}")
            item.bind(on_release=self.homePMListPress)
            self.root.ids.homePmList.add_widget(item)
            item=OneLineListItem(text=f"{equipname}", id=f"{pmID}")
            item.bind(on_release=self.homePMListPress)
            self.root.ids.homePmList.add_widget(item)
            item=OneLineListItem(text=f"{dueDate}", id=f"{pmID}")
            item.bind(on_release=self.homePMListPress)
            self.root.ids.homePmList.add_widget(item)
        #populate the task list
        self.cur.execute('select * from taskt')
        taskItems = self.cur.fetchall()
        self.root.ids.homeTaskList.clear_widgets()
        for i in taskItems:
            taskID= i[0]
            taskname=i[1]
            taskDesc=i[2]
            taskCreationDate=i[3]
            taskDoneDate=i[4]
            if taskDoneDate==None:
                item = OneLineListItem(text=f"{taskname}", id=f"{taskID}")
                item.bind(on_release=self.homeTaskListPress)
                self.root.ids.homeTaskList.add_widget(item)
                item = OneLineListItem(text=f"{taskCreationDate}", id=f"{taskID}")
                item.bind(on_release=self.homeTaskListPress)
                self.root.ids.homeTaskList.add_widget(item)
                
    def homePMListPress(self, text):
        self.cur.execute(
            'select pmname, equipname, pmfreqqty, pmfrequnit, recurdate, pmid, recurid from recurt right join pmt using (pmid) left join equipt using (equipid)')
        pmItems = self.cur.fetchall()
        self.root.ids.sm_sub.current="pm_dets"
        self.pmDetsID=text.id
                
    def homeTaskListPress(self,text):
        insertL= """select * from taskt where taskID=%s;"""
        dataL=(text.id)
        self.cur.execute(insertL, dataL)
        taskItems = self.cur.fetchall()
        self.root.ids.taskDetName.text = taskItems[0][1]
        self.root.ids.taskDetDesc.text = taskItems[0][2]
        self.root.ids.taskDetDate.text = f"{taskItems[0][3]}"
        if taskItems[0][4] == None:
            pass
        else:
            self.root.ids.taskDetComp.text = taskItems[0][4]
        self.root.ids.sm_sub.current="task_dets"
        self.taskDetsID=text.id
            
    def dueDate(self, curdate, freq, quant):
        if freq == "Day":
            dateMath = curdate + datetime.timedelta(days = quant)
        if freq == "Month":
            dateMath = curdate + datetime.timedelta(days = quant*30)
        if freq == "Year":
            dateMath = curdate + datetime.timedelta(days = quant*365)
        return dateMath

#Location Screen
    def locOpen(self):
        self.cur.execute('Select * from locT')
        loc_i = self.cur.fetchall()
        self.root.ids.locList.clear_widgets()
        for i in loc_i:
            self.root.ids.locList.add_widget(
                OneLineListItem(text=i[1])
                )
            
    def addLoc(self):
        insertL= """INSERT INTO locT (locName, locDesc) VALUES (%s, %s);"""
        locName=self.root.ids.locName.text
        locDesc=self.root.ids.locDesc.text
        dataL=(locName, locDesc)
        if locName=="":
            self.root.ids.locText.text = 'Location has to have a name.'
        else:    
            if locDesc=="":
                self.root.ids.locText.text='Location needs a Description'
            else:
                try:
                    self.cur.execute(insertL, dataL)
                    self.conn.commit()
                    
                    self.root.ids.locName.text=""
                    self.root.ids.locDesc.text=""
                    self.root.ids.locText.text=""
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
            
    def equipOpen(self):
        self.cur.execute('Select * from equipT')
        equip_i = self.cur.fetchall()
        self.root.ids.equipList.clear_widgets()
        for i in equip_i:
            self.root.ids.equipList.add_widget(
                OneLineListItem(text=i[2])
                )
            
    def addEquipOpen(self):
        self.cur.execute('Select locName, locID from locT')
        self.loc_list = self.cur.fetchall()
        menuItems=[
            {
                "text": f"{i[0]}",
                "height": dp(56),
                "on_release": lambda x=f"{i[0]}", y=i[1]: self.equipSetItem(x,y),
            } for i in self.loc_list
        ]
        self.locMenu = MDDropdownMenu(
            caller=self.root.ids.equipDropItem,
            items=menuItems,
            position="center",
            width_mult=4,
        )
        self.locMenu.bind()

    def equipSetItem(self, textItem, locID):
        self.root.ids.equipDropItem.set_item(textItem)
        self.locMenu.dismiss()
        self.locID = locID
            
    def addEquip(self):
        insertL= """INSERT INTO equipT (equipName, equipDesc, locID) VALUES (%s, %s, %s);"""
        equipName=self.root.ids.equipName.text
        equipDesc=self.root.ids.equipDesc.text
        locID=self.locID
        dataL=(equipName, equipDesc, locID)
        if equipName=="":
            self.root.ids.equipText.text = 'Equipment has to have a name.'
        else:
            if equipDesc=="":
                self.root.ids.equipText.text='Equipment needs a Description'
            else:
                if locID=="":
                    self.root.ids.equipText.text='Equipment needs a location'
                else:
                    try:
                        self.cur.execute(insertL, dataL)
                        self.conn.commit()
                        
                        self.root.ids.equipName.text=""
                        self.root.ids.equipDesc.text=""
                        self.root.ids.equipText.text=""
                        self.root.ids.equipDropItem.set_item("Locations")
                        self.locID=""
                    except (Exception, psycopg2.DatabaseError) as error:
                        print(error)
            
    def pmOpen(self):
        self.cur.execute('select pmname, equipname, recurdate from recurt right join pmt using (pmid) left join equipt using (equipid)')
        pm_i = self.cur.fetchall()
        self.root.ids.pmList.clear_widgets()
        self.root.ids.pmList.add_widget(OneLineListItem(text='PM'))
        self.root.ids.pmList.add_widget(OneLineListItem(text='Equipment'))
        self.root.ids.pmList.add_widget(OneLineListItem(text='Last PM'))
        for i in pm_i:
            self.root.ids.pmList.add_widget(OneLineListItem(text=i[0]))
            self.root.ids.pmList.add_widget(OneLineListItem(text=i[1]))
            self.root.ids.pmList.add_widget(OneLineListItem(text='{}'.format(i[2])))
            
    def pastOpen(self):
        self.cur.execute(
            'select equipname, pmname, recurdate from recurt left join pmt using (pmid)left join equipt using (equipid)')
        past_i = self.cur.fetchall()
        self.root.ids.pastList.clear_widgets()
        self.root.ids.pastList.add_widget(OneLineListItem(text='Equipment'))
        self.root.ids.pastList.add_widget(OneLineListItem(text='Task'))
        self.root.ids.pastList.add_widget(OneLineListItem(text='Date'))
        for i in past_i:
            print('{}'.format(i[2]))
            self.root.ids.pastList.add_widget(OneLineListItem(text=i[0]))
            self.root.ids.pastList.add_widget(OneLineListItem(text=i[1]))
            self.root.ids.pastList.add_widget(OneLineListItem(text='{}'.format(i[2])))
            
    def addTask(self):
        insertL= """INSERT INTO taskT (taskName, taskDesc, taskCreationDate) VALUES (%s, %s, %s);"""
        taskName=self.root.ids.taskName.text
        taskDesc=self.root.ids.taskDesc.text
        taskDate = datetime.date.today()
        dataL=(taskName, taskDesc, taskDate)
        if taskName=="":
            self.root.ids.taskText.text = 'Task has to have a name.'
        else:
            if taskDesc=="":
                self.root.ids.taskText.text='Task needs a Description'
            else:
                try:
                    self.cur.execute(insertL, dataL)
                    self.conn.commit()
                    
                    self.root.ids.taskName.text=""
                    self.root.ids.taskDesc.text=""
                    self.root.ids.taskText.text=""
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    
    def taskMarkComp(self):
        insertL= """update taskt set taskdonedate=%s where taskid=%s;"""
        dataL=(datetime.date.today(), self.taskDetsID)
        self.cur.execute(insertL, dataL)
        self.conn.commit()
          
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        #self.theme_text_color='Custom'
        self.connectPostgres()
        return Builder.load_file('design.kv')
    
    def on_start(self):
        self.homeOpen()

if __name__ == "__main__":
    MainApp().run()
    
#update taskt set taskcreationdate='03/11/2025' where taskid=1