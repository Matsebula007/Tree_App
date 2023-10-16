

def letter_point_Ass(mark_in):
    """functoin

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


    print (grade_point)


if __name__ =="__main__":

   
    pass