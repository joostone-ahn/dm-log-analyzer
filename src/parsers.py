"""
프로토콜 파싱 관련 함수
- RRC/NAS 메시지 정보 추출
- 중첩 메시지 추출
- 방향 및 노드 판단
- Call Flow 파싱
"""
import json
from message_types import get_nas_5gs_message_name, get_nas_eps_message_name
from utils import format_timestamp, enhance_pco_fields


def extract_nested_nas_message(rrc_element):
    """RRC 메시지 안에 중첩된 NAS 메시지 추출"""
    if not isinstance(rrc_element, dict):
        return None
    
    # dedicatedNAS_Message_tree 찾기
    nas_tree = None
    if 'nr-rrc.dedicatedNAS_Message_tree' in rrc_element:
        nas_tree = rrc_element['nr-rrc.dedicatedNAS_Message_tree']
    elif 'lte-rrc.dedicatedNAS_Message_tree' in rrc_element:
        nas_tree = rrc_element['lte-rrc.dedicatedNAS_Message_tree']
    
    # 재귀적으로 찾기
    if not nas_tree:
        for value in rrc_element.values():
            if isinstance(value, dict):
                result = extract_nested_nas_message(value)
                if result:
                    return result
        return None
    
    # NAS 메시지 파싱
    if 'nas-5gs' in nas_tree:
        nas_5gs = nas_tree['nas-5gs']
        
        # Plain NAS 메시지
        if 'Plain NAS 5GS Message' in nas_5gs:
            plain_nas = nas_5gs['Plain NAS 5GS Message']
            if 'nas-5gs.mm.message_type' in plain_nas:
                msg_type_hex = plain_nas['nas-5gs.mm.message_type']
                msg_name, _ = get_nas_5gs_message_name(msg_type_hex)
                return msg_name
        
        # Security protected 메시지 (복호화 안된 경우)
        if 'Security protected NAS 5GS message' in nas_5gs:
            # Security protected 안에 Plain이 있는지 확인
            sec_nas = nas_5gs['Security protected NAS 5GS message']
            if isinstance(sec_nas, dict):
                # 다음 레벨에 Plain NAS가 있을 수 있음
                for key in nas_5gs:
                    if 'Plain NAS 5GS Message' in key or key == 'Plain NAS 5GS Message':
                        plain_nas = nas_5gs[key]
                        if isinstance(plain_nas, dict) and 'nas-5gs.mm.message_type' in plain_nas:
                            msg_type_hex = plain_nas['nas-5gs.mm.message_type']
                            msg_name, _ = get_nas_5gs_message_name(msg_type_hex)
                            return msg_name
            return "Security Protected NAS"
    
    if 'nas-eps' in nas_tree:
        nas_eps = nas_tree['nas-eps']
        
        # EMM 메시지
        if 'nas-eps.nas_msg_emm_type' in nas_eps:
            msg_type_hex = nas_eps['nas-eps.nas_msg_emm_type']
            msg_name, _ = get_nas_eps_message_name(msg_type_hex)
            return msg_name
        
        # ESM 메시지
        if 'nas-eps.nas_msg_esm_type' in nas_eps:
            msg_type_hex = nas_eps['nas-eps.nas_msg_esm_type']
            msg_name, _ = get_nas_eps_message_name(msg_type_hex)
            return msg_name
        
        # Security protected 확인
        if 'nas-eps.security_header_type' in nas_eps:
            sec_type = nas_eps['nas-eps.security_header_type']
            if sec_type != '0x00' and sec_type != '0':
                return "Security Protected NAS"
    
    return None


def extract_nested_nas_from_transport(nas_5gs_layer):
    """UL/DL NAS Transport 메시지 안의 중첩된 NAS 메시지 추출"""
    try:
        # Plain NAS 5GS Message 찾기
        if 'Plain NAS 5GS Message' in nas_5gs_layer:
            plain_nas = nas_5gs_layer['Plain NAS 5GS Message']
            
            # Payload container 찾기
            if 'Payload container' in plain_nas and isinstance(plain_nas['Payload container'], dict):
                payload = plain_nas['Payload container']
                
                # Payload container 안의 Plain NAS 5GS Message 찾기
                if 'Plain NAS 5GS Message' in payload and isinstance(payload['Plain NAS 5GS Message'], dict):
                    nested_nas = payload['Plain NAS 5GS Message']
                    
                    # 5GSM 메시지 타입 찾기
                    if 'nas-5gs.sm.message_type' in nested_nas:
                        msg_type_hex = nested_nas['nas-5gs.sm.message_type']
                        msg_name, _ = get_nas_5gs_message_name(msg_type_hex)
                        return msg_name
                    
                    # 5GMM 메시지 타입 찾기
                    if 'nas-5gs.mm.message_type' in nested_nas:
                        msg_type_hex = nested_nas['nas-5gs.mm.message_type']
                        msg_name, _ = get_nas_5gs_message_name(msg_type_hex)
                        return msg_name
    except:
        pass
    
    return None


def extract_nested_nr_rrc_message(lte_rrc_element):
    """LTE RRC 메시지 안에 중첩된 NR RRC 메시지 추출"""
    if not isinstance(lte_rrc_element, dict):
        return None
    
    # 재귀적으로 nr_SecondaryCellGroupConfig_r15_tree 찾기
    def find_nr_rrc(obj, depth=0):
        if depth > 20 or not isinstance(obj, dict):
            return None
        
        # nr_SecondaryCellGroupConfig_r15_tree 찾기
        for key in obj:
            if 'nr_SecondaryCellGroupConfig_r15_tree' in key or 'nr-SecondaryCellGroupConfig-r15-tree' in key:
                nr_tree = obj[key]
                if isinstance(nr_tree, dict):
                    # NR RRC 메시지 찾기
                    for nr_key in nr_tree:
                        if ('nr-rrc.' in nr_key or 'nr_rrc.' in nr_key) and '_element' in nr_key:
                            msg_name = nr_key.replace('nr-rrc.', '').replace('nr_rrc.', '').replace('_element', '')
                            return msg_name
        
        # 재귀적으로 탐색
        for value in obj.values():
            if isinstance(value, dict):
                result = find_nr_rrc(value, depth + 1)
                if result:
                    return result
        
        return None
    
    return find_nr_rrc(lte_rrc_element)


def extract_sib_info(system_info_element):
    """SystemInformation 메시지에서 SIB 타입 추출"""
    if not isinstance(system_info_element, dict):
        return None
    
    sib_types = []
    
    # criticalExtensions_tree 찾기
    def find_sibs(obj, depth=0):
        if depth > 10 or not isinstance(obj, dict):
            return
        
        for key, value in obj.items():
            # SIB 관련 키 찾기
            if 'sib' in key.lower() and '_element' in key:
                # lte-rrc.sib2_element, lte_rrc.sib3_element 등
                sib_match = key.replace('lte-rrc.', '').replace('lte_rrc.', '').replace('_element', '').replace('_tree', '')
                if sib_match.startswith('sib'):
                    sib_num = sib_match.replace('sib', '').upper()
                    if sib_num and sib_num not in sib_types:
                        sib_types.append(f'SIB{sib_num}')
            
            # 재귀적으로 탐색
            if isinstance(value, dict):
                find_sibs(value, depth + 1)
    
    find_sibs(system_info_element)
    
    if sib_types:
        return ' '.join(sorted(sib_types, key=lambda x: int(x.replace('SIB', ''))))
    
    return None


def determine_direction_and_nodes(layers):
    """메시지 방향과 노드 판단"""
    msg_info = extract_message_info(layers)
    msg_name = msg_info['name']
    direction = msg_info.get('direction', 'UL')
    
    # 노드 결정
    if 'lte-rrc' in msg_info['protocol']:
        if direction == 'DL':
            return direction, 'eNB', 'UE'
        else:
            return direction, 'UE', 'eNB'
    
    elif 'nr-rrc' in msg_info['protocol']:
        if direction == 'DL':
            return direction, 'gNB', 'UE'
        else:
            return direction, 'UE', 'gNB'
    
    elif 'nas-eps' in msg_info['protocol']:
        if direction == 'DL':
            return direction, 'MME', 'UE'
        else:
            return direction, 'UE', 'MME'
    
    elif 'nas-5gs' in msg_info['protocol']:
        if direction == 'DL':
            return direction, 'AMF', 'UE'
        else:
            return direction, 'UE', 'AMF'
    
    return direction, 'UE', 'Unknown'


def extract_message_info(layers):
    """메시지 정보 추출 (GSMTAPv3 배열 형식 지원)"""
    
    # NR RRC (언더스코어 버전도 체크)
    nr_rrc_key = None
    if 'nr-rrc' in layers:
        nr_rrc_key = 'nr-rrc'
    elif 'nr_rrc' in layers:
        nr_rrc_key = 'nr_rrc'
    
    if nr_rrc_key:
        nr_rrc = layers[nr_rrc_key]
        
        # nr-rrc가 배열인 경우 처리 (GSMTAPv3)
        if isinstance(nr_rrc, list):
            # [0]은 문자열 "NR Radio Resource Control (RRC) protocol"
            # [1]이 실제 데이터 딕셔너리
            if len(nr_rrc) > 1 and isinstance(nr_rrc[1], dict):
                nr_rrc = nr_rrc[1]
            elif len(nr_rrc) > 0 and isinstance(nr_rrc[0], dict):
                nr_rrc = nr_rrc[0]
            else:
                # 배열이지만 딕셔너리가 없는 경우 - 다음 프로토콜로
                nr_rrc = None
        
        if nr_rrc and isinstance(nr_rrc, dict):
            # 방법 1: Message_element가 있는 경우 (예: UL_CCCH_Message_element)
            for key in nr_rrc:
                if 'Message_element' in key:
                    msg_type = key.replace('nr-rrc.', '').replace('nr_rrc.', '').replace('_element', '')
                    
                    msg_element = nr_rrc[key]
                    if isinstance(msg_element, dict):
                        msg_tree = None
                        msg_tree_key = None
                        
                        for sub_key in msg_element:
                            if 'message_tree' in sub_key.lower():
                                msg_tree_key = sub_key
                                msg_tree = msg_element[sub_key]
                                break
                        
                        if msg_tree and isinstance(msg_tree, dict):
                            # BCCH_BCH_Message의 경우 mib_element가 바로 있음
                            if 'nr-rrc.mib_element' in msg_tree or 'nr_rrc.mib_element' in msg_tree:
                                actual_msg = 'MIB'
                                if 'UL_CCCH' in msg_type or 'UL_DCCH' in msg_type:
                                    direction = 'UL'
                                elif 'DL_CCCH' in msg_type or 'DL_DCCH' in msg_type or 'BCCH' in msg_type or 'PCCH' in msg_type:
                                    direction = 'DL'
                                else:
                                    direction = 'UL'
                                return {'protocol': 'nr-rrc', 'name': actual_msg, 'raw_key': key, 'direction': direction, 'channel': msg_type}
                            
                            c1_tree = None
                            if 'nr-rrc.c1_tree' in msg_tree:
                                c1_tree = msg_tree['nr-rrc.c1_tree']
                            elif 'nr_rrc.c1_tree' in msg_tree:
                                c1_tree = msg_tree['nr_rrc.c1_tree']
                            
                            if c1_tree and isinstance(c1_tree, dict):
                                for c1_key in c1_tree:
                                    if ('nr-rrc.' in c1_key or 'nr_rrc.' in c1_key) and '_element' in c1_key:
                                        actual_msg = c1_key.replace('nr-rrc.', '').replace('nr_rrc.', '').replace('_element', '')
                                        
                                        if actual_msg == 'systemInformationBlockType1':
                                            actual_msg = 'SystemInformationBlockType1'
                                        
                                        nas_msg = extract_nested_nas_message(c1_tree[c1_key])
                                        if nas_msg:
                                            actual_msg = f"{actual_msg} ({nas_msg})"
                                        
                                        if 'UL_CCCH' in msg_type or 'UL_DCCH' in msg_type:
                                            direction = 'UL'
                                        elif 'DL_CCCH' in msg_type or 'DL_DCCH' in msg_type or 'BCCH' in msg_type or 'PCCH' in msg_type:
                                            direction = 'DL'
                                        else:
                                            direction = 'UL'
                                        return {'protocol': 'nr-rrc', 'name': actual_msg, 'raw_key': key, 'direction': direction, 'channel': msg_type}
                    
                    if 'UL_CCCH' in msg_type or 'UL_DCCH' in msg_type:
                        direction = 'UL'
                    elif 'DL_CCCH' in msg_type or 'DL_DCCH' in msg_type or 'BCCH' in msg_type or 'PCCH' in msg_type:
                        direction = 'DL'
                    else:
                        direction = 'UL'
                    
                    return {'protocol': 'nr-rrc', 'name': msg_type, 'raw_key': key, 'direction': direction, 'channel': msg_type}
        
            # 방법 2: GSMTAPv3에서 직접 메시지 타입이 있는 경우 (예: RRCReconfiguration_element)
            for key in nr_rrc:
                if ('nr-rrc.' in key or 'nr_rrc.' in key) and '_element' in key and 'Message' not in key:
                    # nr-rrc.RRCReconfiguration_element 같은 형태
                    actual_msg = key.replace('nr-rrc.', '').replace('nr_rrc.', '').replace('_element', '')
                    
                    # 방향 판단: criticalExtensions_tree 안을 확인
                    direction = 'DL'  # 기본값
                    msg_element = nr_rrc[key]
                    if isinstance(msg_element, dict):
                        # UL 메시지 패턴 확인
                        if any(ul_pattern in actual_msg.lower() for ul_pattern in ['complete', 'request', 'response', 'failure']):
                            direction = 'UL'
                    
                    return {'protocol': 'nr-rrc', 'name': actual_msg, 'raw_key': key, 'direction': direction, 'channel': 'GSMTAP'}
    
    # 방법 3: layers 최상위에 nr-rrc 메시지가 직접 있는 경우 (GSMTAPv3)
    for key in layers:
        if ('nr-rrc.' in key or 'nr_rrc.' in key) and '_element' in key:
            actual_msg = key.replace('nr-rrc.', '').replace('nr_rrc.', '').replace('_element', '')
            
            # 방향 판단
            direction = 'DL'  # 기본값
            if any(ul_pattern in actual_msg.lower() for ul_pattern in ['complete', 'request', 'response', 'failure']):
                direction = 'UL'
            
            return {'protocol': 'nr-rrc', 'name': actual_msg, 'raw_key': key, 'direction': direction, 'channel': 'GSMTAP'}
    
    # LTE RRC (언더스코어 버전도 체크)
    lte_rrc_key = None
    if 'lte-rrc' in layers:
        lte_rrc_key = 'lte-rrc'
    elif 'lte_rrc' in layers:
        lte_rrc_key = 'lte_rrc'
    
    if lte_rrc_key:
        lte_rrc = layers[lte_rrc_key]
        
        # lte-rrc가 배열인 경우 처리 (GSMTAPv3)
        if isinstance(lte_rrc, list):
            if len(lte_rrc) > 1 and isinstance(lte_rrc[1], dict):
                lte_rrc = lte_rrc[1]
            elif len(lte_rrc) > 0 and isinstance(lte_rrc[0], dict):
                lte_rrc = lte_rrc[0]
            else:
                lte_rrc = None
        
        if lte_rrc and isinstance(lte_rrc, dict):
            for key in lte_rrc:
                # PCCH_Message_element, UL_DCCH_Message_element 등 찾기
                if 'Message_element' in key:
                    msg_type = key.replace('lte-rrc.', '').replace('lte_rrc.', '').replace('_element', '')
                    
                    # 내부 메시지 찾기
                    msg_element = lte_rrc[key]
                    if isinstance(msg_element, dict):
                        # 메시지별 message_tree 찾기
                        msg_tree = None
                        msg_tree_key = None
                        
                        # 모든 키를 순회하면서 message_tree 찾기
                        for sub_key in msg_element:
                            if 'message_tree' in sub_key.lower():
                                msg_tree_key = sub_key
                                msg_tree = msg_element[sub_key]
                                break
                        
                        if msg_tree and isinstance(msg_tree, dict):
                            # c1_tree 찾기
                            c1_tree = None
                            if 'lte-rrc.c1_tree' in msg_tree:
                                c1_tree = msg_tree['lte-rrc.c1_tree']
                            elif 'lte_rrc.c1_tree' in msg_tree:
                                c1_tree = msg_tree['lte_rrc.c1_tree']
                            
                            if c1_tree and isinstance(c1_tree, dict):
                                for c1_key in c1_tree:
                                    if ('lte-rrc.' in c1_key or 'lte_rrc.' in c1_key) and '_element' in c1_key:
                                        actual_msg = c1_key.replace('lte-rrc.', '').replace('lte_rrc.', '').replace('_element', '')
                                        
                                        # SystemInformation 메시지 처리
                                        if actual_msg == 'systemInformation':
                                            # SIB 타입 확인
                                            sib_info = extract_sib_info(c1_tree[c1_key])
                                            if sib_info:
                                                actual_msg = f"SystemInformation ({sib_info})"
                                        
                                        # 중첩된 NAS 메시지 확인
                                        nas_msg = extract_nested_nas_message(c1_tree[c1_key])
                                        if nas_msg:
                                            actual_msg = f"{actual_msg} ({nas_msg})"
                                        
                                        # 중첩된 NR RRC 메시지 확인
                                        nr_rrc_msg = extract_nested_nr_rrc_message(c1_tree[c1_key])
                                        if nr_rrc_msg:
                                            actual_msg = f"{actual_msg} ({nr_rrc_msg})"
                                        
                                        if 'UL_CCCH' in msg_type or 'UL_DCCH' in msg_type:
                                            direction = 'UL'
                                        elif 'DL_CCCH' in msg_type or 'DL_DCCH' in msg_type or 'BCCH' in msg_type or 'PCCH' in msg_type:
                                            direction = 'DL'
                                        else:
                                            direction = 'UL'
                                        return {'protocol': 'lte-rrc', 'name': actual_msg, 'raw_key': key, 'direction': direction, 'channel': msg_type}
                    
                    # 메시지를 찾지 못한 경우 채널 타입만 반환
                    if 'UL_CCCH' in msg_type or 'UL_DCCH' in msg_type:
                        direction = 'UL'
                    elif 'DL_CCCH' in msg_type or 'DL_DCCH' in msg_type or 'BCCH' in msg_type or 'PCCH' in msg_type:
                        direction = 'DL'
                    else:
                        direction = 'UL'
                    
                    return {'protocol': 'lte-rrc', 'name': msg_type, 'raw_key': key, 'direction': direction, 'channel': msg_type}
    
    # NAS 5GS
    if 'nas-5gs' in layers:
        nas_5gs = layers['nas-5gs']
        
        # 5GMM message_type 필드 찾기
        if 'nas-5gs.mm.message_type' in nas_5gs:
            msg_type_hex = nas_5gs['nas-5gs.mm.message_type']
            msg_name, direction = get_nas_5gs_message_name(msg_type_hex)
            
            # UL/DL NAS Transport인 경우 중첩된 메시지 확인
            if msg_type_hex in ['0x67', '0x68']:  # UL/DL NAS Transport
                nested_msg = extract_nested_nas_from_transport(nas_5gs)
                if nested_msg:
                    msg_name = f"{msg_name} ({nested_msg})"
            
            return {'protocol': 'nas-5gs', 'name': msg_name, 'raw_key': 'nas-5gs.mm.message_type', 'direction': direction}
        
        # Plain/Security protected 메시지 확인
        for key in nas_5gs:
            if 'NAS 5GS' in key or 'message' in key.lower():
                if 'Security protected' in key:
                    return {'protocol': 'nas-5gs', 'name': 'Security Protected NAS', 'raw_key': key, 'direction': 'UL'}
                elif 'Plain' in key:
                    if isinstance(nas_5gs[key], dict):
                        plain_nas = nas_5gs[key]
                        
                        # 5GMM 메시지 타입
                        if 'nas-5gs.mm.message_type' in plain_nas:
                            msg_type_hex = plain_nas['nas-5gs.mm.message_type']
                            msg_name, direction = get_nas_5gs_message_name(msg_type_hex)
                            
                            # UL/DL NAS Transport인 경우 중첩된 메시지 확인
                            if msg_type_hex in ['0x67', '0x68']:  # UL/DL NAS Transport
                                nested_msg = extract_nested_nas_from_transport(nas_5gs)
                                if nested_msg:
                                    msg_name = f"{msg_name} ({nested_msg})"
                            
                            return {'protocol': 'nas-5gs', 'name': msg_name, 'raw_key': key, 'direction': direction}
                        
                        # 5GSM 메시지 타입
                        if 'nas-5gs.sm.message_type' in plain_nas:
                            msg_type_hex = plain_nas['nas-5gs.sm.message_type']
                            msg_name, direction = get_nas_5gs_message_name(msg_type_hex)
                            return {'protocol': 'nas-5gs', 'name': msg_name, 'raw_key': key, 'direction': direction}
    
    # NAS EPS
    if 'nas-eps' in layers:
        nas_eps = layers['nas-eps']
        
        # EMM message_type 필드 찾기
        if 'nas-eps.nas_msg_emm_type' in nas_eps:
            msg_type_hex = nas_eps['nas-eps.nas_msg_emm_type']
            msg_name, direction = get_nas_eps_message_name(msg_type_hex)
            return {'protocol': 'nas-eps', 'name': msg_name, 'raw_key': 'nas-eps.nas_msg_emm_type', 'direction': direction}
        
        # ESM message_type 필드 찾기
        if 'nas-eps.nas_msg_esm_type' in nas_eps:
            msg_type_hex = nas_eps['nas-eps.nas_msg_esm_type']
            msg_name, direction = get_nas_eps_message_name(msg_type_hex)
            return {'protocol': 'nas-eps', 'name': msg_name, 'raw_key': 'nas-eps.nas_msg_esm_type', 'direction': direction}
        
        # Security protected NAS message 확인
        if 'nas-eps.security_header_type' in nas_eps:
            sec_type = nas_eps['nas-eps.security_header_type']
            # Security header type이 0이 아니면 암호화/무결성 보호됨
            if sec_type != '0x00' and sec_type != '0':
                # 복호화된 메시지가 있는지 확인
                if 'nas-eps.nas_msg_emm_type' in nas_eps:
                    msg_type_hex = nas_eps['nas-eps.nas_msg_emm_type']
                    msg_name, direction = get_nas_eps_message_name(msg_type_hex)
                    return {'protocol': 'nas-eps', 'name': msg_name, 'raw_key': 'nas-eps.nas_msg_emm_type', 'direction': direction}
                elif 'nas-eps.nas_msg_esm_type' in nas_eps:
                    msg_type_hex = nas_eps['nas-eps.nas_msg_esm_type']
                    msg_name, direction = get_nas_eps_message_name(msg_type_hex)
                    return {'protocol': 'nas-eps', 'name': msg_name, 'raw_key': 'nas-eps.nas_msg_esm_type', 'direction': direction}
                else:
                    # 복호화 안된 경우
                    return {'protocol': 'nas-eps', 'name': 'Security Protected NAS', 'raw_key': 'nas-eps.security_header_type', 'direction': 'UL'}
    
    return {'protocol': 'unknown', 'name': 'Unknown', 'raw_key': None, 'direction': 'UL'}


def parse_call_flow(json_path):
    """JSON을 call flow로 파싱"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    flows = []
    debug_info = []
    nr_rrc_debug = []  # NR RRC 전용 디버그
    
    for idx, packet in enumerate(data):
        layers = packet.get('_source', {}).get('layers', {})
        
        frame = layers.get('frame', {})
        frame_num = frame.get('frame.number', [''])[0] if isinstance(frame.get('frame.number'), list) else frame.get('frame.number', '')
        timestamp_full = frame.get('frame.time', [''])[0] if isinstance(frame.get('frame.time'), list) else frame.get('frame.time', '')
        
        # 시간 포맷 변경
        timestamp = format_timestamp(timestamp_full)
        
        msg_info = extract_message_info(layers)
        
        # NR RRC 메시지 디버깅
        if msg_info['protocol'] == 'nr-rrc':
            nr_rrc_data = {
                'frame': frame_num,
                'message': msg_info['name'],
                'layers_keys': list(layers.keys()),
                'nr_rrc_type': type(layers.get('nr-rrc', None)).__name__,
                'nr_rrc_content': None
            }
            
            if 'nr-rrc' in layers:
                nr_rrc = layers['nr-rrc']
                if isinstance(nr_rrc, list):
                    nr_rrc_data['nr_rrc_content'] = f'Array with {len(nr_rrc)} items: {nr_rrc}'
                elif isinstance(nr_rrc, dict):
                    nr_rrc_data['nr_rrc_content'] = f'Dict with keys: {list(nr_rrc.keys())[:10]}'
                else:
                    nr_rrc_data['nr_rrc_content'] = str(nr_rrc)[:200]
            
            # nr-rrc로 시작하는 모든 키 찾기
            nr_rrc_keys = [k for k in layers.keys() if k.startswith('nr-rrc.') or k.startswith('nr_rrc.')]
            nr_rrc_data['nr_rrc_element_keys'] = nr_rrc_keys
            
            nr_rrc_debug.append(nr_rrc_data)
        
        # 디버깅 정보 수집 (처음 5개만)
        if idx < 5:
            debug_info.append({
                'frame': frame_num,
                'layers_keys': list(layers.keys()),
                'msg_info': msg_info
            })
        
        if msg_info['name'] == 'Unknown':
            continue
        
        direction, source, destination = determine_direction_and_nodes(layers)
        
        # 프로토콜별로 해당 레이어만 추출
        protocol_details = {}
        if msg_info['protocol'] == 'nr-rrc':
            # 먼저 nr-rrc.XXX_element 키를 찾기 (실제 데이터)
            nr_rrc_element_key = None
            for key in layers.keys():
                if (key.startswith('nr-rrc.') or key.startswith('nr_rrc.')) and '_element' in key:
                    nr_rrc_element_key = key
                    break
            
            if nr_rrc_element_key:
                # 실제 메시지 데이터 사용
                protocol_details = layers[nr_rrc_element_key]
            elif 'nr-rrc' in layers:
                # fallback: nr-rrc 레이어 사용
                nr_rrc_data = layers['nr-rrc']
                if isinstance(nr_rrc_data, list):
                    # 배열인 경우 처리
                    if len(nr_rrc_data) > 1 and isinstance(nr_rrc_data[1], dict):
                        protocol_details = nr_rrc_data[1]
                    elif len(nr_rrc_data) > 0 and isinstance(nr_rrc_data[0], dict):
                        protocol_details = nr_rrc_data[0]
                    else:
                        protocol_details = {'_raw_array': nr_rrc_data}
                else:
                    protocol_details = nr_rrc_data
            elif 'nr_rrc' in layers:
                protocol_details = layers['nr_rrc']
        elif msg_info['protocol'] == 'lte-rrc':
            if 'lte-rrc' in layers:
                protocol_details = layers['lte-rrc']
            elif 'lte_rrc' in layers:
                protocol_details = layers['lte_rrc']
        elif msg_info['protocol'] == 'nas-5gs':
            if 'nas-5gs' in layers:
                protocol_details = layers['nas-5gs']
                # PCO 필드 향상
                enhance_pco_fields(protocol_details)
        elif msg_info['protocol'] == 'nas-eps':
            if 'nas-eps' in layers:
                protocol_details = layers['nas-eps']
                # PCO 필드 향상
                enhance_pco_fields(protocol_details)
        else:
            # 알 수 없는 프로토콜인 경우 전체 레이어 저장
            protocol_details = layers
        
        flow = {
            'frame': str(frame_num),
            'timestamp': timestamp,
            'source': source,
            'destination': destination,
            'direction': direction,
            'message': msg_info['name'],
            'protocol': msg_info['protocol'],
            'details': protocol_details
        }
        
        flows.append(flow)
    
    # 디버깅 정보 저장
    debug_path = json_path.replace('.json', '_parse_debug.json')
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_packets': len(data),
            'parsed_flows': len(flows),
            'sample_debug': debug_info,
            'nr_rrc_debug': nr_rrc_debug  # NR RRC 전용 디버그 추가
        }, f, indent=2, ensure_ascii=False)
    
    return flows
