module s382 (CK,
    CLR,
    FM,
    GRN1,
    GRN2,
    RED1,
    RED2,
    TEST,
    YLW1,
    YLW2);
 input CK;
 input CLR;
 input FM;
 output GRN1;
 output GRN2;
 output RED1;
 output RED2;
 input TEST;
 output YLW1;
 output YLW2;

 wire OLATCH_G1L;
 wire OLATCH_G2L;
 wire OLATCH_R1L;
 wire OLATCH_Y2L;
 wire C1VCO0;
 wire C3_Q0;
 wire C3_Q0VD;
 wire C3_Q1;
 wire C3_Q1VD;
 wire C3_Q2;
 wire C3_Q2VD;
 wire C3_Q3;
 wire C3_Q3VD;
 wire FML;
 wire FMLVIINLATCHVCDAD;
 wire OLATCHVUC_5;
 wire OLATCHVUC_6;
 wire OLATCH_FEL;
 wire R2C;
 wire TCOMB_FE;
 wire TCOMB_GA1;
 wire TCOMB_GA2;
 wire TCOMB_RA1;
 wire TCOMB_YA2;
 wire TESTL;
 wire TESTLVIINLATCHVCDAD;
 wire UC_10;
 wire UC_10VD;
 wire UC_11VD;
 wire UC_16;
 wire UC_16VD;
 wire UC_17;
 wire UC_17VD;
 wire UC_18;
 wire UC_18VD;
 wire UC_19;
 wire UC_19VD;
 wire UC_8;
 wire UC_8VD;
 wire UC_9;
 wire UC_9VD;
 wire Y1C;
 wire _000_;
 wire _001_;
 wire _002_;
 wire _003_;
 wire _004_;
 wire _005_;
 wire _006_;
 wire _007_;
 wire _008_;
 wire _009_;
 wire _010_;
 wire _011_;
 wire _012_;
 wire _013_;
 wire _014_;
 wire _015_;
 wire _016_;
 wire _017_;
 wire _018_;
 wire _019_;
 wire _020_;
 wire _021_;
 wire _022_;
 wire _023_;
 wire _024_;
 wire _025_;
 wire _026_;
 wire _027_;
 wire _028_;
 wire _029_;
 wire _030_;
 wire _031_;
 wire _032_;
 wire _033_;
 wire _034_;
 wire _035_;
 wire _036_;
 wire _037_;
 wire _038_;
 wire _039_;
 wire _040_;
 wire _041_;
 wire _042_;
 wire _043_;
 wire _044_;
 wire _045_;
 wire clknet_0_CK;
 wire clknet_1_0__leaf_CK;
 wire clknet_1_1__leaf_CK;
 wire net1;
 wire net18;
 wire net19;
 wire net2;
 wire net20;
 wire net3;
 wire net4;
 wire net9;

 sky130_fd_sc_hd__dfxtp_4 \DFF_0/_0_  (.D(TESTLVIINLATCHVCDAD),
    .Q(TESTL),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_4 \DFF_1/_0_  (.D(FMLVIINLATCHVCDAD),
    .Q(FML),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_2 \DFF_10/_0_  (.D(C3_Q2VD),
    .Q(C3_Q2),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_4 \DFF_11/_0_  (.D(C3_Q1VD),
    .Q(C3_Q1),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_4 \DFF_12/_0_  (.D(C3_Q0VD),
    .Q(C3_Q0),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_13/_0_  (.D(UC_16VD),
    .Q(UC_16),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_14/_0_  (.D(UC_17VD),
    .Q(UC_17),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_15/_0_  (.D(UC_18VD),
    .Q(UC_18),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_16/_0_  (.D(UC_19VD),
    .Q(UC_19),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_17/_0_  (.D(UC_8VD),
    .Q(UC_8),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_2 \DFF_18/_0_  (.D(UC_9VD),
    .Q(UC_9),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_2 \DFF_19/_0_  (.D(UC_10VD),
    .Q(UC_10),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_2/_0_  (.D(TCOMB_YA2),
    .Q(OLATCH_Y2L),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_20/_0_  (.D(UC_11VD),
    .Q(C1VCO0),
    .CLK(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_3/_0_  (.D(Y1C),
    .Q(OLATCHVUC_6),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_4/_0_  (.D(R2C),
    .Q(OLATCHVUC_5),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_5/_0_  (.D(TCOMB_RA1),
    .Q(OLATCH_R1L),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_6/_0_  (.D(TCOMB_GA2),
    .Q(OLATCH_G2L),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_7/_0_  (.D(TCOMB_GA1),
    .Q(OLATCH_G1L),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_1 \DFF_8/_0_  (.D(TCOMB_FE),
    .Q(OLATCH_FEL),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__dfxtp_2 \DFF_9/_0_  (.D(C3_Q3VD),
    .Q(C3_Q3),
    .CLK(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__clkinv_1 _046_ (.A(OLATCHVUC_6),
    .Y(YLW1));
 sky130_fd_sc_hd__clkinv_1 _047_ (.A(OLATCHVUC_5),
    .Y(RED2));
 sky130_fd_sc_hd__clkinv_1 _048_ (.A(CLR),
    .Y(_007_));
 sky130_fd_sc_hd__clkinv_1 _049_ (.A(C3_Q1),
    .Y(_008_));
 sky130_fd_sc_hd__nand2b_1 _050_ (.A_N(CLR),
    .B(OLATCH_FEL),
    .Y(_009_));
 sky130_fd_sc_hd__nor4b_4 _051_ (.A(C3_Q1),
    .B(FML),
    .C(C3_Q3),
    .D_N(C3_Q0),
    .Y(_010_));
 sky130_fd_sc_hd__a21oi_2 _052_ (.A1(_010_),
    .A2(C3_Q2),
    .B1(_009_),
    .Y(_011_));
 sky130_fd_sc_hd__nand2b_1 _053_ (.A_N(CLR),
    .B(C3_Q2),
    .Y(_012_));
 sky130_fd_sc_hd__or3b_4 _054_ (.A(C3_Q0),
    .B(C3_Q1),
    .C_N(FML),
    .X(_013_));
 sky130_fd_sc_hd__nor2_2 _055_ (.A(_012_),
    .B(_013_),
    .Y(_014_));
 sky130_fd_sc_hd__lpflow_inputiso1p_1 _056_ (.A(_011_),
    .SLEEP(_014_),
    .X(TCOMB_FE));
 sky130_fd_sc_hd__o31a_1 _057_ (.A1(UC_9),
    .A2(UC_10),
    .A3(C1VCO0),
    .B1(UC_8),
    .X(_015_));
 sky130_fd_sc_hd__o31a_1 _058_ (.A1(UC_19),
    .A2(UC_18),
    .A3(UC_17),
    .B1(UC_16),
    .X(_016_));
 sky130_fd_sc_hd__o21ai_2 _059_ (.A1(TESTL),
    .A2(_015_),
    .B1(_016_),
    .Y(_017_));
 sky130_fd_sc_hd__nand2_1 _060_ (.A(_007_),
    .B(_017_),
    .Y(_018_));
 sky130_fd_sc_hd__or3_1 _061_ (.A(C3_Q0),
    .B(C3_Q1),
    .C(C3_Q2),
    .X(_019_));
 sky130_fd_sc_hd__nand2_1 _062_ (.A(C3_Q3),
    .B(_019_),
    .Y(_020_));
 sky130_fd_sc_hd__o21ai_2 _063_ (.A1(_017_),
    .A2(_020_),
    .B1(_007_),
    .Y(_021_));
 sky130_fd_sc_hd__o211ai_1 _064_ (.A1(TESTL),
    .A2(net1),
    .B1(_016_),
    .C1(C3_Q0),
    .Y(_022_));
 sky130_fd_sc_hd__xor2_1 _065_ (.A(C3_Q0),
    .B(_017_),
    .X(_023_));
 sky130_fd_sc_hd__nor2_1 _066_ (.A(_021_),
    .B(_023_),
    .Y(C3_Q0VD));
 sky130_fd_sc_hd__o2111ai_1 _067_ (.A1(TESTL),
    .A2(_015_),
    .B1(_016_),
    .C1(C3_Q1),
    .D1(C3_Q0),
    .Y(_024_));
 sky130_fd_sc_hd__xnor2_1 _068_ (.A(_008_),
    .B(_022_),
    .Y(_025_));
 sky130_fd_sc_hd__nor2_1 _069_ (.A(_021_),
    .B(_025_),
    .Y(C3_Q1VD));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _070_ (.A(C3_Q2),
    .SLEEP(_024_),
    .X(_026_));
 sky130_fd_sc_hd__nor2b_1 _071_ (.A(C3_Q2),
    .B_N(_024_),
    .Y(_027_));
 sky130_fd_sc_hd__nor3_1 _072_ (.A(_021_),
    .B(_026_),
    .C(_027_),
    .Y(C3_Q2VD));
 sky130_fd_sc_hd__o21ba_1 _073_ (.A1(C3_Q3),
    .A2(_026_),
    .B1_N(_021_),
    .X(C3_Q3VD));
 sky130_fd_sc_hd__o21ai_1 _074_ (.A1(_011_),
    .A2(_014_),
    .B1(UC_17),
    .Y(_028_));
 sky130_fd_sc_hd__nand2_1 _075_ (.A(_007_),
    .B(C3_Q3),
    .Y(_029_));
 sky130_fd_sc_hd__o31ai_1 _076_ (.A1(C3_Q0),
    .A2(net20),
    .A3(_029_),
    .B1(_012_),
    .Y(_030_));
 sky130_fd_sc_hd__o21ai_1 _077_ (.A1(_011_),
    .A2(_030_),
    .B1(_028_),
    .Y(R2C));
 sky130_fd_sc_hd__nor2_1 _078_ (.A(C3_Q3),
    .B(C3_Q2),
    .Y(_031_));
 sky130_fd_sc_hd__a21oi_2 _079_ (.A1(_013_),
    .A2(_019_),
    .B1(_031_),
    .Y(_032_));
 sky130_fd_sc_hd__and3_1 _080_ (.A(_007_),
    .B(_020_),
    .C(_032_),
    .X(_033_));
 sky130_fd_sc_hd__o21ai_1 _081_ (.A1(_011_),
    .A2(_033_),
    .B1(_028_),
    .Y(Y1C));
 sky130_fd_sc_hd__nor3_1 _082_ (.A(TESTL),
    .B(UC_19),
    .C(_015_),
    .Y(_034_));
 sky130_fd_sc_hd__o21a_1 _083_ (.A1(_015_),
    .A2(TESTL),
    .B1(UC_19),
    .X(_035_));
 sky130_fd_sc_hd__nor3_1 _084_ (.A(_018_),
    .B(_034_),
    .C(net2),
    .Y(UC_19VD));
 sky130_fd_sc_hd__xnor2_1 _085_ (.A(UC_18),
    .B(_035_),
    .Y(_036_));
 sky130_fd_sc_hd__nor2_1 _086_ (.A(_018_),
    .B(_036_),
    .Y(UC_18VD));
 sky130_fd_sc_hd__and3_1 _087_ (.A(UC_18),
    .B(_035_),
    .C(UC_17),
    .X(_037_));
 sky130_fd_sc_hd__a21oi_1 _088_ (.A1(UC_18),
    .A2(_035_),
    .B1(UC_17),
    .Y(_038_));
 sky130_fd_sc_hd__nor3_1 _089_ (.A(_018_),
    .B(_038_),
    .C(_037_),
    .Y(UC_17VD));
 sky130_fd_sc_hd__a31oi_1 _090_ (.A1(_035_),
    .A2(UC_17),
    .A3(UC_18),
    .B1(UC_16),
    .Y(_039_));
 sky130_fd_sc_hd__nor2_1 _091_ (.A(_018_),
    .B(_039_),
    .Y(UC_16VD));
 sky130_fd_sc_hd__xnor2_1 _092_ (.A(C1VCO0),
    .B(net4),
    .Y(_040_));
 sky130_fd_sc_hd__nor3_2 _093_ (.A(CLR),
    .B(net18),
    .C(_040_),
    .Y(UC_10VD));
 sky130_fd_sc_hd__and3_1 _094_ (.A(C1VCO0),
    .B(net4),
    .C(net3),
    .X(_041_));
 sky130_fd_sc_hd__a21oi_1 _095_ (.A1(C1VCO0),
    .A2(net4),
    .B1(net3),
    .Y(_042_));
 sky130_fd_sc_hd__nor4_1 _096_ (.A(net18),
    .B(CLR),
    .C(_041_),
    .D(_042_),
    .Y(UC_9VD));
 sky130_fd_sc_hd__nor2_1 _097_ (.A(UC_8),
    .B(_041_),
    .Y(_043_));
 sky130_fd_sc_hd__nor3_2 _098_ (.A(CLR),
    .B(net18),
    .C(_043_),
    .Y(UC_8VD));
 sky130_fd_sc_hd__a21oi_1 _099_ (.A1(FML),
    .A2(C3_Q3),
    .B1(OLATCH_FEL),
    .Y(_044_));
 sky130_fd_sc_hd__nor2_1 _100_ (.A(net9),
    .B(_044_),
    .Y(_045_));
 sky130_fd_sc_hd__nor3b_1 _101_ (.A(_045_),
    .B(_012_),
    .C_N(_013_),
    .Y(TCOMB_GA1));
 sky130_fd_sc_hd__nand2_2 _102_ (.A(C3_Q0),
    .B(net20),
    .Y(_000_));
 sky130_fd_sc_hd__nor2_1 _103_ (.A(CLR),
    .B(_000_),
    .Y(_001_));
 sky130_fd_sc_hd__nor4_1 _104_ (.A(CLR),
    .B(OLATCH_FEL),
    .C(C3_Q2),
    .D(_000_),
    .Y(TCOMB_YA2));
 sky130_fd_sc_hd__nor2_1 _105_ (.A(C3_Q0),
    .B(_029_),
    .Y(_002_));
 sky130_fd_sc_hd__nand2_1 _106_ (.A(_009_),
    .B(_012_),
    .Y(_003_));
 sky130_fd_sc_hd__nor3_1 _107_ (.A(_001_),
    .B(_002_),
    .C(_003_),
    .Y(TCOMB_GA2));
 sky130_fd_sc_hd__nor3_1 _108_ (.A(CLR),
    .B(C1VCO0),
    .C(net19),
    .Y(UC_11VD));
 sky130_fd_sc_hd__a21oi_1 _109_ (.A1(C3_Q0),
    .A2(_008_),
    .B1(_029_),
    .Y(_004_));
 sky130_fd_sc_hd__nor2_1 _110_ (.A(_003_),
    .B(_004_),
    .Y(TCOMB_RA1));
 sky130_fd_sc_hd__xnor2_2 _111_ (.A(TESTL),
    .B(TEST),
    .Y(_005_));
 sky130_fd_sc_hd__nor2_1 _112_ (.A(CLR),
    .B(_005_),
    .Y(TESTLVIINLATCHVCDAD));
 sky130_fd_sc_hd__xnor2_2 _113_ (.A(FM),
    .B(FML),
    .Y(_006_));
 sky130_fd_sc_hd__nor2_1 _114_ (.A(CLR),
    .B(_006_),
    .Y(FMLVIINLATCHVCDAD));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_CK (.A(CK),
    .X(clknet_0_CK));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_CK (.A(clknet_0_CK),
    .X(clknet_1_0__leaf_CK));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_CK (.A(clknet_0_CK),
    .X(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__clkbuf_4 clkload0 (.A(clknet_1_1__leaf_CK));
 sky130_fd_sc_hd__buf_6 rebuffer1 (.A(_015_),
    .X(net1));
 sky130_fd_sc_hd__buf_6 rebuffer18 (.A(net1),
    .X(net18));
 sky130_fd_sc_hd__buf_4 rebuffer19 (.A(net18),
    .X(net19));
 sky130_fd_sc_hd__buf_4 rebuffer2 (.A(_035_),
    .X(net2));
 sky130_fd_sc_hd__buf_6 rebuffer20 (.A(C3_Q1),
    .X(net20));
 sky130_fd_sc_hd__buf_4 rebuffer3 (.A(UC_9),
    .X(net3));
 sky130_fd_sc_hd__buf_4 rebuffer4 (.A(UC_10),
    .X(net4));
 sky130_fd_sc_hd__buf_4 rebuffer9 (.A(_010_),
    .X(net9));
 assign GRN1 = OLATCH_G1L;
 assign GRN2 = OLATCH_G2L;
 assign RED1 = OLATCH_R1L;
 assign YLW2 = OLATCH_Y2L;
endmodule