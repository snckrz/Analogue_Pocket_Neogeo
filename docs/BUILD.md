# Prototype build

Quartus Prime Lite 21.1.1, build 850, using the existing `ghcr.io/drizzt/quartus:21.1` container. Run `bash /source/tools/build.sh` with this repository mounted read-only at `/source` and an empty writable volume at `/build`.

The Composite Blend prototype compiled with 0 errors. It fits at 10,999/18,480 ALMs (60%), 279/308 RAM blocks (91%), 2,091,463/3,153,920 memory bits (66%) and 5/66 DSP blocks.

**Timing failed; this is not a validated hardware release.** The worst setup/hold paths inspected are in the SDRAM I/O interface, not the blend arithmetic. The unmodified upstream source also fails timing with this compiler: minimum setup -8.229 ns and hold 0.096 ns, versus -8.459 ns and -1.793 ns for this prototype. Upstream uses 11,039 ALMs and the same 279 RAM blocks. Placement differences mean the lower prototype ALM total is not a measurement of the filter’s isolated cost. Existing constraints have not been relaxed. There are also unconstrained paths and upstream power-up-level warnings.

Simulation passed for RGB arithmetic, bypass, overflow, line boundaries, both 304/320 widths and all eight scaler metadata slots. With Icarus and Python installed:

```sh
iverilog -g2012 -s composite_blend_tb -o /tmp/blend "src/NeoGeo Cart/core/composite_blend.sv" tests/composite_blend_tb.sv
vvp /tmp/blend
python3 tests/check_video_stage.py
```

Memories remain unimplemented and Sleep remains disabled. No hardware testing has been performed on this modified core.
