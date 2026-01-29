"""
3GPP 표준 기반 NAS 메시지 타입 매핑
- NAS 5GS: 3GPP TS 24.501
- NAS EPS: 3GPP TS 24.301
"""

def get_nas_5gs_message_name(msg_type):
    """NAS 5GS 메시지 타입을 이름과 방향으로 변환 (3GPP TS 24.501 Table 9.7.1, 9.7.2)"""
    nas_5gs_messages = {
        # 5GMM messages (Table 9.7.1)
        '0x41': ('Registration Request', 'UL'),
        '0x42': ('Registration Accept', 'DL'),
        '0x43': ('Registration Complete', 'UL'),
        '0x44': ('Registration Reject', 'DL'),
        '0x45': ('Deregistration Request (UE originating)', 'UL'),
        '0x46': ('Deregistration Accept (UE originating)', 'DL'),
        '0x47': ('Deregistration Request (UE terminated)', 'DL'),
        '0x48': ('Deregistration Accept (UE terminated)', 'UL'),
        
        '0x4c': ('Service Request', 'UL'),
        '0x4d': ('Service Reject', 'DL'),
        '0x4e': ('Service Accept', 'DL'),
        '0x4f': ('Control Plane Service Request', 'UL'),
        
        '0x50': ('Network Slice-Specific Authentication Command', 'DL'),
        '0x51': ('Network Slice-Specific Authentication Complete', 'UL'),
        '0x52': ('Network Slice-Specific Authentication Result', 'DL'),
        
        '0x54': ('Configuration Update Command', 'DL'),
        '0x55': ('Configuration Update Complete', 'UL'),
        
        '0x56': ('Authentication Request', 'DL'),
        '0x57': ('Authentication Response', 'UL'),
        '0x58': ('Authentication Reject', 'DL'),
        '0x59': ('Authentication Failure', 'UL'),
        '0x5a': ('Authentication Result', 'DL'),
        
        '0x5b': ('Identity Request', 'DL'),
        '0x5c': ('Identity Response', 'UL'),
        
        '0x5d': ('Security Mode Command', 'DL'),
        '0x5e': ('Security Mode Complete', 'UL'),
        '0x5f': ('Security Mode Reject', 'UL'),
        
        '0x64': ('5GMM Status', 'UL/DL'),
        '0x65': ('Notification', 'DL'),
        '0x66': ('Notification Response', 'UL'),
        '0x67': ('UL NAS Transport', 'UL'),
        '0x68': ('DL NAS Transport', 'DL'),
        
        '0x69': ('Relay Key Request', 'UL'),
        '0x6a': ('Relay Key Accept', 'DL'),
        '0x6b': ('Relay Key Reject', 'DL'),
        '0x6c': ('Relay Authentication Request', 'DL'),
        '0x6d': ('Relay Authentication Response', 'UL'),
        
        # 5GSM messages (Table 9.7.2)
        '0xc1': ('PDU Session Establishment Request', 'UL'),
        '0xc2': ('PDU Session Establishment Accept', 'DL'),
        '0xc3': ('PDU Session Establishment Reject', 'DL'),
        '0xc5': ('PDU Session Authentication Command', 'DL'),
        '0xc6': ('PDU Session Authentication Complete', 'UL'),
        '0xc7': ('PDU Session Authentication Result', 'DL'),
        '0xc9': ('PDU Session Modification Request', 'UL'),
        '0xca': ('PDU Session Modification Reject', 'DL'),
        '0xcb': ('PDU Session Modification Command', 'DL'),
        '0xcc': ('PDU Session Modification Complete', 'UL'),
        '0xcd': ('PDU Session Modification Command Reject', 'UL'),
        '0xd1': ('PDU Session Release Request', 'UL'),
        '0xd2': ('PDU Session Release Reject', 'DL'),
        '0xd3': ('PDU Session Release Command', 'DL'),
        '0xd4': ('PDU Session Release Complete', 'UL'),
        '0xd6': ('5GSM Status', 'UL/DL'),
        '0xd8': ('Service-Level Authentication Command', 'DL'),
        '0xd9': ('Service-Level Authentication Complete', 'UL'),
        '0xda': ('Remote UE Report', 'UL'),
        '0xdb': ('Remote UE Report Response', 'DL'),
    }
    msg_info = nas_5gs_messages.get(str(msg_type), (f'NAS-5GS {msg_type}', 'UL'))
    # Status 메시지는 양방향이므로 기본값 UL
    if msg_info[1] == 'UL/DL':
        return (msg_info[0], 'UL')
    return msg_info


def get_nas_eps_message_name(msg_type):
    """NAS EPS 메시지 타입을 이름과 방향으로 변환 (3GPP TS 24.301 Table 9.8.1, 9.8.2)"""
    nas_eps_messages = {
        # EMM messages (Table 9.8.1)
        '0x41': ('Attach Request', 'UL'),
        '0x42': ('Attach Accept', 'DL'),
        '0x43': ('Attach Complete', 'UL'),
        '0x44': ('Attach Reject', 'DL'),
        '0x45': ('Detach Request', 'UL/DL'),
        '0x46': ('Detach Accept', 'UL/DL'),
        '0x48': ('Tracking Area Update Request', 'UL'),
        '0x49': ('Tracking Area Update Accept', 'DL'),
        '0x4a': ('Tracking Area Update Complete', 'UL'),
        '0x4b': ('Tracking Area Update Reject', 'DL'),
        '0x4c': ('Extended Service Request', 'UL'),
        '0x4d': ('Control Plane Service Request', 'UL'),
        '0x4e': ('Service Reject', 'DL'),
        '0x4f': ('Service Accept', 'DL'),
        '0x50': ('GUTI Reallocation Command', 'DL'),
        '0x51': ('GUTI Reallocation Complete', 'UL'),
        '0x52': ('Authentication Request', 'DL'),
        '0x53': ('Authentication Response', 'UL'),
        '0x54': ('Authentication Reject', 'DL'),
        '0x5c': ('Authentication Failure', 'UL'),
        '0x55': ('Identity Request', 'DL'),
        '0x56': ('Identity Response', 'UL'),
        '0x5d': ('Security Mode Command', 'DL'),
        '0x5e': ('Security Mode Complete', 'UL'),
        '0x5f': ('Security Mode Reject', 'UL'),
        '0x60': ('EMM Status', 'UL/DL'),
        '0x61': ('EMM Information', 'DL'),
        '0x62': ('Downlink NAS Transport', 'DL'),
        '0x63': ('Uplink NAS Transport', 'UL'),
        '0x64': ('CS Service Notification', 'DL'),
        '0x68': ('Downlink Generic NAS Transport', 'DL'),
        '0x69': ('Uplink Generic NAS Transport', 'UL'),
        
        # ESM messages (Table 9.8.2)
        '0xc1': ('Activate Default EPS Bearer Context Request', 'DL'),
        '0xc2': ('Activate Default EPS Bearer Context Accept', 'UL'),
        '0xc3': ('Activate Default EPS Bearer Context Reject', 'UL'),
        '0xc5': ('Activate Dedicated EPS Bearer Context Request', 'DL'),
        '0xc6': ('Activate Dedicated EPS Bearer Context Accept', 'UL'),
        '0xc7': ('Activate Dedicated EPS Bearer Context Reject', 'UL'),
        '0xc9': ('Modify EPS Bearer Context Request', 'DL'),
        '0xca': ('Modify EPS Bearer Context Accept', 'UL'),
        '0xcb': ('Modify EPS Bearer Context Reject', 'UL'),
        '0xcd': ('Deactivate EPS Bearer Context Request', 'DL'),
        '0xce': ('Deactivate EPS Bearer Context Accept', 'UL'),
        '0xd0': ('PDN Connectivity Request', 'UL'),
        '0xd1': ('PDN Connectivity Reject', 'DL'),
        '0xd2': ('PDN Disconnect Request', 'UL'),
        '0xd3': ('PDN Disconnect Reject', 'DL'),
        '0xd4': ('Bearer Resource Allocation Request', 'UL'),
        '0xd5': ('Bearer Resource Allocation Reject', 'DL'),
        '0xd6': ('Bearer Resource Modification Request', 'UL'),
        '0xd7': ('Bearer Resource Modification Reject', 'DL'),
        '0xd9': ('ESM Information Request', 'DL'),
        '0xda': ('ESM Information Response', 'UL'),
        '0xdb': ('Notification', 'DL'),
        '0xdc': ('ESM Dummy Message', 'UL'),
        '0xe8': ('ESM Status', 'UL/DL'),
        '0xe9': ('Remote UE Report', 'UL'),
        '0xea': ('Remote UE Report Response', 'DL'),
        '0xeb': ('ESM Data Transport', 'UL/DL'),
    }
    msg_info = nas_eps_messages.get(str(msg_type), (f'NAS-EPS {msg_type}', 'UL'))
    # 양방향 메시지는 기본값 UL
    if msg_info[1] == 'UL/DL':
        return (msg_info[0], 'UL')
    return msg_info
