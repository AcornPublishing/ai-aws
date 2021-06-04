# 필요한 라이브러리 로드
# 사용자-도서 행렬을 생성하기 위한 라이브러리
library(reshape2)
# 사용자 간의 코사인 유사도를 계산하기 위한 라이브러리
library(recommenderlab)
# 조인, 필터 등의 데이터셋 작업을 수행하기 위한 라이브러리
library(dplyr)

library(plumber)
library(jsonlite)

# 컨테이너에서 훈련 데이터, 모델 및 출력 파일이 저장될 위치를 정의
prefix <- '/opt/ml'
input_path <- paste(prefix, 'input/data', sep='/')
output_path <- paste(prefix, 'output', sep='/')
model_path <- paste(prefix, 'model', sep='/')
param_path <- paste(prefix, 'input/config/hyperparameters.json', sep='/') #similarity method and number of nearest neighbors

# 훈련 데이터를 갖는 채널
channel_name = 'train'
training_path <- paste(input_path, channel_name, sep='/')


# 훈련 함수 정의
train <- function() {
  
  # 초매개변수 일기
  training_params <- read_json(param_path)
  
  # 유사도 메소드
  if (!is.null(training_params$method)) {
    method <- training_params$method }
  else {
    method <- 'Cosine'}
  
  # 최근접 이웃 수 계산
  if (!is.null(training_params$nn)) {
    nn <- as.numeric(training_params$nn) }
  else {
    nn <- 10 }
  
  # 훈련할 사용자 수
  if (!is.null(training_params$n_users)) {
    n_users <- as.numeric(training_params$n_users) }
  else {
    n_users <- 190 }
  
  # 사용자의 도서 평점 데이터 읽기 
  training_files = list.files(path=training_path, full.names=TRUE, pattern='*.csv')
  training_test_data = do.call(rbind, lapply(training_files, read.csv))

  # 도서 평점 행렬 생성
  ratings_mat = dcast(training_test_data, user_ind~book_ind, value.var = "rating", fun.aggregate=mean)

  # user_ind 열 삭제
  ratings_mat = as.matrix(ratings_mat[,-1])

  # 행렬 크기 축소(조밀 행렬 생성)
  ratings_mat = as(ratings_mat, "realRatingMatrix")  
    
  print(paste("Ratings Matrix size: ", nrow(ratings_mat)))  
  
  # 사용자 기반 CF로 모형 훈련 
  # 각 사용자에 대해 (도서 평점에 의해 정의되는) 벡터 거리 기반으로 10명의 유사 사용자를 식별 
  rec_model = Recommender(ratings_mat[1:n_users], method = "UBCF", param=list(method=method, nn=nn))
  
  # 출력 생성
  #attributes(rec_model)$class <- 'cosinesimilarity'
  save(rec_model, file=paste(model_path, 'rec_model.RData', sep='/'))
  print(summary(rec_model))
  write('success', file=paste(output_path, 'success', sep='/'))}


# 평점 매기는 함수의 정의
serve <- function() {
  app <- plumb(paste(prefix, 'plumber.R', sep='/'))
  app$run(host='0.0.0.0', port=8080)}

# 명령행 인자 파싱 - train 또는 serve에 따라 대응 함수 호출
args <- commandArgs()
if (any(grepl('train', args))) {
  train()}
if (any(grepl('serve', args))) {
  serve()}