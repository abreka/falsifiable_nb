# Run a test

```bash
jupyter nbconvert --to falsifiable_nb.FalsifiableNB ./tests/fixtures/Untitled.ipynb
python3 -m http.server

poetry run falsifiable
```

