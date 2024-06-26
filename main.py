from flask import Flask, abort, request
import json
from datetime import datetime
import hashlib, secrets

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def hash_password(p):#взятие хеш-кода от пароля
    return hashlib.sha256(p.encode()).hexdigest()

def generate_user_key():#генерируется ключ при входе пользователя в аккаунт, длина 32 символа
    return secrets.token_hex(16)


def serialize_datetime(obj):# функция нужна для вывода datetime в формате json
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user="postgres",password="V0r0beshek65",host="127.0.0.1",port="5432",database="agro_tracker")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # Курсор для выполнения операций с базой данных
    cursor = connection.cursor()

except (Exception, Error) as error:
    print("\nОшибка при работе с PostgreSQL", error)
# finally:
#     if connection:
#         cursor.close()
#         connection.close()
#         print("\nСоединение с PostgreSQL закрыто")
app = Flask(__name__)
# api = Api(app)


@app.route('/agro_tracker/works/<int:work_id>', methods=['GET'])
def select_work(work_id):
    # вывод основной информации о полевой работе, которая содержится в таблице works
    cursor.execute(f"select works.id,technics.name, cultures.name, fields.name, work_types.name,users.name,works.name, start_time, end_time from works, technics, cultures, fields, users, work_types where works.technic_id = technics.id and works.culture_id = cultures.id and works.field_id = fields.id and works.work_type_id = work_types.id and works.creator_id = users.id and works.id = {work_id}")
    record = cursor.fetchall()
    # необходимо перевести формат datetime в пригодный для json
    json_start_time = json.dumps(record[0][7], default=serialize_datetime)
    json_end_time = json.dumps(record[0][8], default=serialize_datetime)
    field_name = record[0][3]
    work = {
        "work_id": record[0][0],
        "technic_name": record[0][1],
        "culture_name": record[0][2],
        "field_name": record[0][3],
        "work_type_name": record[0][4],
        "creator_name": record[0][5],
        "name": record[0][6],
        "start_time": json_start_time,
        "end_time": json_end_time
    }
    if (cursor.rowcount == 1): # если информация по такой работе имеется
        if (record[0][8] != None):  # если время окончания работы не пустое, вывод дополнительной информации
            cursor.execute(f"select parameters.id,parameters.name, work_parameter_values.value from works, work_types, work_parameter_values, parameters where works.work_type_id = work_types.id and work_parameter_values.work_id = works.id and parameters.id = work_parameter_values.parameter_id and works.id = {work_id}")
            record0 = cursor.fetchall()
            if(cursor.rowcount==1):# если дополнительный параметр один, вывод информации только о топливе
                work = {
                    "work_id": record[0][0],
                    "technic_name": record[0][1],
                    "culture_name": record[0][2],
                    "field_name": record[0][3],
                    "work_type_name": record[0][4],
                    "creator_name": record[0][5],
                    "name": record[0][6],
                    "start_time": json_start_time,
                    "end_time": json_end_time,
                    "fuel": record0[0][2]
                }
            elif(cursor.rowcount==2):# если дополнительных параметров два, вывод информации о топливе и втором параметре
                work = {
                    "work_id": record[0][0],
                    "technic_name": record[0][1],
                    "culture_name": record[0][2],
                    "field_name": record[0][3],
                    "work_type_name": record[0][4],
                    "creator_name": record[0][5],
                    "name": record[0][6],
                    "start_time": json_start_time,
                    "end_time": json_end_time,
                    "fuel": record0[0][2],
                    "second_parameter_name": record0[1][1],
                    "second_parameter_value": record0[1][2]
                }

        else:#выводим основное инфо, если время окончания работы пустое => работа еще не завершена
            work['end_time']="В процессе"
        # вывод точек маршрута сельскохозяйственной техники, который был проделан в ходе выполнения данной полевой работы
        cursor.execute(f"select latitude,longitude,point_time,id from points where work_id={work_id};")
        record0 = cursor.fetchall()
        points = []
        if (cursor.rowcount > 0):
            for i in range(cursor.rowcount):
                json_point_time = json.dumps(record0[i][2], default=serialize_datetime)
                point = {
                    "latitude": record0[i][0],
                    "longitude": record0[i][1],
                    "point_time": json_point_time,
                    "id": record0[i][3],
                }
                points.append(point)
        work['points']=points
        # вывод границ поля, на котором выполнялась полевая работа
        cursor.execute(f"select area from fields where name='{field_name}';")
        record1=cursor.fetchall()
        if (cursor.rowcount > 0):
            area=str(record1[0])
            field_points=area.split('),(')
            field_points[0]=field_points[0].split('(\'((')[1]
            field_points[len(field_points)-1] = field_points[len(field_points)-1].split('))\',')[0]
            field_area = []
            for i in range(len(field_points)):
                lat,lon=field_points[i].split(',')
                point=[]
                point.append(lat)
                point.append(lon)
                field_area.append(point)
            work['field_area'] = field_area
        else:
            work['field_area'] = None
        return work, 200
    else:
        abort(404)


@app.route('/agro_tracker/works/<int:creator_id>&<string:start_time>', methods=['GET'])
def select_work_id(creator_id,start_time):
    # вывод ID только что созданной оператором полевой работы
    cursor.execute(f"select id from works where start_time='{start_time}' and creator_id={creator_id}")
    record = cursor.fetchall()
    if(cursor.rowcount>=1):
        work_id={"work_id": record[0][0]}
        return work_id, 200
    else:
        abort(404)


@app.route('/agro_tracker/works/', methods=['GET'])
def select_works():
    # вывод списка всех полевых работ, имеющихся в базе данных
    cursor.execute(f"select works.id,fields.name, start_time, work_types.name, end_time,technics.name from works, technics,fields,work_types where works.technic_id=technics.id  and works.field_id=fields.id and works.work_type_id=work_types.id order by works.end_time desc;")
    record = cursor.fetchall()
    works=[]
    if (cursor.rowcount > 1):
        for i in range(cursor.rowcount):
            json_start_time = json.dumps(record[i][2], default=serialize_datetime)
            json_end_time = json.dumps(record[i][4], default=serialize_datetime)
            work = {
                    "work_id": record[i][0],
                    "field_name": record[i][1],
                    "start_time": json_start_time,
                    "work_type_name": record[i][3],
                    "end_time": json_end_time,
                    "technic_name": record[i][5]
                }
            works.append(work)
        return works, 200
    else:
        abort(404)


@app.route('/agro_tracker/start_form/', methods=['GET'])
def select_start_form():
    # вывод списков параметров полевых работ для создания новой полевой работы
    start_form={}#информация о типах обработки, технике, культурах, полях
    # добавляем типы обработки
    cursor.execute(f"select id,name from work_types order by id asc;")
    record = cursor.fetchall()
    worktypes=[]
    if (cursor.rowcount > 1):
        for i in range(cursor.rowcount):
            worktype = {
                    "worktype_id": record[i][0],
                    "worktype_name": record[i][1]
                }
            worktypes.append(worktype)
        start_form["worktypes"] = worktypes
    else:
        abort(404)
    # добавляем поля
    cursor.execute(f"select id,name from fields order by id asc;")
    record = cursor.fetchall()
    fields = []
    if (cursor.rowcount > 1):
        for i in range(cursor.rowcount):
            field = {
                "field_id": record[i][0],
                "field_name": record[i][1]
            }
            fields.append(field)
        start_form["fields"] = fields
    else:
        abort(404)
    # добавляем технику
    cursor.execute(f"select id,name from technics  order by id asc;")
    record = cursor.fetchall()
    technics = []
    if (cursor.rowcount > 1):
        for i in range(cursor.rowcount):
            technic = {
                "technic_id": record[i][0],
                "technic_name": record[i][1]
            }
            technics.append(technic)
        start_form["technics"] = technics
    else:
        abort(404)
    # добавляем культуры
    cursor.execute(f"select id,name from cultures where id>0 order by id asc;")
    record = cursor.fetchall()
    cultures = []
    if (cursor.rowcount > 1):
        for i in range(cursor.rowcount):
            culture = {
                "culture_id": record[i][0],
                "culture_name": record[i][1]
            }
            cultures.append(culture)
        start_form["cultures"] = cultures
    else:
        abort(404)
    return start_form, 200


@app.route('/agro_tracker/users', methods=['GET'])
def select_user():
    # проверка существования пользователя с такой парой логин-пароль
    login = request.args.get('login')
    password = hash_password(request.args.get('password'))# в базе хранится хеш от пароля, поэтому для сравнения от введенного пароля берется хеш
    cursor.execute(f"SELECT users.id,users.name,roles.name as role, login,password from users left join roles on roles.id=role_id where login='{login}' and password='{password}'")
    record = cursor.fetchall()
    if(cursor.rowcount==1):# если пользователь найден, для него генерируется токен
        #генерация и запись токена
        user_id=record[0][0]
        token = generate_user_key()
        if (cursor.rowcount == 1):
            user = {
                    "id": record[0][0],
                    "name": record[0][1],
                    "role": record[0][2],
                    "login": record[0][3],
                    "password": record[0][4],
                    "token": token
                }
            cursor.execute(f"insert into user_keys(user_id, key) values({user_id}, '{token}')")
            connection.commit()
            return user, 200
    else:
        abort(404)


@app.route('/agro_tracker/user_info', methods=['GET'])
def select_user_info():
    # вывод информации об авторизованном пользователе
    token = request.args.get('token')
    cursor.execute(f"SELECT users.id,users.name,roles.name as role, login,password from users left join roles on roles.id=role_id left join user_keys on users.id=user_keys.user_id where user_keys.key='{token}'")
    record = cursor.fetchall()
    if (cursor.rowcount == 1 and  len(record)==1):
        user = {
                "id": record[0][0],
                "name": record[0][1],
                "role": record[0][2],
                "login": record[0][3],
                "password": record[0][4],
                "token": token
            }
        return user, 200
    else:
        abort(404)


@app.route('/agro_tracker/works/insert', methods=['POST'])
def insert_work():
    # добавление в базу данных новой полевой работы
    if not request.json or not 'name' in request.json or not 'culture_id' in request.json or not 'technic_id' in request.json or not 'field_id' in request.json or not 'work_type_id' in request.json or not 'creator_id' in request.json or not 'start_time' in request.json:
        abort(400)
    culture_id=request.json['culture_id']
    technic_id=request.json['technic_id']
    field_id=request.json['field_id']
    work_type_id=request.json['work_type_id']
    creator_id=request.json['creator_id']
    name=request.json['name']
    start_time=request.json['start_time']
    work = {
        "culture_id": culture_id,
        "technic_id": technic_id,
        "field_id": field_id,
        "work_type_id": work_type_id,
        "creator_id": creator_id,
        "name": name,
        "start_time": start_time
    }
    cursor.execute(f"insert into works(culture_id, technic_id, field_id, work_type_id, creator_id, name, start_time) values({culture_id}, {technic_id}, {field_id}, {work_type_id}, {creator_id}, '{name}', '{start_time}')")
    connection.commit()
    return work, 201

@app.route('/agro_tracker/works/update', methods=['POST'])
def update_work():
    # обновление существующей в базе данных полевой работы: добавление времени окончания ее выполнения
    if not request.json or not 'work_id' in request.json or not 'end_time' in request.json:
        abort(400)
    work_id=request.json['work_id']
    end_time=request.json['end_time']
    work = {
        "work_id": work_id,
        "end_time": end_time
    }
    cursor.execute(f"update works set end_time='{end_time}' where id={work_id}")
    connection.commit()
    return work, 201

@app.route('/agro_tracker/work_parameter_values/', methods=['POST'])
def insert_work_parameter_values():
    # отправка в базу данных параметров полевой работы, которые вводятся по окончании ее выполнения
    if not request.json or not 'work_id' in request.json or not 'fuel' in request.json or not 'second_parameter_value' in request.json:
        abort(400)
    # получаем по типу выполненной работы параметры, которые нужно передать
    work_id=request.json['work_id']
    fuel=request.json['fuel']# топливо - всегда передается, для любого вида обработки поля
    second_parameter_value=request.json['second_parameter_value']# второй параметр может отсутствовать, название разное для разных типов обработки поля
    cursor.execute(f"select parameter_id,parameters.name from work_type_parameters left join parameters on parameters.id=parameter_id where work_type_id=(select work_type_id from works where id={work_id})")
    record = cursor.fetchall()
    parameters_count=cursor.rowcount
    # вносим соответствующие параметры (сколько параметров, столько и запросов (в нынешней ситуации 1-2 запроса)
    # топливо вносится всегда
    cursor.execute(f"insert into work_parameter_values(work_id, parameter_id, value) values({work_id}, {record[0][0]}, {fuel})")
    connection.commit()
    # второй параметр вносится для всех типов, кроме обычной обработки
    if (parameters_count == 2):
        cursor.execute(f"insert into work_parameter_values(work_id, parameter_id, value) values({work_id}, {record[1][0]}, {second_parameter_value})")
        connection.commit()
    params = {
        "work_id": work_id,
        "fuel": fuel,
        "second_parameter_value": second_parameter_value
    }
    return params, 201

@app.route('/agro_tracker/points/insert', methods=['POST'])
def insert_point():
    # добавление в базу данных точки маршрутка сельскохозяйственной техники
    if not request.json or not 'lat' in request.json or not 'lon' in request.json or not 'work_id' in request.json or not 'point_time' in request.json:
        abort(400)
    lat=request.json['lat']
    lon=request.json['lon']
    work_id=request.json['work_id']
    point_time=request.json['point_time']
    point = {
        "work_id": work_id,
        "lat": lat,
        "lon": lon,
        "point_time": point_time
    }
    cursor.execute(
        f"insert into points(latitude,longitude,work_id,point_time) values({lat},{lon},{work_id},'{point_time}');")
    connection.commit()
    return point, 201



@app.route('/agro_tracker/works/operator/', methods=['GET'])
def select_operator_works():
    # проверка наличия у оператора запущенных (незавершенных) полевых работ
    creator_id=request.args.get('creator_id')
    cursor.execute(f"select id, name, start_time, work_type_id from works where creator_id='{creator_id}' and end_time is null;")
    record = cursor.fetchall()
    if (cursor.rowcount >= 1 and len(record)>=1):
        work = {
            "work_id": record[0][0],
            "name": record[0][1],
            "start_time": str(record[0][2]),
            "work_type_id": record[0][3],
            "comment": "ContinueWorkFragment"
        }
        return work, 200 #возвращается одна из списка незавершенных работ
    else:
        # если не найдено незавершенных работ, проверить, есть ли работы, у которых не отправлены параметры по окончании выполнения работы
        cursor.execute(
            f"select id, name, start_time, work_type_id from works where creator_id='{creator_id}' and not exists (select * from work_parameter_values where work_parameter_values.work_id=works.id);")
        record0 = cursor.fetchall()
        if (cursor.rowcount >= 1 and len(record0)>=1):
            work = {
                "work_id": record0[0][0],
                "name": record0[0][1],
                "start_time": str(record0[0][2]),
                "work_type_id": record0[0][3],
                "comment": "EndWorkFormFragment"
            }
            return work, 200#возвращается одна из списка работ без отправленных по окончании выполнения параметров
        else:
            work = {
                "work_id": 0,
                "name": "name",
                "start_time":"start_time",
                "comment": "StartWorkFormFragment"
            }
            #если нет незавершенных работ, дать доступ к созданию новой полевой работы
            return work, 200

if __name__ == '__main__':
    app.run(host="192.168.0.105",debug=True)


