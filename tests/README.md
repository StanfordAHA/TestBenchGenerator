### Python dependencies
```
pip install --user delegator.py pytest
```

### How to use
```
pytest --rtl-directory='../../CGRAGenerator/hardware/generator_z/top/genesis_verif' --files-to-copy sram_512w_16b.v DW_tap.v -s
```
