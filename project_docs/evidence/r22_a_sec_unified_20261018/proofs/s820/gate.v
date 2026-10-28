module s820(GND, VDD, CK, G0, G1, G10, G11, G12, G13, G14, G15, G16, G18, G2, G288, G290, G292, G296, G298, G3, G300
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
  wire G102;
  wire G228;
  wire G229;
  wire G247;
  wire G38;
  wire G39;
  wire G40;
  wire G41;
  wire G42;
  wire G90;
  wire G93;
  wire G96;
  wire G99;
  wire II133;
  sky130_fd_sc_hd__clkinv_1 _110_ (
    .A(G39),
    .Y(_072_)
  );
  sky130_fd_sc_hd__clkinv_1 _111_ (
    .A(G228),
    .Y(_073_)
  );
  sky130_fd_sc_hd__clkinv_1 _112_ (
    .A(G16),
    .Y(_074_)
  );
  sky130_fd_sc_hd__and2_0 _113_ (
    .A(G40),
    .B(G39),
    .X(_075_)
  );
  sky130_fd_sc_hd__nand2_1 _114_ (
    .A(_073_),
    .B(_075_),
    .Y(_076_)
  );
  sky130_fd_sc_hd__nor3_1 _115_ (
    .A(G42),
    .B(G41),
    .C(_076_),
    .Y(G288)
  );
  sky130_fd_sc_hd__lpflow_inputiso1p_1 _116_ (
    .A(G42),
    .SLEEP(G5),
    .X(_077_)
  );
  sky130_fd_sc_hd__nor3_1 _117_ (
    .A(G41),
    .B(_076_),
    .C(_077_),
    .Y(G47)
  );
  sky130_fd_sc_hd__nand2b_1 _118_ (
    .A_N(G42),
    .B(G41),
    .Y(_078_)
  );
  sky130_fd_sc_hd__nor2_1 _119_ (
    .A(_076_),
    .B(_078_),
    .Y(G296)
  );
  sky130_fd_sc_hd__nand2_1 _120_ (
    .A(G42),
    .B(_075_),
    .Y(_079_)
  );
  sky130_fd_sc_hd__or2b_2 _121_ (
    .A(G41),
    .B_N(G42),
    .X(_080_)
  );
  sky130_fd_sc_hd__nor2_1 _122_ (
    .A(_076_),
    .B(_080_),
    .Y(G310)
  );
  sky130_fd_sc_hd__nor2_1 _123_ (
    .A(G39),
    .B(G228),
    .Y(_081_)
  );
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _124_ (
    .A(G41),
    .SLEEP(G40),
    .X(_082_)
  );
  sky130_fd_sc_hd__and3b_1 _125_ (
    .A_N(G42),
    .B(_081_),
    .C(_082_),
    .X(G53)
  );
  sky130_fd_sc_hd__and2_0 _126_ (
    .A(G15),
    .B(G53),
    .X(G43)
  );
  sky130_fd_sc_hd__nand2_1 _127_ (
    .A(G15),
    .B(G39),
    .Y(_083_)
  );
  sky130_fd_sc_hd__nor2_1 _128_ (
    .A(G40),
    .B(G41),
    .Y(_084_)
  );
  sky130_fd_sc_hd__nor3_1 _129_ (
    .A(G40),
    .B(_080_),
    .C(_083_),
    .Y(G327)
  );
  sky130_fd_sc_hd__lpflow_inputiso1p_1 _130_ (
    .A(G40),
    .SLEEP(G42),
    .X(_085_)
  );
  sky130_fd_sc_hd__nor3_1 _131_ (
    .A(G41),
    .B(_083_),
    .C(_085_),
    .Y(G290)
  );
  sky130_fd_sc_hd__nor2_1 _132_ (
    .A(G40),
    .B(G39),
    .Y(_086_)
  );
  sky130_fd_sc_hd__or4_1 _133_ (
    .A(G39),
    .B(G228),
    .C(G41),
    .D(_085_),
    .X(_087_)
  );
  sky130_fd_sc_hd__nor4b_1 _134_ (
    .A(G16),
    .B(_087_),
    .C(G1),
    .D_N(G3),
    .Y(G300)
  );
  sky130_fd_sc_hd__nor2_1 _135_ (
    .A(_074_),
    .B(G4),
    .Y(_088_)
  );
  sky130_fd_sc_hd__nand2_1 _136_ (
    .A(G40),
    .B(G41),
    .Y(_089_)
  );
  sky130_fd_sc_hd__nand3_1 _137_ (
    .A(G40),
    .B(G42),
    .C(G41),
    .Y(_090_)
  );
  sky130_fd_sc_hd__and2_0 _138_ (
    .A(G42),
    .B(G41),
    .X(_091_)
  );
  sky130_fd_sc_hd__nand2_1 _139_ (
    .A(G42),
    .B(G41),
    .Y(_092_)
  );
  sky130_fd_sc_hd__o2111a_1 _140_ (
    .A1(G40),
    .A2(_073_),
    .B1(G42),
    .C1(G41),
    .D1(_072_),
    .X(_093_)
  );
  sky130_fd_sc_hd__a21oi_1 _141_ (
    .A1(G40),
    .A2(_081_),
    .B1(_093_),
    .Y(_094_)
  );
  sky130_fd_sc_hd__nand2b_1 _142_ (
    .A_N(G42),
    .B(G228),
    .Y(_095_)
  );
  sky130_fd_sc_hd__nand2b_1 _143_ (
    .A_N(G41),
    .B(G228),
    .Y(_096_)
  );
  sky130_fd_sc_hd__o21ai_0 _144_ (
    .A1(G41),
    .A2(_095_),
    .B1(G40),
    .Y(_097_)
  );
  sky130_fd_sc_hd__and3_1 _145_ (
    .A(G39),
    .B(G4),
    .C(_097_),
    .X(_098_)
  );
  sky130_fd_sc_hd__nand2b_1 _146_ (
    .A_N(G40),
    .B(G39),
    .Y(_099_)
  );
  sky130_fd_sc_hd__nor3_1 _147_ (
    .A(G16),
    .B(_091_),
    .C(_099_),
    .Y(_100_)
  );
  sky130_fd_sc_hd__nor3_1 _148_ (
    .A(_074_),
    .B(G1),
    .C(_087_),
    .Y(_101_)
  );
  sky130_fd_sc_hd__nor3_1 _149_ (
    .A(_098_),
    .B(_100_),
    .C(_101_),
    .Y(_102_)
  );
  sky130_fd_sc_hd__o21ai_0 _150_ (
    .A1(_088_),
    .A2(_094_),
    .B1(_102_),
    .Y(G302)
  );
  sky130_fd_sc_hd__nand2_1 _151_ (
    .A(_072_),
    .B(G228),
    .Y(_103_)
  );
  sky130_fd_sc_hd__o22ai_1 _152_ (
    .A1(_075_),
    .A2(_086_),
    .B1(_095_),
    .B2(G41),
    .Y(_104_)
  );
  sky130_fd_sc_hd__a21o_1 _153_ (
    .A1(_103_),
    .A2(_104_),
    .B1(_093_),
    .X(G49)
  );
  sky130_fd_sc_hd__o21ai_0 _154_ (
    .A1(_076_),
    .A2(_092_),
    .B1(_087_),
    .Y(G315)
  );
  sky130_fd_sc_hd__nor3_1 _155_ (
    .A(_074_),
    .B(_076_),
    .C(_092_),
    .Y(G312)
  );
  sky130_fd_sc_hd__and4_1 _156_ (
    .A(G9),
    .B(G6),
    .C(G8),
    .D(G7),
    .X(_105_)
  );
  sky130_fd_sc_hd__nand3_1 _157_ (
    .A(G15),
    .B(G228),
    .C(_105_),
    .Y(_106_)
  );
  sky130_fd_sc_hd__nor2_1 _158_ (
    .A(G4),
    .B(_099_),
    .Y(_107_)
  );
  sky130_fd_sc_hd__nand2_1 _159_ (
    .A(_091_),
    .B(_107_),
    .Y(_108_)
  );
  sky130_fd_sc_hd__a21oi_1 _160_ (
    .A1(G16),
    .A2(_106_),
    .B1(_108_),
    .Y(G292)
  );
  sky130_fd_sc_hd__and3_1 _161_ (
    .A(G15),
    .B(G14),
    .C(G53),
    .X(G298)
  );
  sky130_fd_sc_hd__nor3_1 _162_ (
    .A(G40),
    .B(G41),
    .C(G1),
    .Y(_109_)
  );
  sky130_fd_sc_hd__nor2_1 _163_ (
    .A(G8),
    .B(G7),
    .Y(_000_)
  );
  sky130_fd_sc_hd__a41o_1 _164_ (
    .A1(G15),
    .A2(G9),
    .A3(G6),
    .A4(_000_),
    .B1(G42),
    .X(_001_)
  );
  sky130_fd_sc_hd__nand2_1 _165_ (
    .A(G15),
    .B(G42),
    .Y(_002_)
  );
  sky130_fd_sc_hd__a31oi_1 _166_ (
    .A1(_085_),
    .A2(_001_),
    .A3(_002_),
    .B1(_109_),
    .Y(_003_)
  );
  sky130_fd_sc_hd__nor3_1 _167_ (
    .A(G39),
    .B(G228),
    .C(_003_),
    .Y(_004_)
  );
  sky130_fd_sc_hd__a21oi_1 _168_ (
    .A1(G15),
    .A2(_073_),
    .B1(G42),
    .Y(_005_)
  );
  sky130_fd_sc_hd__a31oi_1 _169_ (
    .A1(G15),
    .A2(G42),
    .A3(G13),
    .B1(_005_),
    .Y(_006_)
  );
  sky130_fd_sc_hd__o211ai_1 _170_ (
    .A1(G40),
    .A2(_105_),
    .B1(G228),
    .C1(G39),
    .Y(_007_)
  );
  sky130_fd_sc_hd__nand2b_1 _171_ (
    .A_N(G40),
    .B(_083_),
    .Y(_008_)
  );
  sky130_fd_sc_hd__o2111a_1 _172_ (
    .A1(G39),
    .A2(_006_),
    .B1(_007_),
    .C1(_008_),
    .D1(G41),
    .X(_009_)
  );
  sky130_fd_sc_hd__o21ai_0 _173_ (
    .A1(G15),
    .A2(G42),
    .B1(G39),
    .Y(_010_)
  );
  sky130_fd_sc_hd__a22oi_1 _174_ (
    .A1(_085_),
    .A2(_008_),
    .B1(_010_),
    .B2(_080_),
    .Y(_011_)
  );
  sky130_fd_sc_hd__o31ai_1 _175_ (
    .A1(_004_),
    .A2(_009_),
    .A3(_011_),
    .B1(G16),
    .Y(_012_)
  );
  sky130_fd_sc_hd__nand3b_1 _176_ (
    .A_N(_084_),
    .B(_085_),
    .C(G4),
    .Y(_013_)
  );
  sky130_fd_sc_hd__nor3_1 _177_ (
    .A(G39),
    .B(G228),
    .C(_013_),
    .Y(_014_)
  );
  sky130_fd_sc_hd__nor2_1 _178_ (
    .A(_073_),
    .B(G0),
    .Y(_015_)
  );
  sky130_fd_sc_hd__nor2_1 _179_ (
    .A(G39),
    .B(G4),
    .Y(_016_)
  );
  sky130_fd_sc_hd__a2111oi_0 _180_ (
    .A1(G39),
    .A2(G0),
    .B1(_090_),
    .C1(_016_),
    .D1(_073_),
    .Y(_017_)
  );
  sky130_fd_sc_hd__nor3_1 _181_ (
    .A(_098_),
    .B(_014_),
    .C(_017_),
    .Y(_018_)
  );
  sky130_fd_sc_hd__nand3_1 _182_ (
    .A(G2),
    .B(_077_),
    .C(_078_),
    .Y(_019_)
  );
  sky130_fd_sc_hd__nor2_1 _183_ (
    .A(G1),
    .B(G3),
    .Y(_020_)
  );
  sky130_fd_sc_hd__nand2b_1 _184_ (
    .A_N(_080_),
    .B(_020_),
    .Y(_021_)
  );
  sky130_fd_sc_hd__a31oi_1 _185_ (
    .A1(_077_),
    .A2(_078_),
    .A3(_021_),
    .B1(_076_),
    .Y(_022_)
  );
  sky130_fd_sc_hd__a21oi_1 _186_ (
    .A1(_019_),
    .A2(_022_),
    .B1(G298),
    .Y(_023_)
  );
  sky130_fd_sc_hd__a31oi_1 _187_ (
    .A1(_012_),
    .A2(_018_),
    .A3(_023_),
    .B1(G18),
    .Y(G102)
  );
  sky130_fd_sc_hd__nand3b_1 _188_ (
    .A_N(G41),
    .B(G16),
    .C(_002_),
    .Y(_024_)
  );
  sky130_fd_sc_hd__a21oi_1 _189_ (
    .A1(_013_),
    .A2(_024_),
    .B1(G39),
    .Y(_025_)
  );
  sky130_fd_sc_hd__nand2_1 _190_ (
    .A(G2),
    .B(_020_),
    .Y(_026_)
  );
  sky130_fd_sc_hd__o22ai_1 _191_ (
    .A1(_072_),
    .A2(_080_),
    .B1(_085_),
    .B2(G41),
    .Y(_027_)
  );
  sky130_fd_sc_hd__o21ai_0 _192_ (
    .A1(_084_),
    .A2(_091_),
    .B1(G16),
    .Y(_028_)
  );
  sky130_fd_sc_hd__nand2_1 _193_ (
    .A(G15),
    .B(G41),
    .Y(_029_)
  );
  sky130_fd_sc_hd__nor3_1 _194_ (
    .A(G14),
    .B(_085_),
    .C(_029_),
    .Y(_030_)
  );
  sky130_fd_sc_hd__nor2_1 _195_ (
    .A(_072_),
    .B(G41),
    .Y(_031_)
  );
  sky130_fd_sc_hd__nor3_1 _196_ (
    .A(_072_),
    .B(G41),
    .C(_077_),
    .Y(_032_)
  );
  sky130_fd_sc_hd__a2111oi_0 _197_ (
    .A1(_026_),
    .A2(_027_),
    .B1(_030_),
    .C1(_032_),
    .D1(_025_),
    .Y(_033_)
  );
  sky130_fd_sc_hd__nand4_1 _198_ (
    .A(_073_),
    .B(_099_),
    .C(_028_),
    .D(_033_),
    .Y(_034_)
  );
  sky130_fd_sc_hd__nand3_1 _199_ (
    .A(G15),
    .B(G16),
    .C(G13),
    .Y(_035_)
  );
  sky130_fd_sc_hd__a22oi_1 _200_ (
    .A1(G39),
    .A2(_015_),
    .B1(_016_),
    .B2(_035_),
    .Y(_036_)
  );
  sky130_fd_sc_hd__nor2_1 _201_ (
    .A(_090_),
    .B(_036_),
    .Y(_037_)
  );
  sky130_fd_sc_hd__o21ai_0 _202_ (
    .A1(G15),
    .A2(G228),
    .B1(_072_),
    .Y(_038_)
  );
  sky130_fd_sc_hd__nand4_1 _203_ (
    .A(_082_),
    .B(_088_),
    .C(_106_),
    .D(_038_),
    .Y(_039_)
  );
  sky130_fd_sc_hd__nand3_1 _204_ (
    .A(G16),
    .B(_002_),
    .C(_029_),
    .Y(_040_)
  );
  sky130_fd_sc_hd__a31oi_1 _205_ (
    .A1(_092_),
    .A2(_107_),
    .A3(_040_),
    .B1(_037_),
    .Y(_041_)
  );
  sky130_fd_sc_hd__a31oi_1 _206_ (
    .A1(_034_),
    .A2(_039_),
    .A3(_041_),
    .B1(G18),
    .Y(G99)
  );
  sky130_fd_sc_hd__nand2_1 _207_ (
    .A(G42),
    .B(_015_),
    .Y(_042_)
  );
  sky130_fd_sc_hd__o21ai_0 _208_ (
    .A1(G4),
    .A2(_096_),
    .B1(_042_),
    .Y(_043_)
  );
  sky130_fd_sc_hd__nor3_1 _209_ (
    .A(G16),
    .B(_087_),
    .C(_026_),
    .Y(_044_)
  );
  sky130_fd_sc_hd__a311oi_1 _210_ (
    .A1(_075_),
    .A2(_080_),
    .A3(_043_),
    .B1(_044_),
    .C1(_022_),
    .Y(_045_)
  );
  sky130_fd_sc_hd__a31o_1 _211_ (
    .A1(G15),
    .A2(_073_),
    .A3(_091_),
    .B1(G40),
    .X(_046_)
  );
  sky130_fd_sc_hd__o21bai_1 _212_ (
    .A1(G11),
    .A2(G10),
    .B1_N(G42),
    .Y(_047_)
  );
  sky130_fd_sc_hd__nand4_1 _213_ (
    .A(G40),
    .B(G15),
    .C(G41),
    .D(_047_),
    .Y(_048_)
  );
  sky130_fd_sc_hd__and3_1 _214_ (
    .A(G16),
    .B(_095_),
    .C(_016_),
    .X(_049_)
  );
  sky130_fd_sc_hd__nand4_1 _215_ (
    .A(_096_),
    .B(_046_),
    .C(_048_),
    .D(_049_),
    .Y(_050_)
  );
  sky130_fd_sc_hd__a21oi_1 _216_ (
    .A1(_081_),
    .A2(_030_),
    .B1(G292),
    .Y(_051_)
  );
  sky130_fd_sc_hd__a31oi_1 _217_ (
    .A1(_045_),
    .A2(_050_),
    .A3(_051_),
    .B1(G18),
    .Y(G96)
  );
  sky130_fd_sc_hd__a211o_1 _218_ (
    .A1(G11),
    .A2(G10),
    .B1(G12),
    .C1(_047_),
    .X(_052_)
  );
  sky130_fd_sc_hd__nand4b_1 _219_ (
    .A_N(_089_),
    .B(_052_),
    .C(_049_),
    .D(G15),
    .Y(_053_)
  );
  sky130_fd_sc_hd__o21ai_0 _220_ (
    .A1(G16),
    .A2(_091_),
    .B1(_107_),
    .Y(_054_)
  );
  sky130_fd_sc_hd__a31oi_1 _221_ (
    .A1(_045_),
    .A2(_053_),
    .A3(_054_),
    .B1(G18),
    .Y(G93)
  );
  sky130_fd_sc_hd__o21ai_0 _222_ (
    .A1(G11),
    .A2(G12),
    .B1(G15),
    .Y(_055_)
  );
  sky130_fd_sc_hd__nor2_1 _223_ (
    .A(_047_),
    .B(_055_),
    .Y(_056_)
  );
  sky130_fd_sc_hd__nand4_1 _224_ (
    .A(G40),
    .B(G41),
    .C(_081_),
    .D(_056_),
    .Y(_057_)
  );
  sky130_fd_sc_hd__a21boi_0 _225_ (
    .A1(G39),
    .A2(_089_),
    .B1_N(_090_),
    .Y(_058_)
  );
  sky130_fd_sc_hd__nand2_1 _226_ (
    .A(G228),
    .B(_079_),
    .Y(_059_)
  );
  sky130_fd_sc_hd__o21ai_0 _227_ (
    .A1(_058_),
    .A2(_059_),
    .B1(_057_),
    .Y(_060_)
  );
  sky130_fd_sc_hd__nand2_1 _228_ (
    .A(_088_),
    .B(_060_),
    .Y(_061_)
  );
  sky130_fd_sc_hd__nand2_1 _229_ (
    .A(G228),
    .B(G16),
    .Y(_062_)
  );
  sky130_fd_sc_hd__nor3_1 _230_ (
    .A(G228),
    .B(G16),
    .C(G1),
    .Y(_063_)
  );
  sky130_fd_sc_hd__lpflow_inputiso1p_1 _231_ (
    .A(_095_),
    .SLEEP(_015_),
    .X(_064_)
  );
  sky130_fd_sc_hd__a21oi_1 _232_ (
    .A1(G42),
    .A2(_062_),
    .B1(_063_),
    .Y(_065_)
  );
  sky130_fd_sc_hd__nand4_1 _233_ (
    .A(_072_),
    .B(_084_),
    .C(_064_),
    .D(_065_),
    .Y(_066_)
  );
  sky130_fd_sc_hd__a22o_1 _234_ (
    .A1(G39),
    .A2(_015_),
    .B1(_031_),
    .B2(G1),
    .X(_067_)
  );
  sky130_fd_sc_hd__nand4_1 _235_ (
    .A(G40),
    .B(G42),
    .C(_096_),
    .D(_067_),
    .Y(_068_)
  );
  sky130_fd_sc_hd__a31oi_1 _236_ (
    .A1(_061_),
    .A2(_066_),
    .A3(_068_),
    .B1(G18),
    .Y(G90)
  );
  sky130_fd_sc_hd__and2_0 _237_ (
    .A(G5),
    .B(G288),
    .X(G55)
  );
  sky130_fd_sc_hd__o21ai_0 _238_ (
    .A1(G10),
    .A2(G12),
    .B1(_088_),
    .Y(_069_)
  );
  sky130_fd_sc_hd__nor2_1 _239_ (
    .A(_057_),
    .B(_069_),
    .Y(G45)
  );
  sky130_fd_sc_hd__o21ai_0 _240_ (
    .A1(G39),
    .A2(_085_),
    .B1(_079_),
    .Y(_070_)
  );
  sky130_fd_sc_hd__nand2_1 _241_ (
    .A(G1),
    .B(_070_),
    .Y(_071_)
  );
  sky130_fd_sc_hd__nor3_1 _242_ (
    .A(G228),
    .B(G41),
    .C(_071_),
    .Y(G322)
  );
  dff DFF_0 (
    .CK(CK),
    .D(G90),
    .Q(G228)
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
  assign G247 = G228;
  assign II133 = G41;
  assign G229 = G15;
  assign G38 = G228;
  assign G325 = G310;
endmodule