# reality-sni-tester

This script creates a reality inbound in x-ui and test provided SNIs against it

## Usage

Clone the repo:

```bash
git clone https://github.com/miadabdi/reality-sni-tester.git
```

Copy configuration file and change it for your likings:

```
cp config.json.example config.json
```

Make sure there are no inbounds created in xui, with the reality port you provided, and then run:

```bash
python main.py
```

### Credit

Some files in this repo has been copied from: [CFScanner python](https://github.com/MortezaBashsiz/CFScanner/tree/main/python)
