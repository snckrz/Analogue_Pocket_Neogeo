# Neo Geo Memories investigation

Status: **not implemented**. This branch implements Composite Blend only. It does not provide Memories or Sleep/Wake. Do not enable those flags in core.json.

Base: Mazamars312/Analogue_Pocket_Neogeo at 988163bcf725271d05858e86ac7bfe48853b938b (0.8.1 source).

## What the source audit found

| Area | Source | Missing work |
|---|---|---|
| Pocket interface | `src/NeoGeo Cart/core/NeoGeoCore/apf_io.sv` | APF save-state query/handshake wires exist but were undriven; this branch explicitly reports unsupported. No snapshot address, data store or save/load engine exists. |
| 68000 | `cpu/cpu_68k.v`, `cpu/FX68K/fx68k.sv` below NeoGeoCore | No exported state read/write interface. Internal register banks, instruction/prefetch state, microcode sequencing, flags and bus phase need capture/restore or a proven safe checkpoint. |
| Z80 | `cpu/cpu_z80.v`, `cpu/T80/T80s.vhd` | Wrapper hardwires CEN=1; no exported state read/write interface. Registers, interrupt state and instruction/bus state need support. |
| Graphics | `video/lspc2_a2.v` and subordinate modules | Derived clocks, both clock edges and asynchronous controls; stopping only a CPU clock cannot make a coherent snapshot. Sprite/scanline state and video RAM need capture/restore. |
| Audio | jt10/YM2610 and jt49 | Registers alone are insufficient: FM phase/envelopes, timers, ADPCM decoder state, addresses and outstanding sample fetches affect resumed audio. |
| Memory and cartridges | `core/Neogeo.sv`, SRAM/CRAM controllers, neo_sma/neo_pvc/neo_zmc2 | Work RAM, Z80 RAM, slow/fast video RAM, palette banks, backup/card state, bank/protection state and in-flight transactions need coordinated handling. |

Paths in the table are relative to `src/NeoGeo Cart/core/NeoGeoCore` unless stated otherwise.

## Viable development order

1. Add independently tested state interfaces to the CPU and audio blocks. Prove save-run-restore-rerun gives identical bus/audio traces using synthetic test programs.
2. Design a safe checkpoint across the clock domains, with all memory requests completed and writes inhibited during capture/restore. Avoid introducing glitches by naively gating clocks.
3. Inventory all mutable memory and cartridge state; define a versioned snapshot format and choose staging storage from the actual memory map. Read-only game ROMs need identity checks, not duplication in every snapshot.
4. Connect a complete state image to the APF save/load commands; validate version, game/BIOS identity, lengths and data integrity before modifying the running machine.
5. Test across AES/MVS, PAL/NTSC, cartridge hardware, repeated loads and audio playback; enable Memories only after coherent round trips work. Sleep/Wake additionally needs restoration after the FPGA is reset.

The SNES experimental implementation is useful as an APF integration example, but its machine-state inventory and per-chip state ports cannot be reused directly here. This audit does not establish that Neo Geo save states are impossible or that they will fit. No functioning save-state feature has been created or claimed.
