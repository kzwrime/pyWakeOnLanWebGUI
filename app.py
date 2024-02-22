import json
import os
import nmap
import wakeonlan
import re
from flask import Flask, render_template, request, redirect, url_for, flash

import time

urlprefix = "/a520"
hosts = '192.168.1.1/24'

app = Flask(__name__)
devices = []
show_scanned_devices = []

# 随便敲的
app.secret_key = 'nfp3oh349ph23904r1h3rfih1023'

# 读取设备信息
def load_devices():
    global devices
    if os.path.exists('devices.json'):
        with open('devices.json', 'r') as f:
            devices = json.load(f)
            return devices
    else:
        devices = []
        return devices

# 保存设备信息
def save_devices(_devices):
    global devices
    devices = _devices
    with open('devices.json', 'w') as f:
        json.dump(devices, f)

# 读取设备信息
def load_scanned_devices():
    global show_scanned_devices
    if os.path.exists('scanned_devices.json'):
        with open('scanned_devices.json', 'r') as f:
            show_scanned_devices = json.load(f)
            return show_scanned_devices
    else:
        show_scanned_devices = []
        return show_scanned_devices

# 保存设备信息
def save_scanned_devices(_scanned_devices):
    global show_scanned_devices
    show_scanned_devices = _scanned_devices
    with open('scanned_devices.json', 'w') as f:
        json.dump(_scanned_devices, f)

# 唤醒设备
def wake_device(mac_address):
    # 使用 wakeonlan 库来唤醒设备
    # 需要确保已安装 wakeonlan 库（pip install wakeonlan）
    wakeonlan.send_magic_packet(mac_address)

# 扫描内网设备
def scan_devices():
    # 使用 nmap 库来扫描内网设备
    # 需要确保已安装 nmap 库（pip install python-nmap）
    nm = nmap.PortScanner()
    print("begin scan")
    ret = nm.scan(hosts=hosts, arguments='-sn')
    print("finish scan")

    scanned_devices = []
    for host in nm.all_hosts():
        print(ret["scan"][host])
        hostnames = ret["scan"][host]["hostnames"][0]["name"]
        if hostnames == "":
            hostnames = "unknown"
        mac = ret["scan"][host]["addresses"].get("mac", "")
        scanned_devices.append({
            'ip': host, 
            'hostnames': hostnames,
            'addresses': ret["scan"][host]["addresses"]["ipv4"],
            'mac': mac,
            'vendor': ret["scan"][host]["vendor"].get(mac, ""),
            'status': ret["scan"][host]["status"]["state"],
        })

    return scanned_devices

# 主页
@app.route('/')
def index_():
    return redirect(url_for('index'))

@app.route(urlprefix)
# @app.route('/')
def index():
    devices = load_devices()
    show_scanned_devices = load_scanned_devices()
    return render_template('index.html', devices=devices, show_scanned_devices=show_scanned_devices, urlprefix=urlprefix)

# 添加设备
# @app.route('/add_device', methods=['POST'])
@app.route(urlprefix + '/add_device', methods=['POST'])
def add_device():
    device_name = request.form['device_name']
    mac_address = request.form['mac_address']
    macth_mac = re.match(r"^\s*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\s*$", mac_address)
    print(macth_mac, not macth_mac)
    if not macth_mac:
        return '<script> alert("MAC 格式不正确"); window.location="/a520"</script>'
    
    devices.append({'device_name': device_name, 'mac_address': mac_address})
    save_devices(devices)
    return redirect(url_for('index'))
    return render_template('index.html', devices=devices, show_scanned_devices=show_scanned_devices, urlprefix=urlprefix)

# 唤醒设备
# @app.route('/wake_device/<mac_address>', methods=['POST'])
@app.route(urlprefix + '/wake_device/<mac_address>', methods=['POST'])
def wake_device_route(mac_address):
    wake_device(mac_address)
    return redirect(url_for('index'))
    return '', 204

# 修改设备
# @app.route('/edit_device/<mac_address>', methods=['POST'])
@app.route(urlprefix + '/edit_device/<mac_address>', methods=['POST'])
def edit_device(mac_address):
    new_device_name = request.form['new_device_name']
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    if device:
        device['device_name'] = new_device_name
        save_devices(devices)
    return redirect(url_for('index'))
    return render_template('index.html', devices=devices, show_scanned_devices=show_scanned_devices, urlprefix=urlprefix)

# 删除设备
# @app.route('/delete_device/<mac_address>', methods=['POST'])
@app.route(urlprefix + '/delete_device/<mac_address>', methods=['POST'])
def delete_device(mac_address):
    global devices
    devices = [d for d in devices if d['mac_address'] != mac_address]
    save_devices(devices)
    return redirect(url_for('index'))
    return render_template('index.html', devices=devices, show_scanned_devices=show_scanned_devices, urlprefix=urlprefix)

# 扫描设备
# @app.route('/scan_devices', methods=['POST'])
@app.route(urlprefix + '/scan_devices', methods=['POST'])
def scan_devices_route():
    print("scan_devices_route")
    show_scanned_devices = scan_devices()
    save_scanned_devices(show_scanned_devices)

    data = json.dumps(show_scanned_devices, indent=4,ensure_ascii=False, sort_keys=False,separators=(',', ':'))
    print(data)

    return redirect(url_for('index'))
    # return render_template('index.html', devices=devices, show_scanned_devices=show_scanned_devices, urlprefix=urlprefix)


if __name__ == '__main__':
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0")