import subprocess
import argparse
import json
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re

def format_ambr(ambr_str):
    if ambr_str == "N/A": return "N/A"
    match = re.search(r"(\d+)", ambr_str)
    if match:
        number = int(match.group(1))
        return f"{number:,} Kbps"
    return ambr_str

def parse_sa_pcap(pcap_file):
    print(f"[*] '{pcap_file}' 분석 중...")
    cmd = ["tshark", "-r", pcap_file, "-Y", "nas_5gs.sm.message_type == 0xc2", "-T", "pdml"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if not proc.stdout.strip():
        print("[-] NAS 5GSM Message를 찾을 수 없습니다.")
        return {}
    
    root = ET.fromstring(proc.stdout)
    sessions = {}
    for packet in root.iter("packet"):
        all_text = ""
        for f in packet.iter("field"):
            all_text += f" | {f.get('showname', '')} : {f.get('show', '')}"
        
        p_id_match = re.search(r"PDU session identity value (\d+)", all_text)
        if not p_id_match: continue
        p_id = p_id_match.group(1)
        
        if p_id not in sessions:
            sd = "N/A"; sst = "N/A"
            sd_match = re.search(r"Slice differentiator \(SD\): (\d+)", all_text)
            if sd_match: sd = sd_match.group(1)
            sst_match = re.search(r"Slice/service type \(SST\):.*?\((\d+)\)", all_text)
            if sst_match: sst = sst_match.group(1)
            
            ambr_match = re.search(r"Session-AMBR for downlink: ([\d\.]+\s?\w+)", all_text)
            ambr = format_ambr(ambr_match.group(1)) if ambr_match else "N/A"
            
            dnn_match = re.search(r"DNN: ([\w\.]+)", all_text)
            dnn = dnn_match.group(1) if dnn_match else "Unknown"
            
            ip_addr = "N/A"; ip_ver = "N/A"
            ipv4_match = re.search(r"PDU address information: ([\d\.]+)", all_text)
            if ipv4_match: ip_ver = "IPv4"; ip_addr = ipv4_match.group(1)
            
            sessions[p_id] = {'dnn': dnn, 'sst': sst, 'sd': sd, 'ambr': ambr, 'ip_ver': ip_ver, 'ip_addr': ip_addr, 'flows': {}}
            
        qfis = re.findall(r"Qos flow identifier: (\d+)", all_text)
        q5is = re.findall(r"5QI: (\d+)", all_text)
        rids = re.findall(r"QoS rule identifier: (\d+)", all_text)
        for q in qfis:
            if q not in sessions[p_id]['flows']:
                sessions[p_id]['flows'][q] = {'qfi': q, '5qi': 'N/A', 'rule_id': 'N/A', 'def': 'No'}
        for i, val in enumerate(q5is):
            if i < len(qfis): sessions[p_id]['flows'][qfis[i]]['5qi'] = val
        for i, val in enumerate(rids):
            if i < len(qfis): sessions[p_id]['flows'][qfis[i]]['rule_id'] = val
            
    for p_id in sessions:
        flow_list = list(sessions[p_id]['flows'].values())
        if flow_list: flow_list[0]['def'] = 'Yes'
        sessions[p_id]['flows'] = flow_list

    # 중간 데이터 출력 로직 추가
    print("\n" + "="*90)
    print("FINAL REFINED DATA")
    print("="*90)
    print(json.dumps(sessions, indent=4))
    print("="*90 + "\n")
    
    return sessions

def draw_final_diagram(sessions, output_file):
    if not sessions: return
    total_flows = sum(len(s['flows']) for s in sessions.values())
    fig_height = max(6, len(sessions) * 3 + total_flows * 0.8)
    fig, ax = plt.subplots(figsize=(16, fig_height))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    
    themes = [
        {'bg': '#F1F8E9', 'text': '#1B5E20', 'flow': '#4CAF50'}, 
        {'bg': '#FFF3E0', 'text': '#E65100', 'flow': '#FF9800'}, 
        {'bg': '#E3F2FD', 'text': '#0D47A1', 'flow': '#2196F3'}
    ]

    curr_y = 95
    for i, (p_id, info) in enumerate(sessions.items()):
        theme = themes[i % len(themes)]
        num_flows = len(info['flows'])
        box_h = 10 + (num_flows * 7)
        
        rect = patches.FancyBboxPatch((5, curr_y - box_h), 90, box_h, 
                                     boxstyle="round,pad=0.5", 
                                     ec="#455A64", fc=theme['bg'], alpha=0.9, lw=2)
        ax.add_patch(rect)
        
        header = (f"PDU Session {p_id} | DNN: {info['dnn']} | SST: {info['sst']} | SD: {info['sd']} | "
                  f"Addr: {info['ip_ver']}({info['ip_addr']}) | AMBR: {info['ambr']}")
        ax.text(7, curr_y - 4, header, weight='bold', fontsize=12, color=theme['text'])

        for j, flow in enumerate(info['flows']):
            fy = curr_y - 11 - (j * 7)
            ax.add_patch(patches.Rectangle((7.5, fy - 2), 85, 4, fc=theme['flow'], ec='white', alpha=0.9))
            
            f_text = f"QFI: {flow['qfi']} (5QI: {flow['5qi']}) | Rule ID: {flow['rule_id']}"
            if flow.get('def') == "Yes": f_text += " [DEFAULT]"
            ax.text(9, fy, f_text, color='white', weight='bold', va='center', fontsize=11)
            
        curr_y -= (box_h + 5)

    ax.set_axis_off()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[*] 시각화 완료: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    args = parser.parse_args()
    data = parse_sa_pcap(args.pcap)
    draw_final_diagram(data, "sa_session_result.png")