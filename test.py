import sqlite3 as sql

def letter_grade(mark_in):
    """Function
    Args:
        mark (number): an interger to be turned to a grade point    
    Returns:
        float: a grade point candresponding to the entered mark
    """    """"""

    mark = float(mark_in)
    if mark < 35.0:
        grade_point =  "F"
    elif mark > 35.0 and mark < 40.0:
        grade_point =  "F+"
    elif mark > 40.0 and mark < 45.0:
        grade_point =  "E"
    elif mark > 45.0 and mark < 50.0:
        grade_point =  "E+"
    elif mark > 50.0 and mark < 55.0:
        grade_point = "D"
    elif mark > 55.0 and mark < 60.0:
        grade_point =  "D+"
    elif mark > 60.0 and mark < 65.0:
        grade_point =  "C"
    elif mark >65.0 and mark < 70.0:
        grade_point =  "C+"
    elif mark > 70.0 and mark < 75.0:
        grade_point =  "B"
    elif mark > 75.0 and mark < 80.0:
        grade_point =  "B+"
    elif mark > 80.0 and mark < 85.0:
        grade_point =  "A-"
    elif mark > 85.0 and mark < 90.0:
        grade_point =  "A"
    elif mark > 90.0 and mark < 101.0:
        grade_point = "A+"
    else:
        grade_point = "U"
    return grade_point


def summaryCal(CourseID):
    """Function

    Args:
        CourseID (str): database to read    

    Returns:
        Update: updates database summary
    """    """"""
    if CourseID!="":
        con = sql.connect(f"{CourseID}.db")
        cursor = con.cursor()
        cursor.execute("SELECT TITTLE FROM CATEGORY")
        array = cursor.fetchall()
        
        for i in array:
            for categ in i:
                cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ} LIMIT 1)")
                count = cursor.fetchone()
                try:
                    for icount in count:
                        if icount>0:
                            cursor.execute(f"INSERT OR REPLACE INTO SUMMARY(CATEGORY) VALUES(?)",(categ,))
                            con.commit()
                            cursor.execute(f"SELECT SUM(CONTRIB) FROM {categ} WHERE ID IS NOT NULL")
                            summCon = cursor.fetchone()
                            for summContr in summCon:
                                cursor.execute(f"SELECT COUNT(TITTLE) FROM {categ} WHERE ID IS NOT NULL")
                                ass_cnt = cursor.fetchone()
                                for ass_count in ass_cnt:
                                    cursor.execute(f"UPDATE SUMMARY SET TUG_COUNT ={ass_count} WHERE CATEGORY =?",(categ,))
                                    con.commit()
                                    summContr =float(summContr)
                                    if summContr>100.00000001:
                                        ass_count =float(ass_count)
                                        finalMark =summContr/ass_count
                                        mark_formt = "{:.1f}".format(finalMark)
                                        cursor.execute(f"UPDATE SUMMARY SET MARK ={mark_formt} WHERE CATEGORY =?",(categ,))
                                        con.commit()
                                    if summContr<100.0:
                                        cursor.execute(f"UPDATE SUMMARY SET MARK ={summContr} WHERE CATEGORY =?",(categ,))
                                        con.commit()
                except Exception:
                    pass
                
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM ( SELECT 0 FROM {categ} LIMIT 1)")
                    count = cursor.fetchone()
                    for icount in count:
                        if icount>0:
                            cursor.execute("SELECT WEIGHT FROM CATEGORY WHERE TITTLE =?",(categ,))
                            weighty = cursor.fetchone()
                            for weight in weighty:
                                weight=float(weight)
                                cursor.execute(f"SELECT MARK FROM SUMMARY WHERE CATEGORY =?",(categ,))
                                markar = cursor.fetchone()
                                for mark in markar:
                                    mark=float(mark)
                                    cat_contrib = (mark*weight)/100.0
                                    contr_fmt = "{:.1f}".format(cat_contrib)
                                    cursor.execute(f"UPDATE SUMMARY SET CAT_CONTRIB ={contr_fmt} WHERE CATEGORY =?",(categ,))
                                    con.commit()
                except Exception as e:
                    pass
    else:pass

if __name__=="__main__":
    
    CourseID =input("Enter CID: ")
    summaryCal(CourseID)
        

