import random
from scoop import futures
from deap import base
from deap import creator
from deap import tools
from deap import cma

import numpy as np
import csv


# 以下設定値
# 初期集団数
initial_population = 300
# 世代数(繰り返し回数)
loop_time = 500
# 想定人数とアサイン人数の差
people_count_sub_sum_weights = -100.0
# 応募していない時間帯へのアサイン数
not_applicated_count_weights = -50.0
# アサイン数が応募数の半分以下の従業員数
few_work_user_weights = -1.0
# 管理者が１人もいないコマ数
no_manager_box_weights = -1.0
# 同一日出勤を防ぐ
three_box_per_day_weights = -150.0
# 担当ラインがローテーション中に被らないようにする
another_line_weights = -10.0

# 従業員を表すクラス
class Employee(object):
  def __init__(self, no, name, age, manager, wills):
    self.no = no
    self.name = name
    self.age = age
    self.manager = manager

    # willは曜日_時間帯。1は朝、2は昼、3は夜。
    # 例）mon_1は月曜日の朝
    self.wills = wills

  def is_applicated(self, box_name):
    return (box_name in self.wills)

# シフトを表すクラス
# 内部的には 3(朝昼晩) * 7日 * 10人 = 210次元のタプルで構成される
class Shift(object):
  # コマの定義
  SHIFT_BOXES = [
    'mon_1_CB1_Fr','mon_1_CB1_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB2_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu'    
    #,'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    #'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'
    ]
    
  # 各コマの想定人数
  NEED_PEOPLE = [
    1,1,1,1,1,
    1,1,1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,1,1
    #,0,0,0,0,0,
    #0,0,0,0,0,0,0
    ]

  def __init__(self, list):
    if list == None:
      self.make_sample()
    else:
      self.list = list
    self.employees = []

  # ランダムなデータを生成
  def make_sample(self):
    sample_list = []
    for num in range(len(self.SHIFT_BOXES)*len(employees)):
      sample_list.append(random.randint(0, 1))
    self.list = tuple(sample_list)

  # タプルを1ユーザ単位に分割
  def slice(self):
    sliced = []
    start = 0
    for num in range(len(employees)):
      sliced.append(self.list[start:(start + len(self.SHIFT_BOXES))])
      start = start + len(self.SHIFT_BOXES)
    return tuple(sliced)

  # ユーザ別にアサインコマ名を出力する
  def print_inspect(self):
    user_no = 0
    for line in self.slice():
      print ("ユーザ%d" % user_no)
      print (line)
      user_no = user_no + 1
      index = 0
      for e in line:
        if e == 1:
          print (self.SHIFT_BOXES[index])
        index = index + 1

  # CSV形式でアサイン結果の出力をする
  def print_csv(self):
    for line in self.slice():
      print (','.join(map(str, line)))
    #with open('schedule.csv','w',newline="")as f:
    #    writer=csv.writer(f)
    #    writer.writerows(self.slice())

  # TSV形式でアサイン結果の出力をする
  def print_tsv(self):
    for line in self.slice():
      print ("\t".join(map(str, line)))
  
  # 勤務表アウトプット
  def print_output(self):
      index = 0
      #print(self.SHIFT_BOXES)
      for line in self.slice():
          print("従業員%d:\t" % (index) , end="")
          #print(employees[index,1]+":\t",end="") # うまくうごかない。employeesがおかしい。
          for i in range(len(line)):
            if line[i]==1:
              print(self.SHIFT_BOXES[i]+"\t",end="")
          print("")
          index += 1
      with open('schedule.csv','a',newline="")as f:
        writer=csv.writer(f)
        writer.writerow("初期集団：%d\n世代数：%d\n配属人数違い：%f\n力量：%f\n希望配属：%f\n管理者：%f\n同一日出勤：%f\n多能工化：%f" % (initial_population,loop_time,people_count_sub_sum_weights,not_applicated_count_weights,few_work_user_weights,no_manager_box_weights,three_box_per_day_weights,another_line_weights))
        #writer.writerows("目的関数：%s" % best_ind.fitness.values )
        writer.writerows(self.slice())
        writer.writerow("")


  # ユーザ番号を指定してコマ名を取得する
  def get_boxes_by_user(self, user_no):
    line = self.slice()[user_no]
    return self.line_to_box(line)

  # 1ユーザ分のタプルからコマ名を取得する
  def line_to_box(self, line):
    result = []
    index = 0
    for e in line:
      if e == 1:
        result.append(self.SHIFT_BOXES[index])
      index = index + 1
    return result    

  # コマ番号を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_index(self, box_index):
    user_nos = []
    index = 0
    for line in self.slice():
      if line[box_index] == 1:
        user_nos.append(index)
      index += 1
    return user_nos

  # コマ名を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_name(self, box_name):
    box_index = self.SHIFT_BOXES.index(box_name)
    return self.get_user_nos_by_box_index(box_index)

  # 想定人数と実際の人数の差分を取得する
  def abs_people_between_need_and_actual(self):
    result = []
    index = 0
    for need in self.NEED_PEOPLE:
      actual = len(self.get_user_nos_by_box_index(index))
      result.append(abs(need - actual))
      index += 1
    return result

  # 応募していないコマにアサインされている件数を取得する
  def not_applicated_assign(self):
    count = 0
    for box_name in self.SHIFT_BOXES:
      user_nos = self.get_user_nos_by_box_name(box_name)
      for user_no in user_nos:
        e = self.employees[user_no]
        if not e.is_applicated(box_name):
          count += 1
    return count

  # アサインが応募コマ数の50%に満たないユーザを取得
  def few_work_user(self):
    result = []
    for user_no in range(len(employees)):
      e = self.employees[user_no]
      ratio = float(len(self.get_boxes_by_user(user_no))) / float(len(e.wills))
      if ratio < 0.5:
        result.append(e)
    return result

  # 管理者が1人もいないコマ
  def no_manager_box(self):
    result = []
    for box_name in self.SHIFT_BOXES:
      manager_included = False
      user_nos = self.get_user_nos_by_box_name(box_name)
      for user_no in user_nos:
        e = self.employees[user_no]
        if e.manager:
          manager_included = True
      if not manager_included:
        result.append(box_name)
    return result

  # 同一日出勤を防ぐ
  def three_box_per_day(self):
    result = []
    for user_no in range(12):
    #for user_no in range(len(employees)):
      boxes = self.get_boxes_by_user(user_no)
      wdays = []
      for box in boxes:
        wdays.append(box.split('_')[0])
      wday_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
      for wday_name in wday_names:
        if wdays.count(wday_name) > 1:
          result.append(wday_name)
    return result

  # できるだけラインが分かれるように
  def another_line(self):
    result2 = []
    for user_no in range(12):
    #for user_no in range(len(employees)):
      boxes2 = self.get_boxes_by_user(user_no)
      wdays2 = []
      for box2 in boxes2:
        wdays2.append(box2.split('_')[2])
      wday_names2 = ['CB1', 'CB2', 'GC1', 'GC2', 'GC3']
      for wday_name2 in wday_names2:
        if wdays2.count(wday_name2) >1:
          result2.append(wday_name2)
    return result2
  
  def another_line3(self):
    result3 = []
    for user_no in range(12):
      boxes3 = self.get_boxes_by user(user_no)
      wdays3 = []
      for box3 in boxes3:
        wday3.append(box3.split('_')[])


# 従業員定義
"""
e0 = Employee(0, "CBFr社員1", 20, True,[    #完全多能工化の場合
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e1 = Employee(1, "CBFr社員2", 21, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e2 = Employee(2, "CB製丸社員1", 18, True,[
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e3 = Employee(3, "CB製丸社員2", 35, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e4 = Employee(4, "CB包装社員1", 19, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e5 = Employee(5, "CB包装社員2", 43, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e6 = Employee(6, "GCFr社員1", 25, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e7 = Employee(7, "GCFr社員2", 22, False, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e8 = Employee(8, "GCFr社員3", 18, True,[
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e9 = Employee(9, "GC充填社員1", 30, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e10 = Employee(10, "GC充填社員2", 30, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
e11 = Employee(11, "GC充填社員3", 30, True, [
    'mon_1_CB1_Fr','mon_1_CB2_sei','mon_1_CB1_hou','mon_1_GC1_Fr','mon_1_GC1_juu',
    'mon_2_CB1_Fr','mon_2_CB2_sei','mon_2_CB2_hou','mon_2_GC2_Fr','mon_2_GC2_juu','mon_3_GC3_Fr','mon_3_GC3_juu', 
    'tue_1_CB1_Fr','tue_1_CB1_sei','tue_1_CB1_hou','tue_1_GC1_Fr','tue_1_GC1_juu',
    'tue_2_CB2_Fr','tue_2_CB2_sei','tue_2_CB2_hou','tue_2_GC2_Fr','tue_2_GC2_juu','tue_3_GC3_Fr','tue_3_GC3_juu', 
    'wed_1_CB1_Fr','wed_1_CB1_sei','wed_1_CB1_hou','wed_1_GC1_Fr','wed_1_GC1_juu',
    'wed_2_CB2_Fr','wed_2_CB2_sei','wed_2_CB2_hou','wed_2_GC2_Fr','wed_2_GC2_juu','wed_3_GC3_Fr','wed_3_GC3_juu', 
    'thu_1_CB1_Fr','thu_1_CB1_sei','thu_1_CB1_hou','thu_1_GC1_Fr','thu_1_GC1_juu',
    'thu_2_CB2_Fr','thu_2_CB2_sei','thu_2_CB2_hou','thu_2_GC2_Fr','thu_2_GC2_juu','thu_3_GC3_Fr','thu_3_GC3_juu', 
    'fri_1_CB1_Fr','fri_1_CB1_sei','fri_1_CB1_hou','fri_1_GC1_Fr','fri_1_GC1_juu',
    'fri_2_CB2_Fr','fri_2_CB2_sei','fri_2_CB2_hou','fri_2_GC2_Fr','fri_2_GC2_juu','fri_3_GC3_Fr','fri_3_GC3_juu', 
    'sat_1_CB1_Fr','sat_1_CB1_sei','sat_1_CB1_hou','sat_1_GC1_Fr','sat_1_GC1_juu',
    'sat_2_CB2_Fr','sat_2_CB2_sei','sat_2_CB2_hou','sat_2_GC2_Fr','sat_2_GC2_juu','sat_3_GC3_Fr','sat_3_GC3_juu'])
"""
e0 = Employee(0, "CBFr社員1", 20, True,[    #近い部署優先の場合
    'mon_1_CB1_Fr','mon_1_GC1_Fr',
    'mon_2_CB1_Fr','mon_2_GC2_Fr','mon_3_GC3_Fr',
    'tue_1_CB1_Fr','tue_1_GC1_Fr',
    'tue_2_CB2_Fr','tue_2_GC2_Fr','tue_3_GC3_Fr',
    'wed_1_CB1_Fr','wed_1_GC1_Fr',
    'wed_2_CB2_Fr','wed_2_GC2_Fr','thu_3_GC3_Fr', 
    'thu_1_CB1_Fr','thu_1_GC1_Fr',
    'thu_2_CB2_Fr','thu_2_GC2_Fr','thu_3_GC3_Fr', 
    'fri_1_CB1_Fr','fri_1_GC1_Fr',
    'fri_2_CB2_Fr','fri_2_GC2_Fr','fri_3_GC3_Fr', 
    'sat_1_CB1_Fr','sat_1_GC1_Fr',
    'sat_2_CB2_Fr','sat_2_GC2_Fr','sat_3_GC3_Fr'])
e1 = Employee(1, "CBFr社員2", 21, True, [    #近い部署優先の場合
    'mon_1_CB1_Fr','mon_1_GC1_Fr',
    'mon_2_CB1_Fr','mon_2_GC2_Fr','mon_3_GC3_Fr',
    'tue_1_CB1_Fr','tue_1_GC1_Fr',
    'tue_2_CB2_Fr','tue_2_GC2_Fr','tue_3_GC3_Fr',
    'wed_1_CB1_Fr','wed_1_GC1_Fr',
    'wed_2_CB2_Fr','wed_2_GC2_Fr','thu_3_GC3_Fr', 
    'thu_1_CB1_Fr','thu_1_GC1_Fr',
    'thu_2_CB2_Fr','thu_2_GC2_Fr','thu_3_GC3_Fr', 
    'fri_1_CB1_Fr','fri_1_GC1_Fr',
    'fri_2_CB2_Fr','fri_2_GC2_Fr','fri_3_GC3_Fr', 
    'sat_1_CB1_Fr','sat_1_GC1_Fr',
    'sat_2_CB2_Fr','sat_2_GC2_Fr','sat_3_GC3_Fr'])
e2 = Employee(2, "CB製丸社員1", 18, True,[
    'mon_1_CB2_sei','mon_1_GC1_juu',
    'mon_2_CB2_sei','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_sei','tue_1_GC1_juu',
    'tue_2_CB2_sei','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_sei','wed_1_GC1_juu',
    'wed_2_CB2_sei','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_sei','thu_1_GC1_juu',
    'thu_2_CB2_sei','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_sei','fri_1_GC1_juu',
    'fri_2_CB2_sei','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_sei','sat_1_GC1_juu',
    'sat_2_CB2_sei','sat_2_GC2_juu','sat_3_GC3_juu'])
e3 = Employee(3, "CB製丸社員2", 35, True, [
    'mon_1_CB2_sei','mon_1_GC1_juu',
    'mon_2_CB2_sei','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_sei','tue_1_GC1_juu',
    'tue_2_CB2_sei','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_sei','wed_1_GC1_juu',
    'wed_2_CB2_sei','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_sei','thu_1_GC1_juu',
    'thu_2_CB2_sei','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_sei','fri_1_GC1_juu',
    'fri_2_CB2_sei','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_sei','sat_1_GC1_juu',
    'sat_2_CB2_sei','sat_2_GC2_juu','sat_3_GC3_juu'])
e4 = Employee(4, "CB包装社員1", 19, True, [
    'mon_1_CB1_hou','mon_1_GC1_juu',
    'mon_2_CB2_hou','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_hou','tue_1_GC1_juu',
    'tue_2_CB2_hou','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_hou','wed_1_GC1_juu',
    'wed_2_CB2_hou','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_hou','thu_1_GC1_juu',
    'thu_2_CB2_hou','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_hou','fri_1_GC1_juu',
    'fri_2_CB2_hou','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_hou','sat_1_GC1_juu',
    'sat_2_CB2_hou','sat_2_GC2_juu','sat_3_GC3_juu'])
e5 = Employee(5, "CB包装社員2", 43, True, [
    'mon_1_CB1_hou','mon_1_GC1_juu',
    'mon_2_CB2_hou','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_hou','tue_1_GC1_juu',
    'tue_2_CB2_hou','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_hou','wed_1_GC1_juu',
    'wed_2_CB2_hou','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_hou','thu_1_GC1_juu',
    'thu_2_CB2_hou','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_hou','fri_1_GC1_juu',
    'fri_2_CB2_hou','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_hou','sat_1_GC1_juu',
    'sat_2_CB2_hou','sat_2_GC2_juu','sat_3_GC3_juu'])
e6 = Employee(6, "GCFr社員1", 25, True, [
    'mon_1_CB1_Fr','mon_1_GC1_Fr',
    'mon_2_CB1_Fr','mon_2_GC2_Fr','mon_3_GC3_Fr',
    'tue_1_CB1_Fr','tue_1_GC1_Fr',
    'tue_2_CB2_Fr','tue_2_GC2_Fr','tue_3_GC3_Fr',
    'wed_1_CB1_Fr','wed_1_GC1_Fr',
    'wed_2_CB2_Fr','wed_2_GC2_Fr','thu_3_GC3_Fr', 
    'thu_1_CB1_Fr','thu_1_GC1_Fr',
    'thu_2_CB2_Fr','thu_2_GC2_Fr','thu_3_GC3_Fr', 
    'fri_1_CB1_Fr','fri_1_GC1_Fr',
    'fri_2_CB2_Fr','fri_2_GC2_Fr','fri_3_GC3_Fr', 
    'sat_1_CB1_Fr','sat_1_GC1_Fr',
    'sat_2_CB2_Fr','sat_2_GC2_Fr','sat_3_GC3_Fr'])
e7 = Employee(7, "GCFr社員2", 22, False, [
    'mon_1_CB1_Fr','mon_1_GC1_Fr',
    'mon_2_CB1_Fr','mon_2_GC2_Fr','mon_3_GC3_Fr',
    'tue_1_CB1_Fr','tue_1_GC1_Fr',
    'tue_2_CB2_Fr','tue_2_GC2_Fr','tue_3_GC3_Fr',
    'wed_1_CB1_Fr','wed_1_GC1_Fr',
    'wed_2_CB2_Fr','wed_2_GC2_Fr','thu_3_GC3_Fr', 
    'thu_1_CB1_Fr','thu_1_GC1_Fr',
    'thu_2_CB2_Fr','thu_2_GC2_Fr','thu_3_GC3_Fr', 
    'fri_1_CB1_Fr','fri_1_GC1_Fr',
    'fri_2_CB2_Fr','fri_2_GC2_Fr','fri_3_GC3_Fr', 
    'sat_1_CB1_Fr','sat_1_GC1_Fr',
    'sat_2_CB2_Fr','sat_2_GC2_Fr','sat_3_GC3_Fr'])
e8 = Employee(8, "GCFr社員3", 18, True,[
    'mon_1_CB1_Fr','mon_1_GC1_Fr',
    'mon_2_CB1_Fr','mon_2_GC2_Fr','mon_3_GC3_Fr',
    'tue_1_CB1_Fr','tue_1_GC1_Fr',
    'tue_2_CB2_Fr','tue_2_GC2_Fr','tue_3_GC3_Fr',
    'wed_1_CB1_Fr','wed_1_GC1_Fr',
    'wed_2_CB2_Fr','wed_2_GC2_Fr','thu_3_GC3_Fr', 
    'thu_1_CB1_Fr','thu_1_GC1_Fr',
    'thu_2_CB2_Fr','thu_2_GC2_Fr','thu_3_GC3_Fr', 
    'fri_1_CB1_Fr','fri_1_GC1_Fr',
    'fri_2_CB2_Fr','fri_2_GC2_Fr','fri_3_GC3_Fr', 
    'sat_1_CB1_Fr','sat_1_GC1_Fr',
    'sat_2_CB2_Fr','sat_2_GC2_Fr','sat_3_GC3_Fr'])
e9 = Employee(9, "GC充填社員1", 30, True, [
    'mon_1_CB2_sei','mon_1_GC1_juu',
    'mon_2_CB2_sei','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_sei','tue_1_GC1_juu',
    'tue_2_CB2_sei','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_sei','wed_1_GC1_juu',
    'wed_2_CB2_sei','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_sei','thu_1_GC1_juu',
    'thu_2_CB2_sei','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_sei','fri_1_GC1_juu',
    'fri_2_CB2_sei','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_sei','sat_1_GC1_juu',
    'sat_2_CB2_sei','sat_2_GC2_juu','sat_3_GC3_juu'])
e10 = Employee(10, "GC充填社員2", 30, True, [
    'mon_1_CB2_sei','mon_1_GC1_juu',
    'mon_2_CB2_sei','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_sei','tue_1_GC1_juu',
    'tue_2_CB2_sei','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_sei','wed_1_GC1_juu',
    'wed_2_CB2_sei','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_sei','thu_1_GC1_juu',
    'thu_2_CB2_sei','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_sei','fri_1_GC1_juu',
    'fri_2_CB2_sei','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_sei','sat_1_GC1_juu',
    'sat_2_CB2_sei','sat_2_GC2_juu','sat_3_GC3_juu'])
e11 = Employee(11, "GC充填社員3", 30, True, [
    'mon_1_CB2_sei','mon_1_GC1_juu',
    'mon_2_CB2_sei','mon_2_GC2_juu','mon_3_GC3_juu', 
    'tue_1_CB1_sei','tue_1_GC1_juu',
    'tue_2_CB2_sei','tue_2_GC2_juu','tue_3_GC3_juu', 
    'wed_1_CB1_sei','wed_1_GC1_juu',
    'wed_2_CB2_sei','wed_2_GC2_juu','wed_3_GC3_juu', 
    'thu_1_CB1_sei','thu_1_GC1_juu',
    'thu_2_CB2_sei','thu_2_GC2_juu','thu_3_GC3_juu', 
    'fri_1_CB1_sei','fri_1_GC1_juu',
    'fri_2_CB2_sei','fri_2_GC2_juu','fri_3_GC3_juu', 
    'sat_1_CB1_sei','sat_1_GC1_juu',
    'sat_2_CB2_sei','sat_2_GC2_juu','sat_3_GC3_juu'])

employees = [e0, e1, e2, e3, e4, e5, e6, e7, e8, e9,e10,e11]
member = len(employees)

creator.create("FitnessPeopleCount", base.Fitness, weights=(people_count_sub_sum_weights, not_applicated_count_weights,few_work_user_weights,no_manager_box_weights,three_box_per_day_weights,another_line_weights))

creator.create("Individual", list, fitness=creator.FitnessPeopleCount)

toolbox = base.Toolbox()
toolbox.register("map", futures.map)
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, len(Shift.SHIFT_BOXES)*len(employees))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalShift(individual):
  s = Shift(individual)
  s.employees = employees

  # 想定人数とアサイン人数の差
  people_count_sub_sum = sum(s.abs_people_between_need_and_actual()) / (member*len(s.SHIFT_BOXES))
  # 応募していない時間帯へのアサイン数
  not_applicated_count = s.not_applicated_assign() / (member*len(s.SHIFT_BOXES))
  # アサイン数が応募数の半分以下の従業員数
  few_work_user = len(s.few_work_user()) / member
  # 管理者が１人もいないコマ数
  no_manager_box = len(s.no_manager_box()) / len(s.SHIFT_BOXES)
  # 朝・昼・夜の全部にアサインされている
  three_box_per_day = len(s.three_box_per_day()) / (member*len(s.SHIFT_BOXES)/5)
  # 担当ラインがローテーション中に被らないようにする
  another_line = len(s.another_line()) / (member*len(s.SHIFT_BOXES)/5)
  return (people_count_sub_sum, not_applicated_count, few_work_user, no_manager_box, three_box_per_day, another_line)

toolbox.register("evaluate", evalShift)

# 交叉関数を定義(二点交叉)
toolbox.register("mate", tools.cxTwoPoint)
# 変異関数を定義(ビット反転、変異隔離が5%ということ?)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
# 選択関数を定義(トーナメント選択、tournsizeはトーナメントの数？)
toolbox.register("select", tools.selTournament, tournsize=3)

if __name__ == '__main__':
    # 初期集団を生成する
    pop = toolbox.population(n=initial_population)
    CXPB, MUTPB, NGEN = 0.6, 0.5, loop_time # 交差確率、突然変異確率、進化計算のループ回数

    print("進化開始")

    # 初期集団の個体を評価する
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
        # 適合性をセットする
        ind.fitness.values = fit

    #print("  %i の個体を評価" % len(pop))

     # 進化計算開始
    for g in range(NGEN):
        #print("-- %i 世代 --" % g)
        print("\r-- %i / %d 世代 --" % (g+1,loop_time) , end="")

        # 選択
        # 次世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))
        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # 選択した個体群に交差と突然変異を適応する

        # 交叉
        # 偶数番目と奇数番目の個体を取り出して交差
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # 交叉された個体の適合度を削除する
                del child1.fitness.values
                del child2.fitness.values

        # 変異
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 適合度が計算されていない個体を集めて適合度を計算
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        #print("  %i の個体を評価" % len(invalid_ind))

        # 次世代群をoffspringにする
        pop[:] = offspring

        # すべての個体の適合度を配列にする
        index = 1
        for v in ind.fitness.values:
          fits = [v for ind in pop]
          """ #パラメータ状態表示
          length = len(pop)
          mean = sum(fits) / length
          sum2 = sum(x*x for x in fits)
          std = abs(sum2 / length - mean**2)**0.5
          print("* パラメータ%d"% index)
          print("  Min %s" % min(fits))
          print("  Max %s" % max(fits))
          print("  Avg %s" % mean)
          print("  Std %s" % std)
          """
          index += 1


    print("-- 進化終了 --")

    best_ind = tools.selBest(pop, 1)[0]
    #print("最も優れていた個体: %s, %s" % (best_ind, best_ind.fitness.values))
    s = Shift(best_ind)
    #s.print_csv()
    #s.print_tsv()
    print("遺伝的アルゴリズムによる勤務表生成結果：")
    s.print_output()
    

    