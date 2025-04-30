# Auxiliary-Injector

Auxiliary-Injector is a lightweight Python tool designed to handle auxiliary data injection into processing pipelines, with a focus on flexibility and integration with astronomical alert systems and scheduling frameworks.

## Features

 - Ingestion of non-GW ToO event triggers (e.g., neutrino, gamma ray, and x-ray)
 - Interfaces cleanly with Slack 

## Installation

Clone the repository and install dependencies:

```
git clone https://github.com/SSantosLab/Auxiliary-Injector.git
cd Auxiliary-Injector
pip install -r requirements.txt
```

(You may also wish to install in a virtual environment.)

## Structure
```
Auxiliary-Injector/
├── listener.py                    # The top-level listener script that listens for ToO alerts
├── configs/                       # Folder containing credentials for gcn, slack, and email alerts
├── handlers/                      # Core package
│   ├── streamer.py                # Alert parsing, JSON handling, slack communication
│   ├── slack.py                   # Slack utilities
│   ├── emails.py                  # Email utilities
│   └── short_latency_plots.py     # Fast plots for quick analysis, posted to slack
├── data/exampleJsons/             # Example json files
├── tests/                         # Unit tests
├── requirements.txt               # Python dependencies
├── SOURCEFILE                     # A sourcefile used to activate the virtual environment
└── README.md                      # Project overview (this file)
```

## Contributing

Contributions are very welcome! Feel free to open an issue or submit a pull request if you have improvements, bugfixes, or new ideas.

Please follow standard GitHub workflows for feature branches and PR reviews.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).
