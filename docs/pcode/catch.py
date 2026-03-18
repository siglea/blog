import requests

def get_douban_rating(title, author):
    url = f'https://api.douban.com/v2/book/search?q={title}&author={author}'
    response = requests.get(url)
    printResponse(response)
    data = response.json()
    
    if data['total'] > 0:
        book = data['books'][0]
        rating = book['rating']['average']
        return rating
    else:
        return '书籍未找到或没有评分'

titles_and_authors = [
    ('The House on Mango Street', 'Sandra Cisneros'),
    ('The Old Man and the Sea', 'Ernest Hemingway'),
    ('Fantastic Mr. Fox', 'Roald Dahl'),
    # 添加更多书籍
]

def printResponse(response):
    # 获取响应状态码
    status_code = response.status_code
    print(f'Status code: {status_code}')

    # 获取响应头
    headers = response.headers
    print(f'Headers: {headers}')

    # 获取响应内容
    content = response.content
    print(f'Content: {content}')

    # 将响应内容解码为字符串
    text = response.text
    print(f'Text: {text}')

    
for title, author in titles_and_authors:
    rating = get_douban_rating(title, author)
    print(f'{title} by {author}: 豆瓣评分 {rating}')
