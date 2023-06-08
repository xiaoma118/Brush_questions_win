# 导入工具库
import ast
import sqlite3

# 创建连接
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, "database")
conn = sqlite3.connect('database')


# 游标

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn.row_factory = dict_factory
c = conn.cursor()


def insert_info(problems: [], classroom_id: int, exercise_id: int):
    """
    添加
    :return:
    """
    for i in problems:
        problem_id = i.get('problem_id')
        answer = i['user'].get('answer')
        info = (problem_id, classroom_id, str(answer), exercise_id)
        c.execute("INSERT INTO answer (problem_id,classroom_id,answer,exercise_id) \
                  VALUES (?,?,?,?)", info)
    conn.commit()
    print(c.fetchall())
    # 关闭连接
    # conn.close()


def get_info(problem_id):
    """
    查询
    :return:
    """

    info = c.execute(
        "select problem_id,classroom_id,answer from main.answer where problem_id= %s" % problem_id).fetchone()
    info['answer'] = ast.literal_eval(info['answer'])
    # for info in info_list:
    #     info['answer'] = ast.literal_eval(info['answer'])
    #     print(info)
    return info


def update_info():
    """
    更新
    :return:
    """
    c.execute("UPDATE answer set  exercise_id=3064957")
    conn.commit()


def add_user_info(user, header):
    """
    添加用户信息
    :return:
    """
    info = (user['name'], user['avatar'], header['Cookie'].replace(' ', ''), header['X-Csrftoken'], user['user_id'])

    user_info = db_get_user_info()
    if user_info:
        c.execute("UPDATE user_info set name=?,image=?,cookie=?,token=?,user_id=?", info)
    else:
        c.execute("INSERT INTO user_info (name,image,cookie,token,user_id) \
                          VALUES (?,?,?,?,?)", info)
    conn.commit()


def db_get_user_info():
    """
    获取用户信息
    默认第一条
    :return:
    """
    user_info = c.execute("select * from user_info").fetchone()
    print(user_info)
    return user_info


if __name__ == '__main__':
    # get_info()
    # update_info()
    db_get_user_info()
