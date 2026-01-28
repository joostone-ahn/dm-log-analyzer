#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import subprocess
import math
import re
import os

def calculate_mos(loss_fraction, jitter_units, sampling_rate=16000):
    if loss_fraction is None: return 1.0
    divisor = sampling_rate / 1000.0
    jit_ms = (jitter_units or 0) / divisor
    r = 94.77 - (0.024 * (jit_ms * 2 + 20)) - (30 * math.log(1 + 15 * (loss_fraction / 256.0 + 0.00001)))
    r_final = max(0, min(r, 94.77))
    mos = 1 + (0.035 * r_final) + (r_final * (r_final - 60) * (100 - r_final) * 0.000007)
    return round(max(1.0, min(mos, 4.5)), 2)

def extract_tft_ports(pcap):
    print(f"[*] 1단계: NAS TFT Rule 추출 중...")
    cmd = ["tshark", "-r", pcap, "-V", "-Y", "nas-eps"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    ue_ports, svr_ports = set(), set()
    is_uplink_filter = False
    for line in proc.stdout.splitlines():
        if "Packet filter direction: Uplink only" in line:
            is_uplink_filter = True
            continue
        if is_uplink_filter:
            match = re.search(r"Port:\s+(\d+)", line)
            if match:
                port = match.group(1)
                if int(port) < 30000: ue_ports.add(port)
                else: svr_ports.add(port)
            if line.strip() == "" or ("Packet filter:" in line and "direction" not in line):
                is_uplink_filter = False
    return ue_ports, svr_ports

def run_analysis(pcap, out_prefix):
    ue_ports, svr_ports = extract_tft_ports(pcap)
    if not ue_ports:
        print("[-] NAS TFT 정보를 찾지 못했습니다.")
        return

    print("[*] 2단계: RTCP 품질 데이터 추출 및 상세 매칭 중...")
    cmd = [
        "tshark", "-r", pcap, "-Y", "rtcp.ssrc.fraction",
        "-T", "fields", "-E", "separator=/t",
        "-e", "frame.time_epoch", "-e", "udp.srcport", 
        "-e", "rtcp.senderssrc", "-e", "rtcp.ssrc.fraction", "-e", "rtcp.ssrc.jitter",
        "-e", "rtcp.pt", "-e", "rtcp.ssrc.identifier"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    
    results = {}
    
    for line in proc.stdout.splitlines():
        v = line.split('\t')
        if len(v) < 6 or not v[2]: continue
        
        t_epoch = v[0]
        ports_in_packet = v[1].split(',') 
        sender_raw = v[2].split(',')[0]
        loss_raw = v[3].split(',')[0]
        jit_raw = v[4].split(',')[0]
        pt_raw = v[5].split(',')[0]
        target_raw = v[6].split(',')[0] if len(v) > 6 and v[6] else sender_raw

        if not loss_raw or not jit_raw: continue

        reporter = None
        dir_short = "" # 파일명용 (DL/UL)
        dir_display = "" # 화면출력용 (DL Stream/UL Stream)
        
        for p in ports_in_packet:
            if p in ue_ports:
                reporter = "UE"
                dir_short = "DL"
                dir_display = "DL Stream"
                break
            elif p in svr_ports:
                reporter = "Server"
                dir_short = "UL"
                dir_display = "UL Stream"
                break
        
        if not reporter: continue 

        s_hex = sender_raw if sender_raw.startswith('0x') else hex(int(sender_raw))
        t_hex = target_raw if target_raw.startswith('0x') else hex(int(target_raw))

        key = f"{t_hex}_{reporter}"
        if key not in results:
            msg_type = "SR" if pt_raw == "200" else "RR" if pt_raw == "201" else "RTCP"
            results[key] = {
                "msg": msg_type, 
                "sender": f"{s_hex} ({reporter})", 
                "target": f"{t_hex} ({dir_display})", 
                "data": [], 
                "t0": float(t_epoch), 
                "rep": reporter, 
                "dir_short": dir_short
            }
        
        results[key]["data"].append({
            "t_rel": round(float(t_epoch) - results[key]["t0"], 2),
            "loss_pct": round((int(loss_raw)/256)*100, 2),
            "jitter": int(jit_raw),
            "mos": calculate_mos(int(loss_raw), int(jit_raw))
        })

    if not results:
        print("[-] 매칭된 데이터가 없습니다.")
        return

    print("\n" + "=" * 95)
    print(f"{'Msg':<4} | {'Sender':<22} | {'Target SSRC':<28} | {'Avg MOS'} | {'Samples'}")
    print("-" * 95)

    for key, info in results.items():
        avg_mos = round(sum(d['mos'] for d in info['data']) / len(info['data']), 2)
        print(f"{info['msg']:<4} | {info['sender']:<22} | {info['target']:<28} | {avg_mos:<7} | {len(info['data'])}")
        
        # 파일명 단순화: RTCP_SR_DL_Quality_by_UE.csv 형태
        fname = f"RTCP_{info['msg']}_{info['dir_short']}_Quality_by_{info['rep']}.csv"
        
        with open(fname, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Relative_Time", "Loss_Rate_Pct", "Jitter", "MOS"])
            for d in info['data']:
                w.writerow([d['t_rel'], d['loss_pct'], d['jitter'], d['mos']])
    
    print("=" * 95 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    args = parser.parse_args()
    if os.path.exists(args.pcap): run_analysis(args.pcap, "Result")