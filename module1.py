

def letter_point_Ass(mark):
    """functoin

    Args:
        mark (number): an interger to be turned to a grade point    

    Returns:
        float: a grade point corresponding to the entered mark
    """    """"""
    if mark <= 34:
        grade_point = 0.0
        return grade_point
    elif mark == 34 or mark <= 39:
        grade_point = 0.5
        return grade_point
    elif mark == 40 or mark <= 44:
        grade_point = 1.0
        return grade_point
    elif mark == 45 or mark <= 49:
        grade_point = 1.5
        return grade_point
    elif mark == 50 or mark <= 54:
        grade_point = 2.0
        return grade_point
    elif mark == 55 or mark <= 59:
        grade_point = 2.5
        return grade_point
    elif mark == 60 or mark <= 64:
        grade_point = 3.0
        return grade_point
    elif mark == 65 or mark <= 69:
        grade_point = 3.5
        return grade_point
    elif mark == 70 or mark <= 74:
        grade_point = 4.0
        return grade_point
    elif mark == 75 or mark <= 79:
        grade_point = 4.5
        return grade_point
    elif mark == 80 or mark <= 84:
        grade_point = 5.0
        return grade_point
    elif mark > 85 or mark <= 89:
        grade_point = 5.5
        return grade_point
    elif mark == 90 or mark <= 100:
        grade_point = 6.0
        return grade_point
    else:
        grade_point = 0.0
        
        return grade_point

