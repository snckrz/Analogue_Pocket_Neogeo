#!/bin/bash
set -euo pipefail
mkdir -p /build/source /build/results
cp -a /source/. /build/source/
cd "/build/source/src/NeoGeo Cart"
quartus_sh --flow compile ap_core.qpf > /build/results/build.log 2>&1
cp output_files/*.summary output_files/*.rpt output_files/ap_core.rbf /build/results/
