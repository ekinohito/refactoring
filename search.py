from urllib.request import urlopen
from urllib.parse import quote
from hashlib import md5
from json import loads
from bs4 import BeautifulSoup
from xlrd import open_workbook
from xlwt import Workbook
from itertools import count


# error raised when there is literally no data
class NoDataError(Exception):
    pass


def get_subjects():
    return ['рус', 'мат', 'инф', 'физ']


# get md5 hash of full name
def get_hash(name: str) -> str:
    return md5(name.encode()).hexdigest()


# get url of json file containing information about all students whose hash starts with 2 certain digits
def get_search_query(name_hash: str) -> str:
    return f"http://admlist.ru/fio/{name_hash[:2]}.json"


# search for all registered applications made by student
def search(name: str, timeout=15):
    name_hash = get_hash(name)
    query = get_search_query(name_hash)
    try:
        return loads(urlopen(query, timeout=timeout).read().decode())[name_hash]
    except KeyError:
        raise NoDataError
    except TimeoutError:
        raise NoDataError


# get url of html file containing table of all students participating in certain contest
def get_list_query(contest: str):
    return f"http://admlist.ru/{contest}.html"


# process certain application
def process(name, application):
    contest = application[0]
    query = get_list_query(contest)
    bs = BeautifulSoup(urlopen(query).read().decode(), features="html.parser")
    legend = [child.text for child in bs.thead.tr.children]
    row = bs.find("td", text=name).parent
    values = [child.text for child in row.children]
    result = {}
    for key, value in zip(legend, values):
        result[key] = value
    return result


# process all student's applications
def process_applications(name):
    result = {subject: None for subject in get_subjects()}
    try:
        search_result = search(name)
    except NoDataError:
        return result
    for application in search_result:
        new_data = process(name, application)
        print(f"\t\t{new_data}")
        for k in result:
            if not result[k] and new_data.get(k):
                result[k] = new_data[k]
    return result


def get_search_page(name: str):
    query = '+'.join(map(quote, name.split(' ')))
    r = urlopen(f"http://admlist.ru/search.html?fio={query}")
    return r.read().decode()


def students_generator(file_name: str, sheet_name: str = 'Бюджетники', start: int = 0):
    table = open_workbook(file_name)
    sheet = table.sheet_by_name(sheet_name)
    for cell in sheet.col(1, 2 + start):
        raw = cell.value.strip()
        yield raw[:-1].strip() if raw.endswith('*') else raw


# get a pair of write and save to xlsx methods
def get_xlsx_writer(file_name):
    workbook = Workbook()
    worksheet = workbook.add_sheet('Аспиранты')
    return lambda x, y, v: worksheet.write(y, x, v), lambda: workbook.save(file_name)


def process_students(generator, counter=None, writer=get_xlsx_writer('result.xls')):
    if counter is None:
        counter = count(0, 1)
    write, save = writer
    subjects = get_subjects()
    write(0, 0, 'номер')
    write(1, 0, 'имя')
    for index, subject in enumerate(subjects):
        write(2 + index, 0, subject)
    for student_number, student_name in zip(counter, generator):
        try:
            result = process_applications(student_name)
        except BaseException as e:
            print(e)
            result = {subject: None for subject in get_subjects()}
        print(f"{student_number}: {student_name}\t{result}")
        write(0, 1 + student_number, student_number)
        write(1, 1 + student_number, student_name)
        for index, subject in enumerate(subjects):
            try:
                score = int(result[subject])
            except TypeError:
                score = None
            write(2 + index, 1 + student_number, score)
        save()


def demo():
    name = 'Богатюк Елизавета Сергеевна'
    print(process_applications(name))


if __name__ == '__main__':
    # process_students(students_generator('enr-site-list-first-Moscow.xlsx'))
    process_students(students_generator('source_inf.xlsx', 'Абитуриенты на 01.03.02', 0),
                     writer=get_xlsx_writer('result_inf.xls'))
