import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from typing import List
import json
import uuid


tree = et.parse("rup.xml")
root = tree.getroot()
root_child = root[0][0]


def get_plan_rup():
    """
    Парсит XML и формирует структуру данных с информацией об ООП и учебном плане.
    Новая структура: OOP (StudyPlan) и список циклов (stady_plan),
    в которых находятся дочерние циклы, план строк и ячейки часов.
    """
    plan_dict = []
    rup = {}

    plany_ciclov: List[Element] = []
    plany_ciclov_childs: List[Element] = []
    plany_novie_chasy: List[Element] = []
    plany_stroky: List[Element] = []
    plany_stroky_childs: List[Element] = []

    for child in root_child:
        tag_name = child.tag.replace("{http://tempuri.org/dsMMISDB.xsd}", '')
        match tag_name:
            case "ПланыЦиклы":
                if child.attrib.get('КодРодителя'):
                    plany_ciclov_childs.append(child)
                else:
                    plany_ciclov.append(child)
            case "ПланыСтроки":
                if child.attrib.get('КодРодителя'):
                    plany_stroky_childs.append(child)
                else:
                    plany_stroky.append(child)
            case "ПланыНовыеЧасы":
                plany_novie_chasy.append(child)
            case "ООП":
                rup = {
                    'id': str(uuid.uuid4()),
                    'specialization_code': child.get('Шифр'),
                    'name': child.get('Название'),
                    'create_date': child.get('ДатаДокумента'),
                    'gos_type': child.get('ТипГОСа'),
                    'stady_plan': []
                }

    for cicl in plany_ciclov:
        plan_dict.append({
            "id": cicl.get('Код'),
            "identificator": cicl.get('Идентификатор'),
            "cycles": cicl.get('Цикл'),
            "children": []
        })

    for child in plany_ciclov_childs:
        parent_code = child.get("КодРодителя")
        for parent in plan_dict:
            if parent_code == parent['id']:
                parent['children'].append({
                    "id": child.get('Код'),
                    "identificator": child.get('Идентификатор'),
                    "cycles": child.get('Цикл'),
                    "parent_id": child.get('КодРодителя'),
                    "plans_of_string": []
                })

    for cycl in plan_dict:
        cycl['id'] = str(uuid.uuid4())
        for child in cycl['children']:
            child_id_local = child['id']
            child['id'] = str(uuid.uuid4())
            child['parent_id'] = cycl['id']
            for string in plany_stroky:
                string_block_id = string.get("КодБлока")
                if child_id_local == string_block_id:
                    parent_string_id_local = string.get('Код')
                    parent_string_object = {
                        'id': str(uuid.uuid4()),
                        'discipline': string.get('Дисциплина'),
                        'code_of_cycle_block': child['id'],
                        'clock_cells': [],
                        'children_strings': []
                    }
                    for child_string in plany_stroky_childs:
                        code_of_parent = child_string.get('КодРодителя')
                        if parent_string_id_local == code_of_parent:
                            child_string_id_local = child_string.get('Код')
                            child_string_object = {
                                'id': str(uuid.uuid4()),
                                'discipline': child_string.get('Дисциплина'),
                                'code_of_cycle_block': child['id'],
                                'parent_string_id': parent_string_object['id'],
                                'clock_cells': [],
                            }
                            for hour in plany_novie_chasy:
                                new_hour_parent_id = hour.get("КодОбъекта")
                                if new_hour_parent_id == child_string_id_local:
                                    child_string_object['clock_cells'].append({
                                        'id': str(uuid.uuid4()),
                                        'code_of_type_work': hour.get("КодВидаРаботы"),
                                        'code_of_type_hours': hour.get("КодТипаЧасов"),
                                        'course': hour.get("Курс"),
                                        'semestr': hour.get("Семестр"),
                                        'count_of_clocks': hour.get("Количество"),
                                        'parent_string_id': child_string_object['id']
                                    })
                            parent_string_object['children_strings'].append(child_string_object)
                    for hour in plany_novie_chasy:
                        new_hour_parent_id = hour.get("КодОбъекта")
                        if new_hour_parent_id == parent_string_id_local:
                            parent_string_object['clock_cells'].append({
                                'id': str(uuid.uuid4()),
                                'code_of_type_work': hour.get("КодВидаРаботы"),
                                'code_of_type_hours': hour.get("КодТипаЧасов"),
                                'course': hour.get("Курс"),
                                'semestr': hour.get("Семестр"),
                                'count_of_clocks': hour.get("Количество"),
                                'parent_string_id': parent_string_object['id']
                            })
                    child['plans_of_string'].append(parent_string_object)

    rup['stady_plan'] = plan_dict

    with open("plan.json", "w", encoding="utf-8") as file:
        json.dump(rup, file, ensure_ascii=False, indent=4)
    print("=== JSON data (from XML) ===")
    print(json.dumps(rup, ensure_ascii=False, indent=4))
    return rup

get_plan_rup()
