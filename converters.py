"""
파일 변환 관련 함수
- DM 로그 → PCAP 변환 (scat)
- PCAP → JSON 변환 (tshark)
"""
import os
import json
import subprocess
import tempfile
import shutil
from utils import parse_json_with_duplicate_keys


def check_dependencies():
    """scat과 tshark 설치 확인"""
    try:
        subprocess.run(['scat', '--version'], capture_output=True, timeout=5)
    except FileNotFoundError:
        raise Exception("scat이 설치되지 않았습니다.")
    
    try:
        subprocess.run(['tshark', '--version'], capture_output=True, timeout=5)
    except FileNotFoundError:
        raise Exception("tshark가 설치되지 않았습니다.")


def convert_to_pcap(input_path, pcap_path):
    """scat으로 QMDL/HDF를 PCAP으로 변환"""
    # 파일 확장자로 타입 판단
    file_ext = input_path.lower().split('.')[-1]
    
    if file_ext in ['qmdl', 'dlf', 'sdm', 'lpd', 'hdf', 'hdf5']:
        # Dump 파일 - Qualcomm
        # scat -t qc -d test.qmdl -F test.pcap -L rrc,nas
        cmd = ['scat', '-t', 'qc', '-d', input_path, '-F', pcap_path, '-L', 'rrc,nas']
    else:
        raise Exception(f"지원하지 않는 파일 형식: {file_ext}. QMDL, HDF, SDM, LPD 파일을 사용해주세요.")
    
    # 파일 크기 확인
    file_size = os.path.getsize(input_path)
    if file_size > 100 * 1024 * 1024:  # 100MB 이상
        print(f"경고: 파일 크기가 {file_size / (1024*1024):.1f}MB입니다. 변환에 시간이 걸릴 수 있습니다.")
    
    # 큰 파일을 위해 타임아웃 없이 실행
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=None)
    
    # stderr와 stdout 모두 확인
    if result.returncode != 0:
        error_msg = result.stderr if result.stderr else result.stdout
        raise Exception(f"scat 변환 실패 (return code: {result.returncode}): {error_msg}")
    
    # PCAP 파일이 생성되었는지 확인
    if not os.path.exists(pcap_path):
        error_msg = result.stderr if result.stderr else result.stdout
        raise Exception(f"scat이 PCAP 파일을 생성하지 못했습니다.\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}")
    
    if os.path.getsize(pcap_path) == 0:
        raise Exception("scat이 빈 PCAP 파일을 생성했습니다. 입력 파일에 RRC/NAS 메시지가 없거나 손상되었을 수 있습니다.")
    
    print(f"scat 변환 완료: {os.path.getsize(pcap_path) / 1024:.1f}KB PCAP 생성")
    return True


def convert_pcap_to_json(pcap_path, json_path):
    """tshark로 PCAP을 JSON으로 변환"""
    
    # PCAP 파일 크기 확인
    pcap_size = os.path.getsize(pcap_path)
    if pcap_size > 50 * 1024 * 1024:  # 50MB 이상
        print(f"경고: PCAP 파일 크기가 {pcap_size / (1024*1024):.1f}MB입니다. JSON 변환에 시간이 걸릴 수 있습니다.")
    
    # Lua 플러그인 경로
    lua_plugin_path = os.path.join(os.path.dirname(__file__), 'wireshark', 'scat.lua')
    
    # tshark 명령어 구성
    cmd = ['tshark', '-r', pcap_path, '-T', 'json']
    
    # 환경 변수 복사
    env = os.environ.copy()
    
    # Lua 플러그인이 있으면 임시 디렉토리에 복사하고 적용
    temp_plugin_dir = None
    if os.path.exists(lua_plugin_path):
        try:
            # 임시 디렉토리 생성
            temp_plugin_dir = tempfile.mkdtemp(prefix='wireshark_plugins_')
            temp_lua_path = os.path.join(temp_plugin_dir, 'scat.lua')
            
            # Lua 파일 복사
            shutil.copy2(lua_plugin_path, temp_lua_path)
            
            # Wireshark 개인 플러그인 디렉토리 환경 변수 설정
            env['WIRESHARK_PLUGIN_DIR'] = temp_plugin_dir
            
            print(f"[INFO] SCAT Lua 플러그인 적용: {temp_lua_path}")
            
            # -X lua_script 옵션 추가
            cmd.extend(['-X', f'lua_script:{temp_lua_path}'])
        except Exception as e:
            print(f"[WARNING] Lua 플러그인 설정 실패: {e}")
            temp_plugin_dir = None
    else:
        print(f"[INFO] 기본 tshark 디코더 사용 (NR RRC 내장 지원)")
    
    try:
        # JSON 파싱 실행
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=None, env=env)
        if result.returncode != 0:
            raise Exception(f"tshark 변환 실패: {result.stderr}")
        
        if not result.stdout.strip():
            raise Exception("tshark가 빈 출력을 반환했습니다.")
        
        if result.stdout.strip().startswith('<!'):
            raise Exception("tshark가 HTML 에러를 반환했습니다.")
        
        # 중복 키를 배열로 변환
        try:
            data = parse_json_with_duplicate_keys(result.stdout)
        except json.JSONDecodeError as e:
            debug_path = json_path.replace('.json', '_error.txt')
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(f"JSON 파싱 에러: {str(e)}\n\n")
                f.write("=== tshark 출력 (처음 2000자) ===\n")
                f.write(result.stdout[:2000])
            raise Exception(f"tshark 출력이 유효한 JSON이 아닙니다: {str(e)}")
        
        # JSON 저장
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 추가: PDML 포맷으로도 파싱하여 enum 문자열 추출
        pdml_path = json_path.replace('.json', '_pdml.xml')
        try:
            print(f"[INFO] PDML 포맷으로 enum 값 추출 중...")
            cmd_pdml = ['tshark', '-r', pcap_path, '-T', 'pdml']
            if temp_plugin_dir:
                cmd_pdml.extend(['-X', f'lua_script:{temp_lua_path}'])
            
            result_pdml = subprocess.run(cmd_pdml, capture_output=True, text=True, timeout=None, env=env)
            if result_pdml.returncode == 0:
                with open(pdml_path, 'w', encoding='utf-8') as f:
                    f.write(result_pdml.stdout)
                print(f"[INFO] PDML 저장 완료: {pdml_path}")
        except Exception as e:
            print(f"[WARNING] PDML 생성 실패 (선택사항): {e}")
        
        # 디버깅 정보 저장
        debug_path = json_path.replace('.json', '_debug.txt')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write("=== 전체 JSON (처음 5000자) ===\n")
            f.write(result.stdout[:5000] + "\n...\n\n")
            
            cmd_protocols = ['tshark', '-r', pcap_path, '-c', '5', '-V']
            result_protocols = subprocess.run(cmd_protocols, capture_output=True, text=True, timeout=30, env=env)
            f.write("=== 상세 프로토콜 정보 (처음 5개 패킷) ===\n")
            f.write(result_protocols.stdout + "\n\n")
            
            cmd_text = ['tshark', '-r', pcap_path, '-c', '20']
            result_text = subprocess.run(cmd_text, capture_output=True, text=True, timeout=30, env=env)
            f.write("=== 텍스트 출력 (처음 20개) ===\n")
            f.write(result_text.stdout)
        
        return True
    
    finally:
        # 임시 디렉토리 정리
        if temp_plugin_dir and os.path.exists(temp_plugin_dir):
            try:
                shutil.rmtree(temp_plugin_dir)
                print(f"[INFO] 임시 플러그인 디렉토리 정리")
            except Exception as e:
                print(f"[WARNING] 임시 디렉토리 정리 실패: {e}")
