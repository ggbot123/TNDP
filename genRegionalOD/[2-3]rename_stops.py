# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407111750

import pathlib
import warnings
import pandas as pd
import re
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def parse_boarding_stop_info(stop_name):
    if '的前' in stop_name:
        base_stop, offset = stop_name.split('的前')
        direction = '前'
    elif '的后' in stop_name:
        base_stop, offset = stop_name.split('的后')
        direction = '后'
    else:
        return None, None, None
    offset = int(offset.replace('站', ''))
    return base_stop, direction, offset


def rename_stops(stop_name, line, direction):
    # 处理IC刷卡系统和数知梦平台录入的站名不统一问题
    ic_system_names = ['东区客运中心', '明日星城', '市高级技校', '碱吕', '安康花园', '奥林水岸', '北海花园北门', '北郝新苑', '北齐',
                       '滨海嘉苑', '滨州兵乓球馆', '滨州纺织市场', '滨州市实验中学', '滨州市特殊教育学校', '滨州学院', '上海世家',
                       '渤海先进技术研究院', '渤海先进技术研究院南门+', '德坤华府', '东城交警大队', '候北', '锦城大厦', '京学幼儿园',
                       '剧场街市场', '剧场街市场北门', '梁才工商所', '龙禧御园', '鲁北技师学院', '民安鹊华苑',
                       '南阳南站', '彭李街道安民社区', '青藤苑酒店', '区第二实验小学', '三角洲大数据基地', '市农业农村局',
                       '市社会养老服务中心', '书香福邸', '树人中学', '天虹花园', '天虹花苑东门', '湾刘小区', '梧桐社区', '西皂户',
                       '小开河管理所', '新怡小学', '馨露馨苑', '馨露馨苑南门', '馨露园', '馨苑小区', '亚光宿舍', '韵和嘉苑',
                       '张八棍居委会', '钟楼孙', '堤上胡', '窑洼村', '杜店办事处', '滨南社区', '华祥苑', '福佑家园', '人民医院东门',
                       '凤祥名都', '北郝嘉苑', '雷家村', '永莘路', '西李扎根', '瓦张村', '碧林花园', '博翱高级中学', '梁才农村信用社',
                       '东岳佳苑南门', '高新区幼儿园', '高西村', '市海洋发展和渔业局', '高新区服务中心', '高东村', '店东家',
                       '里则办事处', '坡刘', '墨家集', '天一光电', '东方地毯', '银座中海店', '市公路发展中心', '罗家堡', '小街',
                       '魏福吴', '西牛集', '南杨南站', '西魏', '华医中医院', '市委党校', '凤凰家园', '纺苑三区', '大张家村',
                       '张赵村', '陈哑巴']
    stop_names = ['东客运站', '明日星城小区', '高级技校', '碱吕家', '安康家园', '滨州乒乓球馆', '北海花园', '北郝居委会', '北齐家',
                  '滨海嘉园', '滨州乒乓球馆', '纺织市场', '黄河三角洲交易中心', '滨州特殊教育学校', '学院北门', '生龙欢乐世界',
                  '渤海先进技术研究院南门', '中海清瑞', '张八棍居委会', '交警大队', '侯北', '锦程大厦', '滨州乒乓球馆',
                  '剧场街农贸市场', '剧场街市场农贸市场北门', '梁才市场监督管理所', '龙禧贵苑', '市政务服务中心', '喜鹊湖公园',
                  '南杨南站', '彭集街道安民社区', '青藤苑酒店东门', '五四转盘', '胜利油建七分公司', '市农村农业局',
                  '社会养老服务中心', '书香府邸', '树仁中学', '天虹花苑', '天虹花园东门', '怡华苑', '建设银行', '坡刘村',
                  '小开河管理处', '清怡小学东校区', '馨露鑫苑', '馨露鑫苑南门', '磬露园', '鑫苑小区', '亚光花园', '市政务服务中心',
                  '德坤华府', '钟楼村', '提上胡', '尧洼村', '开发区中心医院', '滨南小区', '华翔苑', '福临家园', '人民医院南门',
                  '凤翔名都', '北郝新苑', '雷家', '秦董姜', '西里扎根', '瓦屋张', '碧林花园南门', '博鳌高级中学', '梁才农商银行',
                  '东岳家园南门', '高新区教育幼儿园', '高西家', '市海洋发展渔业局', '高新区政务服务中心', '高东家', '店东李',
                  '汽车总站', '坡刘村', '安兴花园', '小刘家', '汽车总站', '西城华府', '市公路服务中心', '滨医西门', '牛王',
                  '城建集团', '城建集团', '城建集团', '城建集团', '滨医西门', '至尊门第南门', '蒲湖风景区', '纺苑二区', '南董家',
                  '张赵家', '陈亚吧']
    match = re.match(r'(.*?)(的前\d+站|的后\d+站)?$', stop_name)
    if match:
        base_stop_name = match.group(1)
        suffix = match.group(2)

        try:
            index = ic_system_names.index(base_stop_name)
            new_base_stop_name = stop_names[index]
            if suffix:
                base_stop, dir, offset = parse_boarding_stop_info(new_base_stop_name + suffix)
                stop_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
                stop_file = f'{line}_{direction}.csv'
                stops_data = pd.read_csv(stop_data_folder / stop_file)
                stop_list = stops_data['站点名称'].tolist()
                if base_stop in stop_list:
                    base_index = stop_list.index(base_stop)
                    if dir == '前':
                        new_index = max(0, base_index - offset)
                    else:
                        new_index = min(len(stop_list) - 1, base_index + offset)
                    new_stop_name = stop_list[new_index]
                    return new_stop_name
                else:
                    return stop_name
            return new_base_stop_name
        except ValueError:
            return stop_name
    return stop_name


def find_stop_file(stop_folder_path, line, direction):
    stop_folder_path, line, direction = str(stop_folder_path), str(int(line)), str(direction)
    if direction == '上行':
        dir = '_up'
    elif direction == '下行':
        dir = '_down'
    else:
        dir = ''
    stop_file_name = f"{stop_folder_path}/{line}{dir}.csv"
    return stop_file_name


def match_normalized_stop_name(stop_file_name, stop_name):
    df_stops = pd.read_csv(stop_file_name)
    condition = df_stops['站点名称'] == stop_name
    normalized_stop_name = df_stops.loc[condition, '站点编号'].values
    return normalized_stop_name[0] if len(normalized_stop_name) > 0 else None


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/normalized_boarding")
    file_name = "2024-06-30.csv"
    file_to_open = data_folder / file_name
    df = pd.read_csv(file_to_open)
    df['刷卡时间'] = pd.to_datetime(df['刷卡时间'])
    df = df.sort_values(by=['刷卡时间'])
    stop_folder_path = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")

    update_df = df[df['格式化上车站点编号'].isnull()].copy()
    for idx, row in update_df.iterrows():
        line = str(int(row['线路']))
        direction = 'up' if row['上下行'] == '上行' else 'down'
        stop_name = row['上车站点名称']
        new_stop_name = rename_stops(stop_name, line, direction)
        row['上车站点名称'] = new_stop_name
        df.at[row.name, '上车站点名称'] = new_stop_name
        stop_path = find_stop_file(stop_folder_path, row['线路'], row['上下行'])
        new_normalized_stop_name = match_normalized_stop_name(stop_path, row['上车站点名称'])
        df.at[row.name, '格式化上车站点编号'] = new_normalized_stop_name

    save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/"
                               "pythonProject/IC_Smartcard/normalized_renamed_boarding")
    # df = df.dropna()

    df.to_csv(save_folder/file_name, index=False, encoding='utf-8')
    print(len(df[df['格式化上车站点编号'].isnull()].copy()))
    print(df[df['格式化上车站点编号'].isnull()].copy())
