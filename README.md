<p align="center">
     <a><img src="https://github.com/royreznik/rexi/blob/master/docs/rexi.png" alt="Rexi"></a>
</p>

<p align="center">
     <a href="https://github.com/royreznik/greps/actions/workflows/tests.yml"><img src="https://github.com/royreznik/rexi/actions/workflows/tests.yml/badge.svg" alt="Testing"></a>
     <a href="https://img.shields.io/github/license/royreznik/rexi"><img src="https://img.shields.io/github/license/royreznik/rexi" alt="License"></a>
     <a href="https://codecov.io/gh/royreznik/rexi"><img src="https://codecov.io/gh/royreznik/rexi/graph/badge.svg?token=LOIYAMEI08" alt="coverage"></a>
     <a href="https://pypi.org/project/rexi/"><img src="https://img.shields.io/pypi/pyversions/rexi" alt="versions"></a>
     <img src="https://img.shields.io/badge/code%20style-black-black" alt="style">
</p>

---

`rexi` is a simple yet powerful CLI tool designed for developers, data scientists, and anyone interested in working with regular expressions directly from the terminal.
Built with Python and leveraging the `textual` library, `rexi` offers a user-friendly terminal UI to interactively work with regular expressions.
![Demo](https://github.com/royreznik/rexi/blob/master/docs/demo.gif)

## Features

- **Interactive UI:** Built on top of the `textual` library, providing a clean and intuitive interface to work with.
- **Regex Evaluation:** Supports evaluating regular expressions using either `match` or `finditer` modes, allowing users to select the most suitable method for their needs.
- **Real-time Feedback:** Instantly see how your regular expression patterns match or find iterations over your input, enhancing learning and debugging experiences.
- **Easy to Use:** Get started quickly with a simple command. `rexi` reads input directly from stdin, streamlining the process of testing regular expressions.


# Installation
```bash
pip install rexi
```

# Usage
```bash
cat /etc/hosts | rexi
```
Once the UI is open, you can:

1. **Write a Regex Pattern:** Enter your regex pattern in the designated input area.
2. **Choose a Mode:** Select either `match` or `finditer` to apply your regex pattern.
3. **View Results:** See the marked output based on your regex pattern and selected mode in real-time.

## Contributing

We welcome contributions from the community! Whether it's adding new features, fixing bugs, or improving documentation, your help is appreciated. Please see our contribution guidelines for more information on how to contribute to `rexi`.

`rexi` is here to make working with regular expressions in the terminal an easy and interactive experience. Try it out and see how it can streamline your regex testing and learning process!


## License
This project is licensed under the terms of the MIT license.

