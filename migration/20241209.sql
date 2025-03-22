pairs = [x.split("\t") for x in """
0002458	AF0311
0003448	AF0537
0004426	AF0063
0010234	AF0390
0027028	AF0123
0102446	AF0535
1211053	AF0433
0103291	AF0540
0105417	AF0533
0106210	AF0284
0110029	AF0491
0122009	AF0125
0201348	AF0543
0204081	AF0113
0208052	AF0493
0303060	AF0541
0303423	AF0097
0304407	AF0110
0305048	AF0214
0306487	AF0507
0311068	AF0544
0331003	AF0506
0404464	AF0521
0406544	AF0315
0407149	AF0496
0408003	AF0534
0428090	AF0426
0431033	AF0510
0505435	AF0461
0507697	AC0014
0511312	AF0145
0603187	AF0300
0701207	AF0044
0702093	
0703230	AF0038
0707539	AF0448
0709147	AF0539
0802015	AF0505
0802081	AF0280
0807283	AF0003
0910194	AF0120
0911196	AF0211
1001039	AF0114
1003495	AF0509
1010105	AF0514
1010139	AF0194
1010257	AF0508
1010262	AF0407
1010449	AF0313
1011080	AF0258
1011246	AF0503
1011266	AF0532
1011329	AF0221
1012077	AF0518
1012100	AF0149
1101048	
1105117	AF0546
1111176	AF0039
1111210	AF0348
1112053	AF0341
1201023	AF0010
1205511	AF0058
1205534	AF0413
1205864	AF0002
1207802	AF0229
1209172	AF0210
1209184	AF0494
1312017	AF0202
1312066	AF0066
1403311	AF0064
1409259	AF0498
1410114	AF0319
1410118	
1411271	AF0152
1411284	AF0143
1502020	AF0385
1504234	AF0501
1505509	
1506291	AF0035
1509004	AF0032
1509006	AF0453
1509183	AF0134
1509188	AF0061
1609112	AF0122
1609114	AF0397
1704147	AF0492
1705019	AF0454
1706037	AF0439
1706166	AF0446
1711204	AF0244
1805286	AF0195
1807358	AF0324
1807458	
1811087	AC0021
1901051	AF0099
1905007	AF0241
1908043	AF0136
1910040	AF0427
1912029	AF0247
2003058	AF0007
2007176	AF0118
2009012	AF0268
2009096	AF0394
2012038	AF0012
2012116	AF0252
2101013	
2101054	AF0266
2101080	
2101090	AF0421
2102114	AF0435
2103061	AF0531
2103179	
2105104	AF0523
2106003	AF0027
2106051	AF0107
2107338	AF0405
2107340	AF0082
2107341	AF0261
2108120	AF0410
2108246	
2108292	AF0517
2109033	AF0549
2109227	
2109235	
2111071	AF0049
2112049	AF0502
2201013	AF0538
2202074	AF0526
2202076	AF0432
2202111	AF0406
2204253	AF0392
2205262	AF0449
2206027	AF0232
2206167	AF0425
2207215	
2207249	AF0036
2208047	AF0253
2208074	AF0320
2208099	
2209046	
2209074	AF0019
2209098	AF0547
2209100	AF0254
2209114	AF0087
2209116	AF0312
2210016	AF0337
2210045	AF0077
2211013	AF0051
2212004	AF0094
2304034	AF0424
2307103	AF0014
2307106	AF0369
2307144	AF0366
2307147	
2307168	
2308066	AF0298
2308151	AF0008
2308154	AF0228
2308161	AF0084
2309024	
2309109	AF0511
2309111	AF0331
2309112	
2310087	AF0515
2311065	AF0004
2403023	AF0462
2403109	AF0070
2404020	AF0499
2405096	AF0273
2408007	
2408042	AF0522
2409080	AF0497
2409127	AF0525
2409199	AF0550
9803403	AF0379
9805401	AF0542
9812209	AF0092
2309021	AF0548
HQ21040	AF0516
HQ21046	AF0203
HQ21174	AF0308
HQ21204	AF0275
HQ21251	AF0277
HQ21277	AF0520
HQ21287	
HQ21315	AF0230
HQ21341	AF0236
HQ21364	AF0356
HQ21366	AF0175
HQ21369	AF0196
HQ21375	AF0471
HQ22070	AF0205
HQ22074	AF0200
HQ22086	AF0267
HQ23019	AF0349
HQ23026	AF0174
HQ23027	AF0513
HQ23028	
HQ23029	AF0199
HQ23029	AF0199
HQ23031	AF0154
HQ23047	AF0519
HQ23059	AF0256
HQ23061	AF0354
HQ24028	AF0512
HQ24069	
O2312007	AF0545
徐弘迪	
劉匡祥	
0602670	AF0093

""".strip().split('\n')]

for pair in pairs:
    if len(pair) != 2:
        continue
    if pair[1] == "":
        continue
    print(f"update measure.infos set subject_id = (select id from measure.subjects where upper(number) = '{pair[1]}')\nwhere number = '{pair[0]}' and (select id from measure.subjects where upper(number) = '{pair[1]}') is not null;")



begin;

update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0311')
where number = '0002458' and (select id from measure.subjects where upper(number) = 'AF0311') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0537')
where number = '0003448' and (select id from measure.subjects where upper(number) = 'AF0537') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0063')
where number = '0004426' and (select id from measure.subjects where upper(number) = 'AF0063') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0390')
where number = '0010234' and (select id from measure.subjects where upper(number) = 'AF0390') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0123')
where number = '0027028' and (select id from measure.subjects where upper(number) = 'AF0123') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0535')
where number = '0102446' and (select id from measure.subjects where upper(number) = 'AF0535') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0433')
where number = '1211053' and (select id from measure.subjects where upper(number) = 'AF0433') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0540')
where number = '0103291' and (select id from measure.subjects where upper(number) = 'AF0540') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0533')
where number = '0105417' and (select id from measure.subjects where upper(number) = 'AF0533') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0284')
where number = '0106210' and (select id from measure.subjects where upper(number) = 'AF0284') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0491')
where number = '0110029' and (select id from measure.subjects where upper(number) = 'AF0491') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0125')
where number = '0122009' and (select id from measure.subjects where upper(number) = 'AF0125') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0543')
where number = '0201348' and (select id from measure.subjects where upper(number) = 'AF0543') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0113')
where number = '0204081' and (select id from measure.subjects where upper(number) = 'AF0113') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0493')
where number = '0208052' and (select id from measure.subjects where upper(number) = 'AF0493') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0541')
where number = '0303060' and (select id from measure.subjects where upper(number) = 'AF0541') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0097')
where number = '0303423' and (select id from measure.subjects where upper(number) = 'AF0097') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0110')
where number = '0304407' and (select id from measure.subjects where upper(number) = 'AF0110') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0214')
where number = '0305048' and (select id from measure.subjects where upper(number) = 'AF0214') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0507')
where number = '0306487' and (select id from measure.subjects where upper(number) = 'AF0507') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0544')
where number = '0311068' and (select id from measure.subjects where upper(number) = 'AF0544') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0506')
where number = '0331003' and (select id from measure.subjects where upper(number) = 'AF0506') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0521')
where number = '0404464' and (select id from measure.subjects where upper(number) = 'AF0521') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0315')
where number = '0406544' and (select id from measure.subjects where upper(number) = 'AF0315') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0496')
where number = '0407149' and (select id from measure.subjects where upper(number) = 'AF0496') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0534')
where number = '0408003' and (select id from measure.subjects where upper(number) = 'AF0534') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0426')
where number = '0428090' and (select id from measure.subjects where upper(number) = 'AF0426') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0510')
where number = '0431033' and (select id from measure.subjects where upper(number) = 'AF0510') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0461')
where number = '0505435' and (select id from measure.subjects where upper(number) = 'AF0461') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AC0014')
where number = '0507697' and (select id from measure.subjects where upper(number) = 'AC0014') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0145')
where number = '0511312' and (select id from measure.subjects where upper(number) = 'AF0145') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0300')
where number = '0603187' and (select id from measure.subjects where upper(number) = 'AF0300') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0044')
where number = '0701207' and (select id from measure.subjects where upper(number) = 'AF0044') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0038')
where number = '0703230' and (select id from measure.subjects where upper(number) = 'AF0038') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0448')
where number = '0707539' and (select id from measure.subjects where upper(number) = 'AF0448') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0539')
where number = '0709147' and (select id from measure.subjects where upper(number) = 'AF0539') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0505')
where number = '0802015' and (select id from measure.subjects where upper(number) = 'AF0505') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0280')
where number = '0802081' and (select id from measure.subjects where upper(number) = 'AF0280') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0003')
where number = '0807283' and (select id from measure.subjects where upper(number) = 'AF0003') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0120')
where number = '0910194' and (select id from measure.subjects where upper(number) = 'AF0120') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0211')
where number = '0911196' and (select id from measure.subjects where upper(number) = 'AF0211') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0114')
where number = '1001039' and (select id from measure.subjects where upper(number) = 'AF0114') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0509')
where number = '1003495' and (select id from measure.subjects where upper(number) = 'AF0509') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0514')
where number = '1010105' and (select id from measure.subjects where upper(number) = 'AF0514') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0194')
where number = '1010139' and (select id from measure.subjects where upper(number) = 'AF0194') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0508')
where number = '1010257' and (select id from measure.subjects where upper(number) = 'AF0508') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0407')
where number = '1010262' and (select id from measure.subjects where upper(number) = 'AF0407') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0313')
where number = '1010449' and (select id from measure.subjects where upper(number) = 'AF0313') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0258')
where number = '1011080' and (select id from measure.subjects where upper(number) = 'AF0258') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0503')
where number = '1011246' and (select id from measure.subjects where upper(number) = 'AF0503') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0532')
where number = '1011266' and (select id from measure.subjects where upper(number) = 'AF0532') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0221')
where number = '1011329' and (select id from measure.subjects where upper(number) = 'AF0221') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0518')
where number = '1012077' and (select id from measure.subjects where upper(number) = 'AF0518') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0149')
where number = '1012100' and (select id from measure.subjects where upper(number) = 'AF0149') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0546')
where number = '1105117' and (select id from measure.subjects where upper(number) = 'AF0546') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0039')
where number = '1111176' and (select id from measure.subjects where upper(number) = 'AF0039') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0348')
where number = '1111210' and (select id from measure.subjects where upper(number) = 'AF0348') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0341')
where number = '1112053' and (select id from measure.subjects where upper(number) = 'AF0341') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0010')
where number = '1201023' and (select id from measure.subjects where upper(number) = 'AF0010') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0058')
where number = '1205511' and (select id from measure.subjects where upper(number) = 'AF0058') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0413')
where number = '1205534' and (select id from measure.subjects where upper(number) = 'AF0413') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0002')
where number = '1205864' and (select id from measure.subjects where upper(number) = 'AF0002') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0229')
where number = '1207802' and (select id from measure.subjects where upper(number) = 'AF0229') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0210')
where number = '1209172' and (select id from measure.subjects where upper(number) = 'AF0210') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0494')
where number = '1209184' and (select id from measure.subjects where upper(number) = 'AF0494') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0202')
where number = '1312017' and (select id from measure.subjects where upper(number) = 'AF0202') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0066')
where number = '1312066' and (select id from measure.subjects where upper(number) = 'AF0066') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0064')
where number = '1403311' and (select id from measure.subjects where upper(number) = 'AF0064') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0498')
where number = '1409259' and (select id from measure.subjects where upper(number) = 'AF0498') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0319')
where number = '1410114' and (select id from measure.subjects where upper(number) = 'AF0319') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0152')
where number = '1411271' and (select id from measure.subjects where upper(number) = 'AF0152') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0143')
where number = '1411284' and (select id from measure.subjects where upper(number) = 'AF0143') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0385')
where number = '1502020' and (select id from measure.subjects where upper(number) = 'AF0385') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0501')
where number = '1504234' and (select id from measure.subjects where upper(number) = 'AF0501') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0035')
where number = '1506291' and (select id from measure.subjects where upper(number) = 'AF0035') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0032')
where number = '1509004' and (select id from measure.subjects where upper(number) = 'AF0032') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0453')
where number = '1509006' and (select id from measure.subjects where upper(number) = 'AF0453') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0134')
where number = '1509183' and (select id from measure.subjects where upper(number) = 'AF0134') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0061')
where number = '1509188' and (select id from measure.subjects where upper(number) = 'AF0061') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0122')
where number = '1609112' and (select id from measure.subjects where upper(number) = 'AF0122') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0397')
where number = '1609114' and (select id from measure.subjects where upper(number) = 'AF0397') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0492')
where number = '1704147' and (select id from measure.subjects where upper(number) = 'AF0492') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0454')
where number = '1705019' and (select id from measure.subjects where upper(number) = 'AF0454') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0439')
where number = '1706037' and (select id from measure.subjects where upper(number) = 'AF0439') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0446')
where number = '1706166' and (select id from measure.subjects where upper(number) = 'AF0446') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0244')
where number = '1711204' and (select id from measure.subjects where upper(number) = 'AF0244') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0195')
where number = '1805286' and (select id from measure.subjects where upper(number) = 'AF0195') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0324')
where number = '1807358' and (select id from measure.subjects where upper(number) = 'AF0324') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AC0021')
where number = '1811087' and (select id from measure.subjects where upper(number) = 'AC0021') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0099')
where number = '1901051' and (select id from measure.subjects where upper(number) = 'AF0099') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0241')
where number = '1905007' and (select id from measure.subjects where upper(number) = 'AF0241') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0136')
where number = '1908043' and (select id from measure.subjects where upper(number) = 'AF0136') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0427')
where number = '1910040' and (select id from measure.subjects where upper(number) = 'AF0427') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0247')
where number = '1912029' and (select id from measure.subjects where upper(number) = 'AF0247') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0007')
where number = '2003058' and (select id from measure.subjects where upper(number) = 'AF0007') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0118')
where number = '2007176' and (select id from measure.subjects where upper(number) = 'AF0118') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0268')
where number = '2009012' and (select id from measure.subjects where upper(number) = 'AF0268') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0394')
where number = '2009096' and (select id from measure.subjects where upper(number) = 'AF0394') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0012')
where number = '2012038' and (select id from measure.subjects where upper(number) = 'AF0012') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0252')
where number = '2012116' and (select id from measure.subjects where upper(number) = 'AF0252') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0266')
where number = '2101054' and (select id from measure.subjects where upper(number) = 'AF0266') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0421')
where number = '2101090' and (select id from measure.subjects where upper(number) = 'AF0421') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0435')
where number = '2102114' and (select id from measure.subjects where upper(number) = 'AF0435') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0531')
where number = '2103061' and (select id from measure.subjects where upper(number) = 'AF0531') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0523')
where number = '2105104' and (select id from measure.subjects where upper(number) = 'AF0523') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0027')
where number = '2106003' and (select id from measure.subjects where upper(number) = 'AF0027') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0107')
where number = '2106051' and (select id from measure.subjects where upper(number) = 'AF0107') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0405')
where number = '2107338' and (select id from measure.subjects where upper(number) = 'AF0405') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0082')
where number = '2107340' and (select id from measure.subjects where upper(number) = 'AF0082') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0261')
where number = '2107341' and (select id from measure.subjects where upper(number) = 'AF0261') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0410')
where number = '2108120' and (select id from measure.subjects where upper(number) = 'AF0410') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0517')
where number = '2108292' and (select id from measure.subjects where upper(number) = 'AF0517') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0549')
where number = '2109033' and (select id from measure.subjects where upper(number) = 'AF0549') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0049')
where number = '2111071' and (select id from measure.subjects where upper(number) = 'AF0049') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0502')
where number = '2112049' and (select id from measure.subjects where upper(number) = 'AF0502') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0538')
where number = '2201013' and (select id from measure.subjects where upper(number) = 'AF0538') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0526')
where number = '2202074' and (select id from measure.subjects where upper(number) = 'AF0526') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0432')
where number = '2202076' and (select id from measure.subjects where upper(number) = 'AF0432') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0406')
where number = '2202111' and (select id from measure.subjects where upper(number) = 'AF0406') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0392')
where number = '2204253' and (select id from measure.subjects where upper(number) = 'AF0392') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0449')
where number = '2205262' and (select id from measure.subjects where upper(number) = 'AF0449') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0232')
where number = '2206027' and (select id from measure.subjects where upper(number) = 'AF0232') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0425')
where number = '2206167' and (select id from measure.subjects where upper(number) = 'AF0425') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0036')
where number = '2207249' and (select id from measure.subjects where upper(number) = 'AF0036') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0253')
where number = '2208047' and (select id from measure.subjects where upper(number) = 'AF0253') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0320')
where number = '2208074' and (select id from measure.subjects where upper(number) = 'AF0320') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0019')
where number = '2209074' and (select id from measure.subjects where upper(number) = 'AF0019') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0547')
where number = '2209098' and (select id from measure.subjects where upper(number) = 'AF0547') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0254')
where number = '2209100' and (select id from measure.subjects where upper(number) = 'AF0254') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0087')
where number = '2209114' and (select id from measure.subjects where upper(number) = 'AF0087') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0312')
where number = '2209116' and (select id from measure.subjects where upper(number) = 'AF0312') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0337')
where number = '2210016' and (select id from measure.subjects where upper(number) = 'AF0337') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0077')
where number = '2210045' and (select id from measure.subjects where upper(number) = 'AF0077') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0051')
where number = '2211013' and (select id from measure.subjects where upper(number) = 'AF0051') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0094')
where number = '2212004' and (select id from measure.subjects where upper(number) = 'AF0094') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0424')
where number = '2304034' and (select id from measure.subjects where upper(number) = 'AF0424') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0014')
where number = '2307103' and (select id from measure.subjects where upper(number) = 'AF0014') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0369')
where number = '2307106' and (select id from measure.subjects where upper(number) = 'AF0369') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0366')
where number = '2307144' and (select id from measure.subjects where upper(number) = 'AF0366') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0298')
where number = '2308066' and (select id from measure.subjects where upper(number) = 'AF0298') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0008')
where number = '2308151' and (select id from measure.subjects where upper(number) = 'AF0008') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0228')
where number = '2308154' and (select id from measure.subjects where upper(number) = 'AF0228') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0084')
where number = '2308161' and (select id from measure.subjects where upper(number) = 'AF0084') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0511')
where number = '2309109' and (select id from measure.subjects where upper(number) = 'AF0511') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0331')
where number = '2309111' and (select id from measure.subjects where upper(number) = 'AF0331') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0515')
where number = '2310087' and (select id from measure.subjects where upper(number) = 'AF0515') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0004')
where number = '2311065' and (select id from measure.subjects where upper(number) = 'AF0004') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0462')
where number = '2403023' and (select id from measure.subjects where upper(number) = 'AF0462') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0070')
where number = '2403109' and (select id from measure.subjects where upper(number) = 'AF0070') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0499')
where number = '2404020' and (select id from measure.subjects where upper(number) = 'AF0499') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0273')
where number = '2405096' and (select id from measure.subjects where upper(number) = 'AF0273') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0522')
where number = '2408042' and (select id from measure.subjects where upper(number) = 'AF0522') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0497')
where number = '2409080' and (select id from measure.subjects where upper(number) = 'AF0497') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0525')
where number = '2409127' and (select id from measure.subjects where upper(number) = 'AF0525') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0550')
where number = '2409199' and (select id from measure.subjects where upper(number) = 'AF0550') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0379')
where number = '9803403' and (select id from measure.subjects where upper(number) = 'AF0379') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0542')
where number = '9805401' and (select id from measure.subjects where upper(number) = 'AF0542') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0092')
where number = '9812209' and (select id from measure.subjects where upper(number) = 'AF0092') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0548')
where number = '2309021' and (select id from measure.subjects where upper(number) = 'AF0548') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0516')
where number = 'HQ21040' and (select id from measure.subjects where upper(number) = 'AF0516') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0203')
where number = 'HQ21046' and (select id from measure.subjects where upper(number) = 'AF0203') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0308')
where number = 'HQ21174' and (select id from measure.subjects where upper(number) = 'AF0308') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0275')
where number = 'HQ21204' and (select id from measure.subjects where upper(number) = 'AF0275') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0277')
where number = 'HQ21251' and (select id from measure.subjects where upper(number) = 'AF0277') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0520')
where number = 'HQ21277' and (select id from measure.subjects where upper(number) = 'AF0520') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0230')
where number = 'HQ21315' and (select id from measure.subjects where upper(number) = 'AF0230') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0236')
where number = 'HQ21341' and (select id from measure.subjects where upper(number) = 'AF0236') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0356')
where number = 'HQ21364' and (select id from measure.subjects where upper(number) = 'AF0356') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0175')
where number = 'HQ21366' and (select id from measure.subjects where upper(number) = 'AF0175') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0196')
where number = 'HQ21369' and (select id from measure.subjects where upper(number) = 'AF0196') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0471')
where number = 'HQ21375' and (select id from measure.subjects where upper(number) = 'AF0471') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0205')
where number = 'HQ22070' and (select id from measure.subjects where upper(number) = 'AF0205') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0200')
where number = 'HQ22074' and (select id from measure.subjects where upper(number) = 'AF0200') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0267')
where number = 'HQ22086' and (select id from measure.subjects where upper(number) = 'AF0267') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0349')
where number = 'HQ23019' and (select id from measure.subjects where upper(number) = 'AF0349') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0174')
where number = 'HQ23026' and (select id from measure.subjects where upper(number) = 'AF0174') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0513')
where number = 'HQ23027' and (select id from measure.subjects where upper(number) = 'AF0513') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0199')
where number = 'HQ23029' and (select id from measure.subjects where upper(number) = 'AF0199') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0199')
where number = 'HQ23029' and (select id from measure.subjects where upper(number) = 'AF0199') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0154')
where number = 'HQ23031' and (select id from measure.subjects where upper(number) = 'AF0154') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0519')
where number = 'HQ23047' and (select id from measure.subjects where upper(number) = 'AF0519') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0256')
where number = 'HQ23059' and (select id from measure.subjects where upper(number) = 'AF0256') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0354')
where number = 'HQ23061' and (select id from measure.subjects where upper(number) = 'AF0354') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0512')
where number = 'HQ24028' and (select id from measure.subjects where upper(number) = 'AF0512') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0545')
where number = 'O2312007' and (select id from measure.subjects where upper(number) = 'AF0545') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0093')
where number = '0602670' and (select id from measure.subjects where upper(number) = 'AF0093') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0315')
where number = '0406544' and (select id from measure.subjects where upper(number) = 'AF0315') is not null;

commit;




-- not exist number subject by query
{# select number
from measure.infos
where number in ('0002458', '0003448', '0004426', '0010234', '0027028', '0102220', '0102446', '0103291', '0105417', '0106210', '0110029', '0122009', '0201348', '0204081', '0208052', '0303060', '0303423', '0304407', '0305048', '0306487', '0311068', '0331003', '0404464', '0406544', '0407149', '0408003', '0428090', '0431033', '0505435', '0507697', '0511312', '0602670', '0603187', '0701207', '0703230', '0707539', '0709147', '0802015', '0802081', '0807283', '0910194', '0911196', '1001039', '1003495', '1010105', '1010139', '1010257', '1010262', '1010449', '1011080', '1011266', '1011329', '1012077', '1012100', '1105117', '1111176', '1111210', '1112053', '1201023', '1205511', '1205534', '1205864', '1207802', '1209172', '1209184', '1211053', '1312017', '1312066', '1403311', '1409259', '1410114', '1411271', '1411284', '1502020', '1504234', '1506291', '1509004', '1509006', '1509183', '1509188', '1609112', '1609114', '1704147', '1705019', '1706037', '1706166', '1711204', '1805286', '1807358', '1811087', '1901051', '1905007', '1908043', '1910040', '1912029', '2003058', '2007176', '2009012', '2009096', '2012038', '2012116', '2101054', '2101090', '2102114', '2103061', '2105104', '2106003', '2106051', '2107338', '2107340', '2107341', '2108120', '2108292', '2109033', '2111071', '2112049', '2201013', '2202074', '2202076', '2202111', '2204253', '2205262', '2206027', '2206167', '2207249', '2208047', '2208074', '2209074', '2209098', '2209100', '2209114', '2209116', '2210016', '2210045', '2211013', '2212004', '2304034', '2307103', '2307106', '2307144', '2308066', '2308151', '2308154', '2308161', '2309021', '2309024', '2309109', '2309111', '2309112', '2310087', '2311065', '2403023', '2403109', '2404020', '2405096', '2408042', '2409080', '2409127', '2409199', '9803403', '9805401', '9812209', 'HQ21040', 'HQ21046', 'HQ21174', 'HQ21204', 'HQ21251', 'HQ21277', 'HQ21315', 'HQ21341', 'HQ21364', 'HQ21366', 'HQ21369', 'HQ22070', 'HQ22074', 'HQ22086', 'HQ23019', 'HQ23026', 'HQ23027', 'HQ23029', 'HQ23031', 'HQ23047', 'HQ23059', 'HQ23061', 'HQ24028', 'O2312007'); #}

update_subject_list = ['0110029', '1409259', '0105417', '2409080', '2103061', '0201348', '0208052', '1704147', '1209184', '1011266', '0408003', '0103291', '0331003', '9805401', '1010257', '0603187', '0311068', '2112049', '0802015', '0431033', '2309109', '1010105', '0102446', 'HQ24028', '1504234', '2108292', 'HQ21040', '2105104', '0404464', '2309021', '0709147', '0306487', '0303060', '1105117', '2408042', '1003495', 'HQ21277', 'HQ23027', '2109033', '2209098', '2409199', '2202074', '2201013', '1012077', '2310087', '2409127', 'HQ23047',]
pair_dict = dict([pair for pair in pairs if len(pair) == 2 and pair[1] != ""])

for employee_no in update_subject_list:
    if employee_no in pair_dict:
        number = pair_dict[employee_no]
        print(f"update measure.subjects set number = '{number}', sid = '{number}', name = '{number}' where number = '{employee_no}';")

update measure.subjects set number = 'AF0491', sid = 'AF0491', name = 'AF0491' where number = '0110029';
update measure.subjects set number = 'AF0498', sid = 'AF0498', name = 'AF0498' where number = '1409259';
update measure.subjects set number = 'AF0533', sid = 'AF0533', name = 'AF0533' where number = '0105417';
update measure.subjects set number = 'AF0497', sid = 'AF0497', name = 'AF0497' where number = '2409080';
update measure.subjects set number = 'AF0531', sid = 'AF0531', name = 'AF0531' where number = '2103061';
update measure.subjects set number = 'AF0543', sid = 'AF0543', name = 'AF0543' where number = '0201348';
update measure.subjects set number = 'AF0493', sid = 'AF0493', name = 'AF0493' where number = '0208052';
update measure.subjects set number = 'AF0492', sid = 'AF0492', name = 'AF0492' where number = '1704147';
update measure.subjects set number = 'AF0494', sid = 'AF0494', name = 'AF0494' where number = '1209184';
update measure.subjects set number = 'AF0532', sid = 'AF0532', name = 'AF0532' where number = '1011266';
update measure.subjects set number = 'AF0534', sid = 'AF0534', name = 'AF0534' where number = '0408003';
update measure.subjects set number = 'AF0540', sid = 'AF0540', name = 'AF0540' where number = '0103291';
update measure.subjects set number = 'AF0506', sid = 'AF0506', name = 'AF0506' where number = '0331003';
update measure.subjects set number = 'AF0542', sid = 'AF0542', name = 'AF0542' where number = '9805401';
update measure.subjects set number = 'AF0508', sid = 'AF0508', name = 'AF0508' where number = '1010257';
update measure.subjects set number = 'AF0544', sid = 'AF0544', name = 'AF0544' where number = '0311068';
update measure.subjects set number = 'AF0502', sid = 'AF0502', name = 'AF0502' where number = '2112049';
update measure.subjects set number = 'AF0505', sid = 'AF0505', name = 'AF0505' where number = '0802015';
update measure.subjects set number = 'AF0510', sid = 'AF0510', name = 'AF0510' where number = '0431033';
update measure.subjects set number = 'AF0511', sid = 'AF0511', name = 'AF0511' where number = '2309109';
update measure.subjects set number = 'AF0514', sid = 'AF0514', name = 'AF0514' where number = '1010105';
update measure.subjects set number = 'AF0535', sid = 'AF0535', name = 'AF0535' where number = '0102446';
update measure.subjects set number = 'AF0512', sid = 'AF0512', name = 'AF0512' where number = 'HQ24028';
update measure.subjects set number = 'AF0501', sid = 'AF0501', name = 'AF0501' where number = '1504234';
update measure.subjects set number = 'AF0517', sid = 'AF0517', name = 'AF0517' where number = '2108292';
update measure.subjects set number = 'AF0516', sid = 'AF0516', name = 'AF0516' where number = 'HQ21040';
update measure.subjects set number = 'AF0523', sid = 'AF0523', name = 'AF0523' where number = '2105104';
update measure.subjects set number = 'AF0521', sid = 'AF0521', name = 'AF0521' where number = '0404464';
update measure.subjects set number = 'AF0548', sid = 'AF0548', name = 'AF0548' where number = '2309021';
update measure.subjects set number = 'AF0539', sid = 'AF0539', name = 'AF0539' where number = '0709147';
update measure.subjects set number = 'AF0507', sid = 'AF0507', name = 'AF0507' where number = '0306487';
update measure.subjects set number = 'AF0541', sid = 'AF0541', name = 'AF0541' where number = '0303060';
update measure.subjects set number = 'AF0546', sid = 'AF0546', name = 'AF0546' where number = '1105117';
update measure.subjects set number = 'AF0522', sid = 'AF0522', name = 'AF0522' where number = '2408042';
update measure.subjects set number = 'AF0509', sid = 'AF0509', name = 'AF0509' where number = '1003495';
update measure.subjects set number = 'AF0520', sid = 'AF0520', name = 'AF0520' where number = 'HQ21277';
update measure.subjects set number = 'AF0513', sid = 'AF0513', name = 'AF0513' where number = 'HQ23027';
update measure.subjects set number = 'AF0549', sid = 'AF0549', name = 'AF0549' where number = '2109033';
update measure.subjects set number = 'AF0547', sid = 'AF0547', name = 'AF0547' where number = '2209098';
update measure.subjects set number = 'AF0550', sid = 'AF0550', name = 'AF0550' where number = '2409199';
update measure.subjects set number = 'AF0526', sid = 'AF0526', name = 'AF0526' where number = '2202074';
update measure.subjects set number = 'AF0538', sid = 'AF0538', name = 'AF0538' where number = '2201013';
update measure.subjects set number = 'AF0518', sid = 'AF0518', name = 'AF0518' where number = '1012077';
update measure.subjects set number = 'AF0515', sid = 'AF0515', name = 'AF0515' where number = '2310087';
update measure.subjects set number = 'AF0525', sid = 'AF0525', name = 'AF0525' where number = '2409127';
update measure.subjects set number = 'AF0519', sid = 'AF0519', name = 'AF0519' where number = 'HQ23047';

update measure.subjects set number = 'AF0537', sid = 'AF0537', name = 'AF0537' where number = '0003448';
update measure.subjects set number = 'AF0125', sid = 'AF0125', name = 'AF0125' where number = '0122009';
update measure.subjects set number = 'AF0032', sid = 'AF0032', name = 'AF0032' where number = '1509004';
update measure.subjects set number = 'AF0315', sid = 'AF0315', name = 'AF0315' where number = '0406544';
update measure.subjects set number = 'AF0496', sid = 'AF0496', name = 'AF0496' where number = '0407149';
update measure.subjects set number = 'AF0499', sid = 'AF0499', name = 'AF0499' where number = '2404020';

-- fix survey and db different number
update measure.subjects set number = '0602670', sid = '0602670', name = '0602670' where number = '602670';
update measure.subjects set number = '9812209', sid = '9812209', name = '9812209' where number = '102117';
update measure.subjects set number = '0406544', sid = '0406544', name = '0406544' where number = '406544';
update measure.subjects set number = '0407149', sid = '0407149', name = '0407149' where number = '407149';
update measure.subjects set number = '2404020', sid = '2404020', name = '2404020' where number = '0404020';
update measure.subjects set number = 'O2312007', sid = 'O2312007', name = 'O2312007' where number = '2312007';
update measure.subjects set number = 'AF0545', sid = 'AF0545', name = 'AF0545' where number = 'O2312007';
update measure.subjects set number = 'AF0093', sid = 'AF0093', name = 'AF0093' where number = '0602670';
update measure.subjects set number = 'AF0202', sid = 'AF0202', name = 'AF0202' where number = '1312017';
update measure.subjects set number = 'AF0549', sid = 'AF0549', name = 'AF0549' where number = '2109033';

update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0202')
where number = '1312107' and (select id from measure.subjects where upper(number) = 'AF0202') is not null;

update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0093')
where number = '602670' and (select id from measure.subjects where upper(number) = 'AF0093') is not null;


-- AF0174 有兩筆檢測資料需要哪一筆
-- 2024_1030_1057_AF0174.zip (X)
-- 2024_1030_1122_AF0174.zip (O)
update measure.infos
set is_active = false
where file_id = (select id
from app.upload_files
where name = '2024_1030_1057_AF0174.zip');


begin;
update measure.infos as i
set subject_id = s.id, number = s.number
from measure.subjects as s
where subject_id = s.id
and i.number != s.number
and i.org_id = '4ce79cc1-1994-4bd5-868b-6c1e1efefabe'
and measure_time >= '2024-07-01';
rollback;



begin;
update measure.subjects as s
set last_measure_time = i.last_measure_time
from (
  select subject_id, max(measure_time) as last_measure_time
  from measure.infos
  where org_id = '4ce79cc1-1994-4bd5-868b-6c1e1efefabe'
  and  measure_time >= '2024-07-01'
  group by subject_id
) as i
where i.subject_id = s.id
and i.last_measure_time != s.last_measure_time
;
rollback;

select subjects.number, score_yang, score_yin, score_phlegm, percentage_yang, percentage_yin, percentage_phlegm,measure_time
from measure.infos
inner join measure.bcqs on bcqs.measure_id = infos.id
inner join measure.subjects on subjects.id = infos.subject_id
where subjects.number ~ 'A' and measure_time > '2024-10-01' and subjects.org_id = (select id from app.auth_orgs where name = 'nricm');


-- 未量測
{# error_dict {'nricm 問卷': ['AF0503', 'AF0471']} #}