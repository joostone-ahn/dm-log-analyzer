import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# 모듈 임포트
from converters import check_dependencies, convert_to_pcap, convert_pcap_to_json
from parsers import parse_call_flow

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PCAP_FOLDER'] = 'pcaps'
app.config['JSON_FOLDER'] = 'jsons'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB

# 필요한 디렉토리 생성
for folder in [app.config['UPLOAD_FOLDER'], app.config['PCAP_FOLDER'], app.config['JSON_FOLDER']]:
    os.makedirs(folder, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        check_dependencies()
    except Exception as e:
        print(f"[ERROR] 의존성 체크 실패: {e}")
        return jsonify({'error': str(e)}), 500
    
    if 'file' not in request.files:
        print("[ERROR] 파일이 요청에 없음")
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    if not file or file.filename == '':
        print("[ERROR] 파일명이 비어있음")
        return jsonify({'error': '파일을 선택하세요'}), 400
    
    filename = secure_filename(file.filename)
    file_ext = filename.lower().split('.')[-1]
    base_name = filename.rsplit('.', 1)[0]
    
    try:
        # PCAP 파일인 경우 scat 변환 건너뛰기
        if file_ext == 'pcap':
            print(f"[INFO] PCAP 파일 감지: {filename}")
            pcap_path = os.path.join(app.config['PCAP_FOLDER'], filename)
            print(f"[INFO] PCAP 파일 저장: {pcap_path}")
            file.save(pcap_path)
        else:
            # QMDL/HDF 파일인 경우 scat 변환 수행
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"[INFO] 파일 저장: {filename} -> {input_path}")
            file.save(input_path)
            
            pcap_path = os.path.join(app.config['PCAP_FOLDER'], base_name + '.pcap')
            print(f"[INFO] PCAP 변환 시작: {input_path} -> {pcap_path}")
            convert_to_pcap(input_path, pcap_path)
        
        # JSON 변환 및 파싱
        json_path = os.path.join(app.config['JSON_FOLDER'], base_name + '.json')
        print(f"[INFO] JSON 변환 시작: {pcap_path} -> {json_path}")
        convert_pcap_to_json(pcap_path, json_path)
        
        print(f"[INFO] Call Flow 파싱 시작: {json_path}")
        flows = parse_call_flow(json_path)
        print(f"[INFO] 파싱 완료: {len(flows)}개 메시지")
        
        return jsonify({'success': True, 'flows': flows})
    except Exception as e:
        print(f"[ERROR] 처리 중 에러: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
