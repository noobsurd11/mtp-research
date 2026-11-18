# Predicted / pseudo-label class shares on the unlabelled pool: `ucf_pvs3_v2_ssl20_s0` (step 95700)

7,650 unlabelled images, whole image at shorter side 295; t_pos = 0.6. Confident pixel fraction: teacher 0.9937, student 0.9936.

| class | GT share, 1,912 labelled | teacher argmax share | teacher pseudo-label share (conf >= t_pos) | student argmax share | ratio teacher argmax / labelled GT | GT share, unlabelled pool (reference) |
|---|---|---|---|---|---|---|
| background | 0.91037 | 0.89064 | 0.89310 | 0.89017 | 0.98x | 0.91479 |
| crack | 0.06896 | 0.07522 | 0.07403 | 0.07524 | 1.09x | 0.06536 |
| contact | 0.01955 | 0.02387 | 0.02269 | 0.02422 | 1.22x | 0.01834 |
| interconnect | 0.00070 | 0.00066 | 0.00061 | 0.00067 | 0.95x | 0.00089 |
| corrosion | 0.00041 | 0.00960 | 0.00958 | 0.00970 | 23.19x | 0.00061 |
