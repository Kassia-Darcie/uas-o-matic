import time
import teste

cookies = teste.login()
courses = teste.get_materias()
for course in courses:
    uas = teste.get_course_uas(course['url'], course)
    #print(courses)

    teste.download_pdfs(course['uas'], course['name'], cookies)
time.sleep(3)
