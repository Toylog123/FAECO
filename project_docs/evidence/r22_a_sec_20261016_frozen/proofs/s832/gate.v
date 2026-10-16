module s832(GND, VDD, CK, G0, G1, G10, G11, G12, G13, G14, G15, G16, G18, G2, G288, G290, G292, G296, G298, G3, G300
, G302, G310, G312, G315, G322, G325, G327, G4, G43, G45, G47, G49, G5, G53, G55, G6, G7, G8, G9);
  input GND;
  wire GND;
  input VDD;
  wire VDD;
  input CK;
  wire CK;
  input G0;
  wire G0;
  input G1;
  wire G1;
  input G10;
  wire G10;
  input G11;
  wire G11;
  input G12;
  wire G12;
  input G13;
  wire G13;
  input G14;
  wire G14;
  input G15;
  wire G15;
  input G16;
  wire G16;
  input G18;
  wire G18;
  input G2;
  wire G2;
  output G288;
  wire G288;
  output G290;
  wire G290;
  output G292;
  wire G292;
  output G296;
  wire G296;
  output G298;
  wire G298;
  input G3;
  wire G3;
  output G300;
  wire G300;
  output G302;
  wire G302;
  output G310;
  wire G310;
  output G312;
  wire G312;
  output G315;
  wire G315;
  output G322;
  wire G322;
  output G325;
  wire G325;
  output G327;
  wire G327;
  input G4;
  wire G4;
  output G43;
  wire G43;
  output G45;
  wire G45;
  output G47;
  wire G47;
  output G49;
  wire G49;
  input G5;
  wire G5;
  output G53;
  wire G53;
  output G55;
  wire G55;
  input G6;
  wire G6;
  input G7;
  wire G7;
  input G8;
  wire G8;
  input G9;
  wire G9;
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
  wire _046_;
  wire _047_;
  wire _048_;
  wire _049_;
  wire _050_;
  wire _051_;
  wire _052_;
  wire _053_;
  wire _054_;
  wire _055_;
  wire _056_;
  wire _057_;
  wire _058_;
  wire _059_;
  wire _060_;
  wire _061_;
  wire _062_;
  wire _063_;
  wire _064_;
  wire _065_;
  wire _066_;
  wire _067_;
  wire _068_;
  wire _069_;
  wire _070_;
  wire _071_;
  wire _072_;
  wire _073_;
  wire _074_;
  wire _075_;
  wire _076_;
  wire _077_;
  wire _078_;
  wire _079_;
  wire _080_;
  wire _081_;
  wire _082_;
  wire _083_;
  wire _084_;
  wire _085_;
  wire _086_;
  wire _087_;
  wire _088_;
  wire _089_;
  wire _090_;
  wire _091_;
  wire _092_;
  wire _093_;
  wire _094_;
  wire _095_;
  wire _096_;
  wire _097_;
  wire _098_;
  wire _099_;
  wire _100_;
  wire _101_;
  wire _102_;
  wire _103_;
  wire _104_;
  wire _105_;
  wire _106_;
  wire _107_;
  wire _108_;
  wire _109_;
  wire _110_;
  wire _111_;
  wire _112_;
  wire _113_;
  wire _114_;
  wire _115_;
  wire _116_;
  wire G102;
  wire G38;
  wire G39;
  wire G40;
  wire G41;
  wire G42;
  wire G90;
  wire G93;
  wire G96;
  wire G99;
  sky130_fd_sc_hd__clkinv_1 _117_ (
    .A(G38),
    .Y(_075_)
  );
  sky130_fd_sc_hd__clkinv_1 _118_ (
    .A(G40),
    .Y(_076_)
  );
  sky130_fd_sc_hd__clkinv_1 _119_ (
    .A(G4),
    .Y(_077_)
  );
  sky130_fd_sc_hd__clkinv_1 _120_ (
    .A(G14),
    .Y(_078_)
  );
  sky130_fd_sc_hd__nand2_1 _121_ (
    .A(G39),
    .B(G40),
    .Y(_079_)
  );
  sky130_fd_sc_hd__nor2_1 _122_ (
    .A(G38),
    .B(G41),
    .Y(_080_)
  );
  sky130_fd_sc_hd__nor4_1 _123_ (
    .A(G38),
    .B(G41),
    .C(G42),
    .D(_079_),
    .Y(G288)
  );
  sky130_fd_sc_hd__and2_0 _124_ (
    .A(G5),
    .B(G288),
    .X(G55)
  );
  sky130_fd_sc_hd__nor2_1 _125_ (
    .A(G38),
    .B(G39),
    .Y(_081_)
  );
  sky130_fd_sc_hd__nor2_1 _126_ (
    .A(G40),
    .B(G42),
    .Y(_082_)
  );
  sky130_fd_sc_hd__nand2b_1 _127_ (
    .A_N(G42),
    .B(G41),
    .Y(_083_)
  );
  sky130_fd_sc_hd__and3_1 _128_ (
    .A(G41),
    .B(_081_),
    .C(_082_),
    .X(G53)
  );
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _129_ (
    .A(G288),
    .SLEEP(G5),
    .X(G47)
  );
  sky130_fd_sc_hd__and3_1 _130_ (
    .A(G40),
    .B(G41),
    .C(G15),
    .X(_084_)
  );
  sky130_fd_sc_hd__nor2_1 _131_ (
    .A(G11),
    .B(G12),
    .Y(_085_)
  );
  sky130_fd_sc_hd__nand2_1 _132_ (
    .A(G16),
    .B(_077_),
    .Y(_086_)
  );
  sky130_fd_sc_hd__nor2_1 _133_ (
    .A(G11),
    .B(G10),
    .Y(_087_)
  );
  sky130_fd_sc_hd__nor2_1 _134_ (
    .A(_085_),
    .B(_087_),
    .Y(_088_)
  );
  sky130_fd_sc_hd__nor3_1 _135_ (
    .A(G38),
    .B(G42),
    .C(_086_),
    .Y(_089_)
  );
  sky130_fd_sc_hd__nand3_1 _136_ (
    .A(_084_),
    .B(_088_),
    .C(_089_),
    .Y(_090_)
  );
  sky130_fd_sc_hd__nor2_1 _137_ (
    .A(G10),
    .B(G12),
    .Y(_091_)
  );
  sky130_fd_sc_hd__nor3_1 _138_ (
    .A(G39),
    .B(_090_),
    .C(_091_),
    .Y(G45)
  );
  sky130_fd_sc_hd__and2_0 _139_ (
    .A(G15),
    .B(G53),
    .X(G43)
  );
  sky130_fd_sc_hd__and2_2 _140_ (
    .A(G41),
    .B(G42),
    .X(_092_)
  );
  sky130_fd_sc_hd__nand2_1 _141_ (
    .A(G41),
    .B(G42),
    .Y(_093_)
  );
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _142_ (
    .A(G39),
    .SLEEP(G38),
    .X(_094_)
  );
  sky130_fd_sc_hd__nor2_1 _143_ (
    .A(G38),
    .B(_079_),
    .Y(_095_)
  );
  sky130_fd_sc_hd__nand2_1 _144_ (
    .A(G40),
    .B(_092_),
    .Y(_096_)
  );
  sky130_fd_sc_hd__nand2_1 _145_ (
    .A(_092_),
    .B(_095_),
    .Y(_097_)
  );
  sky130_fd_sc_hd__or3_1 _146_ (
    .A(G39),
    .B(G40),
    .C(G42),
    .X(_098_)
  );
  sky130_fd_sc_hd__or3_1 _147_ (
    .A(G38),
    .B(G41),
    .C(_098_),
    .X(_099_)
  );
  sky130_fd_sc_hd__nand2_1 _148_ (
    .A(_097_),
    .B(_099_),
    .Y(G315)
  );
  sky130_fd_sc_hd__a211oi_1 _149_ (
    .A1(G38),
    .A2(_076_),
    .B1(_093_),
    .C1(G39),
    .Y(_100_)
  );
  sky130_fd_sc_hd__a21o_1 _150_ (
    .A1(G40),
    .A2(_081_),
    .B1(_100_),
    .X(_101_)
  );
  sky130_fd_sc_hd__nor2_1 _151_ (
    .A(_075_),
    .B(G42),
    .Y(_102_)
  );
  sky130_fd_sc_hd__nand2b_1 _152_ (
    .A_N(G42),
    .B(G38),
    .Y(_103_)
  );
  sky130_fd_sc_hd__nor2_1 _153_ (
    .A(_075_),
    .B(G41),
    .Y(_104_)
  );
  sky130_fd_sc_hd__o21ai_0 _154_ (
    .A1(G41),
    .A2(_103_),
    .B1(G40),
    .Y(_105_)
  );
  sky130_fd_sc_hd__nand3_1 _155_ (
    .A(G39),
    .B(G4),
    .C(_105_),
    .Y(_106_)
  );
  sky130_fd_sc_hd__nand2_1 _156_ (
    .A(G39),
    .B(_076_),
    .Y(_107_)
  );
  sky130_fd_sc_hd__nor3_1 _157_ (
    .A(G38),
    .B(G39),
    .C(G1),
    .Y(_108_)
  );
  sky130_fd_sc_hd__nand4b_1 _158_ (
    .A_N(G41),
    .B(G16),
    .C(_082_),
    .D(_108_),
    .Y(_109_)
  );
  sky130_fd_sc_hd__o31ai_1 _159_ (
    .A1(G16),
    .A2(_092_),
    .A3(_107_),
    .B1(_109_),
    .Y(_110_)
  );
  sky130_fd_sc_hd__a21oi_1 _160_ (
    .A1(_086_),
    .A2(_101_),
    .B1(_110_),
    .Y(_111_)
  );
  sky130_fd_sc_hd__nand2_1 _161_ (
    .A(_106_),
    .B(_111_),
    .Y(G302)
  );
  sky130_fd_sc_hd__nor2_1 _162_ (
    .A(G40),
    .B(G41),
    .Y(_112_)
  );
  sky130_fd_sc_hd__and4_1 _163_ (
    .A(G39),
    .B(G42),
    .C(G15),
    .D(_112_),
    .X(G327)
  );
  sky130_fd_sc_hd__nand3_1 _164_ (
    .A(G39),
    .B(G40),
    .C(G42),
    .Y(_113_)
  );
  sky130_fd_sc_hd__nor3_1 _165_ (
    .A(G38),
    .B(G41),
    .C(_113_),
    .Y(G310)
  );
  sky130_fd_sc_hd__nand2b_1 _166_ (
    .A_N(G39),
    .B(G38),
    .Y(_114_)
  );
  sky130_fd_sc_hd__xnor2_1 _167_ (
    .A(G39),
    .B(G40),
    .Y(_115_)
  );
  sky130_fd_sc_hd__o21ai_0 _168_ (
    .A1(G41),
    .A2(_103_),
    .B1(_115_),
    .Y(_116_)
  );
  sky130_fd_sc_hd__a21o_1 _169_ (
    .A1(_114_),
    .A2(_116_),
    .B1(_100_),
    .X(G49)
  );
  sky130_fd_sc_hd__nand2_1 _170_ (
    .A(G1),
    .B(_080_),
    .Y(_000_)
  );
  sky130_fd_sc_hd__a21oi_1 _171_ (
    .A1(_098_),
    .A2(_113_),
    .B1(_000_),
    .Y(G322)
  );
  sky130_fd_sc_hd__and3_1 _172_ (
    .A(G16),
    .B(_092_),
    .C(_095_),
    .X(G312)
  );
  sky130_fd_sc_hd__nor4b_1 _173_ (
    .A(G16),
    .B(_099_),
    .C(G1),
    .D_N(G3),
    .Y(G300)
  );
  sky130_fd_sc_hd__and3_1 _174_ (
    .A(G15),
    .B(G14),
    .C(G53),
    .X(G298)
  );
  sky130_fd_sc_hd__nor2_1 _175_ (
    .A(_076_),
    .B(_083_),
    .Y(_001_)
  );
  sky130_fd_sc_hd__nor3_1 _176_ (
    .A(G38),
    .B(_079_),
    .C(_083_),
    .Y(G296)
  );
  sky130_fd_sc_hd__nand2_1 _177_ (
    .A(G38),
    .B(G15),
    .Y(_002_)
  );
  sky130_fd_sc_hd__nand4_1 _178_ (
    .A(G6),
    .B(G7),
    .C(G9),
    .D(G8),
    .Y(_003_)
  );
  sky130_fd_sc_hd__o21ai_0 _179_ (
    .A1(_002_),
    .A2(_003_),
    .B1(G16),
    .Y(_004_)
  );
  sky130_fd_sc_hd__nor2_1 _180_ (
    .A(G4),
    .B(_107_),
    .Y(_005_)
  );
  sky130_fd_sc_hd__and3_1 _181_ (
    .A(_092_),
    .B(_004_),
    .C(_005_),
    .X(G292)
  );
  sky130_fd_sc_hd__and4b_1 _182_ (
    .A_N(G42),
    .B(G15),
    .C(_112_),
    .D(G39),
    .X(G290)
  );
  sky130_fd_sc_hd__nor2_1 _183_ (
    .A(G42),
    .B(G15),
    .Y(_006_)
  );
  sky130_fd_sc_hd__a21oi_1 _184_ (
    .A1(G39),
    .A2(G15),
    .B1(G40),
    .Y(_007_)
  );
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _185_ (
    .A(G42),
    .SLEEP(G41),
    .X(_008_)
  );
  sky130_fd_sc_hd__o22ai_1 _186_ (
    .A1(_082_),
    .A2(_007_),
    .B1(_008_),
    .B2(G39),
    .Y(_009_)
  );
  sky130_fd_sc_hd__nand4b_1 _187_ (
    .A_N(G42),
    .B(G6),
    .C(G9),
    .D(G40),
    .Y(_010_)
  );
  sky130_fd_sc_hd__o31ai_1 _188_ (
    .A1(G7),
    .A2(G8),
    .A3(_010_),
    .B1(G15),
    .Y(_011_)
  );
  sky130_fd_sc_hd__nand2_1 _189_ (
    .A(_081_),
    .B(_011_),
    .Y(_012_)
  );
  sky130_fd_sc_hd__a21oi_1 _190_ (
    .A1(_009_),
    .A2(_012_),
    .B1(_006_),
    .Y(_013_)
  );
  sky130_fd_sc_hd__nand2_1 _191_ (
    .A(G42),
    .B(G15),
    .Y(_014_)
  );
  sky130_fd_sc_hd__and3_1 _192_ (
    .A(G42),
    .B(G15),
    .C(G13),
    .X(_015_)
  );
  sky130_fd_sc_hd__a31oi_1 _193_ (
    .A1(G39),
    .A2(_076_),
    .A3(_003_),
    .B1(_094_),
    .Y(_016_)
  );
  sky130_fd_sc_hd__o41ai_1 _194_ (
    .A1(G39),
    .A2(_102_),
    .A3(_006_),
    .A4(_015_),
    .B1(_016_),
    .Y(_017_)
  );
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _195_ (
    .A(G41),
    .SLEEP(_007_),
    .X(_018_)
  );
  sky130_fd_sc_hd__a22o_1 _196_ (
    .A1(_108_),
    .A2(_112_),
    .B1(_017_),
    .B2(_018_),
    .X(_019_)
  );
  sky130_fd_sc_hd__o21ai_0 _197_ (
    .A1(_013_),
    .A2(_019_),
    .B1(G16),
    .Y(_020_)
  );
  sky130_fd_sc_hd__nand2b_1 _198_ (
    .A_N(G39),
    .B(G4),
    .Y(_021_)
  );
  sky130_fd_sc_hd__or3_1 _199_ (
    .A(_082_),
    .B(_112_),
    .C(_021_),
    .X(_022_)
  );
  sky130_fd_sc_hd__o21ai_0 _200_ (
    .A1(G38),
    .A2(_022_),
    .B1(_106_),
    .Y(_023_)
  );
  sky130_fd_sc_hd__nor2_1 _201_ (
    .A(_075_),
    .B(G0),
    .Y(_024_)
  );
  sky130_fd_sc_hd__nand2_1 _202_ (
    .A(G39),
    .B(_024_),
    .Y(_025_)
  );
  sky130_fd_sc_hd__a21oi_1 _203_ (
    .A1(_021_),
    .A2(_025_),
    .B1(_096_),
    .Y(_026_)
  );
  sky130_fd_sc_hd__o21a_1 _204_ (
    .A1(G42),
    .A2(G5),
    .B1(_083_),
    .X(_027_)
  );
  sky130_fd_sc_hd__o21ai_0 _205_ (
    .A1(G42),
    .A2(G5),
    .B1(_083_),
    .Y(_028_)
  );
  sky130_fd_sc_hd__nor3b_1 _206_ (
    .A(G1),
    .B(G3),
    .C_N(_008_),
    .Y(_029_)
  );
  sky130_fd_sc_hd__o21ai_0 _207_ (
    .A1(_028_),
    .A2(_029_),
    .B1(_095_),
    .Y(_030_)
  );
  sky130_fd_sc_hd__a21oi_1 _208_ (
    .A1(G2),
    .A2(_027_),
    .B1(_030_),
    .Y(_031_)
  );
  sky130_fd_sc_hd__nor4_1 _209_ (
    .A(G298),
    .B(_023_),
    .C(_026_),
    .D(_031_),
    .Y(_032_)
  );
  sky130_fd_sc_hd__a21oi_1 _210_ (
    .A1(_020_),
    .A2(_032_),
    .B1(G18),
    .Y(G102)
  );
  sky130_fd_sc_hd__or3b_1 _211_ (
    .A(G1),
    .B(G3),
    .C_N(G2),
    .X(_033_)
  );
  sky130_fd_sc_hd__nand2_1 _212_ (
    .A(G42),
    .B(_033_),
    .Y(_034_)
  );
  sky130_fd_sc_hd__o21ai_0 _213_ (
    .A1(G42),
    .A2(G5),
    .B1(_034_),
    .Y(_035_)
  );
  sky130_fd_sc_hd__a22oi_1 _214_ (
    .A1(_082_),
    .A2(_033_),
    .B1(_035_),
    .B2(G39),
    .Y(_036_)
  );
  sky130_fd_sc_hd__a311oi_1 _215_ (
    .A1(G16),
    .A2(G15),
    .A3(G13),
    .B1(G4),
    .C1(G39),
    .Y(_037_)
  );
  sky130_fd_sc_hd__a21oi_1 _216_ (
    .A1(G39),
    .A2(_024_),
    .B1(_037_),
    .Y(_038_)
  );
  sky130_fd_sc_hd__nand3b_1 _217_ (
    .A_N(G41),
    .B(G16),
    .C(_014_),
    .Y(_039_)
  );
  sky130_fd_sc_hd__a21oi_1 _218_ (
    .A1(_081_),
    .A2(_039_),
    .B1(_095_),
    .Y(_040_)
  );
  sky130_fd_sc_hd__o21ai_0 _219_ (
    .A1(_092_),
    .A2(_112_),
    .B1(G16),
    .Y(_041_)
  );
  sky130_fd_sc_hd__nand4_1 _220_ (
    .A(G41),
    .B(G15),
    .C(_078_),
    .D(_082_),
    .Y(_042_)
  );
  sky130_fd_sc_hd__nand3_1 _221_ (
    .A(_022_),
    .B(_041_),
    .C(_042_),
    .Y(_043_)
  );
  sky130_fd_sc_hd__o22ai_1 _222_ (
    .A1(_096_),
    .A2(_038_),
    .B1(_040_),
    .B2(_043_),
    .Y(_044_)
  );
  sky130_fd_sc_hd__o21ai_0 _223_ (
    .A1(G41),
    .A2(_036_),
    .B1(_044_),
    .Y(_045_)
  );
  sky130_fd_sc_hd__a22o_1 _224_ (
    .A1(G41),
    .A2(_002_),
    .B1(_003_),
    .B2(G42),
    .X(_046_)
  );
  sky130_fd_sc_hd__mux2i_1 _225_ (
    .A0(G41),
    .A1(G39),
    .S(G15),
    .Y(_047_)
  );
  sky130_fd_sc_hd__nor4b_1 _226_ (
    .A(G40),
    .B(_047_),
    .C(_086_),
    .D_N(_114_),
    .Y(_048_)
  );
  sky130_fd_sc_hd__a32oi_1 _227_ (
    .A1(_093_),
    .A2(_005_),
    .A3(_039_),
    .B1(_046_),
    .B2(_048_),
    .Y(_049_)
  );
  sky130_fd_sc_hd__a21oi_1 _228_ (
    .A1(_045_),
    .A2(_049_),
    .B1(G18),
    .Y(G99)
  );
  sky130_fd_sc_hd__a22oi_1 _229_ (
    .A1(_077_),
    .A2(_104_),
    .B1(_024_),
    .B2(G42),
    .Y(_050_)
  );
  sky130_fd_sc_hd__o31ai_1 _230_ (
    .A1(_079_),
    .A2(_008_),
    .A3(_050_),
    .B1(_030_),
    .Y(_051_)
  );
  sky130_fd_sc_hd__nor3_1 _231_ (
    .A(G16),
    .B(_099_),
    .C(_033_),
    .Y(_052_)
  );
  sky130_fd_sc_hd__nor2_1 _232_ (
    .A(_051_),
    .B(_052_),
    .Y(_053_)
  );
  sky130_fd_sc_hd__a31oi_1 _233_ (
    .A1(_075_),
    .A2(G15),
    .A3(_092_),
    .B1(G40),
    .Y(_054_)
  );
  sky130_fd_sc_hd__nor2_1 _234_ (
    .A(G42),
    .B(_087_),
    .Y(_055_)
  );
  sky130_fd_sc_hd__o21ai_0 _235_ (
    .A1(G42),
    .A2(_087_),
    .B1(_084_),
    .Y(_056_)
  );
  sky130_fd_sc_hd__nor2_1 _236_ (
    .A(G39),
    .B(_086_),
    .Y(_057_)
  );
  sky130_fd_sc_hd__nand2_1 _237_ (
    .A(_056_),
    .B(_057_),
    .Y(_058_)
  );
  sky130_fd_sc_hd__or4_1 _238_ (
    .A(_102_),
    .B(_104_),
    .C(_054_),
    .D(_058_),
    .X(_059_)
  );
  sky130_fd_sc_hd__a31oi_1 _239_ (
    .A1(G15),
    .A2(_078_),
    .A3(G53),
    .B1(G292),
    .Y(_060_)
  );
  sky130_fd_sc_hd__a31oi_1 _240_ (
    .A1(_053_),
    .A2(_059_),
    .A3(_060_),
    .B1(G18),
    .Y(G96)
  );
  sky130_fd_sc_hd__o21ai_0 _241_ (
    .A1(G16),
    .A2(_092_),
    .B1(_005_),
    .Y(_061_)
  );
  sky130_fd_sc_hd__o21ai_0 _242_ (
    .A1(_085_),
    .A2(_091_),
    .B1(_055_),
    .Y(_062_)
  );
  sky130_fd_sc_hd__nand4_1 _243_ (
    .A(_084_),
    .B(_103_),
    .C(_057_),
    .D(_062_),
    .Y(_063_)
  );
  sky130_fd_sc_hd__a31oi_1 _244_ (
    .A1(_053_),
    .A2(_061_),
    .A3(_063_),
    .B1(G18),
    .Y(G93)
  );
  sky130_fd_sc_hd__nor3_1 _245_ (
    .A(G38),
    .B(G16),
    .C(G1),
    .Y(_064_)
  );
  sky130_fd_sc_hd__a21oi_1 _246_ (
    .A1(G0),
    .A2(_102_),
    .B1(_064_),
    .Y(_065_)
  );
  sky130_fd_sc_hd__nand2_1 _247_ (
    .A(G38),
    .B(G16),
    .Y(_066_)
  );
  sky130_fd_sc_hd__nand2_1 _248_ (
    .A(G42),
    .B(_066_),
    .Y(_067_)
  );
  sky130_fd_sc_hd__nand3_1 _249_ (
    .A(_112_),
    .B(_065_),
    .C(_067_),
    .Y(_068_)
  );
  sky130_fd_sc_hd__a21o_1 _250_ (
    .A1(_090_),
    .A2(_068_),
    .B1(G39),
    .X(_069_)
  );
  sky130_fd_sc_hd__a21o_1 _251_ (
    .A1(G40),
    .A2(G41),
    .B1(G39),
    .X(_070_)
  );
  sky130_fd_sc_hd__nor4b_1 _252_ (
    .A(_075_),
    .B(_001_),
    .C(_086_),
    .D_N(_113_),
    .Y(_071_)
  );
  sky130_fd_sc_hd__a21oi_1 _253_ (
    .A1(G1),
    .A2(_080_),
    .B1(_024_),
    .Y(_072_)
  );
  sky130_fd_sc_hd__nor3_1 _254_ (
    .A(_104_),
    .B(_113_),
    .C(_072_),
    .Y(_073_)
  );
  sky130_fd_sc_hd__o21ai_0 _255_ (
    .A1(_071_),
    .A2(_073_),
    .B1(_070_),
    .Y(_074_)
  );
  sky130_fd_sc_hd__a21oi_1 _256_ (
    .A1(_069_),
    .A2(_074_),
    .B1(G18),
    .Y(G90)
  );
  dff DFF_0 (
    .CK(CK),
    .D(G90),
    .Q(G38)
  );
  dff DFF_1 (
    .CK(CK),
    .D(G93),
    .Q(G39)
  );
  dff DFF_2 (
    .CK(CK),
    .D(G96),
    .Q(G40)
  );
  dff DFF_3 (
    .CK(CK),
    .D(G99),
    .Q(G41)
  );
  dff DFF_4 (
    .CK(CK),
    .D(G102),
    .Q(G42)
  );
  assign G325 = G310;
endmodule