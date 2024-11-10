pairs = [x.split("\t") for x in """
0002458	AF0311
0002491	AF0418
0010234	AF0390
0011209	AF0479
0027028	AF0123
0106210	AF0284
0207098	AF0399
0210080	AF0463
0304407	AF0110
0308037	AF0386
0401017	AF0189
0402578	AF0055
0403443	AF0412
0428090	AF0426
0432021	AF0415
0505435	AF0461
0511312	AF0145
0525011	AF0414
0528111	AF0469
0602353	AF0473
0602536	AF0404
0602670	AF0093
0603187	AF0300
0610392	AF0403
0701207	AF0044
0707539	AF0448
0802081	AF0280
0805219	AF0444
0807283	AF0003
0808180	AF0445
0903005	AF0485
0908109	AF0490
0910084	AF0429
0910194	AF0120
0911196	AF0211
0912052	AF0398
1002055	AF0436
1007108	AF0402
1007303	AF0381
1007311	AF0380
1010139	AF0194
1010262	AF0407
1010449	AF0313
1011054	AF0455
1011080	AF0258
1011329	AF0221
1103721	AF0400
1111176	AF0039
1201023	AF0010
1203066	AF0470
1205534	AF0413
1207158	AF0416
1208014	AF0483
1208210	AF0168
1209172	AF0210
1211053	AF0433
1312017	AF0202
1403311	AF0064
1410118	AF0028
1411284	AF0143
1502020	AF0385
1503444	AF0472
1506287	AF0382
1508314	AF0383
1509006	AF0453
1509183	AF0134
1509188	AF0061
1609112	AF0122
1609114	AF0397
1611039	AF0457
1612135	AF0401
1703217	AF0460
1705018	AF0466
1705019	AF0454
1706037	AF0439
1706166	AF0446
1710094	AF0478
1711092	AF0387
1711204	AF0244
1805286	AF0195
1807358	AF0324
1902008	AF0339
1903011	AF0389
1905007	AF0241
1907124	AF0442
1910040	AF0427
1912029	AF0247
2002101	AF0458
2004068	AF0420
2006012	AF0441
2007176	AF0118
2009096	AF0394
2010043	AF0160
2012038	AF0012
2012116	AF0252
2101013	AF0264
2101090	AF0421
2102113	AF0475
2102114	AF0435
2102121	AF0170
2103145	AF0428
2104191	AF0451
2105004	AF0419
2106051	AF0107
2107338	AF0405
2107340	AF0082
2107341	AF0261
2108120	AF0410
2108246	AF0245
2108252	AF0393
2109227	AF0423
2109229	AF0465
2109235	AF0246
2111006	AF0359
2111008	AF0417
2201036	AF0443
2202076	AF0432
2202111	AF0406
2204253	AF0392
2205178	AF0233
2205262	AF0449
2205298	AF0431
2206167	AF0425
2207188	AF0447
2207215	AF0437
2208047	AF0253
2208074	AF0320
2208099	AF0438
2208110	AF0440
2209084	AF0121
2209100	AF0254
2209114	AF0087
2210016	AF0337
2210020	AF0231
2210045	AF0077
2211040	AF0411
2212004	AF0094
2304034	AF0424
2305085	AF0476
2306006	AF0430
2307103	AF0014
2307106	AF0369
2307144	AF0366
2307147	AF0295
2307148	AF0464
2307224	AF0391
2308066	AF0298
2308070	AF0227
2308151	AF0008
2308154	AF0228
2308161	AF0084
2309021	AF0362
2309024	AF0301
2309107	AF0388
2309111	AF0331
2309112	AF0302
2310010	AF0452
2310088	AF0481
2311005	AF0489
2311060	AF0484
2402039	AF0456
2403015	AF0396
2403023	AF0462
2403090	AF0450
2406091	AF0480
2407039	AF0482
9803403	AF0379
000seth	AF0471
AF0304	AF0304
HQ21251	AF0277
HQ21287	AF0357
HQ21341	AF0236
HQ21366	AF0175
HQ21369	AF0196
HQ21375	AF0217
HQ22074	AF0200
HQ22106	AF0190
HQ23019	AF0349
HQ23026	AF0174
HQ23029	AF0199
HQ23059	AF0256
HQ23061	AF0354
O2201006	AF0486
O2202016	AF0487
O2205007	AF0384
O2308004	AF0488
""".strip().split('\n')]

for pair in pairs:
    print(f"update measure.infos set subject_id = (select id from measure.subjects where upper(number) = '{pair[1]}')\nwhere number = '{pair[0]}' and (select id from measure.subjects where upper(number) = '{pair[1]}') is not null;")



begin;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0311')
where number = '0002458' and (select id from measure.subjects where upper(number) = 'AF0311') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0418')
where number = '0002491' and (select id from measure.subjects where upper(number) = 'AF0418') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0390')
where number = '0010234' and (select id from measure.subjects where upper(number) = 'AF0390') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0479')
where number = '0011209' and (select id from measure.subjects where upper(number) = 'AF0479') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0123')
where number = '0027028' and (select id from measure.subjects where upper(number) = 'AF0123') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0284')
where number = '0106210' and (select id from measure.subjects where upper(number) = 'AF0284') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0399')
where number = '0207098' and (select id from measure.subjects where upper(number) = 'AF0399') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0463')
where number = '0210080' and (select id from measure.subjects where upper(number) = 'AF0463') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0110')
where number = '0304407' and (select id from measure.subjects where upper(number) = 'AF0110') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0386')
where number = '0308037' and (select id from measure.subjects where upper(number) = 'AF0386') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0189')
where number = '0401017' and (select id from measure.subjects where upper(number) = 'AF0189') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0055')
where number = '0402578' and (select id from measure.subjects where upper(number) = 'AF0055') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0412')
where number = '0403443' and (select id from measure.subjects where upper(number) = 'AF0412') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0426')
where number = '0428090' and (select id from measure.subjects where upper(number) = 'AF0426') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0415')
where number = '0432021' and (select id from measure.subjects where upper(number) = 'AF0415') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0461')
where number = '0505435' and (select id from measure.subjects where upper(number) = 'AF0461') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0145')
where number = '0511312' and (select id from measure.subjects where upper(number) = 'AF0145') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0414')
where number = '0525011' and (select id from measure.subjects where upper(number) = 'AF0414') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0469')
where number = '0528111' and (select id from measure.subjects where upper(number) = 'AF0469') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0473')
where number = '0602353' and (select id from measure.subjects where upper(number) = 'AF0473') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0404')
where number = '0602536' and (select id from measure.subjects where upper(number) = 'AF0404') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0093')
where number = '0602670' and (select id from measure.subjects where upper(number) = 'AF0093') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0300')
where number = '0603187' and (select id from measure.subjects where upper(number) = 'AF0300') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0403')
where number = '0610392' and (select id from measure.subjects where upper(number) = 'AF0403') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0044')
where number = '0701207' and (select id from measure.subjects where upper(number) = 'AF0044') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0448')
where number = '0707539' and (select id from measure.subjects where upper(number) = 'AF0448') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0280')
where number = '0802081' and (select id from measure.subjects where upper(number) = 'AF0280') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0444')
where number = '0805219' and (select id from measure.subjects where upper(number) = 'AF0444') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0003')
where number = '0807283' and (select id from measure.subjects where upper(number) = 'AF0003') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0445')
where number = '0808180' and (select id from measure.subjects where upper(number) = 'AF0445') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0485')
where number = '0903005' and (select id from measure.subjects where upper(number) = 'AF0485') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0490')
where number = '0908109' and (select id from measure.subjects where upper(number) = 'AF0490') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0429')
where number = '0910084' and (select id from measure.subjects where upper(number) = 'AF0429') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0120')
where number = '0910194' and (select id from measure.subjects where upper(number) = 'AF0120') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0211')
where number = '0911196' and (select id from measure.subjects where upper(number) = 'AF0211') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0398')
where number = '0912052' and (select id from measure.subjects where upper(number) = 'AF0398') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0436')
where number = '1002055' and (select id from measure.subjects where upper(number) = 'AF0436') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0402')
where number = '1007108' and (select id from measure.subjects where upper(number) = 'AF0402') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0381')
where number = '1007303' and (select id from measure.subjects where upper(number) = 'AF0381') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0380')
where number = '1007311' and (select id from measure.subjects where upper(number) = 'AF0380') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0194')
where number = '1010139' and (select id from measure.subjects where upper(number) = 'AF0194') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0407')
where number = '1010262' and (select id from measure.subjects where upper(number) = 'AF0407') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0313')
where number = '1010449' and (select id from measure.subjects where upper(number) = 'AF0313') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0455')
where number = '1011054' and (select id from measure.subjects where upper(number) = 'AF0455') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0258')
where number = '1011080' and (select id from measure.subjects where upper(number) = 'AF0258') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0221')
where number = '1011329' and (select id from measure.subjects where upper(number) = 'AF0221') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0400')
where number = '1103721' and (select id from measure.subjects where upper(number) = 'AF0400') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0039')
where number = '1111176' and (select id from measure.subjects where upper(number) = 'AF0039') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0010')
where number = '1201023' and (select id from measure.subjects where upper(number) = 'AF0010') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0470')
where number = '1203066' and (select id from measure.subjects where upper(number) = 'AF0470') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0413')
where number = '1205534' and (select id from measure.subjects where upper(number) = 'AF0413') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0416')
where number = '1207158' and (select id from measure.subjects where upper(number) = 'AF0416') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0483')
where number = '1208014' and (select id from measure.subjects where upper(number) = 'AF0483') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0168')
where number = '1208210' and (select id from measure.subjects where upper(number) = 'AF0168') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0210')
where number = '1209172' and (select id from measure.subjects where upper(number) = 'AF0210') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0433')
where number = '1211053' and (select id from measure.subjects where upper(number) = 'AF0433') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0202')
where number = '1312017' and (select id from measure.subjects where upper(number) = 'AF0202') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0064')
where number = '1403311' and (select id from measure.subjects where upper(number) = 'AF0064') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0028')
where number = '1410118' and (select id from measure.subjects where upper(number) = 'AF0028') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0143')
where number = '1411284' and (select id from measure.subjects where upper(number) = 'AF0143') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0385')
where number = '1502020' and (select id from measure.subjects where upper(number) = 'AF0385') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0472')
where number = '1503444' and (select id from measure.subjects where upper(number) = 'AF0472') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0382')
where number = '1506287' and (select id from measure.subjects where upper(number) = 'AF0382') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0383')
where number = '1508314' and (select id from measure.subjects where upper(number) = 'AF0383') is not null;
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
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0457')
where number = '1611039' and (select id from measure.subjects where upper(number) = 'AF0457') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0401')
where number = '1612135' and (select id from measure.subjects where upper(number) = 'AF0401') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0460')
where number = '1703217' and (select id from measure.subjects where upper(number) = 'AF0460') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0466')
where number = '1705018' and (select id from measure.subjects where upper(number) = 'AF0466') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0454')
where number = '1705019' and (select id from measure.subjects where upper(number) = 'AF0454') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0439')
where number = '1706037' and (select id from measure.subjects where upper(number) = 'AF0439') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0446')
where number = '1706166' and (select id from measure.subjects where upper(number) = 'AF0446') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0478')
where number = '1710094' and (select id from measure.subjects where upper(number) = 'AF0478') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0387')
where number = '1711092' and (select id from measure.subjects where upper(number) = 'AF0387') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0244')
where number = '1711204' and (select id from measure.subjects where upper(number) = 'AF0244') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0195')
where number = '1805286' and (select id from measure.subjects where upper(number) = 'AF0195') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0324')
where number = '1807358' and (select id from measure.subjects where upper(number) = 'AF0324') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0339')
where number = '1902008' and (select id from measure.subjects where upper(number) = 'AF0339') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0389')
where number = '1903011' and (select id from measure.subjects where upper(number) = 'AF0389') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0241')
where number = '1905007' and (select id from measure.subjects where upper(number) = 'AF0241') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0442')
where number = '1907124' and (select id from measure.subjects where upper(number) = 'AF0442') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0427')
where number = '1910040' and (select id from measure.subjects where upper(number) = 'AF0427') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0247')
where number = '1912029' and (select id from measure.subjects where upper(number) = 'AF0247') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0458')
where number = '2002101' and (select id from measure.subjects where upper(number) = 'AF0458') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0420')
where number = '2004068' and (select id from measure.subjects where upper(number) = 'AF0420') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0441')
where number = '2006012' and (select id from measure.subjects where upper(number) = 'AF0441') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0118')
where number = '2007176' and (select id from measure.subjects where upper(number) = 'AF0118') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0394')
where number = '2009096' and (select id from measure.subjects where upper(number) = 'AF0394') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0160')
where number = '2010043' and (select id from measure.subjects where upper(number) = 'AF0160') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0012')
where number = '2012038' and (select id from measure.subjects where upper(number) = 'AF0012') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0252')
where number = '2012116' and (select id from measure.subjects where upper(number) = 'AF0252') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0264')
where number = '2101013' and (select id from measure.subjects where upper(number) = 'AF0264') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0421')
where number = '2101090' and (select id from measure.subjects where upper(number) = 'AF0421') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0475')
where number = '2102113' and (select id from measure.subjects where upper(number) = 'AF0475') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0435')
where number = '2102114' and (select id from measure.subjects where upper(number) = 'AF0435') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0170')
where number = '2102121' and (select id from measure.subjects where upper(number) = 'AF0170') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0428')
where number = '2103145' and (select id from measure.subjects where upper(number) = 'AF0428') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0451')
where number = '2104191' and (select id from measure.subjects where upper(number) = 'AF0451') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0419')
where number = '2105004' and (select id from measure.subjects where upper(number) = 'AF0419') is not null;
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
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0245')
where number = '2108246' and (select id from measure.subjects where upper(number) = 'AF0245') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0393')
where number = '2108252' and (select id from measure.subjects where upper(number) = 'AF0393') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0423')
where number = '2109227' and (select id from measure.subjects where upper(number) = 'AF0423') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0465')
where number = '2109229' and (select id from measure.subjects where upper(number) = 'AF0465') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0246')
where number = '2109235' and (select id from measure.subjects where upper(number) = 'AF0246') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0359')
where number = '2111006' and (select id from measure.subjects where upper(number) = 'AF0359') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0417')
where number = '2111008' and (select id from measure.subjects where upper(number) = 'AF0417') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0443')
where number = '2201036' and (select id from measure.subjects where upper(number) = 'AF0443') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0432')
where number = '2202076' and (select id from measure.subjects where upper(number) = 'AF0432') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0406')
where number = '2202111' and (select id from measure.subjects where upper(number) = 'AF0406') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0392')
where number = '2204253' and (select id from measure.subjects where upper(number) = 'AF0392') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0233')
where number = '2205178' and (select id from measure.subjects where upper(number) = 'AF0233') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0449')
where number = '2205262' and (select id from measure.subjects where upper(number) = 'AF0449') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0431')
where number = '2205298' and (select id from measure.subjects where upper(number) = 'AF0431') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0425')
where number = '2206167' and (select id from measure.subjects where upper(number) = 'AF0425') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0447')
where number = '2207188' and (select id from measure.subjects where upper(number) = 'AF0447') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0437')
where number = '2207215' and (select id from measure.subjects where upper(number) = 'AF0437') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0253')
where number = '2208047' and (select id from measure.subjects where upper(number) = 'AF0253') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0320')
where number = '2208074' and (select id from measure.subjects where upper(number) = 'AF0320') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0438')
where number = '2208099' and (select id from measure.subjects where upper(number) = 'AF0438') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0440')
where number = '2208110' and (select id from measure.subjects where upper(number) = 'AF0440') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0121')
where number = '2209084' and (select id from measure.subjects where upper(number) = 'AF0121') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0254')
where number = '2209100' and (select id from measure.subjects where upper(number) = 'AF0254') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0087')
where number = '2209114' and (select id from measure.subjects where upper(number) = 'AF0087') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0337')
where number = '2210016' and (select id from measure.subjects where upper(number) = 'AF0337') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0231')
where number = '2210020' and (select id from measure.subjects where upper(number) = 'AF0231') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0077')
where number = '2210045' and (select id from measure.subjects where upper(number) = 'AF0077') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0411')
where number = '2211040' and (select id from measure.subjects where upper(number) = 'AF0411') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0094')
where number = '2212004' and (select id from measure.subjects where upper(number) = 'AF0094') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0424')
where number = '2304034' and (select id from measure.subjects where upper(number) = 'AF0424') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0476')
where number = '2305085' and (select id from measure.subjects where upper(number) = 'AF0476') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0430')
where number = '2306006' and (select id from measure.subjects where upper(number) = 'AF0430') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0014')
where number = '2307103' and (select id from measure.subjects where upper(number) = 'AF0014') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0369')
where number = '2307106' and (select id from measure.subjects where upper(number) = 'AF0369') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0366')
where number = '2307144' and (select id from measure.subjects where upper(number) = 'AF0366') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0295')
where number = '2307147' and (select id from measure.subjects where upper(number) = 'AF0295') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0464')
where number = '2307148' and (select id from measure.subjects where upper(number) = 'AF0464') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0391')
where number = '2307224' and (select id from measure.subjects where upper(number) = 'AF0391') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0298')
where number = '2308066' and (select id from measure.subjects where upper(number) = 'AF0298') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0227')
where number = '2308070' and (select id from measure.subjects where upper(number) = 'AF0227') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0008')
where number = '2308151' and (select id from measure.subjects where upper(number) = 'AF0008') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0228')
where number = '2308154' and (select id from measure.subjects where upper(number) = 'AF0228') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0084')
where number = '2308161' and (select id from measure.subjects where upper(number) = 'AF0084') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0362')
where number = '2309021' and (select id from measure.subjects where upper(number) = 'AF0362') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0301')
where number = '2309024' and (select id from measure.subjects where upper(number) = 'AF0301') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0388')
where number = '2309107' and (select id from measure.subjects where upper(number) = 'AF0388') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0331')
where number = '2309111' and (select id from measure.subjects where upper(number) = 'AF0331') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0302')
where number = '2309112' and (select id from measure.subjects where upper(number) = 'AF0302') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0452')
where number = '2310010' and (select id from measure.subjects where upper(number) = 'AF0452') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0481')
where number = '2310088' and (select id from measure.subjects where upper(number) = 'AF0481') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0489')
where number = '2311005' and (select id from measure.subjects where upper(number) = 'AF0489') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0484')
where number = '2311060' and (select id from measure.subjects where upper(number) = 'AF0484') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0456')
where number = '2402039' and (select id from measure.subjects where upper(number) = 'AF0456') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0396')
where number = '2403015' and (select id from measure.subjects where upper(number) = 'AF0396') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0462')
where number = '2403023' and (select id from measure.subjects where upper(number) = 'AF0462') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0450')
where number = '2403090' and (select id from measure.subjects where upper(number) = 'AF0450') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0480')
where number = '2406091' and (select id from measure.subjects where upper(number) = 'AF0480') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0482')
where number = '2407039' and (select id from measure.subjects where upper(number) = 'AF0482') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0379')
where number = '9803403' and (select id from measure.subjects where upper(number) = 'AF0379') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0471')
where number = '000seth' and (select id from measure.subjects where upper(number) = 'AF0471') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0304')
where number = 'AF0304' and (select id from measure.subjects where upper(number) = 'AF0304') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0277')
where number = 'HQ21251' and (select id from measure.subjects where upper(number) = 'AF0277') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0357')
where number = 'HQ21287' and (select id from measure.subjects where upper(number) = 'AF0357') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0236')
where number = 'HQ21341' and (select id from measure.subjects where upper(number) = 'AF0236') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0175')
where number = 'HQ21366' and (select id from measure.subjects where upper(number) = 'AF0175') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0196')
where number = 'HQ21369' and (select id from measure.subjects where upper(number) = 'AF0196') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0217')
where number = 'HQ21375' and (select id from measure.subjects where upper(number) = 'AF0217') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0200')
where number = 'HQ22074' and (select id from measure.subjects where upper(number) = 'AF0200') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0190')
where number = 'HQ22106' and (select id from measure.subjects where upper(number) = 'AF0190') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0349')
where number = 'HQ23019' and (select id from measure.subjects where upper(number) = 'AF0349') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0174')
where number = 'HQ23026' and (select id from measure.subjects where upper(number) = 'AF0174') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0199')
where number = 'HQ23029' and (select id from measure.subjects where upper(number) = 'AF0199') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0256')
where number = 'HQ23059' and (select id from measure.subjects where upper(number) = 'AF0256') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0354')
where number = 'HQ23061' and (select id from measure.subjects where upper(number) = 'AF0354') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0486')
where number = 'O2201006' and (select id from measure.subjects where upper(number) = 'AF0486') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0487')
where number = 'O2202016' and (select id from measure.subjects where upper(number) = 'AF0487') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0384')
where number = 'O2205007' and (select id from measure.subjects where upper(number) = 'AF0384') is not null;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0488')
where number = 'O2308004' and (select id from measure.subjects where upper(number) = 'AF0488') is not null
;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0471')
where number = 'seth' and (select id from measure.subjects where upper(number) = 'AF0471') is not null
;



commit;



begin;
update
measure.subjects
set sid = 'AF0471', name = 'AF0471', number = 'AF0471'
where number = 'seth';
rollback;

begin;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0471')
where number = 'seth' and (select id from measure.subjects where upper(number) = 'AF0471') is not null
;
rollback;


begin;
update measure.infos set subject_id = (select id from measure.subjects where upper(number) = 'AF0304'), number = 'AF0304'
where number = 'Bonnie'
;
rollback;



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
where subjects.number ~ 'A' and measure_time > '2024-07-01' and subjects.org_id = (select id from app.auth_orgs where name = 'nricm');
