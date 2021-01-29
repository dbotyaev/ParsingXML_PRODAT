import os

import xmltodict
import csv
import json

from loguru import logger


XML_FILE = 'PRODAT.xml'
CSV_FILE = 'PRODAT.csv'

# первая строка CSV файла
TITLE = [
    'SenderPrdCode',
    'ReceiverPrdCode',
    'ProductName',
    'Price2',
    'RetailPrice',
    'CustPrice',
    'QTY',
    'UOM',
    'ParentProdGroup',
    'ProductGroup',
    'VendorProdNum',
    'Brand',
    'Img',
    'Attributes'
]


# функция разбора json одной записи в csv-файл
def rowWrite(doc):
    # формируем значения столбца Img
    image = ''
    if ('Image' in doc) and doc['Image']:
        if type(doc['Image']['Value']) == str:
            image = doc['Image']['Value']
        elif type(doc['Image']['Value']) == list:
            image = doc['Image']['Value'][0]

    # формируем значение столбца Attributes
    attributes = ''
    if doc['FeatureETIMDetails']:
        if type(doc['FeatureETIMDetails']['FeatureETIM']) == list:
            for attr in doc['FeatureETIMDetails']['FeatureETIM']:
                name = attr['FeatureName'] if attr['FeatureName'] else ''  # избавляемся от None
                value = attr['FeatureValue'] if attr['FeatureValue'] else ''
                uom = attr['FeatureUom'] if attr['FeatureUom'] else ''
                attributes += f"{name}:{value} {uom}^"
        elif type(doc['FeatureETIMDetails']['FeatureETIM']) == dict:
            attr = doc['FeatureETIMDetails']['FeatureETIM']
            name = attr['FeatureName'] if attr['FeatureName'] else ''  # избавляемся от None
            value = attr['FeatureValue'] if attr['FeatureValue'] else ''
            uom = attr['FeatureUom'] if attr['FeatureUom'] else ''
            attributes = f"{name}:{value} {uom}^"

    row = [
        # проверяем наличие ключа в словаре и что значения по ключу не пустое, избавляемся от None
        doc['SenderPrdCode'] if ('SenderPrdCode' in doc) and doc['SenderPrdCode'] else '',
        doc['ReceiverPrdCode'] if ('ReceiverPrdCode' in doc) and doc['ReceiverPrdCode'] else '',
        doc['ProductName'] if ('ProductName' in doc) and doc['ProductName'] else '',
        '',  # Price2
        '',  # RetailPrice
        '',  # CustPrice
        '',  # QTY
        doc['UOM'] if ('UOM' in doc) and doc['UOM'] else '',
        doc['ParentProdGroup'] if ('ParentProdGroup' in doc) and doc['ParentProdGroup'] else '',
        doc['ProductGroup'] if ('ProductGroup' in doc) and doc['ProductGroup'] else '',
        doc['VendorProdNum'] if ('VendorProdNum' in doc) and doc['VendorProdNum'] else '',
        doc['Brand'] if ('Brand' in doc) and doc['Brand'] else '',
        image,
        attributes
    ]
    return row


def parseXML(xmlFile, csvFile):
    # открываем xml-файл и парсим в словарь
    logger.info(f'Считывание данных из xml-файла {xmlFile}')
    with open(xmlFile) as xml_file:
        xml = xml_file.read()
        logger.info(f'Данные успешно считаны')

        logger.info(f'Конвертация данных в словарь')
        data_dict = xmltodict.parse(xml)
        logger.info(f'Данные успешно сконвертированы')

    # сохранянем данные json-файл
    logger.info(f'Запись данных в формате json в файл data.json')
    with open('data.json', 'w', encoding='utf-8') as file_json:
        json.dump(data_dict, file_json, ensure_ascii=False)
        logger.info(f'Данные успешно записаны в файл')

    # считываем данные из json-файла и получаем список для обработки в сsv-файл
    logger.info(f'Чтение данных из файла data.json для конвертации в csv')
    with open("data.json", "r", encoding="utf-8") as file:
        data = file.read()
        json_data = json.loads(data)
        logger.info(f'Данные успешно считаны')
        docdetails = json_data['Document']['DocDetail']
        logger.info(f'Получен список DocDetail для обработки')

    # формирование csv-файла c результатом
    logger.info(f'Создание файла {csvFile} для выгрузки результатов')
    with open(csvFile, 'w', encoding='utf-8') as file_csv:
        file_writer = csv.writer(file_csv, delimiter=";", lineterminator="\r")
        file_writer.writerow(TITLE)
        logger.info(f'Записана первая строка в файл с заголовками столбцов')
        count = 1
        for doc in docdetails:
            file_writer.writerow(rowWrite(doc))
            logger.info(f'{count} Записан товар {doc["SenderPrdCode"]}')
            count += 1



if __name__ == '__main__':
    # настраиваем логирование
    path_log = os.getcwd() + f'\\logs\\debug.log'
    logger.add(path_log, level='DEBUG', compression="zip", rotation="9:00", retention="10 days")

    logger.info(f'Запуск скрипта')

    parseXML(XML_FILE, CSV_FILE)

    logger.info(f'Скрипт завершен')
