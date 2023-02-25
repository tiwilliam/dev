import fcntl
import io  # readline
import os
import select
import signal
import socket
import struct
import sys
import tty
import unittest
from test.support import reap_children, verbose

from dev import pty

TEST_STRING_1 = b"I wish to buy a fish license.\n"
TEST_STRING_2 = b"For my pet fish, Eric.\n"

try:
    _TIOCGWINSZ = tty.TIOCGWINSZ  # type: ignore
    _TIOCSWINSZ = tty.TIOCSWINSZ  # type: ignore
    _HAVE_WINSZ = True
except AttributeError:
    _HAVE_WINSZ = False

if verbose:

    def debug(msg):
        print(msg)

else:

    def debug(msg):
        ...


# Note that os.read() is nondeterministic so we need to be very careful
# to make the test suite deterministic.  A normal call to os.read() may
# give us less than expected.
#
# Beware, on my Linux system, if I put 'foo\n' into a terminal fd, I get
# back 'foo\r\n' at the other end.  The behavior depends on the termios
# setting.  The newline translation may be OS-specific.  To make the
# test suite deterministic and OS-independent, the functions _readline
# and normalize_output can be used.


def normalize_output(data):
    # Some operating systems do conversions on newline.  We could possibly fix
    # that by doing the appropriate termios.tcsetattr()s.  I couldn't figure out
    # the right combo on Tru64.  So, just normalize the output and doc the
    # problem O/Ses by allowing certain combinations for some platforms, but
    # avoid allowing other differences (like extra whitespace, trailing garbage,
    # etc.)

    # This is about the best we can do without getting some feedback
    # from someone more knowledgable.

    # OSF/1 (Tru64) apparently turns \n into \r\r\n.
    if data.endswith(b'\r\r\n'):
        return data.replace(b'\r\r\n', b'\n')

    if data.endswith(b'\r\n'):
        return data.replace(b'\r\n', b'\n')

    return data


def _readline(fd):
    """Read one line.  May block forever if no newline is read."""
    reader = io.FileIO(fd, mode='rb', closefd=False)
    return reader.readline()


def expectedFailureIfStdinIsTTY(fun):
    # avoid isatty()
    try:
        tty.tcgetattr(pty.STDIN_FILENO)  # type: ignore
        return unittest.expectedFailure(fun)
    except tty.error:  # type: ignore
        ...
    return fun


def _get_term_winsz(fd):
    s = struct.pack("HHHH", 0, 0, 0, 0)
    return fcntl.ioctl(fd, _TIOCGWINSZ, s)


def _set_term_winsz(fd, winsz):
    fcntl.ioctl(fd, _TIOCSWINSZ, winsz)


# Marginal testing of pty suite. Cannot do extensive 'do or fail' testing
# because pty code is not too portable.
class PtyTest(unittest.TestCase):
    def setUp(self):
        old_alarm = signal.signal(signal.SIGALRM, self.handle_sig)
        self.addCleanup(signal.signal, signal.SIGALRM, old_alarm)

        old_sighup = signal.signal(signal.SIGHUP, self.handle_sighup)
        self.addCleanup(signal.signal, signal.SIGHUP, old_sighup)

        # isatty() and close() can hang on some platforms. Set an alarm
        # before running the test to make sure we don't hang forever.
        self.addCleanup(signal.alarm, 0)
        signal.alarm(10)

        # Save original stdin window size
        self.stdin_rows = None
        self.stdin_cols = None
        if _HAVE_WINSZ:
            try:
                stdin_dim = os.get_terminal_size(pty.STDIN_FILENO)
                self.stdin_rows = stdin_dim.lines
                self.stdin_cols = stdin_dim.columns
                old_stdin_winsz = struct.pack("HHHH", self.stdin_rows, self.stdin_cols, 0, 0)
                self.addCleanup(_set_term_winsz, pty.STDIN_FILENO, old_stdin_winsz)
            except OSError:
                ...

    def handle_sig(self, sig, frame):
        self.fail("isatty hung")

    @staticmethod
    def handle_sighup(signum, frame):
        ...

    def test_fork(self):
        debug("calling pty.fork()")
        pid, master_fd = pty.fork()
        self.addCleanup(os.close, master_fd)
        if pid == pty.CHILD:
            # stdout should be connected to a tty.
            if not os.isatty(1):
                debug("Child's fd 1 is not a tty?!")
                os._exit(3)

            # After pty.fork(), the child should already be a session leader.
            # (on those systems that have that concept.)
            debug("In child, calling os.setsid()")
            try:
                os.setsid()
            except OSError:
                # Good, we already were session leader
                debug("Good: OSError was raised.")
                ...
            except AttributeError:
                # Have pty, but not setsid()?
                debug("No setsid() available?")
                ...
            except Exception:
                # We don't want this error to propagate, escaping the call to
                # os._exit() and causing very peculiar behavior in the calling
                # regrtest.py !
                # Note: could add traceback printing here.
                debug("An unexpected error was raised.")
                os._exit(1)
            else:
                debug("os.setsid() succeeded! (bad!)")
                os._exit(2)
            os._exit(4)
        else:
            debug("Waiting for child (%d) to finish." % pid)
            # In verbose mode, we have to consume the debug output from the
            # child or the child will block, causing this test to hang in the
            # parent's waitpid() call.  The child blocks after a
            # platform-dependent amount of data is written to its fd.  On
            # Linux 2.6, it's 4000 bytes and the child won't block, but on OS
            # X even the small writes in the child above will block it.  Also
            # on Linux, the read() will raise an OSError (input/output error)
            # when it tries to read past the end of the buffer but the child's
            # already exited, so catch and discard those exceptions.  It's not
            # worth checking for EIO.
            while True:
                try:
                    data = os.read(master_fd, 80)
                except OSError:
                    break
                if not data:
                    break
                sys.stdout.write(str(data.replace(b'\r\n', b'\n'), encoding='ascii'))

            (pid, status) = os.waitpid(pid, 0)
            res = pty.waitstatus_to_exitcode(status)
            debug("Child (%d) exited with code %d (status %d)." % (pid, res, status))
            if res == 1:
                self.fail("Child raised an unexpected exception in os.setsid()")
            elif res == 2:
                self.fail("pty.fork() failed to make child a session leader.")
            elif res == 3:
                self.fail("Child spawned by pty.fork() did not have a tty as stdout")
            elif res != 4:
                self.fail("pty.fork() failed for unknown reasons.")

    def test_spawn_doesnt_hang(self):
        pty.spawn((sys.executable, '-c', 'print("hi there")'))


class SmallPtyTests(unittest.TestCase):
    """These tests don't spawn children or hang."""

    def setUp(self):
        self.orig_stdin_fileno = pty.STDIN_FILENO
        self.orig_stdout_fileno = pty.STDOUT_FILENO
        self.orig_pty_close = pty.close
        self.orig_pty__copy = pty._copy
        self.orig_pty_fork = pty.fork
        self.orig_pty_select = pty.select
        self.orig_pty_setraw = pty.setraw
        self.orig_pty_tcgetattr = pty.tcgetattr
        self.orig_pty_tcsetattr = pty.tcsetattr
        self.orig_pty_waitpid = pty.waitpid
        self.fds = []  # A list of file descriptors to close.
        self.files = []
        self.select_rfds_lengths = []
        self.select_rfds_results = []
        self.tcsetattr_mode_setting = None

    def tearDown(self):
        pty.STDIN_FILENO = self.orig_stdin_fileno
        pty.STDOUT_FILENO = self.orig_stdout_fileno
        pty.close = self.orig_pty_close
        pty._copy = self.orig_pty__copy
        pty.fork = self.orig_pty_fork
        pty.select = self.orig_pty_select
        pty.setraw = self.orig_pty_setraw
        pty.tcgetattr = self.orig_pty_tcgetattr
        pty.tcsetattr = self.orig_pty_tcsetattr
        pty.waitpid = self.orig_pty_waitpid
        for file in self.files:
            try:
                file.close()
            except OSError:
                ...
        for fd in self.fds:
            try:
                os.close(fd)
            except OSError:
                ...

    def _pipe(self):
        pipe_fds = os.pipe()
        self.fds.extend(pipe_fds)
        return pipe_fds

    def _socketpair(self):
        socketpair = socket.socketpair()
        self.files.extend(socketpair)
        return socketpair

    def _mock_select(self, rfds, wfds, xfds, timeout=0):
        # This will raise IndexError when no more expected calls exist.
        # This ignores the timeout
        self.assertEqual(self.select_rfds_lengths.pop(0), len(rfds))
        return self.select_rfds_results.pop(0), [], []

    def _make_mock_fork(self, pid):
        def mock_fork():
            return (pid, 12)

        return mock_fork

    def _mock_tcsetattr(self, fileno, opt, mode):
        self.tcsetattr_mode_setting = mode

    def test__copy_to_each(self):
        """Test the normal data case on both master_fd and stdin."""
        read_from_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() for s in socketpair]

        # Feed data.  Smaller than PIPEBUF.  These writes will not block.
        os.write(masters[1], b'from master')
        os.write(write_to_stdin_fd, b'from stdin')

        # Expect two select calls, the last one will cause IndexError
        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        self.select_rfds_lengths.append(2)

        with self.assertRaises(IndexError):
            pty._copy(masters[0])

        # Test that the right data went to the right places.
        rfds = select.select([read_from_stdout_fd, masters[1]], [], [], 0)[0]
        self.assertEqual([read_from_stdout_fd, masters[1]], rfds)
        self.assertEqual(os.read(read_from_stdout_fd, 20), b'from master')
        self.assertEqual(os.read(masters[1], 20), b'from stdin')

    def test__copy_eof_on_all(self):
        """Test the empty read EOF case on both master_fd and stdin."""
        read_from_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() for s in socketpair]

        socketpair[1].close()
        os.close(write_to_stdin_fd)

        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        # We expect that both fds were removed from the fds list as they
        # both encountered an EOF before the second select call.
        self.select_rfds_lengths.append(0)

        # We expect the function to return without error.
        self.assertEqual(pty._copy(masters[0]), None)

    def test__restore_tty_mode_normal_return(self):
        """Test that spawn resets the tty mode no when _copy returns normally."""

        # PID 1 is returned from mocked fork to run the parent branch
        # of code
        pty.fork = self._make_mock_fork(1)

        status_sentinel = object()
        pty.waitpid = lambda _1, _2: [None, status_sentinel]
        pty.close = lambda _: None

        pty._copy = lambda _1, _2, _3: None

        mode_sentinel = object()
        pty.tcgetattr = lambda fd: mode_sentinel
        pty.tcsetattr = self._mock_tcsetattr
        pty.setraw = lambda _: None

        self.assertEqual(
            pty.spawn(()), status_sentinel, "pty.waitpid process status not returned by pty.spawn"
        )
        self.assertEqual(
            self.tcsetattr_mode_setting,
            mode_sentinel,
            "pty.tcsetattr not called with original mode value",
        )


def tearDownModule():
    reap_children()
