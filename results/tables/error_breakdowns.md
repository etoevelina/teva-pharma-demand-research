| scenario   | breakdown           | group                                                 | model               |      n |        MAE |       RMSE |      WAPE |      bias |   actual_total |
|:-----------|:--------------------|:------------------------------------------------------|:--------------------|-------:|-----------:|-----------:|----------:|----------:|---------------:|
| A          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | naive               |  19812 |  2108.3010 |  8401.2545 |    0.2675 |    0.0485 | 156163888.1542 |
| A          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |  19812 |  3124.2155 | 17604.2871 |    0.3964 |   -0.0166 | 156163888.1542 |
| A          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |  19812 |  2306.5305 |  9148.4908 |    0.2926 |   -0.0516 | 156163888.1542 |
| A          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | naive               |   6408 |  1746.1267 |  7510.3335 |    0.2531 |    0.0118 |  44209696.6824 |
| A          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |   6408 |  2145.9715 |  8610.7443 |    0.3110 |   -0.1380 |  44209696.6824 |
| A          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |   6408 |  1794.1334 |  6957.8599 |    0.2601 |   -0.0766 |  44209696.6824 |
| A          | atc1                | C CARDIOVASCULAR SYSTEM                               | naive               |  16896 |  1583.4581 |  5921.1346 |    0.2064 |    0.0320 | 129594517.8649 |
| A          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |  16896 |  2290.0437 | 10611.8130 |    0.2986 |   -0.0746 | 129594517.8649 |
| A          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |  16896 |  1718.2137 |  5719.0060 |    0.2240 |   -0.0509 | 129594517.8649 |
| A          | atc1                | D DERMATOLOGICAL                                      | naive               |   9192 |  2253.5240 |  7303.9561 |    0.3171 |   -0.0784 |  65320443.2641 |
| A          | atc1                | D DERMATOLOGICAL                                      | catboost_none       |   9192 |  2360.8728 |  7133.0001 |    0.3322 |   -0.0065 |  65320443.2641 |
| A          | atc1                | D DERMATOLOGICAL                                      | catboost_both       |   9192 |  2408.0684 |  7207.0786 |    0.3389 |   -0.0896 |  65320443.2641 |
| A          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | naive               |   6840 |   559.7010 |  1478.4905 |    0.1910 |    0.0192 |  20048678.2291 |
| A          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |   6840 |   789.3272 |  2029.0789 |    0.2693 |   -0.1161 |  20048678.2291 |
| A          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |   6840 |   717.1040 |  1624.9289 |    0.2447 |   -0.1551 |  20048678.2291 |
| A          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | naive               |   1320 |   902.0519 |  2165.7958 |    0.1958 |   -0.0762 |   6081661.8168 |
| A          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |   1320 |  1528.2644 |  3176.4491 |    0.3317 |   -0.1669 |   6081661.8168 |
| A          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |   1320 |  1212.7116 |  2718.6610 |    0.2632 |   -0.0692 |   6081661.8168 |
| A          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | naive               |  12384 |  1415.0868 |  5134.5670 |    0.3719 |    0.1842 |  47123384.3838 |
| A          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |  12384 |  1352.2159 |  4365.6200 |    0.3554 |   -0.0676 |  47123384.3838 |
| A          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |  12384 |  1179.3904 |  3386.1950 |    0.3099 |   -0.0487 |  47123384.3838 |
| A          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | naive               |   5808 |   172.1538 |   798.7044 |    0.4435 |    0.2695 |   2254504.3781 |
| A          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |   5808 |   158.0739 |   494.1216 |    0.4072 |    0.1625 |   2254504.3781 |
| A          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |   5808 |   124.5159 |   406.7707 |    0.3208 |    0.0410 |   2254504.3781 |
| A          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | naive               |   9324 |  2213.7559 |  6788.8913 |    0.3095 |    0.0302 |  66691266.7312 |
| A          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |   9324 |  2355.6075 |  6510.2920 |    0.3293 |   -0.0877 |  66691266.7312 |
| A          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |   9324 |  2298.3938 |  6884.4207 |    0.3213 |   -0.1221 |  66691266.7312 |
| A          | atc1                | N NERVOUS SYSTEM                                      | naive               |  18276 |  2253.6464 | 17898.1335 |    0.2667 |    0.0737 | 154435686.4066 |
| A          | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |  18276 |  2746.1010 | 23572.4374 |    0.3250 |   -0.1288 | 154435686.4066 |
| A          | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |  18276 |  3020.5127 | 27761.4433 |    0.3574 |    0.0275 | 154435686.4066 |
| A          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | naive               |    552 |  1342.4952 |  2505.7323 |    0.1704 |   -0.0432 |   4348454.3248 |
| A          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |    552 |  2135.8805 |  4394.8730 |    0.2711 |   -0.1561 |   4348454.3248 |
| A          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |    552 |  1682.2488 |  2811.7520 |    0.2135 |   -0.1257 |   4348454.3248 |
| A          | atc1                | R RESPIRATORY SYSTEM                                  | naive               |  13080 |  4406.9466 | 13247.2331 |    0.4781 |    0.2335 | 120574346.4776 |
| A          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |  13080 |  3407.3994 |  9766.3664 |    0.3696 |    0.0343 | 120574346.4776 |
| A          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |  13080 |  2986.0748 |  9883.3920 |    0.3239 |   -0.0138 | 120574346.4776 |
| A          | atc1                | S SENSORY ORGANS                                      | naive               |   3168 |  1399.2701 |  3546.2531 |    0.2394 |   -0.1105 |  18518453.4023 |
| A          | atc1                | S SENSORY ORGANS                                      | catboost_none       |   3168 |  1421.8440 |  3495.5259 |    0.2432 |   -0.0636 |  18518453.4023 |
| A          | atc1                | S SENSORY ORGANS                                      | catboost_both       |   3168 |  1637.5584 |  3706.7295 |    0.2801 |   -0.1853 |  18518453.4023 |
| A          | atc1                | V VARIOUS                                             | naive               |   1512 |   328.9052 |  2051.5505 |    0.2874 |    0.0091 |   1730402.5813 |
| A          | atc1                | V VARIOUS                                             | catboost_none       |   1512 |   288.5680 |  1867.4233 |    0.2521 |   -0.0491 |   1730402.5813 |
| A          | atc1                | V VARIOUS                                             | catboost_both       |   1512 |   327.2944 |  1872.4076 |    0.2860 |   -0.0414 |   1730402.5813 |
| A          | nfc                 | Lung Administration                                   | naive               |    912 |  1375.0775 |  3528.6981 |    0.2667 |    0.1432 |   4702968.7722 |
| A          | nfc                 | Lung Administration                                   | catboost_none       |    912 |  1319.9304 |  3667.3504 |    0.2560 |    0.0188 |   4702968.7722 |
| A          | nfc                 | Lung Administration                                   | catboost_both       |    912 |  1218.3044 |  3465.0327 |    0.2363 |   -0.0161 |   4702968.7722 |
| A          | nfc                 | Nasal Topical                                         | naive               |   2064 |  6832.1018 | 16983.6527 |    0.3195 |    0.1657 |  44130543.7721 |
| A          | nfc                 | Nasal Topical                                         | catboost_none       |   2064 |  5907.0506 | 14664.2535 |    0.2763 |    0.0642 |  44130543.7721 |
| A          | nfc                 | Nasal Topical                                         | catboost_both       |   2064 |  5935.7372 | 17842.2643 |    0.2776 |   -0.0473 |  44130543.7721 |
| A          | nfc                 | Nasal systemic                                        | naive               |     84 |  1030.7497 |  2022.0164 |    0.3953 |    0.1510 |    219032.5998 |
| A          | nfc                 | Nasal systemic                                        | catboost_none       |     84 |   720.9962 |  1095.5765 |    0.2765 |    0.1296 |    219032.5998 |
| A          | nfc                 | Nasal systemic                                        | catboost_both       |     84 |   733.0865 |  1067.1076 |    0.2811 |   -0.0270 |    219032.5998 |
| A          | nfc                 | Non-Human Use and Others                              | naive               |     84 |   648.6811 |  1326.6659 |    0.3250 |   -0.1127 |    167643.8290 |
| A          | nfc                 | Non-Human Use and Others                              | catboost_none       |     84 |  2374.3240 |  5351.6374 |    1.1897 |    1.0860 |    167643.8290 |
| A          | nfc                 | Non-Human Use and Others                              | catboost_both       |     84 |  3340.1312 |  7011.1421 |    1.6736 |    1.3768 |    167643.8290 |
| A          | nfc                 | Ophthalmic                                            | naive               |   2916 |  1304.7332 |  3368.6584 |    0.2380 |   -0.1213 |  15988966.8910 |
| A          | nfc                 | Ophthalmic                                            | catboost_none       |   2916 |  1337.0736 |  3373.4888 |    0.2438 |   -0.0446 |  15988966.8910 |
| A          | nfc                 | Ophthalmic                                            | catboost_both       |   2916 |  1530.6774 |  3597.1331 |    0.2792 |   -0.1729 |  15988966.8910 |
| A          | nfc                 | Oral Liquid Ordinary                                  | naive               |  15276 |  2303.7578 |  7441.3693 |    0.4373 |    0.2316 |  80474325.7151 |
| A          | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |  15276 |  2150.7936 |  7884.5851 |    0.4083 |    0.1817 |  80474325.7151 |
| A          | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |  15276 |  1722.5301 |  5593.9222 |    0.3270 |    0.0378 |  80474325.7151 |
| A          | nfc                 | Oral Solid Ordinary                                   | naive               |  57096 |  2275.8816 | 12253.5834 |    0.2665 |    0.0619 | 487517535.4785 |
| A          | nfc                 | Oral Solid Ordinary                                   | catboost_none       |  57096 |  2912.2001 | 17799.6375 |    0.3411 |   -0.1265 | 487517535.4785 |
| A          | nfc                 | Oral Solid Ordinary                                   | catboost_both       |  57096 |  2521.4554 | 17010.4840 |    0.2953 |   -0.0407 | 487517535.4785 |
| A          | nfc                 | Oral Solid Retard                                     | naive               |   2400 |  1066.9203 |  2344.5967 |    0.2384 |    0.0033 |  10739076.6516 |
| A          | nfc                 | Oral Solid Retard                                     | catboost_none       |   2400 |  1126.3537 |  2352.4395 |    0.2517 |    0.0221 |  10739076.6516 |
| A          | nfc                 | Oral Solid Retard                                     | catboost_both       |   2400 |  1209.3811 |  2453.6735 |    0.2703 |   -0.0934 |  10739076.6516 |
| A          | nfc                 | Oral Topical                                          | naive               |   2364 |  4763.7857 | 14992.5250 |    0.5972 |    0.3324 |  18855997.1411 |
| A          | nfc                 | Oral Topical                                          | catboost_none       |   2364 |  3568.3547 |  9220.9722 |    0.4474 |    0.2015 |  18855997.1411 |
| A          | nfc                 | Oral Topical                                          | catboost_both       |   2364 |  3172.1384 |  8464.2140 |    0.3977 |    0.0714 |  18855997.1411 |
| A          | nfc                 | Other systemic                                        | naive               |    444 |   771.6324 |  2521.6319 |    0.2386 |   -0.0444 |   1435911.7768 |
| A          | nfc                 | Other systemic                                        | catboost_none       |    444 |  1028.7403 |  2872.1432 |    0.3181 |   -0.1596 |   1435911.7768 |
| A          | nfc                 | Other systemic                                        | catboost_both       |    444 |   838.5018 |  2437.5813 |    0.2593 |   -0.1231 |   1435911.7768 |
| A          | nfc                 | Otic                                                  | naive               |    276 |  2487.9328 |  5065.4313 |    0.2562 |   -0.0242 |   2680708.7993 |
| A          | nfc                 | Otic                                                  | catboost_none       |    276 |  2412.2412 |  4568.2839 |    0.2484 |   -0.1645 |   2680708.7993 |
| A          | nfc                 | Otic                                                  | catboost_both       |    276 |  2813.9379 |  4682.8276 |    0.2897 |   -0.2492 |   2680708.7993 |
| A          | nfc                 | Parenteral Ordinary                                   | naive               |  24984 |   749.9653 |  3949.1825 |    0.2597 |   -0.0049 |  72157131.9825 |
| A          | nfc                 | Parenteral Ordinary                                   | catboost_none       |  24984 |   916.4535 |  4784.3284 |    0.3173 |   -0.0973 |  72157131.9825 |
| A          | nfc                 | Parenteral Ordinary                                   | catboost_both       |  24984 |   807.4255 |  3797.0218 |    0.2796 |   -0.1212 |  72157131.9825 |
| A          | nfc                 | Parenteral Retard                                     | naive               |    948 |   497.3009 |  1064.6040 |    0.2736 |    0.1788 |   1723023.0513 |
| A          | nfc                 | Parenteral Retard                                     | catboost_none       |    948 |   487.4000 |  1015.0401 |    0.2682 |    0.1840 |   1723023.0513 |
| A          | nfc                 | Parenteral Retard                                     | catboost_both       |    948 |   423.8405 |   909.8182 |    0.2332 |    0.0331 |   1723023.0513 |
| A          | nfc                 | Rectal systemic                                       | naive               |    912 |  1520.7195 |  2931.5092 |    0.3177 |    0.1253 |   4364761.6539 |
| A          | nfc                 | Rectal systemic                                       | catboost_none       |    912 |  1295.1011 |  2698.9207 |    0.2706 |    0.0319 |   4364761.6539 |
| A          | nfc                 | Rectal systemic                                       | catboost_both       |    912 |  1331.9915 |  2572.0060 |    0.2783 |   -0.0543 |   4364761.6539 |
| A          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | naive               |  12420 |  2284.3873 |  8061.3715 |    0.3208 |   -0.0657 |  88432486.4431 |
| A          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |  12420 |  2385.3726 |  7923.1022 |    0.3350 |   -0.0058 |  88432486.4431 |
| A          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |  12420 |  2384.7182 |  7795.3302 |    0.3349 |   -0.0864 |  88432486.4431 |
| A          | nfc                 | Vaginal                                               | naive               |   1392 |   615.9072 |  1685.9462 |    0.2446 |   -0.0236 |   3505270.1401 |
| A          | nfc                 | Vaginal                                               | catboost_none       |   1392 |   610.1503 |  1496.8697 |    0.2423 |   -0.0470 |   3505270.1401 |
| A          | nfc                 | Vaginal                                               | catboost_both       |   1392 |   784.5641 |  1681.8243 |    0.3116 |   -0.1916 |   3505270.1401 |
| A          | volume_quintile     | Q1 (smallest)                                         | naive               |  24924 |    86.8534 |  3117.7599 |   12.2902 |   11.5105 |    176134.9101 |
| A          | volume_quintile     | Q1 (smallest)                                         | catboost_none       |  24924 |    88.3937 |  1984.5913 |   12.5082 |   12.1475 |    176134.9101 |
| A          | volume_quintile     | Q1 (smallest)                                         | catboost_both       |  24924 |    88.2051 |  2360.3457 |   12.4815 |   12.0708 |    176134.9101 |
| A          | volume_quintile     | Q2                                                    | naive               |  24912 |   186.9577 |   468.2058 |    0.8213 |    0.3648 |   5670674.1712 |
| A          | volume_quintile     | Q2                                                    | catboost_none       |  24912 |   255.2521 |   626.1701 |    1.1214 |    0.8483 |   5670674.1712 |
| A          | volume_quintile     | Q2                                                    | catboost_both       |  24912 |   208.9318 |   578.1034 |    0.9179 |    0.4960 |   5670674.1712 |
| A          | volume_quintile     | Q3                                                    | naive               |  24912 |   544.4540 |  1152.7818 |    0.4872 |    0.1102 |  27841259.4972 |
| A          | volume_quintile     | Q3                                                    | catboost_none       |  24912 |   635.2591 |  1349.0121 |    0.5684 |    0.2144 |  27841259.4972 |
| A          | volume_quintile     | Q3                                                    | catboost_both       |  24912 |   550.8384 |  1167.0490 |    0.4929 |    0.0334 |  27841259.4972 |
| A          | volume_quintile     | Q4                                                    | naive               |  24912 |  1447.4087 |  2823.6941 |    0.3783 |    0.0610 |  95321308.4847 |
| A          | volume_quintile     | Q4                                                    | catboost_none       |  24912 |  1556.5818 |  2775.1714 |    0.4068 |    0.0360 |  95321308.4847 |
| A          | volume_quintile     | Q4                                                    | catboost_both       |  24912 |  1475.5199 |  2700.2898 |    0.3856 |   -0.0623 |  95321308.4847 |
| A          | volume_quintile     | Q5 (largest)                                          | naive               |  24912 |  7734.0243 | 21339.0491 |    0.2721 |    0.0603 | 708086007.6341 |
| A          | volume_quintile     | Q5 (largest)                                          | catboost_none       |  24912 |  8863.0835 | 28875.7752 |    0.3118 |   -0.0916 | 708086007.6341 |
| A          | volume_quintile     | Q5 (largest)                                          | catboost_both       |  24912 |  7811.9974 | 27371.8487 |    0.2748 |   -0.0553 | 708086007.6341 |
| B          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | hierarchical_median |  14832 |  9040.8099 | 26760.6123 |    1.0170 |   -0.5362 | 131855829.7337 |
| B          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |  14832 |  9016.1819 | 26113.5951 |    1.0142 |   -0.4399 | 131855829.7337 |
| B          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |  14832 |  9091.6762 | 25719.8956 |    1.0227 |   -0.3286 | 131855829.7337 |
| B          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | hierarchical_median |   4440 |  8691.9977 | 27190.0052 |    0.9646 |   -0.6720 |  40008719.3940 |
| B          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |   4440 |  9374.5786 | 26028.5169 |    1.0404 |   -0.3988 |  40008719.3940 |
| B          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |   4440 |  8852.5457 | 25472.0861 |    0.9824 |   -0.4206 |  40008719.3940 |
| B          | atc1                | C CARDIOVASCULAR SYSTEM                               | hierarchical_median |  14676 |  7984.6688 | 24544.0569 |    0.9945 |   -0.5036 | 117828410.2381 |
| B          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |  14676 |  8132.0492 | 24391.6110 |    1.0129 |   -0.3580 | 117828410.2381 |
| B          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |  14676 |  8192.8668 | 23924.8214 |    1.0205 |   -0.2639 | 117828410.2381 |
| B          | atc1                | D DERMATOLOGICAL                                      | hierarchical_median |   7572 |  7635.5027 | 20910.0455 |    1.0123 |   -0.5675 |  57116233.0636 |
| B          | atc1                | D DERMATOLOGICAL                                      | catboost_none       |   7572 |  8417.2964 | 19904.6407 |    1.1159 |   -0.1475 |  57116233.0636 |
| B          | atc1                | D DERMATOLOGICAL                                      | catboost_both       |   7572 |  8528.4108 | 20090.4526 |    1.1306 |   -0.1493 |  57116233.0636 |
| B          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | hierarchical_median |   4464 |  2623.1612 |  6430.5724 |    0.9555 |   -0.4611 |  12255299.0003 |
| B          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |   4464 |  3107.2617 |  6622.1732 |    1.1318 |    0.0341 |  12255299.0003 |
| B          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |   4464 |  2651.2808 |  6243.2248 |    0.9657 |   -0.2075 |  12255299.0003 |
| B          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | hierarchical_median |   1152 |  4970.2840 |  8409.0343 |    0.9840 |   -0.1931 |   5818862.7663 |
| B          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |   1152 |  4703.3894 |  8140.2054 |    0.9312 |   -0.3746 |   5818862.7663 |
| B          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |   1152 |  5161.9163 |  7999.3927 |    1.0219 |   -0.0134 |   5818862.7663 |
| B          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | hierarchical_median |  10668 |  4386.3493 | 11795.1571 |    1.0936 |   -0.5040 |  42789124.6923 |
| B          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |  10668 |  6154.5799 | 11835.0231 |    1.5344 |    0.3462 |  42789124.6923 |
| B          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |  10668 |  4623.5592 | 11036.1747 |    1.1527 |   -0.1752 |  42789124.6923 |
| B          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | hierarchical_median |   3852 |   406.5482 |  1508.2450 |    0.9927 |   -0.5300 |   1577593.2105 |
| B          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |   3852 |  2495.1633 |  3471.6440 |    6.0924 |    5.4779 |   1577593.2105 |
| B          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |   3852 |   494.6855 |  1543.6393 |    1.2079 |   -0.0581 |   1577593.2105 |
| B          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | hierarchical_median |   7836 |  7315.5697 | 17990.7419 |    0.9554 |   -0.5131 |  59998620.5684 |
| B          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |   7836 |  8214.4926 | 18914.5124 |    1.0728 |   -0.2468 |  59998620.5684 |
| B          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |   7836 |  7913.3221 | 17578.8558 |    1.0335 |   -0.2310 |  59998620.5684 |
| B          | atc1                | N NERVOUS SYSTEM                                      | hierarchical_median |  15432 |  9084.1447 | 63852.6087 |    1.0022 |   -0.6874 | 139875137.8964 |
| B          | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |  15432 | 10868.0373 | 64556.5803 |    1.1990 |   -0.3358 | 139875137.8964 |
| B          | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |  15432 |  9743.7021 | 63085.6813 |    1.0750 |   -0.4288 | 139875137.8964 |
| B          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | hierarchical_median |    420 |  8106.2485 | 16915.5254 |    0.8935 |   -0.5273 |   3810377.1344 |
| B          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |    420 | 10757.5871 | 19131.7033 |    1.1858 |   -0.1716 |   3810377.1344 |
| B          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |    420 |  7683.7144 | 16379.7398 |    0.8469 |   -0.4859 |   3810377.1344 |
| B          | atc1                | R RESPIRATORY SYSTEM                                  | hierarchical_median |   9756 |  9596.3730 | 32103.4775 |    0.9872 |   -0.6065 |  94836042.0275 |
| B          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |   9756 | 10643.0202 | 31287.0153 |    1.0949 |   -0.2570 |  94836042.0275 |
| B          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |   9756 | 10382.5701 | 31040.2093 |    1.0681 |   -0.2668 |  94836042.0275 |
| B          | atc1                | S SENSORY ORGANS                                      | hierarchical_median |   2508 |  6136.1927 | 12475.1646 |    1.0205 |   -0.5716 |  15081070.5454 |
| B          | atc1                | S SENSORY ORGANS                                      | catboost_none       |   2508 |  6123.7806 | 11992.7174 |    1.0184 |   -0.3813 |  15081070.5454 |
| B          | atc1                | S SENSORY ORGANS                                      | catboost_both       |   2508 |  6432.2943 | 12390.2524 |    1.0697 |   -0.3372 |  15081070.5454 |
| B          | atc1                | V VARIOUS                                             | hierarchical_median |    576 |  1814.4590 |  5562.4926 |    0.9954 |   -0.6605 |   1049977.0686 |
| B          | atc1                | V VARIOUS                                             | catboost_none       |    576 |  2523.4446 |  5218.0011 |    1.3843 |    0.0689 |   1049977.0686 |
| B          | atc1                | V VARIOUS                                             | catboost_both       |    576 |  1870.2000 |  5570.1947 |    1.0260 |   -0.5191 |   1049977.0686 |
| B          | nfc                 | Lung Administration                                   | hierarchical_median |    744 |  6222.6847 | 16430.0894 |    1.0324 |   -0.5514 |   4484270.3809 |
| B          | nfc                 | Lung Administration                                   | catboost_none       |    744 |  6287.0861 | 16358.9638 |    1.0431 |   -0.4485 |   4484270.3809 |
| B          | nfc                 | Lung Administration                                   | catboost_both       |    744 |  6236.2681 | 15978.5585 |    1.0347 |   -0.3148 |   4484270.3809 |
| B          | nfc                 | Nasal Topical                                         | hierarchical_median |   1728 | 22664.8263 | 66610.5836 |    0.9423 |   -0.6968 |  41564454.8837 |
| B          | nfc                 | Nasal Topical                                         | catboost_none       |   1728 | 24728.5314 | 65069.1100 |    1.0281 |   -0.3770 |  41564454.8837 |
| B          | nfc                 | Nasal Topical                                         | catboost_both       |   1728 | 24829.0733 | 65086.5504 |    1.0322 |   -0.3833 |  41564454.8837 |
| B          | nfc                 | Nasal systemic                                        | hierarchical_median |     84 |  2215.2099 |  3459.2377 |    0.8495 |   -0.7515 |    219032.5998 |
| B          | nfc                 | Nasal systemic                                        | catboost_none       |     84 |  2615.9200 |  3365.2535 |    1.0032 |   -0.5274 |    219032.5998 |
| B          | nfc                 | Nasal systemic                                        | catboost_both       |     84 |  2296.0020 |  3455.7145 |    0.8805 |   -0.5900 |    219032.5998 |
| B          | nfc                 | Non-Human Use and Others                              | hierarchical_median |     84 |  4380.8728 |  5848.0416 |    2.1951 |    1.1130 |    167643.8290 |
| B          | nfc                 | Non-Human Use and Others                              | catboost_none       |     84 |  3603.9174 |  4055.3465 |    1.8058 |    1.1302 |    167643.8290 |
| B          | nfc                 | Non-Human Use and Others                              | catboost_both       |     84 |  5996.1280 |  7135.4552 |    3.0044 |    2.1711 |    167643.8290 |
| B          | nfc                 | Ophthalmic                                            | hierarchical_median |   2316 |  5851.3938 | 12064.8256 |    1.0311 |   -0.5790 |  13143023.0203 |
| B          | nfc                 | Ophthalmic                                            | catboost_none       |   2316 |  5833.6024 | 11485.0090 |    1.0280 |   -0.3638 |  13143023.0203 |
| B          | nfc                 | Ophthalmic                                            | catboost_both       |   2316 |  6154.4592 | 11968.6649 |    1.0845 |   -0.3275 |  13143023.0203 |
| B          | nfc                 | Oral Liquid Ordinary                                  | hierarchical_median |  10596 |  5881.6317 | 16599.5715 |    0.9942 |   -0.5091 |  62687800.5954 |
| B          | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |  10596 |  6238.0310 | 16263.4405 |    1.0544 |   -0.2827 |  62687800.5954 |
| B          | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |  10596 |  6306.9511 | 16095.8490 |    1.0661 |   -0.1853 |  62687800.5954 |
| B          | nfc                 | Oral Solid Ordinary                                   | hierarchical_median |  47412 |  9216.5312 | 42254.0148 |    1.0029 |   -0.5894 | 435701535.0735 |
| B          | nfc                 | Oral Solid Ordinary                                   | catboost_none       |  47412 | 10390.5745 | 42531.6027 |    1.1307 |   -0.3041 | 435701535.0735 |
| B          | nfc                 | Oral Solid Ordinary                                   | catboost_both       |  47412 |  9537.9366 | 41458.0545 |    1.0379 |   -0.3560 | 435701535.0735 |
| B          | nfc                 | Oral Solid Retard                                     | hierarchical_median |   2052 |  4182.0621 |  9352.9096 |    0.9357 |   -0.4480 |   9171563.4020 |
| B          | nfc                 | Oral Solid Retard                                     | catboost_none       |   2052 |  4855.4514 |  9321.4461 |    1.0863 |   -0.1599 |   9171563.4020 |
| B          | nfc                 | Oral Solid Retard                                     | catboost_both       |   2052 |  4320.9124 |  9026.2422 |    0.9667 |   -0.2008 |   9171563.4020 |
| B          | nfc                 | Oral Topical                                          | hierarchical_median |   1452 |  7492.5079 | 16398.2997 |    1.0128 |   -0.4861 |  10741336.9495 |
| B          | nfc                 | Oral Topical                                          | catboost_none       |   1452 |  8167.5738 | 15651.6764 |    1.1041 |   -0.0783 |  10741336.9495 |
| B          | nfc                 | Oral Topical                                          | catboost_both       |   1452 |  7821.6401 | 15440.3836 |    1.0573 |   -0.1191 |  10741336.9495 |
| B          | nfc                 | Other systemic                                        | hierarchical_median |    372 |  2993.4794 |  8438.6918 |    0.8428 |   -0.7077 |   1321300.5379 |
| B          | nfc                 | Other systemic                                        | catboost_none       |    372 |  3785.6220 |  9068.6539 |    1.0658 |   -0.6908 |   1321300.5379 |
| B          | nfc                 | Other systemic                                        | catboost_both       |    372 |  3153.8088 |  7778.2849 |    0.8879 |   -0.4956 |   1321300.5379 |
| B          | nfc                 | Otic                                                  | hierarchical_median |    204 | 11496.1524 | 19591.1178 |    1.1898 |   -0.2554 |   1971179.9450 |
| B          | nfc                 | Otic                                                  | catboost_none       |    204 |  8678.4602 | 16272.7712 |    0.8981 |   -0.5307 |   1971179.9450 |
| B          | nfc                 | Otic                                                  | catboost_both       |    204 |  9413.4322 | 16184.7904 |    0.9742 |   -0.3753 |   1971179.9450 |
| B          | nfc                 | Parenteral Ordinary                                   | hierarchical_median |  19152 |  3408.5616 | 13023.7126 |    1.0261 |   -0.5314 |  63617911.2042 |
| B          | nfc                 | Parenteral Ordinary                                   | catboost_none       |  19152 |  4099.4439 | 12559.2554 |    1.2341 |   -0.0964 |  63617911.2042 |
| B          | nfc                 | Parenteral Ordinary                                   | catboost_both       |  19152 |  3658.6926 | 12351.9084 |    1.1014 |   -0.2014 |  63617911.2042 |
| B          | nfc                 | Parenteral Retard                                     | hierarchical_median |    648 |  1913.4154 |  2833.0511 |    0.9735 |   -0.2152 |   1273671.2408 |
| B          | nfc                 | Parenteral Retard                                     | catboost_none       |    648 |  2096.1544 |  2711.1401 |    1.0665 |    0.4463 |   1273671.2408 |
| B          | nfc                 | Parenteral Retard                                     | catboost_both       |    648 |  1864.3423 |  2495.2007 |    0.9485 |    0.1785 |   1273671.2408 |
| B          | nfc                 | Rectal systemic                                       | hierarchical_median |    744 |  4331.3301 |  6889.0158 |    1.0234 |   -0.3135 |   3148913.8653 |
| B          | nfc                 | Rectal systemic                                       | catboost_none       |    744 |  3868.3443 |  6413.4106 |    0.9140 |   -0.2995 |   3148913.8653 |
| B          | nfc                 | Rectal systemic                                       | catboost_both       |    744 |  4296.0442 |  6562.0653 |    1.0150 |   -0.1405 |   3148913.8653 |
| B          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | hierarchical_median |   9564 |  7525.9771 | 20696.9163 |    0.9968 |   -0.5596 |  72208160.3416 |
| B          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |   9564 |  8357.2406 | 19897.9686 |    1.1069 |   -0.1606 |  72208160.3416 |
| B          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |   9564 |  8407.0436 | 19978.6964 |    1.1135 |   -0.1442 |  72208160.3416 |
| B          | nfc                 | Vaginal                                               | hierarchical_median |   1032 |  2534.2469 |  3713.2238 |    1.0548 |   -0.1289 |   2479499.4705 |
| B          | nfc                 | Vaginal                                               | catboost_none       |   1032 |  2307.7238 |  3235.9650 |    0.9605 |   -0.1584 |   2479499.4705 |
| B          | nfc                 | Vaginal                                               | catboost_both       |   1032 |  2276.4084 |  3257.0750 |    0.9475 |   -0.2077 |   2479499.4705 |
| B          | volume_quintile     | Q1 (smallest)                                         | hierarchical_median |  19644 |  1955.6421 |  4032.9800 |  170.5506 |  170.3311 |    225250.6701 |
| B          | volume_quintile     | Q1 (smallest)                                         | catboost_none       |  19644 |  4001.5092 |  5220.1123 |  348.9696 |  348.9661 |    225250.6701 |
| B          | volume_quintile     | Q1 (smallest)                                         | catboost_both       |  19644 |  3313.3207 |  5080.7057 |  288.9531 |  288.9332 |    225250.6701 |
| B          | volume_quintile     | Q2                                                    | hierarchical_median |  19632 |  1880.3772 |  3911.8726 |    6.9914 |    6.7433 |   5280171.9899 |
| B          | volume_quintile     | Q2                                                    | catboost_none       |  19632 |  4235.4206 |  5585.7060 |   15.7476 |   15.7353 |   5280171.9899 |
| B          | volume_quintile     | Q2                                                    | catboost_both       |  19632 |  3482.6268 |  5252.9626 |   12.9486 |   12.9181 |   5280171.9899 |
| B          | volume_quintile     | Q3                                                    | hierarchical_median |  19632 |  2449.7950 |  7843.8364 |    1.9633 |    1.4230 |  24496741.7541 |
| B          | volume_quintile     | Q3                                                    | catboost_none       |  19632 |  3888.8692 |  6889.9991 |    3.1166 |    3.0496 |  24496741.7541 |
| B          | volume_quintile     | Q3                                                    | catboost_both       |  19632 |  3708.7445 |  7381.9370 |    2.9722 |    2.8720 |  24496741.7541 |
| B          | volume_quintile     | Q4                                                    | hierarchical_median |  19632 |  3502.8434 |  6680.6810 |    0.8459 |   -0.1400 |  81294233.1074 |
| B          | volume_quintile     | Q4                                                    | catboost_none       |  19632 |  3635.8361 | 10271.9582 |    0.8780 |    0.4607 |  81294233.1074 |
| B          | volume_quintile     | Q4                                                    | catboost_both       |  19632 |  3550.3900 |  6378.3138 |    0.8574 |    0.3866 |  81294233.1074 |
| B          | volume_quintile     | Q5 (largest)                                          | hierarchical_median |  19644 | 27095.2155 | 71757.2236 |    0.8688 |   -0.8353 | 612604899.8178 |
| B          | volume_quintile     | Q5 (largest)                                          | catboost_none       |  19644 | 25491.6373 | 71245.8607 |    0.8174 |   -0.7659 | 612604899.8178 |
| B          | volume_quintile     | Q5 (largest)                                          | catboost_both       |  19644 | 24746.1619 | 70103.7899 |    0.7935 |   -0.7373 | 612604899.8178 |
| C          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | hierarchical_mean   |  19812 |  9786.5087 | 24719.5670 |    1.2416 |   -0.1768 | 156163888.1542 |
| C          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |  19812 |  8733.2112 | 23706.8881 |    1.1080 |   -0.2738 | 156163888.1542 |
| C          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |  19812 |  8179.7564 | 23728.7669 |    1.0377 |   -0.3908 | 156163888.1542 |
| C          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | hierarchical_mean   |   6408 |  9513.6323 | 23803.8335 |    1.3790 |   -0.1092 |  44209696.6824 |
| C          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |   6408 |  8322.2386 | 23077.7462 |    1.2063 |   -0.3159 |  44209696.6824 |
| C          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |   6408 |  7175.8184 | 23038.6885 |    1.0401 |   -0.5829 |  44209696.6824 |
| C          | atc1                | C CARDIOVASCULAR SYSTEM                               | hierarchical_mean   |  16896 | 10465.0547 | 24609.7567 |    1.3644 |    0.0631 | 129594517.8649 |
| C          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |  16896 |  8175.6096 | 23213.5854 |    1.0659 |   -0.2605 | 129594517.8649 |
| C          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |  16896 |  7860.0221 | 23149.0277 |    1.0248 |   -0.3388 | 129594517.8649 |
| C          | atc1                | D DERMATOLOGICAL                                      | hierarchical_mean   |   9192 |  9484.3792 | 19744.5788 |    1.3347 |    0.0831 |  65320443.2641 |
| C          | atc1                | D DERMATOLOGICAL                                      | catboost_none       |   9192 |  8085.7697 | 18782.0413 |    1.1378 |   -0.1078 |  65320443.2641 |
| C          | atc1                | D DERMATOLOGICAL                                      | catboost_both       |   9192 |  7824.9594 | 18742.2233 |    1.1011 |   -0.1827 |  65320443.2641 |
| C          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | hierarchical_mean   |   6840 |  3368.2735 |  7119.2078 |    1.1492 |   -0.1964 |  20048678.2291 |
| C          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |   6840 |  4943.6814 |  7559.2867 |    1.6866 |    0.8419 |  20048678.2291 |
| C          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |   6840 |  3140.1509 |  7079.6565 |    1.0713 |   -0.2087 |  20048678.2291 |
| C          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | hierarchical_mean   |   1320 |  4937.0280 |  7751.6301 |    1.0716 |    0.0116 |   6081661.8168 |
| C          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |   1320 |  5100.5163 |  7669.6504 |    1.1070 |   -0.0356 |   6081661.8168 |
| C          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |   1320 |  4392.2645 |  7801.7392 |    0.9533 |   -0.4350 |   6081661.8168 |
| C          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | hierarchical_mean   |  12384 |  5529.2036 | 11623.1437 |    1.4531 |    0.0773 |  47123384.3838 |
| C          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |  12384 |  6521.0862 | 11138.7509 |    1.7137 |    0.6010 |  47123384.3838 |
| C          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |  12384 |  4524.2471 | 10886.9416 |    1.1890 |   -0.2378 |  47123384.3838 |
| C          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | hierarchical_mean   |   5808 |   606.0522 |  1660.8193 |    1.5613 |    0.1806 |   2254504.3781 |
| C          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |   5808 |  4534.5975 |  4810.4062 |   11.6819 |   11.2855 |   2254504.3781 |
| C          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |   5808 |   680.3131 |  1601.7800 |    1.7526 |    0.4561 |   2254504.3781 |
| C          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | hierarchical_mean   |   9324 |  8519.5381 | 16914.1805 |    1.1911 |   -0.0143 |  66691266.7312 |
| C          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |   9324 |  7932.0352 | 16701.9742 |    1.1090 |   -0.1515 |  66691266.7312 |
| C          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |   9324 |  7548.2330 | 16644.3673 |    1.0553 |   -0.2230 |  66691266.7312 |
| C          | atc1                | N NERVOUS SYSTEM                                      | hierarchical_mean   |  18276 | 10175.9459 | 59151.7921 |    1.2042 |   -0.3499 | 154435686.4066 |
| C          | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |  18276 | 10307.3381 | 58897.4362 |    1.2198 |   -0.2889 | 154435686.4066 |
| C          | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |  18276 |  9150.8874 | 58752.8246 |    1.0829 |   -0.4723 | 154435686.4066 |
| C          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | hierarchical_mean   |    552 |  9236.1843 | 16326.4657 |    1.1725 |   -0.0587 |   4348454.3248 |
| C          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |    552 |  7607.8746 | 14783.3041 |    0.9658 |   -0.1746 |   4348454.3248 |
| C          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |    552 |  7118.1317 | 15757.9475 |    0.9036 |   -0.5446 |   4348454.3248 |
| C          | atc1                | R RESPIRATORY SYSTEM                                  | hierarchical_mean   |  13080 | 11900.0664 | 28583.1823 |    1.2909 |    0.0547 | 120574346.4776 |
| C          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |  13080 | 10198.0891 | 28482.3153 |    1.1063 |   -0.2419 | 120574346.4776 |
| C          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |  13080 | 10187.4627 | 28559.1870 |    1.1051 |   -0.2336 | 120574346.4776 |
| C          | atc1                | S SENSORY ORGANS                                      | hierarchical_mean   |   3168 |  5937.1074 | 11299.7266 |    1.0157 |   -0.2570 |  18518453.4023 |
| C          | atc1                | S SENSORY ORGANS                                      | catboost_none       |   3168 |  6614.6622 | 11545.4968 |    1.1316 |   -0.0846 |  18518453.4023 |
| C          | atc1                | S SENSORY ORGANS                                      | catboost_both       |   3168 |  5678.7917 | 11481.5038 |    0.9715 |   -0.4194 |  18518453.4023 |
| C          | atc1                | V VARIOUS                                             | hierarchical_mean   |   1512 |  2183.8743 |  5361.4466 |    1.9082 |    0.2536 |   1730402.5813 |
| C          | atc1                | V VARIOUS                                             | catboost_none       |   1512 |  4426.1069 |  5703.4061 |    3.8675 |    2.6710 |   1730402.5813 |
| C          | atc1                | V VARIOUS                                             | catboost_both       |   1512 |  1537.2093 |  4741.6849 |    1.3432 |   -0.4015 |   1730402.5813 |
| C          | nfc                 | Lung Administration                                   | hierarchical_mean   |    912 |  8015.4194 | 16086.1183 |    1.5544 |    0.1689 |   4702968.7722 |
| C          | nfc                 | Lung Administration                                   | catboost_none       |    912 |  6147.5200 | 14721.0470 |    1.1921 |   -0.2314 |   4702968.7722 |
| C          | nfc                 | Lung Administration                                   | catboost_both       |    912 |  5572.4272 | 14585.7066 |    1.0806 |   -0.3447 |   4702968.7722 |
| C          | nfc                 | Nasal Topical                                         | hierarchical_mean   |   2064 | 26272.2279 | 58932.9684 |    1.2288 |    0.0228 |  44130543.7721 |
| C          | nfc                 | Nasal Topical                                         | catboost_none       |   2064 | 20692.7877 | 60805.1482 |    0.9678 |   -0.5583 |  44130543.7721 |
| C          | nfc                 | Nasal Topical                                         | catboost_both       |   2064 | 23766.7395 | 60926.5206 |    1.1116 |   -0.2994 |  44130543.7721 |
| C          | nfc                 | Nasal systemic                                        | hierarchical_mean   |     84 |  1817.0837 |  2860.4658 |    0.6969 |   -0.2519 |    219032.5998 |
| C          | nfc                 | Nasal systemic                                        | catboost_none       |     84 |  3107.2754 |  3643.8442 |    1.1917 |    0.7694 |    219032.5998 |
| C          | nfc                 | Nasal systemic                                        | catboost_both       |     84 |  1860.4439 |  3251.9509 |    0.7135 |   -0.3221 |    219032.5998 |
| C          | nfc                 | Non-Human Use and Others                              | hierarchical_mean   |     84 |  4129.0579 |  5983.0344 |    2.0689 |    1.2356 |    167643.8290 |
| C          | nfc                 | Non-Human Use and Others                              | catboost_none       |     84 |  3864.6602 |  4300.5567 |    1.9364 |    1.5416 |    167643.8290 |
| C          | nfc                 | Non-Human Use and Others                              | catboost_both       |     84 |  4528.3799 |  5208.5615 |    2.2690 |    1.5415 |    167643.8290 |
| C          | nfc                 | Ophthalmic                                            | hierarchical_mean   |   2916 |  5840.0322 | 11162.5687 |    1.0651 |   -0.2398 |  15988966.8910 |
| C          | nfc                 | Ophthalmic                                            | catboost_none       |   2916 |  6344.8638 | 11065.2834 |    1.1571 |   -0.0673 |  15988966.8910 |
| C          | nfc                 | Ophthalmic                                            | catboost_both       |   2916 |  5477.4527 | 11187.7245 |    0.9990 |   -0.3948 |  15988966.8910 |
| C          | nfc                 | Oral Liquid Ordinary                                  | hierarchical_mean   |  15276 |  7625.4272 | 16351.5156 |    1.4475 |    0.2179 |  80474325.7151 |
| C          | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |  15276 |  6539.4414 | 15145.9896 |    1.2413 |   -0.0260 |  80474325.7151 |
| C          | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |  15276 |  5683.2370 | 14957.7095 |    1.0788 |   -0.2563 |  80474325.7151 |
| C          | nfc                 | Oral Solid Ordinary                                   | hierarchical_mean   |  57096 |  9995.1190 | 39175.7794 |    1.1706 |   -0.2842 | 487517535.4785 |
| C          | nfc                 | Oral Solid Ordinary                                   | catboost_none       |  57096 | 10070.9741 | 38759.8209 |    1.1795 |   -0.1972 | 487517535.4785 |
| C          | nfc                 | Oral Solid Ordinary                                   | catboost_both       |  57096 |  8919.4949 | 38688.6919 |    1.0446 |   -0.4216 | 487517535.4785 |
| C          | nfc                 | Oral Solid Retard                                     | hierarchical_mean   |   2400 |  5983.7887 |  9992.1870 |    1.3373 |    0.1136 |  10739076.6516 |
| C          | nfc                 | Oral Solid Retard                                     | catboost_none       |   2400 |  4946.0235 |  9217.6152 |    1.1054 |   -0.1639 |  10739076.6516 |
| C          | nfc                 | Oral Solid Retard                                     | catboost_both       |   2400 |  4597.1867 |  9343.4702 |    1.0274 |   -0.3920 |  10739076.6516 |
| C          | nfc                 | Oral Topical                                          | hierarchical_mean   |   2364 |  9068.2201 | 15907.1293 |    1.1369 |   -0.0259 |  18855997.1411 |
| C          | nfc                 | Oral Topical                                          | catboost_none       |   2364 |  8634.6656 | 15435.3911 |    1.0825 |   -0.0898 |  18855997.1411 |
| C          | nfc                 | Oral Topical                                          | catboost_both       |   2364 |  8227.8053 | 15308.6322 |    1.0315 |   -0.1554 |  18855997.1411 |
| C          | nfc                 | Other systemic                                        | hierarchical_mean   |    444 |  4120.1788 |  7899.1695 |    1.2740 |   -0.0148 |   1435911.7768 |
| C          | nfc                 | Other systemic                                        | catboost_none       |    444 |  5545.5871 |  9000.0434 |    1.7148 |    0.2107 |   1435911.7768 |
| C          | nfc                 | Other systemic                                        | catboost_both       |    444 |  4418.3262 |  8390.7469 |    1.3662 |   -0.1094 |   1435911.7768 |
| C          | nfc                 | Otic                                                  | hierarchical_mean   |    276 |  8437.2690 | 13597.8745 |    0.8687 |   -0.2013 |   2680708.7993 |
| C          | nfc                 | Otic                                                  | catboost_none       |    276 |  8067.9973 | 13877.7082 |    0.8307 |   -0.3530 |   2680708.7993 |
| C          | nfc                 | Otic                                                  | catboost_both       |    276 |  7928.3578 | 14037.8605 |    0.8163 |   -0.5235 |   2680708.7993 |
| C          | nfc                 | Parenteral Ordinary                                   | hierarchical_mean   |  24984 |  5275.4880 | 13282.4445 |    1.8266 |    0.5201 |  72157131.9825 |
| C          | nfc                 | Parenteral Ordinary                                   | catboost_none       |  24984 |  4933.7967 | 12070.3639 |    1.7083 |    0.3645 |  72157131.9825 |
| C          | nfc                 | Parenteral Ordinary                                   | catboost_both       |  24984 |  3544.6655 | 11778.0820 |    1.2273 |   -0.1823 |  72157131.9825 |
| C          | nfc                 | Parenteral Retard                                     | hierarchical_mean   |    948 |  2257.4596 |  2930.4700 |    1.2420 |    0.5930 |   1723023.0513 |
| C          | nfc                 | Parenteral Retard                                     | catboost_none       |    948 |  2841.5498 |  3338.9592 |    1.5634 |    0.6251 |   1723023.0513 |
| C          | nfc                 | Parenteral Retard                                     | catboost_both       |    948 |  1864.8922 |  2495.0727 |    1.0261 |    0.2422 |   1723023.0513 |
| C          | nfc                 | Rectal systemic                                       | hierarchical_mean   |    912 |  6787.3666 |  8800.7114 |    1.4182 |    0.5158 |   4364761.6539 |
| C          | nfc                 | Rectal systemic                                       | catboost_none       |    912 |  4447.4430 |  6747.7177 |    0.9293 |   -0.2370 |   4364761.6539 |
| C          | nfc                 | Rectal systemic                                       | catboost_both       |    912 |  4642.6656 |  7065.3442 |    0.9701 |   -0.3177 |   4364761.6539 |
| C          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | hierarchical_mean   |  12420 |  9554.6915 | 19364.7773 |    1.3419 |    0.1205 |  88432486.4431 |
| C          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |  12420 |  8042.2087 | 18375.6834 |    1.1295 |   -0.0966 |  88432486.4431 |
| C          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |  12420 |  7721.1473 | 18354.2959 |    1.0844 |   -0.1793 |  88432486.4431 |
| C          | nfc                 | Vaginal                                               | hierarchical_mean   |   1392 |  2646.5422 |  3798.6423 |    1.0510 |   -0.1013 |   3505270.1401 |
| C          | nfc                 | Vaginal                                               | catboost_none       |   1392 |  3477.8430 |  4192.4653 |    1.3811 |    0.6348 |   3505270.1401 |
| C          | nfc                 | Vaginal                                               | catboost_both       |   1392 |  2385.5303 |  3615.3007 |    0.9473 |   -0.1911 |   3505270.1401 |
| C          | volume_quintile     | Q1 (smallest)                                         | hierarchical_mean   |  24924 |  4727.1677 |  8159.7937 |  668.9187 |  668.8318 |    176134.9101 |
| C          | volume_quintile     | Q1 (smallest)                                         | catboost_none       |  24924 |  5310.0154 |  5774.6385 |  751.3946 |  751.3946 |    176134.9101 |
| C          | volume_quintile     | Q1 (smallest)                                         | catboost_both       |  24924 |  3220.3831 |  4128.0260 |  455.7009 |  455.7008 |    176134.9101 |
| C          | volume_quintile     | Q2                                                    | hierarchical_mean   |  24912 |  5162.0942 |  8400.0091 |   22.6777 |   22.5916 |   5670674.1712 |
| C          | volume_quintile     | Q2                                                    | catboost_none       |  24912 |  5296.0406 |  5682.9724 |   23.2662 |   23.2662 |   5670674.1712 |
| C          | volume_quintile     | Q2                                                    | catboost_both       |  24912 |  3539.7432 |  4457.3498 |   15.5505 |   15.5381 |   5670674.1712 |
| C          | volume_quintile     | Q3                                                    | hierarchical_mean   |  24912 |  4981.3762 |  7986.4346 |    4.4573 |    4.3061 |  27841259.4972 |
| C          | volume_quintile     | Q3                                                    | catboost_none       |  24912 |  4743.9613 |  5269.0763 |    4.2448 |    4.2384 |  27841259.4972 |
| C          | volume_quintile     | Q3                                                    | catboost_both       |  24912 |  3207.0807 |  4076.9150 |    2.8697 |    2.8227 |  27841259.4972 |
| C          | volume_quintile     | Q4                                                    | hierarchical_mean   |  24912 |  4830.0655 |  8581.2866 |    1.2623 |    0.8114 |  95321308.4847 |
| C          | volume_quintile     | Q4                                                    | catboost_none       |  24912 |  2891.2323 |  3710.4476 |    0.7556 |    0.5887 |  95321308.4847 |
| C          | volume_quintile     | Q4                                                    | catboost_both       |  24912 |  2627.4474 |  4823.3472 |    0.6867 |    0.2996 |  95321308.4847 |
| C          | volume_quintile     | Q5 (largest)                                          | hierarchical_mean   |  24912 | 23195.0163 | 64214.0819 |    0.8161 |   -0.7270 | 708086007.6341 |
| C          | volume_quintile     | Q5 (largest)                                          | catboost_none       |  24912 | 22460.4956 | 64476.8754 |    0.7902 |   -0.7726 | 708086007.6341 |
| C          | volume_quintile     | Q5 (largest)                                          | catboost_both       |  24912 | 23336.0009 | 64537.0104 |    0.8210 |   -0.7936 | 708086007.6341 |
| C          | known_atc_depth     | 1                                                     | hierarchical_mean   |   2016 |  5826.0414 |  8304.3613 |    2.0441 |    1.0854 |   5745975.2675 |
| C          | known_atc_depth     | 1                                                     | catboost_none       |   2016 |  4689.9478 |  7148.7385 |    1.6455 |    0.7630 |   5745975.2675 |
| C          | known_atc_depth     | 1                                                     | catboost_both       |   2016 |  3154.0880 |  6662.4306 |    1.1066 |   -0.0602 |   5745975.2675 |
| C          | known_atc_depth     | 2                                                     | hierarchical_mean   |   6972 |  7450.5577 | 19179.4308 |    1.2041 |   -0.1843 |  43141745.6103 |
| C          | known_atc_depth     | 2                                                     | catboost_none       |   6972 |  6928.9883 | 18256.9375 |    1.1198 |   -0.0872 |  43141745.6103 |
| C          | known_atc_depth     | 2                                                     | catboost_both       |   6972 |  6100.3020 | 18341.9436 |    0.9859 |   -0.3981 |  43141745.6103 |
| C          | known_atc_depth     | 3                                                     | hierarchical_mean   |  31668 |  7620.6444 | 19715.4630 |    1.2848 |   -0.1052 | 187839957.6922 |
| C          | known_atc_depth     | 3                                                     | catboost_none       |  31668 |  7594.5348 | 18615.0864 |    1.2804 |   -0.0467 | 187839957.6922 |
| C          | known_atc_depth     | 3                                                     | catboost_both       |  31668 |  6398.0881 | 18542.9610 |    1.0787 |   -0.3405 | 187839957.6922 |
| C          | known_atc_depth     | 4                                                     | hierarchical_mean   |  61164 |  8954.7703 | 28935.5125 |    1.2731 |   -0.0763 | 430232008.8136 |
| C          | known_atc_depth     | 4                                                     | catboost_none       |  61164 |  8426.2159 | 28764.0008 |    1.1979 |   -0.1643 | 430232008.8136 |
| C          | known_atc_depth     | 4                                                     | catboost_both       |  61164 |  7613.8876 | 28686.3268 |    1.0824 |   -0.3305 | 430232008.8136 |
| C          | known_atc_depth     | 5                                                     | hierarchical_mean   |  22752 |  9491.2172 | 43645.3470 |    1.2692 |   -0.1019 | 170135697.3138 |
| C          | known_atc_depth     | 5                                                     | catboost_none       |  22752 |  8807.0043 | 43082.7307 |    1.1777 |   -0.1754 | 170135697.3138 |
| C          | known_atc_depth     | 5                                                     | catboost_both       |  22752 |  7820.9700 | 42973.4031 |    1.0459 |   -0.3690 | 170135697.3138 |
| D          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | hierarchical_mean   |  19812 | 10649.9922 | 24168.7508 |    1.3511 |    0.0866 | 156163888.1542 |
| D          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |  19812 |  8962.0326 | 23693.4471 |    1.1370 |   -0.1999 | 156163888.1542 |
| D          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |  19812 |  9093.3242 | 23661.7042 |    1.1536 |   -0.1563 | 156163888.1542 |
| D          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | hierarchical_mean   |   6408 |  9591.7475 | 22908.5306 |    1.3903 |   -0.0296 |  44209696.6824 |
| D          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |   6408 |  8355.3742 | 22987.0004 |    1.2111 |   -0.2969 |  44209696.6824 |
| D          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |   6408 |  8093.6572 | 23029.7198 |    1.1731 |   -0.3747 |  44209696.6824 |
| D          | atc1                | C CARDIOVASCULAR SYSTEM                               | hierarchical_mean   |  16896 |  9678.3773 | 23330.4399 |    1.2618 |    0.0709 | 129594517.8649 |
| D          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |  16896 |  8053.3227 | 23267.8989 |    1.0500 |   -0.3198 | 129594517.8649 |
| D          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |  16896 |  8223.5237 | 23307.4017 |    1.0721 |   -0.2817 | 129594517.8649 |
| D          | atc1                | D DERMATOLOGICAL                                      | hierarchical_mean   |   9192 |  8271.0026 | 19330.1197 |    1.1639 |   -0.1625 |  65320443.2641 |
| D          | atc1                | D DERMATOLOGICAL                                      | catboost_none       |   9192 |  8408.1423 | 18849.9566 |    1.1832 |   -0.0241 |  65320443.2641 |
| D          | atc1                | D DERMATOLOGICAL                                      | catboost_both       |   9192 |  8352.9431 | 18910.2701 |    1.1754 |   -0.0443 |  65320443.2641 |
| D          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | hierarchical_mean   |   6840 |  3334.0816 |  7122.5027 |    1.1375 |   -0.1129 |  20048678.2291 |
| D          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |   6840 |  4743.7335 |  7414.1122 |    1.6184 |    0.7371 |  20048678.2291 |
| D          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |   6840 |  4238.8015 |  7163.3349 |    1.4462 |    0.4892 |  20048678.2291 |
| D          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | hierarchical_mean   |   1320 |  8533.1797 | 10424.9994 |    1.8521 |    0.8733 |   6081661.8168 |
| D          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |   1320 |  5262.6036 |  7747.4649 |    1.1422 |   -0.0103 |   6081661.8168 |
| D          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |   1320 |  5594.5364 |  7997.1143 |    1.2143 |    0.0587 |   6081661.8168 |
| D          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | hierarchical_mean   |  12384 |  6458.9423 | 11429.8077 |    1.6974 |    0.4596 |  47123384.3838 |
| D          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |  12384 |  6576.0082 | 11093.3979 |    1.7282 |    0.6190 |  47123384.3838 |
| D          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |  12384 |  6234.1100 | 10965.3135 |    1.6383 |    0.4821 |  47123384.3838 |
| D          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | hierarchical_mean   |   5808 |   804.3920 |  1708.9054 |    2.0723 |    0.5230 |   2254504.3781 |
| D          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |   5808 |  5128.8138 |  5348.8314 |   13.2127 |   12.8898 |   2254504.3781 |
| D          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |   5808 |  4073.6028 |  4348.7163 |   10.4943 |    9.8710 |   2254504.3781 |
| D          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | hierarchical_mean   |   9324 |  8004.1580 | 16812.7495 |    1.1190 |   -0.1654 |  66691266.7312 |
| D          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |   9324 |  8234.1813 | 16675.1562 |    1.1512 |   -0.0424 |  66691266.7312 |
| D          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |   9324 |  8104.6800 | 16644.9079 |    1.1331 |   -0.0875 |  66691266.7312 |
| D          | atc1                | N NERVOUS SYSTEM                                      | hierarchical_mean   |  18276 | 12149.4150 | 59244.8090 |    1.4378 |   -0.0421 | 154435686.4066 |
| D          | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |  18276 | 10172.7246 | 58992.1347 |    1.2038 |   -0.3179 | 154435686.4066 |
| D          | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |  18276 |  9949.1891 | 58989.7580 |    1.1774 |   -0.3527 | 154435686.4066 |
| D          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | hierarchical_mean   |    552 |  7705.7357 | 15464.6928 |    0.9782 |   -0.3217 |   4348454.3248 |
| D          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |    552 |  8443.3488 | 14076.2925 |    1.0718 |    0.1896 |   4348454.3248 |
| D          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |    552 |  7408.3884 | 15003.3445 |    0.9404 |   -0.2824 |   4348454.3248 |
| D          | atc1                | R RESPIRATORY SYSTEM                                  | hierarchical_mean   |  13080 | 11920.7784 | 28937.1501 |    1.2932 |    0.0235 | 120574346.4776 |
| D          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |  13080 |  9942.9718 | 28884.3359 |    1.0786 |   -0.3480 | 120574346.4776 |
| D          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |  13080 | 10007.5435 | 28822.9254 |    1.0856 |   -0.3357 | 120574346.4776 |
| D          | atc1                | S SENSORY ORGANS                                      | hierarchical_mean   |   3168 |  9143.5428 | 12416.6952 |    1.5642 |    0.5666 |  18518453.4023 |
| D          | atc1                | S SENSORY ORGANS                                      | catboost_none       |   3168 |  6192.2456 | 11416.6373 |    1.0593 |   -0.1964 |  18518453.4023 |
| D          | atc1                | S SENSORY ORGANS                                      | catboost_both       |   3168 |  6557.8090 | 11320.7843 |    1.1219 |   -0.0575 |  18518453.4023 |
| D          | atc1                | V VARIOUS                                             | hierarchical_mean   |   1512 |  3536.9518 |  5634.8571 |    3.0905 |    1.5045 |   1730402.5813 |
| D          | atc1                | V VARIOUS                                             | catboost_none       |   1512 |  6025.7476 |  6996.7455 |    5.2652 |    4.1976 |   1730402.5813 |
| D          | atc1                | V VARIOUS                                             | catboost_both       |   1512 |  4284.2244 |  5569.9426 |    3.7435 |    2.4996 |   1730402.5813 |
| D          | nfc                 | Lung Administration                                   | hierarchical_mean   |    912 |  9761.3731 | 15371.7008 |    1.8929 |    0.8114 |   4702968.7722 |
| D          | nfc                 | Lung Administration                                   | catboost_none       |    912 |  5833.5793 | 14528.6997 |    1.1312 |   -0.2506 |   4702968.7722 |
| D          | nfc                 | Lung Administration                                   | catboost_both       |    912 |  7604.0774 | 14516.1490 |    1.4746 |    0.2499 |   4702968.7722 |
| D          | nfc                 | Nasal Topical                                         | hierarchical_mean   |   2064 | 20528.6895 | 60957.2401 |    0.9601 |   -0.5717 |  44130543.7721 |
| D          | nfc                 | Nasal Topical                                         | catboost_none       |   2064 | 20037.6897 | 61752.2688 |    0.9372 |   -0.7205 |  44130543.7721 |
| D          | nfc                 | Nasal Topical                                         | catboost_both       |   2064 | 20002.9052 | 61600.9107 |    0.9355 |   -0.7095 |  44130543.7721 |
| D          | nfc                 | Nasal systemic                                        | hierarchical_mean   |     84 |  5952.0573 |  7732.4354 |    2.2826 |    1.3961 |    219032.5998 |
| D          | nfc                 | Nasal systemic                                        | catboost_none       |     84 |  3483.2724 |  3967.5881 |    1.3359 |    1.0688 |    219032.5998 |
| D          | nfc                 | Nasal systemic                                        | catboost_both       |     84 |  3039.2414 |  3690.6108 |    1.1656 |    0.5134 |    219032.5998 |
| D          | nfc                 | Non-Human Use and Others                              | hierarchical_mean   |     84 |  2911.1638 |  3388.5997 |    1.4587 |    0.8143 |    167643.8290 |
| D          | nfc                 | Non-Human Use and Others                              | catboost_none       |     84 |  6728.4805 |  7315.7957 |    3.3714 |    3.2779 |    167643.8290 |
| D          | nfc                 | Non-Human Use and Others                              | catboost_both       |     84 |  4583.9314 |  5088.1244 |    2.2968 |    1.9043 |    167643.8290 |
| D          | nfc                 | Ophthalmic                                            | hierarchical_mean   |   2916 |  9165.1773 | 12177.5611 |    1.6715 |    0.7185 |  15988966.8910 |
| D          | nfc                 | Ophthalmic                                            | catboost_none       |   2916 |  5988.3368 | 11111.9724 |    1.0921 |   -0.1757 |  15988966.8910 |
| D          | nfc                 | Ophthalmic                                            | catboost_both       |   2916 |  6434.6325 | 11041.3960 |    1.1735 |   -0.0046 |  15988966.8910 |
| D          | nfc                 | Oral Liquid Ordinary                                  | hierarchical_mean   |  15276 |  8595.1050 | 15715.3932 |    1.6316 |    0.5182 |  80474325.7151 |
| D          | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |  15276 |  6892.9538 | 15060.0036 |    1.3085 |    0.1009 |  80474325.7151 |
| D          | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |  15276 |  6571.5995 | 14934.5642 |    1.2475 |    0.0227 |  80474325.7151 |
| D          | nfc                 | Oral Solid Ordinary                                   | hierarchical_mean   |  57096 | 10382.3004 | 38948.6624 |    1.2159 |   -0.1591 | 487517535.4785 |
| D          | nfc                 | Oral Solid Ordinary                                   | catboost_none       |  57096 |  9909.8615 | 38822.2623 |    1.1606 |   -0.2299 | 487517535.4785 |
| D          | nfc                 | Oral Solid Ordinary                                   | catboost_both       |  57096 |  9691.0846 | 38809.2080 |    1.1350 |   -0.2688 | 487517535.4785 |
| D          | nfc                 | Oral Solid Retard                                     | hierarchical_mean   |   2400 |  7406.9507 | 10239.5439 |    1.6553 |    0.7128 |  10739076.6516 |
| D          | nfc                 | Oral Solid Retard                                     | catboost_none       |   2400 |  5355.2807 |  9178.2894 |    1.1968 |    0.0160 |  10739076.6516 |
| D          | nfc                 | Oral Solid Retard                                     | catboost_both       |   2400 |  5468.8704 |  9189.6521 |    1.2222 |    0.0667 |  10739076.6516 |
| D          | nfc                 | Oral Topical                                          | hierarchical_mean   |   2364 |  9645.4916 | 15591.7744 |    1.2093 |    0.1613 |  18855997.1411 |
| D          | nfc                 | Oral Topical                                          | catboost_none       |   2364 |  8505.6763 | 15601.6372 |    1.0664 |   -0.1918 |  18855997.1411 |
| D          | nfc                 | Oral Topical                                          | catboost_both       |   2364 |  8447.7652 | 15567.5251 |    1.0591 |   -0.1870 |  18855997.1411 |
| D          | nfc                 | Other systemic                                        | hierarchical_mean   |    444 |  6302.6348 |  8986.2185 |    1.9488 |    0.6154 |   1435911.7768 |
| D          | nfc                 | Other systemic                                        | catboost_none       |    444 |  6271.7951 |  9033.8997 |    1.9393 |    0.5462 |   1435911.7768 |
| D          | nfc                 | Other systemic                                        | catboost_both       |    444 |  5726.1116 |  8571.4178 |    1.7706 |    0.4565 |   1435911.7768 |
| D          | nfc                 | Otic                                                  | hierarchical_mean   |    276 |  7725.7199 | 14018.4269 |    0.7954 |   -0.4739 |   2680708.7993 |
| D          | nfc                 | Otic                                                  | catboost_none       |    276 |  7995.4341 | 13819.3040 |    0.8232 |   -0.3660 |   2680708.7993 |
| D          | nfc                 | Otic                                                  | catboost_both       |    276 |  7810.1890 | 13690.3594 |    0.8041 |   -0.3787 |   2680708.7993 |
| D          | nfc                 | Parenteral Ordinary                                   | hierarchical_mean   |  24984 |  6336.4844 | 12538.4595 |    2.1940 |    1.0653 |  72157131.9825 |
| D          | nfc                 | Parenteral Ordinary                                   | catboost_none       |  24984 |  5275.9947 | 12113.0676 |    1.8268 |    0.5161 |  72157131.9825 |
| D          | nfc                 | Parenteral Ordinary                                   | catboost_both       |  24984 |  5231.0307 | 12077.3699 |    1.8112 |    0.5304 |  72157131.9825 |
| D          | nfc                 | Parenteral Retard                                     | hierarchical_mean   |    948 |  6175.9284 |  7559.8437 |    3.3980 |    3.3319 |   1723023.0513 |
| D          | nfc                 | Parenteral Retard                                     | catboost_none       |    948 |  3207.2652 |  3486.2601 |    1.7646 |    1.2315 |   1723023.0513 |
| D          | nfc                 | Parenteral Retard                                     | catboost_both       |    948 |  3683.9013 |  3945.6439 |    2.0269 |    1.6724 |   1723023.0513 |
| D          | nfc                 | Rectal systemic                                       | hierarchical_mean   |    912 |  5808.0498 |  7352.8372 |    1.2136 |    0.3302 |   4364761.6539 |
| D          | nfc                 | Rectal systemic                                       | catboost_none       |    912 |  5177.8640 |  6801.4030 |    1.0819 |    0.1243 |   4364761.6539 |
| D          | nfc                 | Rectal systemic                                       | catboost_both       |    912 |  5122.3020 |  6883.7832 |    1.0703 |    0.0411 |   4364761.6539 |
| D          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | hierarchical_mean   |  12420 |  8059.2923 | 18855.5858 |    1.1319 |   -0.1756 |  88432486.4431 |
| D          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |  12420 |  8230.2865 | 18407.1804 |    1.1559 |   -0.0461 |  88432486.4431 |
| D          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |  12420 |  8193.8675 | 18480.2966 |    1.1508 |   -0.0620 |  88432486.4431 |
| D          | nfc                 | Vaginal                                               | hierarchical_mean   |   1392 |  2880.5555 |  4037.0811 |    1.1439 |    0.0495 |   3505270.1401 |
| D          | nfc                 | Vaginal                                               | catboost_none       |   1392 |  3843.3786 |  4573.6991 |    1.5263 |    0.8336 |   3505270.1401 |
| D          | nfc                 | Vaginal                                               | catboost_both       |   1392 |  3502.2518 |  4194.8121 |    1.3908 |    0.6657 |   3505270.1401 |
| D          | volume_quintile     | Q1 (smallest)                                         | hierarchical_mean   |  24924 |  6046.7254 |  7114.1746 |  855.6429 |  855.6429 |    176134.9101 |
| D          | volume_quintile     | Q1 (smallest)                                         | catboost_none       |  24924 |  5538.0624 |  5848.1540 |  783.6645 |  783.6645 |    176134.9101 |
| D          | volume_quintile     | Q1 (smallest)                                         | catboost_both       |  24924 |  5228.5088 |  5478.9253 |  739.8610 |  739.8610 |    176134.9101 |
| D          | volume_quintile     | Q2                                                    | hierarchical_mean   |  24912 |  6656.1656 |  7533.1589 |   29.2414 |   29.2237 |   5670674.1712 |
| D          | volume_quintile     | Q2                                                    | catboost_none       |  24912 |  5330.1655 |  5632.5667 |   23.4161 |   23.4161 |   5670674.1712 |
| D          | volume_quintile     | Q2                                                    | catboost_both       |  24912 |  5219.3350 |  5484.7286 |   22.9292 |   22.9292 |   5670674.1712 |
| D          | volume_quintile     | Q3                                                    | hierarchical_mean   |  24912 |  6174.1361 |  7008.1514 |    5.5245 |    5.4961 |  27841259.4972 |
| D          | volume_quintile     | Q3                                                    | catboost_none       |  24912 |  4783.8579 |  5262.1577 |    4.2805 |    4.2757 |  27841259.4972 |
| D          | volume_quintile     | Q3                                                    | catboost_both       |  24912 |  4614.9823 |  4974.2729 |    4.1294 |    4.1249 |  27841259.4972 |
| D          | volume_quintile     | Q4                                                    | hierarchical_mean   |  24912 |  4145.1526 |  5139.9597 |    1.0833 |    0.9389 |  95321308.4847 |
| D          | volume_quintile     | Q4                                                    | catboost_none       |  24912 |  2813.3638 |  3687.5859 |    0.7353 |    0.5875 |  95321308.4847 |
| D          | volume_quintile     | Q4                                                    | catboost_both       |  24912 |  2708.9757 |  3440.2399 |    0.7080 |    0.5571 |  95321308.4847 |
| D          | volume_quintile     | Q5 (largest)                                          | hierarchical_mean   |  24912 | 22009.7618 | 64468.7888 |    0.7744 |   -0.7418 | 708086007.6341 |
| D          | volume_quintile     | Q5 (largest)                                          | catboost_none       |  24912 | 22524.4889 | 64642.6460 |    0.7925 |   -0.7763 | 708086007.6341 |
| D          | volume_quintile     | Q5 (largest)                                          | catboost_both       |  24912 | 22552.7227 | 64675.6140 |    0.7935 |   -0.7800 | 708086007.6341 |
| D          | known_atc_depth     | 0                                                     | hierarchical_mean   |  16320 |  8762.7268 | 24098.4154 |    1.4017 |    0.1850 | 102021242.0094 |
| D          | known_atc_depth     | 0                                                     | catboost_none       |  16320 |  8006.6278 | 24091.5962 |    1.2808 |   -0.0566 | 102021242.0094 |
| D          | known_atc_depth     | 0                                                     | catboost_both       |  16320 |  7698.5417 | 23972.3060 |    1.2315 |   -0.1133 | 102021242.0094 |
| D          | known_atc_depth     | 1                                                     | hierarchical_mean   | 108252 |  9042.7945 | 30183.0171 |    1.3317 |    0.0201 | 735074142.6879 |
| D          | known_atc_depth     | 1                                                     | catboost_none       | 108252 |  8226.5422 | 29980.1967 |    1.2115 |   -0.1334 | 735074142.6879 |
| D          | known_atc_depth     | 1                                                     | catboost_both       | 108252 |  8119.8232 | 29970.5295 |    1.1958 |   -0.1530 | 735074142.6879 |
| D1         | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | form_mean           |  19812 |  9421.2117 | 23788.0394 |    1.1952 |   -0.1230 | 156163888.1542 |
| D1         | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |  19812 |  8790.7495 | 24130.0006 |    1.1153 |   -0.3260 | 156163888.1542 |
| D1         | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |  19812 |  8579.0722 | 24174.1713 |    1.0884 |   -0.3778 | 156163888.1542 |
| D1         | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | form_mean           |   6408 |  7949.2389 | 22979.5049 |    1.1522 |   -0.3665 |  44209696.6824 |
| D1         | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |   6408 |  7316.3653 | 23413.2480 |    1.0605 |   -0.6090 |  44209696.6824 |
| D1         | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |   6408 |  7332.3391 | 23313.2412 |    1.0628 |   -0.6094 |  44209696.6824 |
| D1         | atc1                | C CARDIOVASCULAR SYSTEM                               | form_mean           |  16896 |  9791.2615 | 23261.9732 |    1.2765 |    0.1300 | 129594517.8649 |
| D1         | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |  16896 |  8167.6956 | 23115.7447 |    1.0649 |   -0.2517 | 129594517.8649 |
| D1         | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |  16896 |  8268.7112 | 23075.0790 |    1.0780 |   -0.2131 | 129594517.8649 |
| D1         | atc1                | D DERMATOLOGICAL                                      | form_mean           |   9192 |  8429.1353 | 18969.3488 |    1.1862 |   -0.0472 |  65320443.2641 |
| D1         | atc1                | D DERMATOLOGICAL                                      | catboost_none       |   9192 |  7907.1329 | 19048.7998 |    1.1127 |   -0.1840 |  65320443.2641 |
| D1         | atc1                | D DERMATOLOGICAL                                      | catboost_both       |   9192 |  8043.8086 | 19070.2330 |    1.1319 |   -0.1430 |  65320443.2641 |
| D1         | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | form_mean           |   6840 |  7142.3411 |  9224.0119 |    2.4367 |    1.7743 |  20048678.2291 |
| D1         | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |   6840 |  5144.6235 |  7608.3594 |    1.7552 |    0.9416 |  20048678.2291 |
| D1         | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |   6840 |  5141.5496 |  7558.9877 |    1.7541 |    0.9413 |  20048678.2291 |
| D1         | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | form_mean           |   1320 |  5884.6525 |  8000.8882 |    1.2772 |    0.3934 |   6081661.8168 |
| D1         | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |   1320 |  5562.4326 |  7735.3408 |    1.2073 |    0.1670 |   6081661.8168 |
| D1         | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |   1320 |  5459.2796 |  7700.1816 |    1.1849 |    0.1410 |   6081661.8168 |
| D1         | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | form_mean           |  12384 |  6787.0326 | 11172.6731 |    1.7836 |    0.7605 |  47123384.3838 |
| D1         | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |  12384 |  8147.2806 | 13051.7509 |    2.1411 |    1.1435 |  47123384.3838 |
| D1         | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |  12384 |  7786.5498 | 12729.5512 |    2.0463 |    1.0355 |  47123384.3838 |
| D1         | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | form_mean           |   5808 |  5838.5011 |  6593.6601 |   15.0410 |   14.7040 |   2254504.3781 |
| D1         | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |   5808 |  5481.5555 |  5701.3273 |   14.1215 |   13.8165 |   2254504.3781 |
| D1         | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |   5808 |  5567.0416 |  5758.6033 |   14.3417 |   13.9558 |   2254504.3781 |
| D1         | atc1                | M MUSCULO-SCELETAL SYSTEM                             | form_mean           |   9324 |  8861.8608 | 16803.0413 |    1.2390 |    0.0650 |  66691266.7312 |
| D1         | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |   9324 |  8566.6930 | 16798.2531 |    1.1977 |    0.0304 |  66691266.7312 |
| D1         | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |   9324 |  8507.7909 | 16709.9343 |    1.1895 |    0.0340 |  66691266.7312 |
| D1         | atc1                | N NERVOUS SYSTEM                                      | form_mean           |  18276 | 11416.6854 | 59018.5079 |    1.3511 |   -0.1380 | 154435686.4066 |
| D1         | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |  18276 | 10936.4133 | 58952.0881 |    1.2942 |   -0.1773 | 154435686.4066 |
| D1         | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |  18276 | 10892.8614 | 58915.4098 |    1.2891 |   -0.1758 | 154435686.4066 |
| D1         | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | form_mean           |    552 |  8746.3154 | 14710.6453 |    1.1103 |    0.1136 |   4348454.3248 |
| D1         | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |    552 |  8023.8218 | 15266.6691 |    1.0186 |   -0.1714 |   4348454.3248 |
| D1         | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |    552 |  8098.2139 | 15235.0250 |    1.0280 |   -0.1512 |   4348454.3248 |
| D1         | atc1                | R RESPIRATORY SYSTEM                                  | form_mean           |  13080 | 10845.5072 | 29020.5163 |    1.1765 |   -0.2273 | 120574346.4776 |
| D1         | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |  13080 |  9877.9130 | 29164.1744 |    1.0716 |   -0.4306 | 120574346.4776 |
| D1         | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |  13080 | 10139.6376 | 29174.1838 |    1.1000 |   -0.3622 | 120574346.4776 |
| D1         | atc1                | S SENSORY ORGANS                                      | form_mean           |   3168 |  5638.6513 | 12388.1176 |    0.9646 |   -0.8323 |  18518453.4023 |
| D1         | atc1                | S SENSORY ORGANS                                      | catboost_none       |   3168 |  5705.3341 | 11639.6216 |    0.9760 |   -0.4282 |  18518453.4023 |
| D1         | atc1                | S SENSORY ORGANS                                      | catboost_both       |   3168 |  5918.3518 | 11493.3682 |    1.0125 |   -0.3118 |  18518453.4023 |
| D1         | atc1                | V VARIOUS                                             | form_mean           |   1512 |  5214.3078 |  6773.7685 |    4.5562 |    3.3288 |   1730402.5813 |
| D1         | atc1                | V VARIOUS                                             | catboost_none       |   1512 |  5596.3259 |  6572.0593 |    4.8900 |    3.7774 |   1730402.5813 |
| D1         | atc1                | V VARIOUS                                             | catboost_both       |   1512 |  4872.0997 |  5988.1953 |    4.2572 |    3.0933 |   1730402.5813 |
| D1         | nfc                 | Lung Administration                                   | form_mean           |    912 |  8121.4287 | 14644.7764 |    1.5749 |    0.3924 |   4702968.7722 |
| D1         | nfc                 | Lung Administration                                   | catboost_none       |    912 |  5504.5740 | 14564.9212 |    1.0674 |   -0.3833 |   4702968.7722 |
| D1         | nfc                 | Lung Administration                                   | catboost_both       |    912 |  5904.3650 | 14573.5804 |    1.1450 |   -0.2491 |   4702968.7722 |
| D1         | nfc                 | Nasal Topical                                         | form_mean           |   2064 | 20638.7365 | 61957.2285 |    0.9653 |   -0.7319 |  44130543.7721 |
| D1         | nfc                 | Nasal Topical                                         | catboost_none       |   2064 | 20129.6572 | 62440.1220 |    0.9415 |   -0.8410 |  44130543.7721 |
| D1         | nfc                 | Nasal Topical                                         | catboost_both       |   2064 | 20059.0382 | 62350.5172 |    0.9382 |   -0.8187 |  44130543.7721 |
| D1         | nfc                 | Nasal systemic                                        | form_mean           |     84 |  3234.9863 |  4206.1776 |    1.2406 |   -0.2198 |    219032.5998 |
| D1         | nfc                 | Nasal systemic                                        | catboost_none       |     84 |  3626.2663 |  3933.0073 |    1.3907 |    1.0330 |    219032.5998 |
| D1         | nfc                 | Nasal systemic                                        | catboost_both       |     84 |  3376.2023 |  3669.9903 |    1.2948 |    0.9139 |    219032.5998 |
| D1         | nfc                 | Non-Human Use and Others                              | form_mean           |     84 |  3259.8887 |  4917.3089 |    1.6334 |    0.6773 |    167643.8290 |
| D1         | nfc                 | Non-Human Use and Others                              | catboost_none       |     84 |  3178.7321 |  3683.6626 |    1.5927 |    0.9252 |    167643.8290 |
| D1         | nfc                 | Non-Human Use and Others                              | catboost_both       |     84 |  3219.5377 |  3700.5690 |    1.6132 |    0.9704 |    167643.8290 |
| D1         | nfc                 | Ophthalmic                                            | form_mean           |   2916 |  5391.1481 | 12247.1386 |    0.9832 |   -0.9292 |  15988966.8910 |
| D1         | nfc                 | Ophthalmic                                            | catboost_none       |   2916 |  5519.4361 | 11321.4654 |    1.0066 |   -0.3943 |  15988966.8910 |
| D1         | nfc                 | Ophthalmic                                            | catboost_both       |   2916 |  5757.6549 | 11207.7225 |    1.0501 |   -0.2871 |  15988966.8910 |
| D1         | nfc                 | Oral Liquid Ordinary                                  | form_mean           |  15276 |  7483.2772 | 15385.9295 |    1.4205 |    0.2312 |  80474325.7151 |
| D1         | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |  15276 |  6417.0062 | 15118.8651 |    1.2181 |   -0.0921 |  80474325.7151 |
| D1         | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |  15276 |  6215.6686 | 14964.9171 |    1.1799 |   -0.1128 |  80474325.7151 |
| D1         | nfc                 | Oral Solid Ordinary                                   | form_mean           |  57096 | 11622.3856 | 38899.7682 |    1.3612 |    0.0852 | 487517535.4785 |
| D1         | nfc                 | Oral Solid Ordinary                                   | catboost_none       |  57096 | 10768.6356 | 39028.0568 |    1.2612 |   -0.0943 | 487517535.4785 |
| D1         | nfc                 | Oral Solid Ordinary                                   | catboost_both       |  57096 | 10722.6373 | 39007.4892 |    1.2558 |   -0.0998 | 487517535.4785 |
| D1         | nfc                 | Oral Solid Retard                                     | form_mean           |   2400 |  5476.5046 |  9332.8120 |    1.2239 |    0.0270 |  10739076.6516 |
| D1         | nfc                 | Oral Solid Retard                                     | catboost_none       |   2400 |  5552.1612 |  9584.1901 |    1.2408 |   -0.0590 |  10739076.6516 |
| D1         | nfc                 | Oral Solid Retard                                     | catboost_both       |   2400 |  5593.4436 |  9614.4715 |    1.2500 |   -0.0596 |  10739076.6516 |
| D1         | nfc                 | Oral Topical                                          | form_mean           |   2364 |  8701.4169 | 16059.4024 |    1.0909 |   -0.2251 |  18855997.1411 |
| D1         | nfc                 | Oral Topical                                          | catboost_none       |   2364 |  8002.6035 | 15993.3416 |    1.0033 |   -0.4431 |  18855997.1411 |
| D1         | nfc                 | Oral Topical                                          | catboost_both       |   2364 |  8493.2005 | 16092.4940 |    1.0648 |   -0.3137 |  18855997.1411 |
| D1         | nfc                 | Other systemic                                        | form_mean           |    444 |  5551.3413 |  9272.6440 |    1.7165 |    0.0951 |   1435911.7768 |
| D1         | nfc                 | Other systemic                                        | catboost_none       |    444 |  5584.8312 |  8485.0078 |    1.7269 |    0.3796 |   1435911.7768 |
| D1         | nfc                 | Other systemic                                        | catboost_both       |    444 |  5740.8207 |  8524.5545 |    1.7751 |    0.4378 |   1435911.7768 |
| D1         | nfc                 | Otic                                                  | form_mean           |    276 |  8078.0101 | 13349.3097 |    0.8317 |   -0.2577 |   2680708.7993 |
| D1         | nfc                 | Otic                                                  | catboost_none       |    276 |  7818.8285 | 14419.9572 |    0.8050 |   -0.6476 |   2680708.7993 |
| D1         | nfc                 | Otic                                                  | catboost_both       |    276 |  7809.1491 | 14013.5518 |    0.8040 |   -0.4787 |   2680708.7993 |
| D1         | nfc                 | Parenteral Ordinary                                   | form_mean           |  24984 |  4601.9111 | 12029.5043 |    1.5934 |    0.1888 |  72157131.9825 |
| D1         | nfc                 | Parenteral Ordinary                                   | catboost_none       |  24984 |  4895.7055 | 12190.5734 |    1.6951 |    0.2778 |  72157131.9825 |
| D1         | nfc                 | Parenteral Ordinary                                   | catboost_both       |  24984 |  4835.5689 | 12069.3957 |    1.6743 |    0.2730 |  72157131.9825 |
| D1         | nfc                 | Parenteral Retard                                     | form_mean           |    948 |  2448.2186 |  3258.2414 |    1.3470 |   -0.1055 |   1723023.0513 |
| D1         | nfc                 | Parenteral Retard                                     | catboost_none       |    948 |  3157.7750 |  3945.9893 |    1.7374 |    0.3042 |   1723023.0513 |
| D1         | nfc                 | Parenteral Retard                                     | catboost_both       |    948 |  3196.1622 |  4002.1455 |    1.7585 |    0.3533 |   1723023.0513 |
| D1         | nfc                 | Rectal systemic                                       | form_mean           |    912 |  5089.3147 |  6994.1924 |    1.0634 |   -0.0134 |   4364761.6539 |
| D1         | nfc                 | Rectal systemic                                       | catboost_none       |    912 |  4764.5812 |  6808.5965 |    0.9955 |    0.0097 |   4364761.6539 |
| D1         | nfc                 | Rectal systemic                                       | catboost_both       |    912 |  4582.8579 |  6731.5785 |    0.9576 |   -0.0909 |   4364761.6539 |
| D1         | nfc                 | Topical Dermatological, Haemorrhoidal, External       | form_mean           |  12420 |  8554.9533 | 18573.9804 |    1.2015 |    0.0131 |  88432486.4431 |
| D1         | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |  12420 |  7963.8701 | 18589.0179 |    1.1185 |   -0.1414 |  88432486.4431 |
| D1         | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |  12420 |  8081.1421 | 18635.6741 |    1.1350 |   -0.1051 |  88432486.4431 |
| D1         | nfc                 | Vaginal                                               | form_mean           |   1392 |  5766.2970 |  6462.7484 |    2.2899 |    1.9389 |   3505270.1401 |
| D1         | nfc                 | Vaginal                                               | catboost_none       |   1392 |  3850.7039 |  4442.1387 |    1.5292 |    0.9505 |   3505270.1401 |
| D1         | nfc                 | Vaginal                                               | catboost_both       |   1392 |  3921.5804 |  4533.6677 |    1.5573 |    0.9527 |   3505270.1401 |
| D1         | volume_quintile     | Q1 (smallest)                                         | form_mean           |  24924 |  6319.2590 |  7114.1235 |  894.2078 |  894.2062 |    176134.9101 |
| D1         | volume_quintile     | Q1 (smallest)                                         | catboost_none       |  24924 |  5584.2195 |  6741.9830 |  790.1959 |  790.1959 |    176134.9101 |
| D1         | volume_quintile     | Q1 (smallest)                                         | catboost_both       |  24924 |  5489.5106 |  6708.6952 |  776.7941 |  776.7941 |    176134.9101 |
| D1         | volume_quintile     | Q2                                                    | form_mean           |  24912 |  6517.3039 |  7282.5569 |   28.6314 |   28.6197 |   5670674.1712 |
| D1         | volume_quintile     | Q2                                                    | catboost_none       |  24912 |  5347.8235 |  6365.8438 |   23.4937 |   23.4883 |   5670674.1712 |
| D1         | volume_quintile     | Q2                                                    | catboost_both       |  24912 |  5363.7190 |  6471.1030 |   23.5635 |   23.5547 |   5670674.1712 |
| D1         | volume_quintile     | Q3                                                    | form_mean           |  24912 |  5994.5949 |  6777.9289 |    5.3639 |    5.3095 |  27841259.4972 |
| D1         | volume_quintile     | Q3                                                    | catboost_none       |  24912 |  4883.3223 |  6454.1879 |    4.3695 |    4.3261 |  27841259.4972 |
| D1         | volume_quintile     | Q3                                                    | catboost_both       |  24912 |  4850.0781 |  6218.1097 |    4.3398 |    4.2845 |  27841259.4972 |
| D1         | volume_quintile     | Q4                                                    | form_mean           |  24912 |  4196.5701 |  5067.1719 |    1.0968 |    0.9106 |  95321308.4847 |
| D1         | volume_quintile     | Q4                                                    | catboost_none       |  24912 |  3324.3950 |  5414.2720 |    0.8688 |    0.6190 |  95321308.4847 |
| D1         | volume_quintile     | Q4                                                    | catboost_both       |  24912 |  3431.3452 |  5713.0109 |    0.8968 |    0.6423 |  95321308.4847 |
| D1         | volume_quintile     | Q5 (largest)                                          | form_mean           |  24912 | 21879.3648 | 64339.6190 |    0.7698 |   -0.7381 | 708086007.6341 |
| D1         | volume_quintile     | Q5 (largest)                                          | catboost_none       |  24912 | 22881.9522 | 64664.5686 |    0.8050 |   -0.7750 | 708086007.6341 |
| D1         | volume_quintile     | Q5 (largest)                                          | catboost_both       |  24912 | 22744.3142 | 64581.0573 |    0.8002 |   -0.7675 | 708086007.6341 |
| D1         | known_atc_depth     | 0                                                     | form_mean           | 124572 |  8981.1621 | 29375.0174 |    1.3365 |    0.0379 | 837095384.6973 |
| D1         | known_atc_depth     | 0                                                     | catboost_none       | 124572 |  8404.0708 | 29455.2528 |    1.2506 |   -0.1158 | 837095384.6973 |
| D1         | known_atc_depth     | 0                                                     | catboost_both       | 124572 |  8375.5154 | 29422.7897 |    1.2464 |   -0.1106 | 837095384.6973 |
| N          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | launch_age_mean     |    580 |  3417.3835 |  8634.8513 |    1.1091 |   -0.4334 |   1787173.7452 |
| N          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_none       |    580 |  2924.1936 |  8654.9699 |    0.9490 |   -0.7061 |   1787173.7452 |
| N          | atc1                | A ALIMENTARY TRACT AND METABOLISM                     | catboost_both       |    580 |  2888.5666 |  8293.7595 |    0.9374 |   -0.6682 |   1787173.7452 |
| N          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | launch_age_mean     |     90 |  1781.6215 |  2149.1818 |    2.2926 |    1.2482 |     69941.2705 |
| N          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_none       |     90 |   678.9152 |  1106.6480 |    0.8736 |    0.1828 |     69941.2705 |
| N          | atc1                | B BLOOD AND BLOOD FORMING ORGANS                      | catboost_both       |     90 |   649.2009 |  1149.9968 |    0.8354 |    0.1156 |     69941.2705 |
| N          | atc1                | C CARDIOVASCULAR SYSTEM                               | launch_age_mean     |    535 |  2303.3253 |  5061.8580 |    1.2251 |   -0.0666 |   1005895.4482 |
| N          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_none       |    535 |  1720.9996 |  5083.8891 |    0.9153 |   -0.5932 |   1005895.4482 |
| N          | atc1                | C CARDIOVASCULAR SYSTEM                               | catboost_both       |    535 |  1845.8683 |  5084.5640 |    0.9818 |   -0.4211 |   1005895.4482 |
| N          | atc1                | D DERMATOLOGICAL                                      | launch_age_mean     |    337 |  2462.8516 |  4355.6367 |    1.0354 |   -0.2636 |    801587.4898 |
| N          | atc1                | D DERMATOLOGICAL                                      | catboost_none       |    337 |  2128.7348 |  4036.4997 |    0.8950 |   -0.4195 |    801587.4898 |
| N          | atc1                | D DERMATOLOGICAL                                      | catboost_both       |    337 |  2038.0412 |  4122.1956 |    0.8568 |   -0.5527 |    801587.4898 |
| N          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | launch_age_mean     |    223 |  1483.7755 |  1546.7681 |    4.2070 |    3.9768 |     78650.1302 |
| N          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_none       |    223 |   438.5989 |   632.2549 |    1.2436 |    0.4919 |     78650.1302 |
| N          | atc1                | G GENITO URINARY SYSTEM AND SEX HORMONES              | catboost_both       |    223 |   357.6062 |   623.8395 |    1.0139 |   -0.1149 |     78650.1302 |
| N          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | launch_age_mean     |     37 |  1569.9667 |  1610.7668 |   22.6323 |   22.6323 |      2566.6300 |
| N          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_none       |     37 |   209.8440 |   233.6412 |    3.0251 |    3.0251 |      2566.6300 |
| N          | atc1                | H SYSTEMIC HORMONAL PREPARATIONS, EXCL. SEX HORMONES  | catboost_both       |     37 |   729.9688 |   892.1960 |   10.5231 |   10.5231 |      2566.6300 |
| N          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | launch_age_mean     |    347 |  2313.8840 |  5068.0311 |    1.7584 |    0.2815 |    456608.5960 |
| N          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_none       |    347 |  1572.6762 |  4954.5645 |    1.1952 |   -0.4379 |    456608.5960 |
| N          | atc1                | J GENERAL ANTIINFECTIVES FOR SYSTEMIC USE             | catboost_both       |    347 |  1307.4338 |  4963.6146 |    0.9936 |   -0.6523 |    456608.5960 |
| N          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | launch_age_mean     |    181 |  1856.2780 |  2183.3694 |    4.3535 |    2.9937 |     77175.6194 |
| N          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_none       |    181 |   928.4087 |  1773.9300 |    2.1774 |    0.5534 |     77175.6194 |
| N          | atc1                | L ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS          | catboost_both       |    181 |   430.7881 |  1776.2159 |    1.0103 |   -0.8876 |     77175.6194 |
| N          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | launch_age_mean     |    585 |  4448.5088 | 11194.2610 |    0.9458 |   -0.6227 |   2751603.6673 |
| N          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_none       |    585 |  4307.9360 | 11173.2668 |    0.9159 |   -0.7586 |   2751603.6673 |
| N          | atc1                | M MUSCULO-SCELETAL SYSTEM                             | catboost_both       |    585 |  4193.5557 | 11163.0612 |    0.8916 |   -0.7115 |   2751603.6673 |
| N          | atc1                | N NERVOUS SYSTEM                                      | launch_age_mean     |    670 |  2591.1441 |  9040.2225 |    1.4011 |   -0.0544 |   1239070.6766 |
| N          | atc1                | N NERVOUS SYSTEM                                      | catboost_none       |    670 |  1964.4073 |  8959.6228 |    1.0622 |   -0.4845 |   1239070.6766 |
| N          | atc1                | N NERVOUS SYSTEM                                      | catboost_both       |    670 |  1948.6772 |  8477.4533 |    1.0537 |   -0.4833 |   1239070.6766 |
| N          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | launch_age_mean     |     13 |  2069.5833 |  2557.6882 |    0.6734 |   -0.4613 |     39952.3895 |
| N          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_none       |     13 |  2499.4266 |  3057.0261 |    0.8133 |   -0.6820 |     39952.3895 |
| N          | atc1                | P ANTIPARASITIC PRODUCTS, INSECTICIDES AND REPELLENTS | catboost_both       |     13 |  2394.7752 |  2739.6406 |    0.7792 |   -0.4842 |     39952.3895 |
| N          | atc1                | R RESPIRATORY SYSTEM                                  | launch_age_mean     |    489 |  5736.2748 | 14337.1548 |    0.9609 |   -0.6982 |   2919073.5441 |
| N          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_none       |    489 |  5402.3477 | 14152.4498 |    0.9050 |   -0.7718 |   2919073.5441 |
| N          | atc1                | R RESPIRATORY SYSTEM                                  | catboost_both       |    489 |  5346.8968 | 13888.3021 |    0.8957 |   -0.7305 |   2919073.5441 |
| N          | atc1                | S SENSORY ORGANS                                      | launch_age_mean     |     74 |  1301.8860 |  1393.7665 |    2.7419 |    2.7198 |     35135.7105 |
| N          | atc1                | S SENSORY ORGANS                                      | catboost_none       |     74 |   504.0282 |   670.9658 |    1.0615 |    0.4529 |     35135.7105 |
| N          | atc1                | S SENSORY ORGANS                                      | catboost_both       |     74 |   434.4704 |   524.9061 |    0.9150 |    0.4352 |     35135.7105 |
| N          | atc1                | V VARIOUS                                             | launch_age_mean     |     98 |  1705.2009 |  1757.8911 |   59.2657 |   59.2657 |      2819.6700 |
| N          | atc1                | V VARIOUS                                             | catboost_none       |     98 |   534.5490 |   762.7341 |   18.5787 |   18.5787 |      2819.6700 |
| N          | atc1                | V VARIOUS                                             | catboost_both       |     98 |   270.8442 |   509.7095 |    9.4134 |    8.8143 |      2819.6700 |
| N          | nfc                 | Lung Administration                                   | launch_age_mean     |     24 |  1495.4304 |  1562.7451 |    4.4885 |    4.4885 |      7995.9899 |
| N          | nfc                 | Lung Administration                                   | catboost_none       |     24 |   244.6292 |   291.2689 |    0.7343 |   -0.2183 |      7995.9899 |
| N          | nfc                 | Lung Administration                                   | catboost_both       |     24 |   516.6096 |   589.7480 |    1.5506 |    1.5506 |      7995.9899 |
| N          | nfc                 | Nasal Topical                                         | launch_age_mean     |     89 | 13170.5854 | 21696.2995 |    0.9187 |   -0.8754 |   1275887.1850 |
| N          | nfc                 | Nasal Topical                                         | catboost_none       |     89 | 12748.2827 | 20846.0223 |    0.8893 |   -0.8657 |   1275887.1850 |
| N          | nfc                 | Nasal Topical                                         | catboost_both       |     89 | 11942.8776 | 19869.7987 |    0.8331 |   -0.7932 |   1275887.1850 |
| N          | nfc                 | Non-Human Use and Others                              | launch_age_mean     |      6 |  1588.3399 |  1626.4843 |  119.9955 |  119.9955 |        79.4200 |
| N          | nfc                 | Non-Human Use and Others                              | catboost_none       |      6 |   340.1137 |   353.9285 |   25.6948 |   25.6948 |        79.4200 |
| N          | nfc                 | Non-Human Use and Others                              | catboost_both       |      6 |   442.7712 |   475.0897 |   33.4504 |   33.4504 |        79.4200 |
| N          | nfc                 | Ophthalmic                                            | launch_age_mean     |     66 |  1316.6950 |  1413.2691 |    2.6800 |    2.6560 |     32425.7404 |
| N          | nfc                 | Ophthalmic                                            | catboost_none       |     66 |   456.6631 |   631.0109 |    0.9295 |    0.2700 |     32425.7404 |
| N          | nfc                 | Ophthalmic                                            | catboost_both       |     66 |   440.4826 |   533.5891 |    0.8966 |    0.4082 |     32425.7404 |
| N          | nfc                 | Oral Liquid Ordinary                                  | launch_age_mean     |    491 |  2669.9018 |  5912.4778 |    1.3435 |   -0.1171 |    975759.8077 |
| N          | nfc                 | Oral Liquid Ordinary                                  | catboost_none       |    491 |  2132.2855 |  5976.3263 |    1.0730 |   -0.5339 |    975759.8077 |
| N          | nfc                 | Oral Liquid Ordinary                                  | catboost_both       |    491 |  2010.5928 |  5876.2233 |    1.0117 |   -0.5678 |    975759.8077 |
| N          | nfc                 | Oral Solid Ordinary                                   | launch_age_mean     |   1853 |  3213.4006 |  8475.8182 |    1.1287 |   -0.3843 |   5275304.7862 |
| N          | nfc                 | Oral Solid Ordinary                                   | catboost_none       |   1853 |  2757.9764 |  8476.9938 |    0.9688 |   -0.6472 |   5275304.7862 |
| N          | nfc                 | Oral Solid Ordinary                                   | catboost_both       |   1853 |  2702.0807 |  8184.4915 |    0.9491 |   -0.6261 |   5275304.7862 |
| N          | nfc                 | Oral Solid Retard                                     | launch_age_mean     |     52 |  1582.2341 |  1626.9599 |   12.8570 |   12.8570 |      6399.3500 |
| N          | nfc                 | Oral Solid Retard                                     | catboost_none       |     52 |   626.7421 |   757.4718 |    5.0928 |    5.0928 |      6399.3500 |
| N          | nfc                 | Oral Solid Retard                                     | catboost_both       |     52 |   434.5033 |   556.9335 |    3.5307 |    3.3465 |      6399.3500 |
| N          | nfc                 | Oral Topical                                          | launch_age_mean     |    194 |  5335.4274 | 16574.2637 |    0.8728 |   -0.7076 |   1185909.5402 |
| N          | nfc                 | Oral Topical                                          | catboost_none       |    194 |  5335.8143 | 16656.7318 |    0.8729 |   -0.7375 |   1185909.5402 |
| N          | nfc                 | Oral Topical                                          | catboost_both       |    194 |  5572.5880 | 16633.6527 |    0.9116 |   -0.7076 |   1185909.5402 |
| N          | nfc                 | Otic                                                  | launch_age_mean     |      8 |  1179.7113 |  1221.0415 |    3.4826 |    3.4826 |      2709.9701 |
| N          | nfc                 | Otic                                                  | catboost_none       |      8 |   894.7898 |   937.7437 |    2.6415 |    2.6415 |      2709.9701 |
| N          | nfc                 | Otic                                                  | catboost_both       |      8 |   384.8703 |   446.8794 |    1.1362 |    0.7577 |      2709.9701 |
| N          | nfc                 | Parenteral Ordinary                                   | launch_age_mean     |    951 |  1596.2686 |  1864.7040 |    2.9694 |    2.2189 |    511236.1828 |
| N          | nfc                 | Parenteral Ordinary                                   | catboost_none       |    951 |   636.5900 |  1310.8326 |    1.1842 |   -0.0152 |    511236.1828 |
| N          | nfc                 | Parenteral Ordinary                                   | catboost_both       |    951 |   536.1993 |  1214.1171 |    0.9974 |   -0.1241 |    511236.1828 |
| N          | nfc                 | Parenteral Retard                                     | launch_age_mean     |     24 |  1634.2547 |  1708.7849 |   21.9394 |   21.9394 |      1787.7500 |
| N          | nfc                 | Parenteral Retard                                     | catboost_none       |     24 |   307.4815 |   330.6483 |    4.1278 |    3.5222 |      1787.7500 |
| N          | nfc                 | Parenteral Retard                                     | catboost_both       |     24 |   334.1810 |   445.8199 |    4.4863 |    3.3754 |      1787.7500 |
| N          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | launch_age_mean     |    477 |  3952.1101 | 10643.9621 |    0.9618 |   -0.5712 |   1960103.7348 |
| N          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_none       |    477 |  3718.5261 | 10449.5498 |    0.9049 |   -0.6656 |   1960103.7348 |
| N          | nfc                 | Topical Dermatological, Haemorrhoidal, External       | catboost_both       |    477 |  3686.4799 | 10533.7015 |    0.8971 |   -0.6792 |   1960103.7348 |
| N          | nfc                 | Vaginal                                               | launch_age_mean     |     24 |  1138.5579 |  1186.2848 |    0.8632 |    0.3324 |     31655.1301 |
| N          | nfc                 | Vaginal                                               | catboost_none       |     24 |   969.3199 |  1373.6615 |    0.7349 |   -0.6700 |     31655.1301 |
| N          | nfc                 | Vaginal                                               | catboost_both       |     24 |  1063.0630 |  1454.5684 |    0.8060 |   -0.7788 |     31655.1301 |
| N          | volume_quintile     | Q1 (smallest)                                         | launch_age_mean     |    687 |  1698.4679 |  1755.5964 | 1374.8968 | 1374.8968 |       848.6800 |
| N          | volume_quintile     | Q1 (smallest)                                         | catboost_none       |    687 |   523.9524 |   721.0925 |  424.1354 |  424.1354 |       848.6800 |
| N          | volume_quintile     | Q1 (smallest)                                         | catboost_both       |    687 |   348.1437 |   574.5590 |  281.8196 |  281.7843 |       848.6800 |
| N          | volume_quintile     | Q2                                                    | launch_age_mean     |    642 |  1625.2170 |  1682.6756 |   52.0315 |   52.0315 |     20053.0400 |
| N          | volume_quintile     | Q2                                                    | catboost_none       |    642 |   652.4647 |   796.0158 |   20.8887 |   20.8801 |     20053.0400 |
| N          | volume_quintile     | Q2                                                    | catboost_both       |    642 |   531.8824 |   748.7780 |   17.0283 |   16.9810 |     20053.0400 |
| N          | volume_quintile     | Q3                                                    | launch_age_mean     |    857 |  1540.2216 |  1598.9587 |    7.4369 |    7.4000 |    177489.4901 |
| N          | volume_quintile     | Q3                                                    | catboost_none       |    857 |   638.4720 |   820.4303 |    3.0828 |    2.8897 |    177489.4901 |
| N          | volume_quintile     | Q3                                                    | catboost_both       |    857 |   566.9906 |   796.4330 |    2.7377 |    2.4790 |    177489.4901 |
| N          | volume_quintile     | Q4                                                    | launch_age_mean     |    999 |  1127.1624 |  1340.1495 |    1.1514 |    0.8316 |    977964.9496 |
| N          | volume_quintile     | Q4                                                    | catboost_none       |    999 |   726.7254 |  1157.7952 |    0.7424 |   -0.0213 |    977964.9496 |
| N          | volume_quintile     | Q4                                                    | catboost_both       |    999 |   892.8571 |  1497.1387 |    0.9121 |    0.1275 |    977964.9496 |
| N          | volume_quintile     | Q5 (largest)                                          | launch_age_mean     |   1074 |  7923.7967 | 16583.3436 |    0.8433 |   -0.8073 |  10090898.4276 |
| N          | volume_quintile     | Q5 (largest)                                          | catboost_none       |   1074 |  8159.0303 | 16554.9006 |    0.8684 |   -0.8387 |  10090898.4276 |
| N          | volume_quintile     | Q5 (largest)                                          | catboost_both       |   1074 |  7962.1480 | 16173.9319 |    0.8474 |   -0.8140 |  10090898.4276 |
| N          | inn_seen            | INN sold before 2023                                  | launch_age_mean     |   3847 |  3230.7430 |  8845.7485 |    1.1346 |   -0.3845 |  10953975.2082 |
| N          | inn_seen            | INN sold before 2023                                  | catboost_none       |   3847 |  2702.9418 |  8759.3503 |    0.9493 |   -0.6529 |  10953975.2082 |
| N          | inn_seen            | INN sold before 2023                                  | catboost_both       |   3847 |  2647.2495 |  8569.0987 |    0.9297 |   -0.6290 |  10953975.2082 |
| N          | inn_seen            | new INN                                               | launch_age_mean     |    113 |  1653.8464 |  2185.7766 |    1.7996 |    0.8071 |    103850.1299 |
| N          | inn_seen            | new INN                                               | catboost_none       |    113 |  1000.1306 |  1946.2595 |    1.0882 |   -0.2577 |    103850.1299 |
| N          | inn_seen            | new INN                                               | catboost_both       |    113 |   885.4325 |  2201.4224 |    0.9634 |   -0.6947 |    103850.1299 |
| N          | inn_seen            | no INN                                                | launch_age_mean     |    299 |  1842.2962 |  2399.2451 |    2.6302 |    1.5182 |    209429.2492 |
| N          | inn_seen            | no INN                                                | catboost_none       |    299 |  1015.2957 |  2188.2570 |    1.4495 |   -0.0695 |    209429.2492 |
| N          | inn_seen            | no INN                                                | catboost_both       |    299 |   755.3266 |  2079.5041 |    1.0784 |   -0.5105 |    209429.2492 |
| N          | twin                | has an older identical twin                           | launch_age_mean     |    871 |  4942.1817 | 12182.1795 |    0.9666 |   -0.6551 |   4453563.5875 |
| N          | twin                | has an older identical twin                           | catboost_none       |    871 |  4660.6658 | 12121.2579 |    0.9115 |   -0.7616 |   4453563.5875 |
| N          | twin                | has an older identical twin                           | catboost_both       |    871 |  4515.8914 | 11975.2533 |    0.8832 |   -0.7528 |   4453563.5875 |
| N          | twin                | no older twin                                         | launch_age_mean     |   3388 |  2615.6314 |  7166.7826 |    1.3006 |   -0.1310 |   6813690.9998 |
| N          | twin                | no older twin                                         | catboost_none       |   3388 |  1993.9095 |  7063.8420 |    0.9914 |   -0.5578 |   6813690.9998 |
| N          | twin                | no older twin                                         | catboost_both       |   3388 |  1941.1228 |  6859.5386 |    0.9652 |   -0.5455 |   6813690.9998 |
| N          | months_since_launch | 1                                                     | launch_age_mean     |    617 |  1674.0990 |  6233.3205 |    1.4833 |   -0.1905 |    696380.7955 |
| N          | months_since_launch | 1                                                     | catboost_none       |    617 |  1314.4272 |  6211.5870 |    1.1646 |   -0.5526 |    696380.7955 |
| N          | months_since_launch | 1                                                     | catboost_both       |    617 |  1305.1927 |  6176.9480 |    1.1564 |   -0.5310 |    696380.7955 |
| N          | months_since_launch | 2                                                     | launch_age_mean     |    578 |  2940.5380 |  8309.2417 |    1.2532 |   -0.3545 |   1356240.3439 |
| N          | months_since_launch | 2                                                     | catboost_none       |    578 |  2383.5185 |  8338.7989 |    1.0158 |   -0.7137 |   1356240.3439 |
| N          | months_since_launch | 2                                                     | catboost_both       |    578 |  2324.5988 |  8221.4930 |    0.9907 |   -0.7053 |   1356240.3439 |
| N          | months_since_launch | 3                                                     | launch_age_mean     |    525 |  3235.3254 |  9118.0602 |    1.1796 |   -0.3461 |   1439976.1174 |
| N          | months_since_launch | 3                                                     | catboost_none       |    525 |  2679.8380 |  9137.4753 |    0.9770 |   -0.6952 |   1439976.1174 |
| N          | months_since_launch | 3                                                     | catboost_both       |    525 |  2584.6336 |  8941.4521 |    0.9423 |   -0.6866 |   1439976.1174 |
| N          | months_since_launch | 4                                                     | launch_age_mean     |    482 |  3231.4698 |  8584.1503 |    1.1638 |   -0.3330 |   1338376.4905 |
| N          | months_since_launch | 4                                                     | catboost_none       |    482 |  2654.1614 |  8568.4625 |    0.9559 |   -0.6811 |   1338376.4905 |
| N          | months_since_launch | 4                                                     | catboost_both       |    482 |  2566.6148 |  8261.6139 |    0.9243 |   -0.6432 |   1338376.4905 |
| N          | months_since_launch | 5                                                     | launch_age_mean     |    439 |  3241.3670 |  9000.4952 |    1.1130 |   -0.4065 |   1278448.5386 |
| N          | months_since_launch | 5                                                     | catboost_none       |    439 |  2747.0261 |  8940.7635 |    0.9433 |   -0.6755 |   1278448.5386 |
| N          | months_since_launch | 5                                                     | catboost_both       |    439 |  2655.7098 |  8628.7090 |    0.9119 |   -0.6374 |   1278448.5386 |
| N          | months_since_launch | 6                                                     | launch_age_mean     |    399 |  3552.6096 |  9956.1682 |    1.0841 |   -0.4485 |   1307571.0900 |
| N          | months_since_launch | 6                                                     | catboost_none       |    399 |  3039.9989 |  9845.9423 |    0.9276 |   -0.6687 |   1307571.0900 |
| N          | months_since_launch | 6                                                     | catboost_both       |    399 |  2906.4827 |  9491.0725 |    0.8869 |   -0.6446 |   1307571.0900 |
| N          | months_since_launch | 7                                                     | launch_age_mean     |    342 |  3226.0498 |  8289.8060 |    1.1282 |   -0.3259 |    977894.3842 |
| N          | months_since_launch | 7                                                     | catboost_none       |    342 |  2661.4524 |  8067.3017 |    0.9308 |   -0.5715 |    977894.3842 |
| N          | months_since_launch | 7                                                     | catboost_both       |    342 |  2611.4039 |  7994.7747 |    0.9133 |   -0.5863 |    977894.3842 |
| N          | months_since_launch | 8                                                     | launch_age_mean     |    299 |  3522.2610 |  8058.3763 |    1.1508 |   -0.2863 |    915140.9364 |
| N          | months_since_launch | 8                                                     | catboost_none       |    299 |  2840.4137 |  7871.6209 |    0.9280 |   -0.5735 |    915140.9364 |
| N          | months_since_launch | 8                                                     | catboost_both       |    299 |  2751.2478 |  7794.9641 |    0.8989 |   -0.5828 |    915140.9364 |
| N          | months_since_launch | 9                                                     | launch_age_mean     |    236 |  4286.3644 |  9986.7088 |    1.0905 |   -0.4131 |    927610.2193 |
| N          | months_since_launch | 9                                                     | catboost_none       |    236 |  3584.6399 |  9681.6772 |    0.9120 |   -0.6319 |    927610.2193 |
| N          | months_since_launch | 9                                                     | catboost_both       |    236 |  3495.9798 |  9553.3187 |    0.8894 |   -0.6347 |    927610.2193 |
| N          | months_since_launch | 10                                                    | launch_age_mean     |    184 |  3702.4413 |  8417.9084 |    1.0964 |   -0.2585 |    621336.1114 |
| N          | months_since_launch | 10                                                    | catboost_none       |    184 |  2954.3309 |  8123.1922 |    0.8749 |   -0.5651 |    621336.1114 |
| N          | months_since_launch | 10                                                    | catboost_both       |    184 |  2910.5043 |  7965.1425 |    0.8619 |   -0.5677 |    621336.1114 |
| N          | months_since_launch | 11                                                    | launch_age_mean     |    104 |  3275.5799 |  6645.3246 |    1.1816 |   -0.0991 |    288311.6799 |
| N          | months_since_launch | 11                                                    | catboost_none       |    104 |  2470.8114 |  6239.9765 |    0.8913 |   -0.4661 |    288311.6799 |
| N          | months_since_launch | 11                                                    | catboost_both       |    104 |  2419.7872 |  6291.4255 |    0.8729 |   -0.5379 |    288311.6799 |
| N          | months_since_launch | 12                                                    | launch_age_mean     |     54 |  2728.2836 |  4370.4136 |    1.2281 |    0.0577 |    119967.8802 |
| N          | months_since_launch | 12                                                    | catboost_none       |     54 |  2129.0488 |  4164.3561 |    0.9583 |   -0.2821 |    119967.8802 |
| N          | months_since_launch | 12                                                    | catboost_both       |     54 |  2099.8892 |  3985.6265 |    0.9452 |   -0.2722 |    119967.8802 |
