# Simulate the actual Neo Geo video output block, including metadata.
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
source = (root / 'src/NeoGeo Cart/core/Neogeo.sv').read_text()
block = source[source.index('localparam\t\tVID_H_BPORCH_SD'):]
header = '''`timescale 1ns/1ps
module video_stage;
reg CLK_VIDEO = 0;
always #5 CLK_VIDEO = ~CLK_VIDEO;
reg HSync = 0, VSync = 0, SHADOW = 0, video_mode = 0;
reg [31:0] screen_x_pos = 0, screen_y_pos = 0;
reg [2:0] APF_Video_ratio = 0;
reg composite_blend_enable = 0;
reg [7:0] VGA_R_wire=0, VGA_G_wire=0, VGA_B_wire=0;
reg [7:0] VGA_R, VGA_G, VGA_B;
reg VGA_DE, VGA_HS, VGA_VS;
'''
tb = '''
module neogeo_video_tb;
video_stage dut();
task pixel(input integer x, input integer y, input integer mode,
           input bit enabled, input [23:0] color, input [23:0] expected, input bit de);
begin
 @(negedge dut.CLK_VIDEO);
 dut.x_count=x; dut.y_count=y; dut.res_reg=mode;
 dut.VID_H_BPORCH=30; dut.VID_H_ACTIVE_REG=width; dut.VID_V_BPORCH=16;
 dut.HSync_reg=0; dut.VSync_reg=0; dut.blend_sync={2{enabled}};
 {dut.VGA_R_reg,dut.VGA_G_reg,dut.VGA_B_reg}=color;
 @(posedge dut.CLK_VIDEO); #1;
 if ({dut.VGA_R,dut.VGA_G,dut.VGA_B} !== expected || dut.VGA_DE !== de)
  $fatal(1,"output mismatch x=%d mode=%d got=%h expected=%h",x,mode,{dut.VGA_R,dut.VGA_G,dut.VGA_B},expected);
end
endtask
integer m;
integer width;
initial begin
 for(width=304;width<=320;width=width+16) begin
 for(m=0;m<8;m=m+1) begin
  pixel(29,16,m,1,24'hffffff,0,0);
  pixel(30,16,m,1,24'hfe8040,24'h7f4020,1);
  pixel(31,16,m,1,24'h0200c0,24'h804080,1);
  pixel(width+29,16,m,1,24'hffffff,24'h807fdf,1);
  pixel(width+30,16,m,1,24'hffffff,m<<13,0);
  pixel(30,17,m,1,24'hfe8040,24'h7f4020,1);
  pixel(31,17,m,0,24'h123456,24'h123456,1);
  pixel(30,240,m,1,24'hffffff,0,0);
 end
 end
 $display("PASS: actual Neo Geo RGB output, bypass, line borders, 304/320 widths and all eight metadata slots");
 $finish;
end
endmodule
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'video.sv';p.write_text(header+block+tb)
 exe=Path(d)/'sim'
 subprocess.run(['iverilog','-g2012','-s','neogeo_video_tb','-o',str(exe),str(p),str(root/'src/NeoGeo Cart/core/composite_blend.sv')],check=True)
 subprocess.run(['vvp',str(exe)],check=True)
