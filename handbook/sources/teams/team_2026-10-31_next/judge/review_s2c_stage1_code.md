# judge: SKR2C stage-1 code review (runner drafts, 3 Nov 2026 ~02:4x IST)
Files (local copies, scripts/s2c/):
- s2c_guard.sh 99291944
- s2c_queue.sh 5179dac4
- s2c_gpumem.sh bee07e59
- s2c_guard_dry.sh 18a5dc84
- s2c_make_jobs.sh e7d20e79
- scripts/pf2/gpu_gate.sh 00fabfdd

Checked against: protocol_SKR2C v1 §2a / §2b and team-lead's rulings.

**Verdict: NOT READY for APPROVED.** There are 8 items; G1-G7 are must-fix and G8 is should-fix.

The core is right:
- targets come only from our pid files, each a jobs-file name;
- every candidate is checked for alive, owner noob, not 6206, and cmdline holding scripts/train.py plus the `run_name=<name>` token (the token is the last opt in s2c_jobs, so the match is exact);
- newest = smallest etimes;
- HOLD is set before any signal; MAXSTOPS is 2;
- the pid file is $! inside the subshell, i.e. the python trainer (fixes the s2q finding);
- the queue HOLDs if the logger or the guard is gone;
- decoys cover wrong cmdline, 6206, PID 1, a dead PID and a stray file.

## Must fix
- **G1. Exact cmdline equality (protocol §2b(a)).** The guard tests "contains scripts/train.py + run_name=<name>". The protocol says "/proc/<pid>/cmdline must equal the recorded cmdline exactly".
  - In the queue, right after `pp=$!`, write `tr '\0' ' ' < /proc/$pp/cmdline > $Q/pids/$name.cmdline`.
  - In the guard, require equality with that file, keeping the token test as well.
  - Otherwise amend the protocol. My preference is the code fix (2 lines).
- **G2. Owner re-check before SIGKILL** (guard l.70). Only the cmdline is re-checked, but team-lead's ruling is owner + cmdline. Add `stat -c %U /proc/$p` = noob.
- **G3. The second stop can come before 30 s.**
  - COOL is 20 samples, and 3 more are needed to trigger. If the first SIGTERM exits at once (w = 0), a second stop can fire ~23 s after the first.
  - team-lead's ruling is ≥ 30 s. Set COOL ≥ 30, or test `now − last_stop ≥ 30`.
  - COOL 30 also gives the 60 s trace "around the event" that §2b(d) asks for (30 before + 30 after).
- **G4. A hung nvidia-smi blinds the guard silently** (guard l.50 / l.58).
  - No timeout means one hung call freezes the loop, while guard.pid stays alive. The queue's gd_ok still passes, so starts continue with no protection.
  - Use `timeout 5 nvidia-smi ...`. After 10 consecutive failed reads: touch HOLD and log. The 1 s logger and the queue's start-line call need the same timeout.
- **G5. The outside-process HOLD is not implemented anywhere** (queue, gate, guard, logger). Protocol §2b and team-lead require: new starts wait while any compute process that is not 6206 and not in our pids/*.pid holds > 1,024 MiB.
  - Add this in the queue loop before `gate_try`: compute-apps, minus 6206, minus our pids, any with used > 1024 → log once per episode, sleep 60, continue.
- **G6. Live per-run startup check (protocol §2a.3).** The queue's cfgcheck only HOLDs on CONFIG FAIL, so the bad run keeps training. There is also no "Labelled … val: 54 test: 54" check.
  - A run whose root was not applied would finish and evaluate the **real test** (50 cells) at its end. A test number would then exist on disk, which is what §2a forbids.
  - Add a one-line grep of the startup "Labelled" line: train 478, val 54, test 54 (the real test would print 50).
  - On a mismatch or CONFIG FAIL, **stop that run** by the guard's verified-PID path (SIGTERM, 30 s, re-check owner + cmdline, SIGKILL), touch HOLD, and log.
- **G7. The dry run never exercises the signal path that runs overnight.** With DRY=1 the guard sends no signal (l.65), so l.66-72 are untested: SIGTERM, the 30 s wait, the re-check and SIGKILL.
  - Split the two switches: FAKE (free from a file) and DRY (no signals).
  - Add pass 3: FAKE trace + real signals, on scratch-Q dummies only. Include:
    - a dummy that ignores SIGTERM (python `signal.signal(SIGTERM, SIG_IGN)` + sleep), which must get SIGKILL after the 30 s re-check, logged;
    - a normal dummy, which must exit on SIGTERM;
    - a second-stop timing case: check the stop-to-stop gap ≥ 30 s in the log;
    - the 3rd trigger: logged only.
  - Decoys stay as they are: never signalled.

## Should fix
- **G8. Unit-test the new queue gates.** Test the outside-process check (G5) and the startup-line check (G6) against fake inputs, e.g. a FAKEAPPS file and a fake stdout head. Show the log lines.

## What I need for APPROVED
The new md5s of guard / queue / harness, plus the dry-run harness.log and guard.log of passes 1-3. In them I check:
- (a) pid file = python child;
- (b) 2 low samples do not trigger, 3 do;
- (c) SIGKILL only after the re-check;
- (d) decoys refused, with their reasons;
- (e) HOLD set;
- (f) 2-stop cap, gap ≥ 30 s;
- (g) outside-process / logger / guard HOLD lines from G8;
- (h) log fields.

## Re-review: v3 (build_s2c.md dc0e7d3e), 2026-11-03 02:58 IST
**Verdict: ACCEPTED for APPROVED (judge side), with 2 arming conditions.**

Files: lib s2c_lib.sh 4edcae9e, guard s2c_guard.sh 334742d6, queue s2c_queue.sh de31c533, gpumem 06791cdd, dry f0782bbe, unit 40dc50fa. Logs: results/s2c_dry/v2 (md5 list -c OK).

**G1-G8 checked in the code and the logs (E):**
- **G1:** launch_run writes pids/NAME.cmdline from /proc after the exec. verify requires live cmdline = recorded + tokens + owner + not 6206.
  - pass 2: a decoy python with a different cmdline (s11) was REFUSED; the sleep decoy, 6206 and PID 1 were refused.
- **G2:** stop_verified re-runs verify right before SIGKILL.
  - pass 2: the SIGTERM-ignoring dummy (SUPPF s10) got "alive 30 s after SIGTERM; re-check passed" and then SIGKILL, gone.
  - pass 3: a dummy that exec'd into sleep gave "re-check FAILED ... no SIGKILL", rc 3.
- **G3:** COOL 30 + GAP 30 s since the first signal.
  - pass 1b (COOL 5 to exercise GAP): a trigger 8 s after stop 1 gave "no signal".
  - pass 2 at defaults: the 2nd stop came 63 s after the 1st; the normal dummy exited on SIGTERM; the 3rd trigger was "cap: 2 of 2 ... no signal".
- **G4:** every nvidia-smi call in lib / guard / gpumem is under timeout 5. pass 5: 10 consecutive failed reads set HOLD.
- **G5:** outside() (unit): 1500 and 1025 flagged; 900, 1024, 6206 and ours not. prestart waits on an outside process. A dead logger or guard sets HOLD.
- **G6:** live check before the next start: cfgcheck plus startcheck (grep -m1 'Labelled:' = the exact root line).
  - unit: a real-test stdout ('test: 50') gave MISMATCH, then HOLD, then stop_verified, rc 143.
- **G7:** FAKE is split from DRY. Passes 2 and 3 are live signals on scratch dummies only. Decoys were never signalled.
- **G8:** queue_unit.log covers the gates.
- **Rootcheck run 2:** the compared fields are a superset of §2a, all but wall sec. IDENTICAL both arms; SKR01's A = el_thin's own data.

**Non-blocking notes (S):**
- (a) The passes ran with guard d8a8eb75. The final 334742d6 adds only `TRIG=""` on a failed read (display; runner's build note), and that fix is re-shown in autostop_trigfix.log.
- (b) If launch_run sees no train.py cmdline within 20 s, the queue HOLDs, but that one run would be unprotected: the watcher cannot verify it, and the live-check stop is refused. This is a low-probability case, logged; check it in the morning if it occurs.
- (c) gate_try (shared gpu_gate.sh 00fabfdd) calls nvidia-smi without a timeout inside the flock. A hang there blocks new starts (safe side), and the independent guard still protects running runs.

**Arming conditions (runner; coach checks before launch):**
1. Deploy exactly lib 4edcae9e, guard 334742d6, queue de31c533 and gpumem 06791cdd (md5 at both ends). Start order: gpumem, then guard, then queue. No env overrides: the guard's start line in autostop.log must read "FAKE none; DRY 0; THR 2048 MiB x 3; COOL 30; GAP 30 s; MAXSTOPS 2".
2. The queue's armed line must show lib 4edcae9e, the root check passed (SPLITS 24568cdb), and the live gpumem and guard PIDs. The first run's "config OK" and "startup line OK" must appear before the second start.
