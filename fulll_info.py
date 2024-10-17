import win32net
import win32netcon
import enum 
import json
import subprocess
import platform
import psutil
import socket
import datetime
import GPUtil
import cpuinfo
import winreg
import traceback
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import ctypes
import sys
import os

class SystemInformation:
    def __init__(self):
        self.system_info = self.get_system_information()
        self.boot_time = self.get_boot_time()
        self.cpu_info = self.get_cpu_information()
        self.memory_info = self.get_memory_information()
        self.disk_info = self.get_disk_information()
        self.network_info = self.get_network_information()
        self.gpu_info = self.get_gpu_information()
        self.bios_info = self.get_bios_information()
        self.software_list = self.get_installed_apps()
        self.product_key = self.get_original_product_key()
        self.logs = self.get_logs()
        self.user_list = self.listusers()

    def get_system_information(self):
        output = subprocess.check_output(['systeminfo'], shell=True).decode('utf-8')
        system_info = {}

        for line in output.splitlines():
            if 'Processor(s)' in line:
                break
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                if key != 'BIOS Version':
                    system_info[key] = value

        system_info['Processor Name'] = cpuinfo.get_cpu_info()['brand_raw']
        return system_info

    def get_boot_time(self):
        boot_time = psutil.boot_time()
        boot_time_formatted = datetime.datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        return boot_time_formatted

    def get_cpu_information(self):
        cpu_info = {}
        cpu_info['Physical cores'] = psutil.cpu_count(logical=False)
        cpu_info['Total cores'] = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_info['Max Frequency'] = f"{cpu_freq.max:.2f}Mhz"
        cpu_info['Min Frequency'] = f"{cpu_freq.min:.2f}Mhz"
        cpu_info['Current Frequency'] = f"{cpu_freq.current:.2f}Mhz"
        cpu_percent = psutil.cpu_percent(percpu=True)
        cpu_info['CPU Usage Per Core'] = {f'Core {i}': f'{cpu_percent[i]}%' for i in range(len(cpu_percent))}
        cpu_info['Total CPU Usage'] = f"{psutil.cpu_percent()}%"
        return cpu_info

    def get_memory_information(self):
        memory_info = {}
        memory = psutil.virtual_memory()
        memory_info['Total'] = f"{memory.total / (1024 ** 3):.2f}GB"
        memory_info['Available'] = f"{memory.available / (1024 ** 3):.2f}GB"
        memory_info['Used'] = f"{memory.used / (1024 ** 3):.2f}GB"
        memory_info['Percentage'] = f"{memory.percent}%"
        swap = psutil.swap_memory()
        memory_info['SWAP'] = {
            'Total': f"{swap.total / (1024 ** 3):.2f}GB",
            'Free': f"{swap.free / (1024 ** 3):.2f}GB",
            'Used': f"{swap.used / (1024 ** 3):.2f}GB",
            'Percentage': f"{swap.percent}%"
        }
        return memory_info

    def get_disk_information(self):
        disk_info = {}
        partitions = psutil.disk_partitions()
        for partition in partitions:
            partition_info = {}
            partition_info['Mountpoint'] = partition.mountpoint
            partition_info['File system type'] = partition.fstype
            partition_usage = psutil.disk_usage(partition.mountpoint)
            partition_info['Total Size'] = f"{partition_usage.total / (1024 ** 3):.2f}GB"
            partition_info['Used'] = f"{partition_usage.used / (1024 ** 3):.2f}GB"
            partition_info['Free'] = f"{partition_usage.free / (1024 ** 3):.2f}GB"
            partition_info['Percentage'] = f"{partition_usage.percent}%"
            disk_info[partition.device] = partition_info
        return disk_info

    def get_network_information(self):
        network_info = {}
        interfaces = psutil.net_if_addrs()
        for interface_name, interface_addresses in interfaces.items():
            interface_info = {}
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    interface_info['IP Address'] = address.address
                    interface_info['Netmask'] = address.netmask
                    interface_info['Broadcast IP'] = address.broadcast
                elif address.family == psutil.AF_LINK:
                    interface_info['MAC Address'] = address.address
                    interface_info['Broadcast MAC'] = address.broadcast
            network_info[interface_name] = interface_info

        bytes_sent = psutil.net_io_counters().bytes_sent
        bytes_received = psutil.net_io_counters().bytes_recv
        network_info['Total Bytes Sent'] = {
            'Bytes Sent': f"{bytes_sent / (1024 ** 2):.2f}MB"
        }
        network_info['Total Bytes Received'] = {
            'Bytes Received': f"{bytes_received / (1024 ** 2):.2f}MB"
        }
        return network_info

    def get_gpu_information(self):
        gpu_info = {}
        gpus = GPUtil.getGPUs()
        for i, gpu in enumerate(gpus):
            gpu_info[f"GPU {i + 1}"] = {
                'ID': gpu.id,
                'Name': gpu.name,
                'UUID': gpu.uuid,
                'Load': f"{gpu.load * 100}%",
                'Memory Total': f"{gpu.memoryTotal}MB",
                'Memory Used': f"{gpu.memoryUsed}MB",
                'Memory Free': f"{gpu.memoryFree}MB",
                'Temperature': f"{gpu.temperature} °C",
                'Driver': gpu.driver
            }
        return gpu_info

    def get_bios_information(self):
        bios_info = {}
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output(['powershell', 'Get-WmiObject', 'win32_bios'], shell=True, universal_newlines=True).strip()
                lines = output.split('\n')
                for line in lines:
                    key, value = map(str.strip, line.split(':', 1))
                    bios_info[key] = value
            except Exception as e:
                print("Error occurred while getting BIOS information:", e)
        return bios_info

    def get_installed_apps(self):
        sources = [[winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"],
            [winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"],
            [winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"]]

        class ReadMode(enum.Enum):
            KEY = 1
            VALUE = 2

        def read(key, mode):
            i = 0
            while True:
                try:
                    if mode == ReadMode.KEY:
                        yield winreg.EnumKey(key, i)
                    elif mode == ReadMode.VALUE:
                        yield winreg.EnumValue(key, i)
                    i += 1
                except OSError:
                    break

        def readRegistery(keyType, registryKeyPath):
            registry = winreg.ConnectRegistry(None, keyType)
            registryKey = winreg.OpenKey(registry, registryKeyPath)
            for subKeyName in read(registryKey, ReadMode.KEY):
                subKey = winreg.OpenKey(registry, f"{registryKeyPath}\\{subKeyName}")
                values = {}
                for subKeyValue in read(subKey, ReadMode.VALUE):
                    values[subKeyValue[0]] = subKeyValue[1]
                yield values

        apps = {}
        for source in sources:
            for data in readRegistery(source[0], source[1]):
                if "DisplayName" in data:
                    display_name = data["DisplayName"].strip()
                    version = data.get(
                        "DisplayVersion", ""
                    ).strip()  
                    apps[display_name] = version
        return apps

    def get_original_product_key(self):
        try:
            command = subprocess.Popen(["powershell","-ExecutionPolicy","Bypass","-Command","wmic path softwarelicensingservice get OA3xOriginalProductKey"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,)
            output, error = command.communicate()

            if error:
                print(f"Error retrieving product key: {error.decode()}")
                return None

            output_str = output.decode()
            product_key = output_str.split("\n")[1].strip() 

            return product_key
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def get_logs(self):
        logs = {}
        # logtypes = ["System", "Application"]
        logtypes = ["System", "Application", "Security"]
        basePath = os.path.dirname(os.path.abspath(__file__))
        for logtype in logtypes:
            try:
                log = self.get_event_logs(logtype, basePath)
                logs[logtype] = log
            except Exception as e:
                print(f"Error occurred while processing {logtype} events:", e)
        return logs

    def get_event_logs(self, logtype, logPath):
        print(f"Logging {logtype} events")
        logs = []

        start_time = datetime.datetime.now() - datetime.timedelta(hours=24)

        hand = win32evtlog.OpenEventLog(None, logtype)
        total = win32evtlog.GetNumberOfEventLogRecords(hand)
        print(f"Total events in {logtype} = {total}")

        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(hand, flags, 0)

        evt_dict = {
            win32con.EVENTLOG_AUDIT_FAILURE: "EVENTLOG_AUDIT_FAILURE",
            win32con.EVENTLOG_AUDIT_SUCCESS: "EVENTLOG_AUDIT_SUCCESS",
            win32con.EVENTLOG_INFORMATION_TYPE: "EVENTLOG_INFORMATION_TYPE",
            win32con.EVENTLOG_WARNING_TYPE: "EVENTLOG_WARNING_TYPE",
            win32con.EVENTLOG_ERROR_TYPE: "EVENTLOG_ERROR_TYPE",
        }

        try:
            events = 1
            while events:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                for ev_obj in events:
                    
                    event_time = datetime.datetime.strptime(ev_obj.TimeGenerated.Format(), "%a %b %d %H:%M:%S %Y")
                    
                    if event_time >= start_time:
                        log_entry = {}
                        log_entry["event_date_time"] = ev_obj.TimeGenerated.Format()
                        log_entry["event_id"] = str(winerror.HRESULT_CODE(ev_obj.EventID))
                        log_entry["computer"] = str(ev_obj.ComputerName)
                        log_entry["category"] = ev_obj.EventCategory
                        log_entry["record"] = ev_obj.RecordNumber
                        log_entry["source"] = str(ev_obj.SourceName)
                        log_entry["event_type"] = evt_dict.get(ev_obj.EventType, "unknown")
                        log_entry["message"] = win32evtlogutil.SafeFormatMessage(ev_obj, logtype)
                        logs.append(log_entry)
        except Exception as e:
            print(traceback.print_exc())
            print(f"Error: {e}")

        return logs
    
    def listusers(self,server=None):
        level = 0
        filter = win32netcon.FILTER_NORMAL_ACCOUNT
        resume_handle = 0
        user_list = []
        while True:
            result = win32net.NetUserEnum(server, level, filter, resume_handle)
            user_list += [user["name"] for user in result[0]]
            resume_handle = result[2]
            if resume_handle == 0:
                break
        user_list.sort()
        users = json.dumps(user_list)
        users = json.loads(users)
        return users

    def get_combined_info(self):
        combined_info = {
            'System Information': self.system_info,
            'Boot Time': self.boot_time,
            'CPU Information': self.cpu_info,
            'Memory Information': self.memory_info,
            'Disk Information': self.disk_info,
            'Network Information': self.network_info,
            'GPU Information': self.gpu_info,
            'BIOS Information': self.bios_info,
            'User List':self.user_list,
            'Software List': self.software_list,
            'Product Key': self.product_key,
            'Logs': self.logs
        }
        host_name  = combined_info['System Information']['Host Name']
        file_name = host_name + '.json'
        return combined_info,file_name

if __name__ == "__main__":
    system_info = SystemInformation()
    combined_info = system_info.get_combined_info()


