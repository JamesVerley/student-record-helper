# ==========================================
# Dependency
# ==========================================
import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import dbSetup

# ==========================================
# Set Up
# ==========================================
app = Flask(__name__)
CORS(app)

# ==========================================
# Uncomment the follow code to reset data.db
# ==========================================
if os.path.exists('data.db'):
    os.remove('data.db')
    dbSetup.setupSQLiteDB()

sqlite3.connect('data.db')

# ==========================================
# SQL Connector - 1. Jsonify query results
# ==========================================

def JsonifyQueryRecords(sqlScript, labels, variableData=[]):
    labelled_records = []
    with sqlite3.connect('data.db') as dbconn_local:
        try:
            c = dbconn_local.cursor()
            c.execute(sqlScript, variableData)
            records = c.fetchall()

            for row in records:
                labelled_record = {}
                labelCounter = 0
                for label in labels:
                    labelled_record[label] = row[labelCounter]
                    labelCounter = labelCounter + 1
                labelled_records.append(labelled_record)
            c.close()
            return jsonify(labelled_records)
        except sqlite3.Error as e:
            print(e)

# 1.1 Students - Get All Students

sql_get_all_students = """ 
    SELECT * FROM student; 
"""

@app.route('/get-all-students', methods=['GET'])
def getAllStudents():
    labels = ["id", "student_number", "first_name", "last_name", "birthday", "gender"]
    return JsonifyQueryRecords(sql_get_all_students, labels)

# 1.2 Students - Get Student By ID

sql_get_student_by_id = """ 
    SELECT * FROM student WHERE id = ?;
"""
@app.route('/get-student-by-id', methods=['GET'])
def getStudentById():
    studentId = request.args.get('id')
    labels = ["id", "student_number", "first_name", "last_name", "birthday", "gender"]
    return JsonifyQueryRecords(sql_get_student_by_id, labels, [studentId])

# 1.3 Students - Get Student By Subject Code

sql_get_student_by_subject_code = """ 
SELECT
	student.student_number,
	student.first_name,
	student.last_name,
	student.gender,
	student.birthday,
	subject.subject_code,
	subject.subject_name
FROM enrolment
INNER join subject on enrolment.subject_id = subject.id
INNER join registration on enrolment.registration_id = registration.id
INNER join student on registration.student_id = student.id
WHERE subject_code=?;
""" 
@app.route('/get-student-by-subject-code', methods=['GET'])
def getStudentBySubjectCode():
    subjectCode = request.args.get('code')
    labels = ["studentNumber", "firstName", "lastName", "gender", "birthday", "subjectCode", "subjectName"]
    return JsonifyQueryRecords(sql_get_student_by_subject_code, labels, [subjectCode])

# 2.1 Subjects - get subjects (id and name) by student id

sql_get_subjects_using_student = """
SELECT
    subject.id,
    subject.subject_code,
    subject.subject_name,
	subject.subject_description
FROM
    student
    INNER JOIN registration ON student.id = registration.student_id
    INNER JOIN enrolment ON registration.id = enrolment.registration_id
    INNER JOIN subject ON enrolment.subject_id = subject.id
WHERE
    student.id = ?;
"""

@app.route('/getsubjectsbystudentid', methods=['GET'])
def getSubjectsByStudentId():
    studentId = request.args.get('id')
    labels = ["subjectId", "subjectCode", "subjectName", "subjectDescription"]
    return JsonifyQueryRecords(sql_get_subjects_using_student, labels, [studentId])

# 2.2 Subjects - get subjects given a teacher id

sql_get_subjects_using_teacher = """
SELECT
    subject.id,
    subject.subject_code,
    subject.subject_name,
	subject.subject_description
FROM
    teacher
    INNER JOIN allocation ON teacher.id = allocation.teacher_id
    INNER JOIN subject ON allocation.subject_id = subject.id
WHERE
    teacher.id = ?;
"""

@app.route('/getsubjectsbyteacherid', methods=['GET'])
def getSubjectsByTeacherId():
    teacherId = request.args.get('id')
    labels = ["subjectId", "subjectCode", "subjectName", "subjectDescription"]
    return JsonifyQueryRecords(sql_get_subjects_using_teacher, labels, [teacherId])

# 2.3 Subjects - get subjects given a yearlevel id

sql_get_subjects_using_level = """
SELECT
    subject.id,
    subject.subject_code,
    subject.subject_name,
	subject.subject_description
FROM
    level
    INNER JOIN registration ON level.id = registration.level_id
    INNER JOIN enrolment ON registration.id = enrolment.registration_id
    INNER JOIN subject ON enrolment.subject_id = subject.id
WHERE
    level.id = ?;
"""

# 3.1 Criteria - get criteria given a subject

sql_get_criteria_using_subject = """
SELECT
	criterion.id,
	criterion.allocation_id,
	criterion.datatype,
	criterion.name,
	criterion.description,
	criterion.min,
	criterion.max,
	criterion.auxiliary
FROM
    subject
    INNER JOIN allocation ON subject.id = allocation.subject_id
    INNER JOIN criterion ON allocation.id = criterion.allocation_id
WHERE
    subject.id = ?;
"""

@app.route('/getcriteriabysubjectid', methods=['GET'])
def getCriteriaBySubjectId():
    subjectId = request.args.get('id')
    labels = ["criterionId", "allocationId", "datatype", "name", "description", "min", "max", "auxiliary"]
    return JsonifyQueryRecords(sql_get_criteria_using_subject, labels, [subjectId])

# ==========================================
# Step to grade students
# 1. Teacher query sessions info based on subject code, day, and teacher id
# 2. Query all students and relevant grade info based on session id
# 3. Grades are updated to DB
# ==========================================

sql_get_session_by_subjectcode_day_teacherid = """ 
SELECT 
	subject.subject_code,
	subject.subject_name,
	subject_periods.day,
	subject_periods.start_time,
	subject_periods.end_time
FROM 
	session
	INNER JOIN subject_periods on session.period_id = subject_periods.id
	INNER JOIN subject on subject_periods.subject_id = subject.id
WHERE
	subject_code = "ENG101" AND
	day = "Monday"
;
""" 

sql_get_session_full_table = """
SELECT 
	student.student_number,
	student.first_name,
	student.last_name,
	student.gender,
	subject.subject_code,
	subject.subject_name,
	subject_periods.day,
	subject_periods.start_time,
	subject_periods.end_time,
    session.session_date
FROM 
	session
	INNER JOIN subject_periods on session.period_id = subject_periods.id
	INNER JOIN subject on subject_periods.subject_id = subject.id
	INNER JOIN enrolment on enrolment.subject_id = subject.id
	INNER JOIN registration on enrolment.registration_id = registration.id
	INNER JOIN student on registration.student_id = student.id
WHERE
	subject_code = "ENG101" AND
	day = "Monday" AND
	session_date = "19/2/2019"
;
"""

sql_test = """ 
SELECT 
	student.student_number,
	student.first_name,
	student.last_name,
	subject.subject_code,
	session.session_date,
	criterion.name,
	grade.grade
FROM 
	session
	INNER JOIN subject_periods on session.period_id = subject_periods.id
	INNER JOIN subject on subject_periods.subject_id = subject.id
	INNER JOIN enrolment on enrolment.subject_id = subject.id
	INNER JOIN registration on enrolment.registration_id = registration.id
	INNER JOIN student on registration.student_id = student.id
	INNER JOIN grade on session.id = grade.session_id AND grade.enrolment_id = enrolment.id
	INNER JOIN criterion on grade.criteria_id = criterion.id
WHERE
	subject_code = "ENG101" AND
	day = "Monday" AND
	session_date = "19/2/2019"
ORDER BY student.student_number
;
"""

# ==========================================
# SQL Connector - Session
# ==========================================

sql_get_sessions_by_subjectcode_date = """
SELECT
    session.id,
	session.session_date,
	subject.subject_code,
	subject.subject_name,
	subject_periods.day,
	subject_periods.start_time,
	subject_periods.end_time
FROM
	session
	INNER JOIN subject_periods on session.period_id = subject_periods.id
	INNER JOIN subject on subject_periods.subject_id = subject.id
WHERE
	subject_code=? AND
	session_date=?
;
"""

@app.route('/get-sessions-by-subjectcode-date', methods=['GET'])
def getSessionsBySubjectCodeDate():
    subjectCode = request.args.get('code')
    sessionDate = request.args.get('date')
    labels = ["sessionId", "sessionDate", "subjectCode", "subjectName", "day", "startTime", "endTime"]
    return JsonifyQueryRecords(sql_get_sessions_by_subjectcode_date, labels, [subjectCode, sessionDate])


# ==========================================
# SQL Connector - Home and Default API
# ==========================================

@app.route('/', methods=['GET'])
def getHomePage():
    return jsonify({"message":"ok"})

@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"message":"local path not found"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)
