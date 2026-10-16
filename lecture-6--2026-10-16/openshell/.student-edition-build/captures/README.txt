Captures behind chapter 1's worked example (2026-10-15, OpenShell 0.1.4, Docker in Colima on the instructor's Mac).

The first Cyberbird sandbox, with the course's policy (read_only lists all of /app), is Task 4.6's capture in
instructor-materials/hw2/feasibility/cyberbird/ (commit c2ab5e3): probes.txt item 4 prints the answer key's first
line, and denials.txt prints the first line of the withheld case BenchmarkTest00284.py.

The second sandbox is this folder's:
  cyberbird-policy-src-only.yaml  the course's policy with read_only narrowed to /app/cyberbird, /app/.venv and the
                                  fixture's src/; ground-truth/ is on no list
  probe-src-only.txt              create, list, the probes (answer key: Permission denied; withheld case: readable;
                                  cyberbird imports and starts), delete
  run-src-only-full.txt           cyberbird reactive --alert-id bc284c6b under that policy: accepted, 8 of 40 model calls
  logs-src-only.txt               the sandbox log for the window, filtered to network, HTTP and file lines: allowed model
                                  calls only, no line about the refused file
  read-file-refusals.txt          Cyberbird's own read_file refusals for the two paths, run on the Mac, outside OpenShell

Image cyberbird:1 (e3caafbbdf8c) is Task 4.6's (instructor-materials hw2/feasibility/cyberbird/Dockerfile). The probe
sandbox se-cbprobe was deleted at 23:21 EDT; nothing of it is left.
