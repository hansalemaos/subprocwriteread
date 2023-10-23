# A class for interacting with subprocesses and capturing their input and output streams

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install subprocwriteread

```python
SubProcInputOutput - A class for interacting with subprocesses and capturing their input and output streams.

This class allows you to run external commands as subprocesses and provides methods to read, write, and control
the standard input, standard output, and standard error streams. It also supports handling and printing of the
captured data.



Args:
    cmd (str or list): The command to run as a subprocess. If it's a string, the command is passed to the system shell.
        If it's a list, the command is executed directly.
    invisible (bool, optional): If True, the subprocess runs invisibly without showing its console window (Windows only).
    print_stdout (bool, optional): If True, capture and print the standard output of the subprocess.
    print_stderr (bool, optional): If True, capture and print the standard error of the subprocess.
    limit_stdout (int, optional): Maximum number of lines to capture in standard output.
    limit_stderr (int, optional): Maximum number of lines to capture in standard error.
    limit_stdin (int, optional): Maximum number of lines to capture in standard input.
    convert_to_83 (bool, optional): If True, convert long file paths to their 8.3 format (Windows only).
    separate_stdout_stderr_with_list (bool, optional): If True, separate standard output and standard error
        into lists; otherwise, use a single string for each.

Attributes:
    cmd (str or list): The command passed to the subprocess.
    stdout (deque): Captured standard output.
    stderr (deque): Captured standard error.
    stdin (deque): Captured standard input.
    print_stdout (bool): Indicates whether standard output is printed.
    print_stderr (bool): Indicates whether standard error is printed.

Methods:
    - kill_proc(press_ctrl_c=True, sleep_after_pipes=1, sleep_after_proc=1, shellkill=True):
        Terminate the subprocess, optionally sending a Ctrl+C signal and forcefully killing it.

    - disable_stderr_print(): Disable printing of standard error.
    - disable_stdout_print(): Disable printing of standard output.
    - enable_stderr_print(): Enable printing of standard error.
    - enable_stdout_print(): Enable printing of standard output.
    - write(cmd, wait_to_complete=0.1, convert_to_83=False): Write data to the standard input of the subprocess.

    - get_lock(): Acquire a lock to protect critical sections.
    - release_lock(): Release the lock acquired with 'get_lock()'.
    - flush_stdout(): Clear the captured standard output.
    - flush_stderr(): Clear the captured standard error.
    - flush_stdin(): Clear the captured standard input.
    - flush_all_pipes(): Clear the captured data from all streams.

    - send_ctrl_c(): Send a Ctrl+C signal to the subprocess.
    - send_ctrl_break(): Send a Ctrl+Break signal to the subprocess.
    - send_ctrl_close(): Send a Ctrl+Close signal to the subprocess.
    - send_ctrl_logoff(): Send a Ctrl+Logoff signal to the subprocess.
    - send_ctrl_shutdown(): Send a Ctrl+Shutdown signal to the subprocess.

    - isalive(): Check if the subprocess is still running (Windows only).

Note:
    Some methods are platform-specific and may not work on non-Windows systems. Make sure to handle platform
    compatibility when using this class.

Example:

from subprocwriteread import SubProcInputOutput

adbexe = r"C:\Android\android-sdk\platform-tools\adb.exe"

self = SubProcInputOutput(
cmd=[adbexe, "-s", "127.0.0.1:5555", "shell"],
invisible=True,
print_stdout=True,
print_stderr=True,
limit_stdout=None,
limit_stderr=None,
limit_stdin=None,
convert_to_83=True,
separate_stdout_stderr_with_list=False,
)
stdout, stderr = self.write("ls")
print(self.isalive())
stdout, stderr = self.write(
"ls -R -i -H -las -s", wait_to_complete=0.2, convert_to_83=False
)
self.disable_stdout_print()
self.write(
'''while true; do
    sleep 1
    echo oioioi
done
''',
wait_to_complete=0,
)
self.kill_proc(
press_ctrl_c=True, sleep_after_pipes=1, sleep_after_proc=1, shellkill=True
)
self.flush_all_pipes()
print(self.isalive())


Methods:
    - kill_proc(press_ctrl_c=True, sleep_after_pipes=1, sleep_after_proc=1, shellkill=True):
        Terminate the subprocess, optionally sending a Ctrl+C signal and forcefully killing it.

        Args:
            press_ctrl_c (bool, optional): Send a Ctrl+C signal to the subprocess before terminating it.
            sleep_after_pipes (float, optional): Time to sleep after closing input and output pipes.
            sleep_after_proc (float, optional): Time to sleep after terminating the subprocess.
            shellkill (bool, optional): If True (Windows only), use a shell command to forcefully kill the subprocess.

    - disable_stderr_print():
        Disable printing of standard error.

    - disable_stdout_print():
        Disable printing of standard output.

    - enable_stderr_print():
        Enable printing of standard error.

    - enable_stdout_print():
        Enable printing of standard output.

    - write(cmd, wait_to_complete=0.1, convert_to_83=False):
        Write data to the standard input of the subprocess.

        Args:
            cmd (str or bytes): The data to write to the subprocess's standard input.
            wait_to_complete (float, optional): Time to wait after writing data before returning.
            convert_to_83 (bool, optional): If True, convert long file paths to their 8.3 format (Windows only).

        Returns:
            list: A list containing lists of standard output and standard error data, size might change after executing if separate_stdout_stderr_with_list is True

    - get_lock():
        Acquire a lock to protect critical sections.

        Returns:
            self: The current instance with the lock acquired.

    - release_lock():
        Release the lock acquired with 'get_lock()'.

        Returns:
            self: The current instance with the lock released.

    - flush_stdout():
        Clear the captured standard output.

        Returns:
            self: The current instance with standard output cleared.

    - flush_stderr():
        Clear the captured standard error.

        Returns:
            self: The current instance with standard error cleared.

    - flush_stdin():
        Clear the captured standard input.

        Returns:
            self: The current instance with standard input cleared.

    - flush_all_pipes():
        Clear the captured data from all streams.

    - send_ctrl_c():
        Send a Ctrl+C signal to the subprocess.

        Returns:
            self: The current instance after sending the Ctrl+C signal.

    - send_ctrl_break():
        Send a Ctrl+Break signal to the subprocess.

        Returns:
            self: The current instance after sending the Ctrl+Break signal.

    - send_ctrl_close():
        Send a Ctrl+Close signal to the subprocess.

        Returns:
            self: The current instance after sending the Ctrl+Close signal.

    - send_ctrl_logoff():
        Send a Ctrl+Logoff signal to the subprocess.

        Returns:
            self: The current instance after sending the Ctrl+Logoff signal.

    - send_ctrl_shutdown():
        Send a Ctrl+Shutdown signal to the subprocess.

        Returns:
            self: The current instance after sending the Ctrl+Shutdown signal.

    - isalive():
        Check if the subprocess is still running (Windows only).

        Returns:
            bool: True if the subprocess is running, False otherwise.
```