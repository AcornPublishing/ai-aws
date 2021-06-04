# plumber란?
# plumber라는 R 패키지는 기존 R 코드를 REST 엔드포인트로 만들어 준다. 
# 기존의 R 코드에 특별한 주석을 덧붙여 이렇게 한다.


#' 서버가 동작 중인 것을 확인하는 Ping
#' @get /ping
function() {
  return('I am alive and listening')
} 

#' 사용자-도서 행렬을 생성하기 위한 입력을 파싱하고 모형의 예측을 리턴
#' @param req Http request sent
#' @post /invocations
function(req) {
  # 해당 컨테이너에 있는 훈련된 모형의 위치를 명시
  prefix <- '/opt/ml'
  model_path <- paste(prefix, 'model', sep='/')
    
  # 해당 데이터셋에 총 275명의 사용자가 있고 이중 270 명의 사용자 데이터를 훈련에 이용한다. 또한 도서를 추천할 대상 사용자를 지명한다.
  ind <- 272  
  
  # 모형을 로드
  load(paste(model_path, 'rec_model.RData', sep='/'), verbose = TRUE)

  
  # 도서를 추천할 대상 사용자의 인텍스를 읽기
  conn <- textConnection(gsub('\\\\n', '\n', req$postBody))
  data <- read.csv(conn)
  #print("This is data:", data)
  close(conn)
    
  # 평점 행렬 준비
  ratings_mat = dcast(data, user_ind~book_ind, value.var = "rating", fun.aggregate=mean)

  # user_ind 열 제거
  ratings_mat = as.matrix(ratings_mat[,-1])

  # 행렬 크기 축소(조밀 행렬 생성)
  ratings_mat = as(ratings_mat, "realRatingMatrix")  
    
  # 한 사용자 또는 사용자 목록에 대한 상위 5개 추천 대상 도서 가져오기
  pred_bkratings <- predict(rec_model, ratings_mat[ind], n=5)
  
  # 예측 평점 리턴
  return(as(pred_bkratings, "list"))}