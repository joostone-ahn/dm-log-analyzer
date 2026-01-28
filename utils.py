"""
유틸리티 함수 모음
- JSON 파싱
- 타임스탬프 포맷
- PCO 필드 향상
"""
import json
import re


def parse_json_with_duplicate_keys(json_str):
    """중복 키를 배열로 변환하는 커스텀 JSON 파서"""
    def object_pairs_hook(pairs):
        """중복 키를 배열로 변환"""
        result = {}
        for key, value in pairs:
            if key in result:
                # 이미 키가 존재하면 배열로 변환
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(value)
            else:
                result[key] = value
        return result
    
    return json.loads(json_str, object_pairs_hook=object_pairs_hook)


def format_timestamp(timestamp_full):
    """타임스탬프 포맷 변경: hh:mm:ss.ms (ms는 3자리)"""
    try:
        # "Jan 27, 2026 16:43:13.790560000 KST" 형식에서 시간 부분만 추출
        match = re.search(r'(\d{2}):(\d{2}):(\d{2})\.(\d+)', timestamp_full)
        if match:
            hh, mm, ss, ms = match.groups()
            ms_3digit = ms[:3]  # 밀리초 3자리만
            return f"{hh}:{mm}:{ss}.{ms_3digit}"
        return timestamp_full
    except:
        return timestamp_full


def enhance_pco_fields(nas_layer):
    """Protocol Configuration Options 필드를 사람이 읽기 쉬운 형태로 변환"""
    if not isinstance(nas_layer, dict):
        return nas_layer
    
    # PCO 매핑 테이블 (3GPP TS 24.008)
    pco_protocol_ids = {
        '0x0001': 'P-CSCF IPv6 Address',
        '0x0003': 'DNS Server IPv6 Address',
        '0x000c': 'P-CSCF IPv4 Address',
        '0x000d': 'DNS Server IPv4 Address',
        '0x0005': 'MS Support of Network Requested Bearer Control indicator',
        '0x0010': 'IPv4 Link MTU',
        '0x0012': 'P-CSCF Re-selection support',
        '0x0013': 'NBIFOM request indicator',
        '0x0014': 'NBIFOM mode',
        '0x0015': 'Non-IP link MTU request',
        '0x0016': 'APN rate control support indicator',
        '0x0017': '3GPP PS data off UE status',
        '0x0018': 'Reliable Data Service request indicator',
        '0x001a': 'Additional APN rate control for exception data support indicator',
        '0x001b': 'PDU session ID',
        '0x001c': 'Ethernet Frame Payload MTU request',
        '0x001d': 'Unstructured link MTU request',
        '0x001e': '5GSM cause value',
        '0x001f': 'QoS rules with the length of two octets support indicator',
        '0x0020': 'QoS flow descriptions with the length of two octets support indicator',
    }
    
    # 재귀적으로 모든 레이어 탐색
    for key, value in list(nas_layer.items()):
        if key == 'Protocol Configuration Options' and isinstance(value, dict):
            pco = value
            
            # pco_pid와 pco_pid_tree가 배열인 경우
            if 'gsm_a.gm.sm.pco_pid' in pco and isinstance(pco['gsm_a.gm.sm.pco_pid'], list):
                pco_pids = pco['gsm_a.gm.sm.pco_pid']
                pco_trees = pco.get('gsm_a.gm.sm.pco_pid_tree', [])
                
                if not isinstance(pco_trees, list):
                    pco_trees = [pco_trees]
                
                # 사람이 읽기 쉬운 형태로 변환
                enhanced_items = []
                for idx, pid in enumerate(pco_pids):
                    protocol_name = pco_protocol_ids.get(pid, f'Unknown Protocol ({pid})')
                    item = {
                        'Protocol or Container ID': protocol_name,
                        'ID': pid
                    }
                    
                    # 해당하는 tree 정보 추가
                    if idx < len(pco_trees):
                        tree = pco_trees[idx]
                        if isinstance(tree, dict):
                            # Length 추가
                            if 'gsm_a.gm.sm.pco.length' in tree:
                                length_hex = tree['gsm_a.gm.sm.pco.length']
                                length_dec = int(length_hex, 16) if isinstance(length_hex, str) and length_hex.startswith('0x') else length_hex
                                item['Length'] = f"{length_hex} ({length_dec})"
                            
                            # IP 주소 추가
                            for tree_key, tree_value in tree.items():
                                if 'ipv6' in tree_key:
                                    item['IPv6'] = tree_value
                                elif 'ipv4' in tree_key:
                                    item['IPv4'] = tree_value
                    
                    enhanced_items.append(item)
                
                # 원본 필드는 유지하고 enhanced 버전 추가
                pco['_enhanced_items'] = enhanced_items
        
        # 재귀적으로 하위 딕셔너리 처리
        elif isinstance(value, dict):
            enhance_pco_fields(value)
    
    return nas_layer
