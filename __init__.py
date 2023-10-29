import ctypes
import itertools
import os
import platform
import signal
import sys
import subprocess
import threading
from collections import deque
import re
from time import sleep as sleep_
from math import floor

compiledregex = re.compile(r"^[A-Z]:\\", flags=re.I)
from functools import cache

iswindows = "win" in platform.platform().lower()
if iswindows:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    creationflags = subprocess.CREATE_NO_WINDOW
    invisibledict = {
        "startupinfo": startupinfo,
        "creationflags": creationflags,
        "start_new_session": True,
    }
    from ctypes import wintypes

    windll = ctypes.LibraryLoader(ctypes.WinDLL)
    user32 = windll.user32
    kernel32 = windll.kernel32
    GetExitCodeProcess = windll.kernel32.GetExitCodeProcess
    CloseHandle = windll.kernel32.CloseHandle
    GetExitCodeProcess.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_ulong),
    ]
    CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    GetExitCodeProcess.restype = ctypes.c_int
    CloseHandle.restype = ctypes.c_int

    GetWindowRect = user32.GetWindowRect
    GetClientRect = user32.GetClientRect
    _GetShortPathNameW = kernel32.GetShortPathNameW
    _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _GetShortPathNameW.restype = wintypes.DWORD
else:
    invisibledict = {}


def is_process_alive(pid):
    if re.search(
        b"ProcessId=" + str(pid).encode() + rb"\s*$",
        subprocess.run(
            "wmic process list FULL", capture_output=True, **invisibledict
        ).stdout,
        flags=re.MULTILINE,
    ):
        return True
    return False


def index_all(s, n):
    indototal = 0
    allindex = []

    while True:
        try:
            indno = s[indototal:].index(n)
            indototal += indno + 1
            allindex.append(indototal - 1)
        except ValueError:
            break
    return allindex


@cache
def convert_path_to_short(string):
    if not iswindows:
        return string

    l2 = [q - 1 for q in index_all(s=string, n=":\\")]
    addtostring = []
    try:
        result1 = list_split(l=string, indices_or_sections=l2)
    except Exception:
        return string
    try:
        for string in result1:
            if not compiledregex.search(string):
                addtostring.append(string)
                continue
            activepath = ""
            lastfoundpath = ""
            lastfoundpath_end = 0
            for ini, letter in enumerate(string):
                activepath += letter
                if ini < 3:
                    continue
                if letter.isspace():
                    continue
                if os.path.exists(activepath):
                    lastfoundpath = activepath
                    lastfoundpath_end = ini
            if lastfoundpath:
                addtostring.append(get_short_path_name(lastfoundpath))
                addtostring.append(string[lastfoundpath_end + 1 :])
            else:
                addtostring.append(string)

        return "".join(addtostring)
    except Exception:
        return string


def list_split(l, indices_or_sections):
    Ntotal = len(l)
    try:
        Nsections = len(indices_or_sections) + 1
        div_points = [0] + list(indices_or_sections) + [Ntotal]
    except TypeError:
        Nsections = int(indices_or_sections)
        if Nsections <= 0:
            raise ValueError("number sections must be larger than 0.") from None
        Neach_section, extras = divmod(Ntotal, Nsections)
        section_sizes = (
            [0] + extras * [Neach_section + 1] + (Nsections - extras) * [Neach_section]
        )
        div_points = []
        new_sum = 0
        for i in section_sizes:
            new_sum += i
            div_points.append(new_sum)

    sub_arys = []
    lenar = len(l)
    for i in range(Nsections):
        st = div_points[i]
        end = div_points[i + 1]
        if st >= lenar:
            break
        sub_arys.append((l[st:end]))

    return sub_arys


@cache
def get_short_path_name(long_name):
    try:
        if not iswindows:
            return long_name
        output_buf_size = 4096
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        return output_buf.value
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        return long_name


def sleep(secs):
    try:
        if secs == 0:
            return
        maxrange = 50 * secs
        if isinstance(maxrange, float):
            sleeplittle = floor(maxrange)
            sleep_((maxrange - sleeplittle) / 50)
            maxrange = int(sleeplittle)
        if maxrange > 0:
            for _ in range(maxrange):
                sleep_(0.016)

    except KeyboardInterrupt:
        return


def killthread(threadobject):
    # based on https://pypi.org/project/kthread/
    if not threadobject.is_alive():
        return True
    tid = -1
    for tid1, tobj in threading._active.items():
        if tobj is threadobject:
            tid = tid1
            break
    if tid == -1:
        sys.stderr.write(f"{threadobject} not found")
        return False
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), ctypes.py_object(SystemExit)
    )
    if res == 0:
        return False
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        return False
    return True


def index_all(s, n):
    indototal = 0
    allindex = []

    while True:
        try:
            indno = s[indototal:].index(n)
            indototal += indno + 1
            allindex.append(indototal - 1)
        except ValueError:
            break
    return allindex


def send_ctrl_commands(pid, command=0):
    # CTRL_C_EVENT = 0
    # CTRL_BREAK_EVENT = 1
    # CTRL_CLOSE_EVENT = 2
    # CTRL_LOGOFF_EVENT = 3
    # CTRL_SHUTDOWN_EVENT = 4
    if iswindows:
        commandstring = r"""import ctypes, sys; CTRL_C_EVENT, CTRL_BREAK_EVENT, CTRL_CLOSE_EVENT, CTRL_LOGOFF_EVENT, CTRL_SHUTDOWN_EVENT = 0, 1, 2, 3, 4; kernel32 = ctypes.WinDLL("kernel32", use_last_error=True); (lambda pid, cmdtosend=CTRL_C_EVENT: [kernel32.FreeConsole(), kernel32.AttachConsole(pid), kernel32.SetConsoleCtrlHandler(None, 1), kernel32.GenerateConsoleCtrlEvent(cmdtosend, 0), sys.exit(0) if isinstance(pid, int) else None])(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else None) if __name__ == '__main__' else None"""
        subprocess.Popen(
            [sys.executable, "-c", commandstring, str(pid), str(command)],
            **invisibledict,
        )  # Send Ctrl-C
    else:
        os.kill(pid, signal.SIGINT)


class dequeslice(deque):
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.__class__(
                itertools.islice(self, index.start, index.stop, index.step)
            )
        return deque.__getitem__(self, index)


class SubProcInputOutput:
    r"""
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

    """

    def __init__(
        self,
        cmd,
        invisible=False,
        print_stdout=True,
        print_stderr=True,
        limit_stdout=None,
        limit_stderr=None,
        limit_stdin=None,
        convert_to_83=True,
        separate_stdout_stderr_with_list=True,
        **kwargs,
    ):
        r"""
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
        """
        if convert_to_83 and iswindows:
            newcommand = []
            if isinstance(cmd, (list, tuple)):
                for element in cmd:
                    if os.path.exists(element):
                        newcommand.append(get_short_path_name(element))
                    else:
                        newcommand.append(element)
            elif isinstance(cmd, str):
                convert_path_to_short(cmd)
            cmd = newcommand

        self.cmd = cmd
        self.separate_stdout_with_list = separate_stdout_stderr_with_list
        self.separate_stderr_with_list = separate_stdout_stderr_with_list
        self.lockobject = threading.Lock()
        if self.separate_stdout_with_list:
            self.stdout = dequeslice([[]], maxlen=limit_stdout)
        else:
            self.stdout = dequeslice([], maxlen=limit_stdout)
        if self.separate_stderr_with_list:
            self.stderr = dequeslice([[]], maxlen=limit_stderr)
        else:
            self.stderr = dequeslice([], maxlen=limit_stderr)

        self.stdin = dequeslice([cmd], maxlen=limit_stdin)
        self.print_stdout = print_stdout
        self.print_stderr = print_stderr
        kwargs.update(
            {
                "stdout": subprocess.PIPE,
                "stdin": subprocess.PIPE,
                "stderr": subprocess.PIPE,
            }
        )
        if invisible:
            kwargs.update(invisibledict)
        kwargs.update({"bufsize": 0})
        self.p = subprocess.Popen(cmd, **kwargs)
        self._t_stdout = threading.Thread(target=self._read_stdout)
        self._t_stderr = threading.Thread(target=self._read_stderr)
        self._t_stdout.start()
        self._t_stderr.start()

    def _close_pipes(self, pipe):
        try:
            getattr(self.p, pipe).close()
        except Exception as e:
            sys.stderr.write(f"{e}\n")

    def _close_proc(self):
        try:
            self.p.terminate()
        except Exception as e:
            sys.stderr.write(f"{e}\n")

    def kill_proc(
        self, press_ctrl_c=True, sleep_after_pipes=1, sleep_after_proc=1, shellkill=True
    ):
        killthread(self._t_stdout)
        killthread(self._t_stderr)
        if press_ctrl_c:
            try:
                send_ctrl_commands(self.p.pid, 0)
            except KeyboardInterrupt:
                pass
        close_stdoutpipe = threading.Thread(target=lambda: self._close_pipes("stdout"))
        close_stderrpipe = threading.Thread(target=lambda: self._close_pipes("stdin"))
        close_stdinpipe = threading.Thread(target=lambda: self._close_pipes("stderr"))
        close_stdoutpipe.start()
        close_stderrpipe.start()
        close_stdinpipe.start()
        sleep(sleep_after_pipes)
        close_proc = threading.Thread(target=self._close_proc)
        close_proc.start()
        sleep(sleep_after_proc)
        if iswindows:
            if shellkill and self.isalive():
                _ = subprocess.Popen(
                    f"taskkill /F /PID {self.p.pid} /T", **invisibledict
                )
        for thr in [close_stdoutpipe, close_stderrpipe, close_stdinpipe, close_proc]:
            try:
                killthread(thr)
            except Exception as e:
                sys.stderr.write(f"{e}\n")
                sys.stderr.flush()

    def _read_stdout(self):
        for l in iter(self.p.stdout.readline, b""):
            try:
                if self.separate_stdout_with_list:
                    self.stdout[-1].append(l)
                else:
                    self.stdout.append(l)
                if self.print_stdout:
                    sys.stdout.write(f'{l.decode("utf-8", "backslashreplace")}')
                    sys.stdout.flush()

            except Exception:
                break

    def _read_stderr(self):
        for l in iter(self.p.stderr.readline, b""):
            try:
                if self.separate_stderr_with_list:
                    self.stderr[-1].append(l)
                else:
                    self.stderr.append(l)
                if self.print_stderr:
                    sys.stderr.write(f'{l.decode("utf-8", "backslashreplace")}')
                    sys.stderr.flush()
            except Exception:
                break

    def disable_stderr_print(self):
        self.print_stderr = False
        return self

    def disable_stdout_print(self):
        self.print_stdout = False
        return self

    def enable_stderr_print(self):
        self.print_stderr = True
        return self

    def enable_stdout_print(self):
        self.print_stdout = True
        return self

    def write(self, cmd, wait_to_complete=0.1, convert_to_83=False):
        if convert_to_83:
            cmd = convert_path_to_short(cmd)
        if isinstance(cmd, str):
            cmd = cmd.encode()
        if not cmd.endswith(b"\n"):
            cmd = cmd + b"\n"
        self.lockobject.acquire()
        stderrlist = []
        stdoutlist = []
        oldsizestderr = len(self.stderr)
        oldsizestdout = len(self.stdout)
        substractstderr = len(self.stderr)
        substractstdout = len(self.stdout)

        if self.separate_stderr_with_list:
            self.stderr.append(stderrlist)
            oldsizestderr = 0

        if self.separate_stdout_with_list:
            self.stdout.append(stdoutlist)
            oldsizestdout = 0

        self.p.stdin.write(cmd)
        try:
            self.p.stdin.flush()
        except OSError as e:
            sys.stderr.write("Connection broken")
            raise e
        self.lockobject.release()
        self.stdin.append(cmd)
        try:
            if wait_to_complete:
                while True:
                    sleep(wait_to_complete)

                    if not self.separate_stderr_with_list:
                        stdoutlist.clear()
                        stderrlist.clear()
                        oldsizestdout = len(self.stdout) - substractstdout
                        oldsizestderr = len(self.stderr) - substractstderr
                        sleep(wait_to_complete)

                        stdoutlist.extend(self.stdout[substractstdout:])
                        stderrlist.extend(self.stderr[substractstderr:])

                    newsizestdout = len(stdoutlist)
                    newsizestderr = len(stderrlist)
                    if newsizestdout > oldsizestdout:
                        oldsizestdout = newsizestdout
                        continue
                    if newsizestderr > oldsizestderr:
                        oldsizestderr = newsizestderr
                        continue

                    break
        except KeyboardInterrupt:
            send_ctrl_commands(self.p.pid, 0)
        return [stdoutlist, stderrlist]

    def get_lock(self):
        self.lockobject.acquire()
        return self

    def release_lock(self):
        self.lockobject.release()
        return self

    def flush_stdout(self):
        try:
            self.get_lock()
            self.stdout.clear()
        finally:
            try:
                self.release_lock()
            except Exception:
                pass
        return self

    def flush_stderr(self):
        try:
            self.get_lock()
            self.stderr.clear()
        finally:
            try:
                self.release_lock()
            except Exception:
                pass
        return self

    def flush_stdin(self):
        try:
            self.get_lock()
            self.stdin.clear()
        finally:
            try:
                self.release_lock()
            except Exception:
                pass
        return self

    def flush_all_pipes(self):
        self.stdin.clear()
        self.stdout.clear()
        self.stderr.clear()

    def send_ctrl_c(self):
        send_ctrl_commands(self.p.pid, command=0)
        return self

    def send_ctrl_break(self):
        send_ctrl_commands(self.p.pid, command=1)
        return self

    def send_ctrl_close(self):
        send_ctrl_commands(self.p.pid, command=2)
        return self

    def send_ctrl_logoff(self):
        send_ctrl_commands(self.p.pid, command=3)
        return self

    def send_ctrl_shutdown(self):
        send_ctrl_commands(self.p.pid, command=4)
        return self

    def isalive(self):
        if iswindows:
            return is_process_alive(self.p.pid)
        else:
            raise NotImplementedError
