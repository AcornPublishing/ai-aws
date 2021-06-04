# -*- coding: utf-8 -*-

## 유틸리티 함수
import numpy as np
import csv, jsonlines
import os
import io
import string
import sys
import pandas as pd

# object2vec에 맞는 형식 데이터 출력
def load_df_data(df, verbose=True):
    """
    입력: users - books - ratings - etc 형태의 데이터 프레임
    출력: 각 행이 {'in0':userID, 'in1':bookID, 'label':rating}인 리스트
    """
    to_data_list = list()
    users = list()
    items = list()
    ratings = list()
    
    userIDMap = list()
    
    unique_users = set()
    unique_items = set()
    
    for idx, row in df.iterrows():
        to_data_list.append({'in0':[int(row['user_ind'])], 'in1':[int(row['book_ind'])], 'label':float(row['rating'])})
        users.append(row['user_ind'])
        items.append(row['book_ind'])
        ratings.append(float(row['rating']))
        unique_users.add(row['user_ind'])
        unique_items.add(row['book_ind'])
   
    if verbose:
        print("There are {} ratings".format(len(ratings)))
        print("The ratings have mean: {}, median: {}, and variance: {}".format(
                                            round(np.mean(ratings), 2), 
                                            round(np.median(ratings), 2), 
                                            round(np.var(ratings), 2)))
        print("There are {} unique users and {} unique books".format(len(unique_users), len(unique_items)))
        
    return to_data_list, ratings

# JSON 행을 파일로 저장
def write_data_list_to_jsonl(data_list, to_fname):
    """
    입력: 각 행이 {'in0':userID, 'in1':bookID, 'label':rating} 형태의 딕셔너리인 리스트
    출력: 해당 리스트를 JSON 행 파일로 저장
    """
    with jsonlines.open(to_fname, mode='w') as writer:
        for row in data_list:
            #print(row)
            writer.write({'in0':row['in0'], 'in1':row['in1'], 'label':row['label']})
    print("Created {} jsonline file".format(to_fname))
    
 
# object2vec에 맞는 형식으로 테스트 데이터를 변형
def data_list_to_inference_format(data_list, binarize=True, label_thres=3):
    """
    입력: 데이터 리스트
    출력: 세이지메이커가 추론하기 위한 테스트 데이터와 레이블
    """
    data_ = [({"in0":row['in0'], 'in1':row['in1']}, row['label']) for row in data_list]
    print("data_ :", data_)
    data, label = zip(*data_)
    print("data :", data)
    print("label :", label)
    
    infer_data = {"instances":data}
    
    print("infer_data : ", infer_data)
    
    if binarize:
        label = get_binarized_label(list(label), label_thres)
    return infer_data, label

# 모형 평가를 위한 MSE의 계산
def get_mse_loss(res, labels):
    if type(res) is dict:
        res = res['predictions']
    assert len(res)==len(labels), 'result and label length mismatch!'
    loss = 0
    for row, label in zip(res, labels):
        if type(row)is dict:
            loss += (row['scores'][0]-label)**2
        else:
            loss += (row-label)**2
    return round(loss/float(len(labels)), 2)

# 사용자 및 도서 딕셔너리 생성
# 사용자 딕셔너리 생성: users[userID] : {bookID, rating}
# 도서 딕셔너리 생성: books[bookID] : {userID1, userID2..}
def jsnl_to_augmented_data_dict(jsnlRatings):
    """
    입력: users - books - ratings - etc 형태의 JSON 행
    출력:
      사용자 딕셔너리 : 키가 userID이고 각 키는 해당 사용자의 도서 평점 리스트에 대응
      도서 딕셔너리: 키가 book ID이고 각 키는 다른 사용자의 해당 도서에 대한 평점 리스트에 대응
    """
    to_users_dict = dict() 
    to_books_dict = dict()
    
    for row in jsnlRatings:
        if row['in0'][0] not in to_users_dict:
            to_users_dict[row['in0'][0]] = [(row['in1'][0], row['label'])]
        else:
            to_users_dict[row['in0'][0]].append((row['in1'][0], row['label']))
        if row['in1'][0] not in to_books_dict:
            to_books_dict[row['in1'][0]] = list(row['in0'])
        else:
            to_books_dict[row['in1'][0]].append(row['in0'])
   
    return to_users_dict, to_books_dict