# Predicted / pseudo-label class shares on the unlabelled pool: `ucf_pvs3_v2_ssl20_s0` (step 95700)

7,650 unlabelled images, whole image at shorter side 295; t_pos = 0.6. Confident pixel fraction: teacher 0.9937.

| class | GT share, 1,912 labelled | teacher argmax share | teacher pseudo-label share (conf >= t_pos) | student argmax share | ratio teacher argmax / labelled GT | GT share, unlabelled pool (reference) |
|---|---|---|---|---|---|---|
| background | 0.91037 | 0.89064 | 0.89310 | nan | 0.98x | 0.91479 |
| crack | 0.06896 | 0.07522 | 0.07403 | nan | 1.09x | 0.06536 |
| contact | 0.01955 | 0.02387 | 0.02269 | nan | 1.22x | 0.01834 |
| interconnect | 0.00070 | 0.00066 | 0.00061 | nan | 0.95x | 0.00089 |
| corrosion | 0.00041 | 0.00960 | 0.00958 | nan | 23.19x | 0.00061 |

Teacher pseudo-label share among pixels with confidence >= threshold (ratio to the labelled-GT share in brackets):

| threshold | confident fraction | background | crack | contact | interconnect | corrosion |
|---|---|---|---|---|---|---|
| 0.6 | 0.9937 | 0.89310 (0.98x) | 0.07403 (1.07x) | 0.02269 (1.16x) | 0.00061 (0.87x) | 0.00958 (23.15x) |
| 0.8 | 0.9788 | 0.89843 (0.99x) | 0.07118 (1.03x) | 0.02033 (1.04x) | 0.00047 (0.68x) | 0.00958 (23.15x) |
| 0.9 | 0.9656 | 0.90273 (0.99x) | 0.06870 (1.00x) | 0.01865 (0.95x) | 0.00037 (0.53x) | 0.00955 (23.06x) |
| 0.95 | 0.9518 | 0.90668 (1.00x) | 0.06630 (0.96x) | 0.01731 (0.89x) | 0.00027 (0.39x) | 0.00944 (22.80x) |
| 0.99 | 0.9117 | 0.91543 (1.01x) | 0.06069 (0.88x) | 0.01485 (0.76x) | 0.00007 (0.10x) | 0.00896 (21.64x) |
