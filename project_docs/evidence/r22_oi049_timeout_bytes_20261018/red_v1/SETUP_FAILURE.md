The first timeout stimulus used subprocess.run(timeout=.5) before observing child readiness. It stopped before any partial stdout arrived, so the harness assertion that stdout was nonempty bytes failed. No CEC/normalization mock or production function was reached, no RESULT was written, no EDA ran. This is a harness setup failure, not a reproduction or rejection of OI049.

Transcribed from the tool result (not an original redirected raw log):

```
Traceback (most recent call last):
  File "scratch/probe_oi049_timeout_bytes_20261018.py", line 24, in <module>
    assert isinstance(actual.stdout,bytes) and actual.stdout
AssertionError
[run] 完成（5s），退出码 1
```

The exact invocation script is retained as probe_v1_setup_failed.py. The next attempt uses a child readiness handshake before communicate timeout, with an enclosing 60-second wrapper, and a distinct output directory.
