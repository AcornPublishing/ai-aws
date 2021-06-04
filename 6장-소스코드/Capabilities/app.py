# -*- coding: utf-8 -*-

from chalice import Chalice
from chalicelib import intelligent_assistant_service

import json

#####
# 챌리스 애플리케이션 설정
#####
app = Chalice(app_name='Capabilities')
app.debug = True

#####
# 서비스 초기화
#####
assistant_name = 'ContactAssistant'
assistant_service = intelligent_assistant_service.IntelligentAssistantService(assistant_name)


#####
# RESTful 엔드포인트
#####
@app.route('/contact-assistant/user-id/{user_id}/send-text', methods = ['POST'], cors = True)
def send_user_text(user_id):
    request_data = json.loads(app.current_request.raw_body)

    message = assistant_service.send_user_text(user_id, request_data['text'])

    return message
