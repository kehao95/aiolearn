_URL_BASE = 'https://learn.tsinghua.edu.cn/MultiLanguage/'
_URL_LOGIN = _URL_BASE + 'lesson/teacher/loginteacher.jsp'
_URL_PREF = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/'
# Semesters
_URL_CURRENT_SEMESTER = _URL_PREF + 'MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = _URL_PREF + 'MyCourse.jsp?typepage=2'
_URL_PERSONAL_INFO = _URL_BASE + 'vspace/vspace_userinfo1.jsp'
# Courses
_ID_COURSE_URL = _URL_PREF + 'course_locate.jsp?course_id=%s'
# Differet Sections of Course
_COURSE_MSG = _URL_BASE + 'public/bbs/getnoteid_student.jsp?course_id=%s'
_COURSE_INFO = _URL_PREF + 'course_info.jsp?course_id=%s'
_COURSE_FILES = _URL_PREF + 'download.jsp?course_id=%s'
_COURSE_LIST = _URL_PREF + 'ware_list.jsp?course_id=%s'
_COURSE_WORK = _URL_PREF + 'hom_wk_brw.jsp?course_id=%s'
# Object Detail Page
_PAGE_MSG = _URL_BASE + 'public/bbs/%s'
_PAGE_FILE = 'http://learn.tsinghua.edu.cn/kejian/data/%s/download/%s'

# for new WebLearning
_GET_TICKET = _URL_PREF + 'MyCourse.jsp?language=cn'
_URL_BASE_NEW = 'http://learn.cic.tsinghua.edu.cn/'
_URL_PREF_NEW = 'http://learn.cic.tsinghua.edu.cn/b/myCourse/'
_COURSE_MSG_NEW  = _URL_PREF_NEW + 'notice/listForStudent/%s'
_COURSE_WORK_NEW = _URL_PREF_NEW + 'homework/list4Student/%s/0'
_COURSE_FILE_NEW = _URL_PREF_NEW + 'tree/getCoursewareTreeData/%s/0'
