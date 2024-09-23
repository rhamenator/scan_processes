import psutil
import time
import socket
import ipaddress
import sqlite3

wait_time = 10
# Parameters for detection
high_cpu_threshold = 80  # Percentage
high_memory_threshold = 70  # Percentage
high_disk_threshold = 50  # MB/s
connection_count = 0

families = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    socket.AF_APPLETALK: 'AppleTalk',
    socket.AF_BLUETOOTH: 'Bluetooth',
    socket.AF_DECnet: 'DECnet',
    socket.AF_HYPERV: 'HyperV',
    socket.AF_IPX: 'IPX',
    socket.AF_IRDA: 'IRDA',
    socket.AF_LINK: 'Link',
    socket.AF_SNA: 'SNA',
    socket.AF_UNSPEC: 'Unspecified',
}

# Create or connect to the SQLite database
conn = sqlite3.connect('process_monitor.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS process_events (
        timestamp TEXT,
        pid INTEGER,
        process_name TEXT,
        event_type TEXT,
        resource_usage REAL,
        open_files TEXT,
        ip_connection_type TEXT,
        ip_connection_status TEXT,
        local_address TEXT,
        local_port TEXT,
        remote_address TEXT,
        remote_port TEXT,
        remote_hostname TEXT,
        ip_address_type TEXT,
        connection_family TEXT
    )
''')
conn.commit()

def monitor_processes():
    process_count = 0
  
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
        # Check for high resource usage
        if proc.info['cpu_percent'] > high_cpu_threshold:
            insert_event(proc, "High CPU", proc.info['cpu_percent'])
            process_count +=1
            investigate_process(proc, process_count)

        if proc.info['memory_percent'] > high_memory_threshold:
            insert_event(proc, "High Memory", proc.info['memory_percent'])
            process_count +=1
            investigate_process(proc, process_count)

        if proc.info['io_counters'].write_bytes / 1024 / 1024 > high_disk_threshold:  # Convert bytes to MB
            insert_event(proc, "High Disk Write", proc.info['io_counters'].write_bytes / 1024 / 1024)
            process_count +=1
            investigate_process(proc, process_count)

def investigate_process(proc, process_count):
    global connection_count
    try:
        open_files = ", ".join([file.path for file in proc.open_files()]) if proc.open_files() else "None"
        # Get network connections
        connections = [conn for conn in psutil.net_connections() if conn.pid == proc.info['pid']]
        for conn in connections:
            connection_count += 1
            try:
                remote_ip = conn.raddr.ip if hasattr(conn.raddr, 'ip') else (conn.raddr[0] if isinstance(conn.raddr, tuple) and len(conn.raddr) > 0 else '')
                remote_port = conn.raddr.port if hasattr(conn.raddr, 'port') else (conn.raddr[1] if isinstance(conn.raddr, tuple) and len(conn.raddr) > 1 else '')
                connection_family = families.get(conn.family, 'Other')
                ip_connection_type = get_connection_type(conn)
                ip_connection_status = conn.status
                if len(remote_ip) > 0: 
                    ip_address_type = get_ip_address_type(remote_ip)
                    try:
                        remote_hostname = socket.gethostbyaddr(remote_ip)[0]
                    except socket.herror:
                        remote_hostname = 'Unresolved'
                else:
                    ip_address_type = ''
                    remote_hostname = ''
                    
                insert_event(
                    proc,
                    "Network Connection",
                    None,
                    open_files,
                    ip_connection_type,
                    ip_connection_status,
                    conn.laddr.ip,
                    conn.laddr.port,
                    remote_ip,
                    remote_port,
                    remote_hostname,
                    ip_address_type,
                    connection_family
                )
                print(f'Processes investigated: {process_count}, {connection_count} connections...', end='\r')                
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

def get_connection_type(conn):
    if conn.type == socket.SOCK_STREAM:
        return "TCP"
    elif conn.type == socket.SOCK_DGRAM:
        return "UDP"
    else:
        return "Unknown"

def get_ip_address_type(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback:
            return "Loopback"
        elif ip.is_private:
            return "Private"
        elif ip.is_link_local:
            return "Link-local"
        elif ip.is_unspecified:
            return "Unspecified"
        else:
            return "Public" 
    except ValueError:
        return "Invalid"

def insert_event(proc, event_type, resource_usage, open_files=None, ip_connection_type=None, ip_connection_status=None, local_address=None, local_port=None, remote_address=None, remote_port=None, remote_hostname=None, ip_address_type=None, connection_family=None):
    cursor.execute('''
        INSERT INTO process_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        time.strftime('%Y-%m-%d %H:%M:%S'),
        proc.info['pid'],
        proc.info['name'],
        event_type,
        resource_usage,
        open_files,
        ip_connection_type,
        ip_connection_status,
        local_address,
        local_port,
        remote_address, 
        remote_port,
        remote_hostname,
        ip_address_type,
        connection_family 
    ))
    conn.commit()

# Main execution
try:
    print('Press ctrl+c to exit.')
    while True:
        monitor_processes()
        time.sleep(wait_time)
except KeyboardInterrupt:
    print('SQLite database {conn.} has been created.')
    print("Exiting ...")
finally:
    # Close the database connection when the script ends
    conn.close()