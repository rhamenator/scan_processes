# Process Monitor

This Python script actively monitors running processes on your system, flagging those that exhibit high resource usage (CPU, memory, or disk) or establish network connections. It records these events in an SQLite database for further analysis.

## Features

- **Resource Monitoring:** Tracks CPU usage, memory consumption, and disk write activity of processes.
- **Network Connection Tracking:** Logs details about network connections established by processes, including remote IP addresses and ports.
- **SQLite Database:** Stores events in a local SQLite database for easy querying and analysis.
- **Real-time Monitoring:** Continuously monitors processes and reports events as they occur.

## Requirements

- Python 3.x
- `psutil`
- `time`
- `socket`
- `ipaddress`
- `sqlite3`

## Usage

1. Install the required libraries using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the script:

    ```bash
    python scan_processes.py
    ```

3. Monitor output: The script will display a summary of investigated processes and connections to the console. The script is designed for continuous monitoring. Press ```Ctrl+C``` to stop it.

4. Access the database: The log containing events that triggered an investigation of a process are contained in an SQLite database called process_monitor.db You can use a tool like DB Browser or any other SQLite-compatible database browser to query and analyze the data.

## Database Structure

The script creates an SQLite database named `process_monitor.db` with a table `process_events` having the following columns:

- `timestamp`: Timestamp of the event
- `pid`: Process ID
- `process_name`: Process name
- `event_type`: Type of event (High CPU, High Memory, High Disk Write, Network Connection)
- `resource_usage`: Resource usage value (if applicable)
- `open_files`: Comma-separated list of open files (if applicable)
- `ip_connection_type`: Type of IP connection (TCP, UDP, Unknown)
- `ip_connection_status`: Status of IP connection (ESTABLISHED, etc.)
- `local_address`: Local IP address and port
- `remote_address`: Remote IP address and port
- `remote_hostname`: Remote hostname (if resolved)
- `ip_address_type`: Type of IP address (Public, Private, Loopback, etc.)
- `connection_family`: Connection family (IPv4, IPv6, etc.)

## Customization

- wait_time: Adjust the interval (in seconds) between process scans.
- Resource Thresholds: Modify the thresholds for high CPU, memory, and disk usage to suit your environment.

## Important Notes

- The script requires administrative/root privileges to access detailed process information and network connections.
- Be cautious when terminating processes based on the script's output. Ensure you understand the implications before taking any action.
- The script is designed for continuous monitoring. Press Ctrl+C to stop it.

## Disclaimer

- This script is intended for educational and monitoring purposes. Use it responsibly and respect privacy and security considerations.
- The script might require administrative or root privileges to access certain process and network information.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.