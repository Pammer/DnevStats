	
import json
import openpyxl

def getData(login):
    with open('data_{}.json'.format(login), "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    maxViews = sorted(data[0]['postPreviews'], key=lambda k: int(k['views']), reverse=True)[:10]
    maxLikes = sorted(data[0]['postPreviews'], key=lambda k: int(k['likesCount']), reverse=True)[:10]
    maxComments = sorted(data[0]['postPreviews'], key=lambda k: int(k['commentsCount']), reverse=True)[:10]
    mywb = openpyxl.Workbook()
    sheet = mywb.active
    sheet.title = 'Данные'
    sheet['A2'] = 'Самые просматриваемые:'
    sheet['A3'] = 'Название'
   # sheet['B3'] = 'Ссылка'
    sheet['B3'] = 'Количество просмотров'
    rows  = 4

    print('Самые просмотренные:')
    for l in maxViews:
        print (l['title'] + ' ' + l['link'] + ' ' + str(l['views']))
        sheet['A' + str(rows)] = l['title']
        sheet['A' + str(rows)].hyperlink = 'http:' + l['link']
        sheet['A' + str(rows)].style = "Hyperlink"
        sheet['B' + str(rows)] = l['views']
        rows +=1
    print('Самые облайканые:')
    rows  = 4
    sheet['D2'] = 'Самые облайканые:'
    sheet['D3'] = 'Название'
    #sheet['F3'] = 'Ссылка'
    sheet['E3'] = 'Количество Лайков'
    for l in maxLikes:
        print (l['title'] + ' ' + l['link'] + ' ' + str(l['likesCount']))
        sheet['D' + str(rows)].value = l['title']
        sheet['D' + str(rows)].hyperlink = 'http:' + l['link']
        sheet['D' + str(rows)].style = "Hyperlink"
        sheet['E' + str(rows)] = l['likesCount']
        rows +=1
    print('Самые обкоменченные:')
    rows  = 4
    sheet['F2'] = 'Самые обкоменченные:'
    sheet['F3'] = 'Название'
   # sheet['J3'] = 'Ссылка'
    sheet['G3'] = 'Количество комментов'
    for l in maxComments:
        print (l['title'] + ' ' + l['link'] + ' ' + str(l['commentsCount']))
        sheet['F' + str(rows)].value = l['title']
        sheet['F' + str(rows)].hyperlink = 'http:' + l['link']
        sheet['F' + str(rows)].style = "Hyperlink"
        sheet['G' + str(rows)] = l['commentsCount']
        rows +=1
    #for preview in data:
     #   print(max(data['postPreviews'].items(), key=lambda x: x[1]))
    sheet['A1'] = 'Общее количество постов: {}'.format(data[0]['postsCount'])
    dims = {}
    for row in sheet.rows:
        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value)))) + 1    
    for col, value in dims.items():
        sheet.column_dimensions[col].width = value
    mywb.save('results_{}.xlsx'.format(login))

#getData('ТЬМА')
